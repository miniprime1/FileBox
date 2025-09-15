from flask import *

from pathlib import Path
import os
import csv
import secrets
import datetime as dt

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

INDEX_CSV = UPLOAD_DIR / "index.csv"
CSV_HEADERS = ["created_at", "uploader", "size", "password", "filename"]

MAX_MB = int(os.getenv("MAX_MB", "100"))
MAX_CONTENT_LENGTH = MAX_MB * 1024 * 1024

SERVICE_HOST = str(os.getenv("SERVICE_HOST", ""))
SERVICE_HOST_ENCODED = f"for {SERVICE_HOST}" if SERVICE_HOST != "" else ""

ANNONYMOUS_NAME = str(os.getenv("ANNONYMOUS_NAME", "Annonymous"))

app = Flask(__name__)
app.config.update(
    MAX_CONTENT_LENGTH=MAX_CONTENT_LENGTH,
    SECRET_KEY=os.getenv("FLASK_SECRET", secrets.token_hex(32)),
)

def ensure_index():
    if not INDEX_CSV.exists():
        with INDEX_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)

def read_index() -> list[dict]:
    ensure_index()
    rows: list[dict] = []
    with INDEX_CSV.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            r["size"] = int(r["size"]) if r.get("size") else 0
            r.setdefault("uploader", ANNONYMOUS_NAME)
            r.setdefault("password", "")
            rows.append(r)
    rows.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return rows

def append_index(created_at: str, uploader: str, size: int, password: str, filename: str) -> None:
    ensure_index()
    with INDEX_CSV.open("a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([created_at, uploader, size, password, filename])

def dedup_filename(target_name: str) -> str:
    safe = (target_name or "").replace("/", "_").replace("\\", "_")
    dest = UPLOAD_DIR / safe
    counter = 1
    while dest.exists():
        name, ext = os.path.splitext(safe)
        dest = UPLOAD_DIR / f"{name}({counter}){ext}"
        counter += 1
    return dest.name

with open('index.html', 'r', encoding='utf-8') as f:
    PAGE = f.read()

@app.get("/")
def index():
    rows = read_index()
    return render_template_string(PAGE, files=rows, max_mb=MAX_MB, service_host_encoded=SERVICE_HOST_ENCODED)

@app.post("/upload")
def upload():
    if "file" not in request.files:
        flash("파일이 첨부되지 않았습니다.")
        return redirect(url_for("index"))

    file = request.files["file"]
    password = (request.form.get("password") or "").strip()
    uploader = (request.form.get("uploader") or "").strip() or ANNONYMOUS_NAME

    if not file or not file.filename:
        flash("유효한 파일이 아닙니다.")
        return redirect(url_for("index"))

    original_name = os.path.basename(file.filename)
    stored_name = dedup_filename(original_name)
    dest = UPLOAD_DIR / stored_name
    file.save(dest)

    size = dest.stat().st_size
    created_at = dt.datetime.now().strftime("%Y-%m-%d %H:%M")

    append_index(created_at, uploader, size, password, stored_name)

    flash("업로드가 완료되었습니다.")
    return redirect(url_for("index"))

@app.post("/download")
def download():
    filename = (request.form.get("filename") or "").strip()
    provided_password = (request.form.get("password") or "").strip()

    if not filename:
        flash("파일명이 누락되었습니다.")
        return redirect(url_for("index"))

    rows = read_index()
    match = next((r for r in rows if r.get("filename") == filename), None)

    if not match:
        flash("해당 파일을 찾을 수 없습니다.")
        return redirect(url_for("index"))

    required_password = match.get("password", "")
    if required_password:
        if provided_password != required_password:
            flash("비밀번호가 올바르지 않습니다.")
            return redirect(url_for("index"))

    path = UPLOAD_DIR / filename
    if not path.exists():
        abort(410, description="파일이 더 이상 존재하지 않습니다.")

    return send_file(path, as_attachment=True, download_name=filename)

@app.get("/healthz")
def healthz():
    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
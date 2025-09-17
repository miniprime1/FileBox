from __future__ import annotations
import os
from pathlib import Path
from flask import *

BASE_DIR = Path(__file__).resolve().parent

app = Flask(__name__)

with open('index.html', 'r', encoding='utf-8') as f:
    PAGE = f.read()

@app.get("/")
def index():
    return render_template_string(PAGE)

@app.get("/healthz")
def healthz():
    return {"ok": True}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)

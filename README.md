# FileBox

FileBox is a lightweight, self-hosted file sharing service.
It runs on a single Flask app ([`main/`](./main/)) and stores metadata in a simple CSV file. No login is required—open the site, upload a file, (optionally) set a password, and share the page with others to download. For multi-instance setups, an optional, customizable landing page is available in [`gateway/`]((./gateway/)) to link multiple FileBox nodes, and a Dockerfile is included for containerizing it if needed.

<p align="center">
  <img src="./screenshot_2.png" alt="Screenshot" width="720">
</p>

## Features

- **One-page Web UI** – Upload & download in a single screen
- **Optional password** – Protect files with a simple password field
- **Optional uploader name** – Record who uploaded each file
- **CSV index** – Tracks upload time, uploader, size, password (plaintext), and filename
- **Docker-ready** – Build once and run anywhere

> **Note on security**: Passwords are stored as **plaintext** in `index.csv` by design for simplicity. Use only in trusted networks or adapt the code to hash passwords if you need stronger security.

## Getting Started (Main App)

The **core FileBox service** lives in the `main/` folder.  
Below are two common ways to run it. **Docker** is recommended for quick setup and persistence.

### A. Run with Docker

```bash
git clone https://github.com/miniprime1/FileBox.git
cd FileBox/main

docker build -t filebox:latest .
mkdir -p ./uploads

docker run -d \
  --name filebox \
  -p 8000:8000 \
  -e MAX_MB=100 \
  -e SERVICE_HOST="your name" \
  -e ANNONYMOUS_NAME="Anonymous" \
  -v "$(pwd)/uploads:/app/uploads" \
  filebox:latest
```

Visit **http://localhost:8000** (or replace `localhost` with your server/NAS IP).

### B. Run locally (Python)

```bash
cd main
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install Flask==3.0.3

export MAX_MB=100
export SERVICE_HOST="your name"
export ANNONYMOUS_NAME="Anonymous"

python main.py
```

Open **http://127.0.0.1:8000** in your browser.

## Configuration Reference

| Variable           | Default       | Description                                           |
|-------------------|-------------|-------------------------------------------------------|
| `MAX_MB`          | `100`       | Maximum upload size (MB). Also shown in UI header.   |
| `SERVICE_HOST`    | *(empty)*   | Optional label shown in the header.                  |
| `ANNONYMOUS_NAME` | `Anonymous` | Name displayed if no uploader is specified.          |

- **Internal storage path:** `/app/uploads`  
- **Index file:** `/app/uploads/index.csv` (auto-created with headers)

## Gateway (Optional)

<p align="center">
  <img src="./screenshot_1.png" alt="Screenshot" width="720">
</p>



This repository also includes a **`gateway/`** folder — a simple landing page that links multiple FileBox instances (e.g., for different classes or teams).

- The gateway app is intentionally minimal and **meant to be customized** (HTML buttons, style, links).
- A `Dockerfile` is provided in `gateway/` so you can containerize it if needed:
```bash
cd gateway
docker build -t filebox-gateway:latest .
docker run -d -p 8080:8000 filebox-gateway:latest
```

> Because each organization or school will have different URLs and design, you are encouraged to edit `templates/index.html` before deployment.

## License

This project is licensed under the [MIT License](LICENSE).

# Day 1 — One service, containerized, with a health check

**Before you start:** read lessons 01–05 of `~/dockyard-course/`. Day 1 assumes
you know what an image, a layer and a probe are.

**Time:** 60–90 minutes.
**Goal:** an API that answers three endpoints, runs in Docker as a non-root
user, and answers a real health check.

Type everything. Do not copy-paste the whole file at once. If something fails,
read the error before asking for help.

---

## 1. Create the folder

```bash
mkdir -p ~/delivery-platform/apps/api/app
cd ~/delivery-platform/apps/api
```

Your repo root is `~/delivery-platform`. Everything below is relative to
`apps/api/`.

---

## 2. The application

Create `app/main.py`:

```python
import os
import socket
import time

from fastapi import FastAPI, HTTPException

app = FastAPI(title="dockyard api", version=os.getenv("APP_VERSION", "dev"))

STARTED_AT = time.time()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "uptime_s": round(time.time() - STARTED_AT, 1),
    }


@app.get("/ready")
def ready():
    # Week 2: this will also check the database and the queue.
    return {"ready": True}


@app.get("/work")
def work(n: int = 1):
    if n < 1 or n > 100:
        raise HTTPException(status_code=400, detail="n must be between 1 and 100")
    return {
        "processed": n,
        "host": socket.gethostname(),
        "version": os.getenv("APP_VERSION", "dev"),
    }
```

Why three endpoints and not one:

- `/health` — **liveness**. Is the process alive? If this fails, restart it.
- `/ready` — **readiness**. Can it serve traffic? If this fails, stop sending
  traffic but do not restart.
- `/work` — a real unit of work, so the worker has something to call.

Confusing liveness and readiness is one of the most common production mistakes.

---

## 3. Dependencies

Create `requirements.txt`:

```text
fastapi==0.115.6
uvicorn[standard]==0.34.0
pytest==8.3.4
httpx==0.28.1
```

Create `requirements-dev.txt`:

```text
-r requirements.txt
```

Pinning versions is not decoration. `latest` means "a build that worked
yesterday can break tomorrow".

---

## 4. Run it without Docker first

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

In another terminal:

```bash
curl -s localhost:8000/health
curl -s "localhost:8000/work?n=3"
curl -s -o /dev/null -w "%{http_code}\n" "localhost:8000/work?n=0"
```

Expected:

- `{"status":"ok","uptime_s":...}`
- `{"processed":3,"host":"...","version":"dev"}`
- `400`

If `curl` says "connection refused", the server is not running. Check the
terminal.

Stop the server with `Ctrl+C`.

---

## 5. A test

Create `tests/test_main.py`:

```python
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ready():
    assert client.get("/ready").json() == {"ready": True}


def test_work_ok():
    body = client.get("/work", params={"n": 5}).json()
    assert body["processed"] == 5
    assert body["version"] == "dev"


def test_work_rejects_zero():
    assert client.get("/work", params={"n": 0}).status_code == 400
```

Run:

```bash
pytest -q
```

Four passing tests. If the import fails, run `pytest` from `apps/api`, not from
the repo root.

---

## 6. The Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt .
RUN python -m venv /opt/venv \
    && /opt/venv/bin/pip install -r requirements.txt

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /opt/venv /opt/venv
COPY app ./app

RUN useradd --create-home --shell /usr/sbin/nologin appuser
USER appuser

EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Why each part:

| Line | Reason |
| --- | --- |
| two `FROM` lines | the build tools and pip cache stay out of the final image |
| `COPY requirements.txt` before `COPY app` | dependency layer is cached; editing code does not reinstall |
| `venv` + `PATH` | dependencies isolated, same layout in both stages |
| `useradd` + `USER` | the container does not run as root |
| `HEALTHCHECK` | Docker itself can report unhealthy, not only Kubernetes |
| `PYTHONUNBUFFERED` | logs appear immediately, not at shutdown |
| `--host 0.0.0.0` | reachable from outside the container; `127.0.0.1` is not |

Create `.dockerignore`:

```text
.venv
__pycache__
*.pyc
.pytest_cache
tests
```

---

## 7. Build and run

```bash
docker build -t dockyard-api:dev .
docker run --rm -p 8000:8000 -e APP_VERSION=dev dockyard-api:dev
```

In another terminal:

```bash
curl -s localhost:8000/health
docker ps --format 'table {{.Names}}\t{{.Status}}'
```

You should see `(healthy)` after about 15 seconds. If it says `(unhealthy)`,
run:

```bash
docker inspect --format '{{json .State.Health}}' <container-id> | python3 -m json.tool
```

Read the last log line in the health output. It tells you the real error.

Check the user:

```bash
docker run --rm dockyard-api:dev whoami
```

Expected: `appuser`, not `root`.

Check the image size:

```bash
docker images dockyard-api:dev
```

Write the number down. It goes in `docs/measurements.md` later.

---

## 8. Commit

```bash
cd ~/delivery-platform
git init -b main
cat > .gitignore <<'EOF'
.venv/
__pycache__/
*.pyc
.pytest_cache/
.env
*.pem
EOF
git add -A
git commit -m "api: health, ready and work endpoints in a non-root container"
```

---

## Done when

- [ ] `pytest -q` passes 4 tests
- [ ] `docker ps` shows `(healthy)`
- [ ] `whoami` inside the container is `appuser`
- [ ] you can explain the difference between `/health` and `/ready`
- [ ] you wrote the image size in a note

## If you get stuck

| Symptom | Likely cause | Check |
| --- | --- | --- |
| `ModuleNotFoundError: app` | wrong folder | run from `apps/api` |
| `curl: connection refused` | container not running | `docker ps`, `docker logs` |
| `(unhealthy)` | app crashed or wrong port | `docker logs <id>` |
| `permission denied` on build | Docker group | `sudo usermod -aG docker $USER`, log out and back in |
| image is huge | copied `.venv` | check `.dockerignore` |

Next: `DAY-02.md` — the worker and Docker Compose.

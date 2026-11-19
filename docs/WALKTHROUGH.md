# Walkthrough — what we built, in simple steps

Last updated: 2026-11-19

Read this file when you come back. It explains everything we did up to now,
what is real, and what is still not done. No magic, no hidden steps.

How to use it: every step ends with **Test yourself**. Predict the answer
first, run the command, then say the explanation out loud without looking.
If you cannot explain it, reread that step.

---

## 0. The two folders (this caused confusion)

```
/home/mhd/
├── dockyard-course/      ← lessons only (.md files). This was your terminal folder.
└── delivery-platform/    ← THE PROJECT. All code is here. This is the git repo.
```

Open `/home/mhd/delivery-platform` in your editor, not `dockyard-course`.

Files starting with a dot are hidden by default: `.gitignore`, `.dockerignore`,
`.github/`, `.git/`. Enable "show hidden files" in the editor to see them.

---

> **Test yourself (30 s):** run `pwd`. If it says `dockyard-course`, you are in the lessons folder. Type `cd ../delivery-platform` and `ls apps/api`. Say out loud: "lessons = read, project = build".

## 1. The big picture in one line

```
your code → git commit → GitHub Actions tests → build image → push to GHCR
→ (later) kind cluster + ArgoCD pulls the image and runs it
```

We have built the first half. The cluster part is not built yet.

---

## 2. Day 1 — one API service

**Goal:** an API with three endpoints, running in Docker as a normal user, with
a working health check.

### Step 1: folders

```bash
mkdir -p apps/api/app apps/api/tests
```

`app/` = Python code. `tests/` = automatic checks. They are separate so tests
can import the code cleanly.

> **Test yourself (30 s):** `ls apps/api` → you should see `app` and `tests`. Say out loud why tests live in their own folder (clean imports and discovery).

### Step 2: `apps/api/app/main.py`

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

What the three doors mean:

| Door | Question it answers | If it fails |
|---|---|---|
| `/health` | Is the process alive? | restart it (liveness) |
| `/ready` | Can it serve traffic? | stop traffic, do not restart (readiness) |
| `/work?n=3` | Can it do a unit of work? | 400 for bad input |

`os.getenv` reads a setting from outside the file. Same image, different
settings — no rebuild needed.

> **Test yourself (2 min):** before running anything, predict the HTTP code for `/work?n=0` and for `/health`. Start the app and check with `curl -s -o /dev/null -w '%{http_code}\n' 'localhost:8000/work?n=0'`. Say out loud: `/health` answers "alive?", `/ready` answers "can take traffic?".

### Step 3: `apps/api/requirements.txt`

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
pytest==8.3.4
httpx==0.28.1
```

`==` = exactly this version. `latest` is dangerous because a build that worked
yesterday can break tomorrow. `requirements-dev.txt` only contains
`-r requirements.txt` for now.

> **Test yourself (1 min):** run `grep fastapi requirements.txt` → `fastapi==0.115.6`. Answer: what does `==` protect against? (A newer release changing behaviour overnight.)

### Step 4: run it on the host (no Docker yet)

```bash
cd apps/api
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

A virtual environment (`.venv`) is a private box for packages. It stops
projects on the same machine from fighting over versions.

`--host 0.0.0.0` means "listen on every network interface". `127.0.0.1` would
only answer from inside the same machine and would break in Docker.

From another terminal:

```bash
curl -s localhost:8000/health
curl -s 'localhost:8000/work?n=3'
curl -s -o /dev/null -w '%{http_code}\n' 'localhost:8000/work?n=0'
```

Real answers we saw:

```json
{"status":"ok","uptime_s":5.0}
{"processed":3,"host":"mhd-laptop","version":"dev"}
400
```

> **Test yourself (2 min):** while uvicorn runs with `--host 0.0.0.0`, run `ss -ltn | grep 8000` — you see `0.0.0.0:8000`. Restart with `--host 127.0.0.1`; the line changes. Explain which one another container could reach and why.

### Step 5: `apps/api/tests/test_main.py`

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

`assert` means "if this is false, fail the test". `TestClient` calls the app in
memory — no port needed.

> **Test yourself (2 min):** change one `assert` so it expects `404`, run `.venv/bin/pytest -q`, read which test fails and on which line, then restore the file. Say what the failing assert was proving.

### Step 6: the error we hit and the fix

`pytest -q` first failed:

```
ModuleNotFoundError: No module named 'app'
```

Cause: pytest added `tests/` to the import path, not the project folder. Fix —
`apps/api/pytest.ini`:

```
[pytest]
pythonpath = .
```

Result: **4 passed**. This file is now part of the repo, so the fix is
reproducible for anyone who clones it.

> **Test yourself (1 min):** rename `pytest.ini` to `pytest.ini.bak`, run pytest, read `ModuleNotFoundError` again, then restore. Explain what `pythonpath = .` adds.

### Step 7: `apps/api/Dockerfile`

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

Two `FROM` lines = two stages. Stage 1 installs packages; stage 2 copies only
the finished packages. Build tools and caches stay behind.

`COPY requirements.txt` before `COPY app`: Docker caches layers. Change code →
the slow dependency layer is reused.

`USER appuser`: never run as root. If the app is compromised, the attacker gets
a limited user, not root.

`HEALTHCHECK`: Docker calls `/health` every 15 seconds. Three failures in a row
→ container shows `(unhealthy)`.

> **Test yourself (2 min):** run `docker build -t dockyard-api:dev .` twice; find `CACHED` on the second run. Change one character in `app/main.py` and rebuild: what re-runs, what stays cached? Explain why `COPY requirements.txt` comes first.

### Step 8: `apps/api/.dockerignore`

```
.venv
__pycache__
*.pyc
.pytest_cache
tests
```

Without this, your host `.venv` (with Python 3.14 packages) would be sent into
a Python 3.12 image. Bad idea.

> **Test yourself (1 min):** predict what would enter the image if `.venv` were not ignored. Check `docker images dockyard-api:dev --format '{{.Size}}'` and explain why host packages must stay out.

### Step 9: build, run, check

```bash
cd apps/api
docker build -t dockyard-api:dev .
docker run -d --name dockyard-api-dev -p 8000:8000 -e APP_VERSION=dev dockyard-api:dev
curl -s localhost:8000/health
docker ps --format 'table {{.Names}}\t{{.Status}}'
docker run --rm dockyard-api:dev whoami
docker images dockyard-api:dev --format '{{.Size}}'
```

Real results: `(healthy)`, `appuser`, **259 MB**. The `/work` response showed
`host` as a container ID instead of `mhd-laptop` — proof the request was served
inside the container.

Small error we hit: `curl` exited with code 56 because it retried only
connection-refused, not an empty reply. The app simply needed a second more to
start. Repeating the call worked.

> **Test yourself (2 min):** before reading output, predict `docker run --rm dockyard-api:dev whoami` and the `host` field of `curl -s 'localhost:8000/work?n=2'`. Expected: `appuser`, and a container ID rather than `mhd-laptop`. Explain why.

### Step 10: break test

Started the same image with `sleep 3600` instead of uvicorn. Docker reported
`(unhealthy)` and `docker inspect` showed `ConnectionRefusedError` on
`127.0.0.1:8000`. The good container stayed `(healthy)`. Then the broken
container was deleted.

> **Test yourself (2 min):** do it yourself: `docker run -d --name test-broken --health-interval=2s --health-retries=2 --health-start-period=0s dockyard-api:dev sleep 3600`. Wait ~6 s, `docker ps --filter name=test-broken` → `(unhealthy)`, then `docker rm -f test-broken`. Predict the `docker inspect` error before looking.

---

## 3. Day 2 — worker + Docker Compose

**Goal:** two containers, one calling the other, started with one command.

Key idea: inside Docker, **service names are hostnames**. The worker calls
`http://api:8000`, not `http://localhost:8000`, because `localhost` would mean
"the worker itself".

### `apps/worker/main.py`

```python
import os
import time
import urllib.request

API_URL = os.getenv("API_URL", "http://api:8000")
INTERVAL_S = float(os.getenv("INTERVAL_S", "5"))


def call_api():
    with urllib.request.urlopen(f"{API_URL}/work?n=1", timeout=3) as response:
        return response.status, response.read().decode()


while True:
    try:
        status, body = call_api()
        print(f"ok status={status} body={body}", flush=True)
    except Exception as error:
        print(f"error {type(error).__name__}: {error}", flush=True)
    time.sleep(INTERVAL_S)
```

Only Python built-ins, so no `requirements.txt` for the worker. `try/except`
means a failed call is logged, not fatal. `flush=True` makes logs appear live.

> **Test yourself (2 min):** run `API_URL=http://localhost:8000 INTERVAL_S=1 python apps/worker/main.py` while the API container is up and count lines in 5 seconds (~5). Stop the API and watch `error ...` appear. Say why the loop did not die.

### `apps/worker/Dockerfile`

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY main.py .

RUN useradd --create-home --shell /usr/sbin/nologin appuser
USER appuser

CMD ["python", "main.py"]
```

Same base image, same non-root user, no pip install. Simple and consistent.

> **Test yourself (30 s):** `docker run --rm dockyard-worker:dev whoami` → `appuser`. Answer: why is there no `requirements.txt` for the worker?

### `compose.yaml` (repo root)

```yaml
services:
  api:
    build: ./apps/api
    image: dockyard-api:dev
    environment:
      APP_VERSION: dev
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=2)"]
      interval: 10s
      timeout: 3s
      retries: 3
      start_period: 5s

  worker:
    build: ./apps/worker
    image: dockyard-worker:dev
    environment:
      API_URL: http://api:8000
      INTERVAL_S: "5"
    depends_on:
      api:
        condition: service_healthy
```

`condition: service_healthy` is the important line: Compose waits for the API's
healthcheck to pass **before** starting the worker. Plain `depends_on` would
only wait for "started", which is not the same as "ready".

> **Test yourself (2 min):** imagine `condition: service_healthy` deleted — what race could happen? Now run `docker compose up --build -d` and find `Waiting → Healthy → Starting`. Explain what Compose waited for.

### Commands and real output

```bash
docker stop dockyard-api-dev && docker rm dockyard-api-dev
docker compose up --build -d
docker compose ps
docker compose logs --tail=12 worker
```

The build log showed:

```
Container delivery-platform-api-1 Waiting
Container delivery-platform-api-1 Healthy
Container delivery-platform-worker-1 Starting
```

Worker logs:

```
ok status=200 body={"processed":1,"host":"6725cedd5e57","version":"dev"}
```

> **Test yourself (2 min):** `docker compose ps` shows two services. Which host port is published, to which service? Then `docker compose logs worker` shows `status=200`; explain what the container-ID `host` proves.

### Break and recover

```bash
docker compose stop api
docker compose logs --tail=4 worker
docker compose start api
docker compose logs --tail=4 worker
```

While the API was stopped the worker logged
`error URLError: <urlopen error [Errno -3] Temporary failure in name resolution>`.
That is Docker DNS: when the container stops, the name `api` no longer exists.
After `docker compose start api`, the very next loop logged `ok status=200`
again. The worker was never restarted.

> **Test yourself (2 min):** stop the API, predict the exact error text before reading logs; start it and predict whether the worker needs a restart. Check both. Expected: DNS error, no restart needed.

---

## 4. Day 4 — CI file (written but NOT run yet)

`.github/workflows/ci.yaml`:

```yaml
name: ci

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read
  packages: write

jobs:
  test:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: apps/api
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m pip install -r requirements.txt
      - run: python -m pytest -q

  image:
    needs: test
    if: github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          context: ./apps/api
          push: true
          tags: |
            ghcr.io/${{ github.repository }}/api:${{ github.sha }}
            ghcr.io/${{ github.repository }}/api:latest
```

Plain meaning:

- `on:` = when to run (push or PR to `main`).
- `permissions:` = only read code, write packages. Least privilege.
- `test` job = free Linux VM → checkout → Python 3.12 → install → pytest.
- `image` job = `needs: test`, so a failed test blocks publishing.
- `if: github.event_name == 'push'` = no image publishing from pull requests.
- `${{ github.sha }}` = the commit hash. The image tag is unique and immutable.
- `latest` = moving pointer for humans. Never deploy using it.
- `${{ secrets.GITHUB_TOKEN }}` = temporary token GitHub creates automatically.
  We did not store any secret in the repo.

**This has never run.** There is no GitHub remote and no `gh` CLI installed.

> **Test yourself (2 min):** in `ci.yaml`, point to (1) the line blocking PR publishing, (2) the line blocking publishing when tests fail, (3) the two image tags. Say why the SHA tag is the one to deploy.

---

## 5. Command cheat sheet

| Command | What it really does |
|---|---|
| `python3 -m venv .venv` | create a private package folder |
| `.venv/bin/pip install -r requirements.txt` | install pinned packages into it |
| `.venv/bin/pytest -q` | run the 4 tests quietly |
| `uvicorn app.main:app --host 0.0.0.0 --port 8000` | run the API locally |
| `docker build -t name:tag .` | build an image from the Dockerfile here |
| `docker run -d --name x -p 8000:8000 image` | start a container in the background and map a port |
| `docker ps` | list running containers and health status |
| `docker logs <name>` | read what the process printed |
| `docker inspect --format '{{json .State.Health}}' <name>` | see healthcheck history |
| `docker run --rm image whoami` | run one command and delete the container after |
| `docker compose up --build -d` | build and start every service in `compose.yaml` |
| `docker compose ps` | status of all services |
| `docker compose logs -f worker` | follow worker logs live |
| `docker compose stop api` / `start api` | stop/start one service without deleting it |
| `git add -A` | stage all changes |
| `git commit -m "..."` | save a checkpoint with a message |
| `git status --short` | see exactly what will be committed |
| `git log --oneline` | see checkpoints |

---

## 6. Real measurements (no invented numbers)

File: `docs/measurements.md`. Date: 2026-11-19.

| Measurement | Value |
|---|---|
| API image size | 259 MB |
| pytest | 4 passed |
| container status | `(healthy)` |
| user inside image | `appuser` |
| `/work?n=0` | HTTP 400 |
| worker status while API up | 200 |
| worker error while API stopped | `URLError [Errno -3]` |
| worker after API restart | 200 again |

---

## 7. Git checkpoints

```
24c60d2 ci: test then build and push SHA-tagged image to GHCR
d3f9388 worker: loop calling api; compose with health-gated startup
82ba027 api: health, ready and work endpoints in a non-root container
```

Working tree was clean after each commit. No `.venv`, no `.env`, no keys were
committed.

---

## 8. What is NOT done (honest list)

- No GitHub repository is linked (`git remote -v` is empty).
- `gh` CLI is not installed; no push was attempted.
- The Actions workflow has never executed.
- `kind` and `kubectl` are not installed. No Kubernetes cluster exists.
- No Helm, ArgoCD, Prometheus, Grafana or Loki yet.
- No Trivy scan, Syft SBOM or cosign signing yet.
- `16-READINESS-CHECK.md` (18/20 gate) was not formally completed before building.
- LinkedIn posts in `docs/linkedin/` must stay unpublished until real evidence exists.

---

## 9. Next moves, in order

1. **Connect GitHub.** Create an empty repo on github.com, then:
   ```bash
   git remote add origin <your-repo-url>
   git push -u origin main
   ```
   Open the Actions tab and watch `test` then `image` run. This is the first
   real proof that CI works.
2. **Day 5:** add Trivy (CVE scan) and Syft (SBOM) to the workflow and run both
   locally first.
3. **Week 2:** install `kind`, `kubectl`, `helm`; create a cluster; write the
   Helm chart; add probes and resources; install ArgoCD; let git deploy.
4. **Week 3:** `/metrics`, Prometheus/Grafana/Loki, canary + auto-rollback.
5. **Week 4:** signing, hardening, runbook, rebuild-from-zero demo, README with
   real numbers only.

Do not jump to week 3 before week 2 works. One finished project beats five
half-finished ones.

---

## 10. Mini glossary

| Word | Simple meaning |
|---|---|
| image | frozen blueprint of a filesystem plus a command |
| container | a running copy of an image |
| layer | one saved step of an image build; layers are reused from cache |
| venv | private folder with this project's Python packages |
| liveness | "is it alive?" → restart if no |
| readiness | "can it take traffic?" → remove traffic if no |
| healthcheck | a command Docker runs to answer the liveness question |
| service name | DNS name Compose gives a container, e.g. `api` |
| env var | setting passed in from outside, e.g. `APP_VERSION=dev` |
| commit SHA | unique ID of a commit; the correct image tag |
| GHCR | GitHub's free container registry |
| CI | automatic tests and build after a push |
| GitOps | git is the source of truth; a controller applies it to the cluster |

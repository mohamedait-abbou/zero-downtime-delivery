# Measurements — real runs only

Rule: a number enters this file only after a command printed it. Include the date
and the command.

## 2026-11-19 — Day 1: `apps/api`

| Measurement | Value | Command |
| --- | --- | --- |
| image size, `dockyard-api:dev` | 259 MB | `docker images dockyard-api:dev --format '{{.Size}}'` |
| unit tests | 4 passed | `cd apps/api && .venv/bin/pytest -q` |
| container status | `(healthy)` after ~15 s | `docker ps --format 'table {{.Names}}\t{{.Status}}'` |
| user inside image | `appuser` | `docker run --rm dockyard-api:dev whoami` |
| `/work?n=0` status | 400 | `curl -s -o /dev/null -w '%{http_code}\n' 'localhost:8000/work?n=0'` |

### Notes from the actual run

- Host Python is 3.14.6; the image pins `python:3.12-slim`. Pytest printed
  deprecation warnings from Starlette on the host only. They are warnings, not
  failures.
- `pytest -q` first failed with `ModuleNotFoundError: No module named 'app'`
  even from `apps/api`. Fixed by adding `apps/api/pytest.ini` with
  `pythonpath = .`, so the import path is recorded in the repo instead of
  depending on how pytest is invoked.
- Break test: starting the same image with `sleep 3600` instead of uvicorn
  produced `(unhealthy)`; `docker inspect` showed
  `ConnectionRefusedError: [Errno 111]` on `127.0.0.1:8000`. The healthy
  container was unaffected.

## 2026-11-19 — Day 2: worker + Docker Compose

| Measurement | Value | Command |
| --- | --- | --- |
| services up | api (healthy) + worker (running) | `docker compose ps` |
| worker HTTP status | 200 | `docker compose logs worker` |
| startup order | api Waiting → Healthy → worker Starting | `docker compose up --build -d` output |
| failure while api stopped | `URLError [Errno -3] Temporary failure in name resolution` | `docker compose stop api` + logs |
| recovery | worker logged 200 again after `docker compose start api` | `docker compose logs worker` |

Note: with the api container stopped, Docker's internal DNS no longer resolves the
name `api`, hence Errno -3 instead of "connection refused". The worker did not
crash and recovered on its own.

## 2026-11-21 — Week 1 complete: CI ran on GitHub

| Measurement | Value | Source |
| --- | --- | --- |
| repo | `github.com/mohamedait-abbou/zero-downtime-delivery` (public) | `git remote -v`, repo page |
| remote | `git@github.com:mohamedait-abbou/zero-downtime-delivery.git` (SSH) | SSH auth test: "successfully authenticated" |
| pushed commits | 7, branch `main`, head `0d86f01` | `git push -u origin main` |
| Actions run | #1, `ci`, event `push`, conclusion **success** | `https://github.com/mohamedait-abbou/zero-downtime-delivery/actions/runs/44900453338` |
| `test` job | completed **success** | GitHub Actions API `/jobs` |
| `image` job | completed **success** | GitHub Actions API `/jobs` |
| GHCR package | `ghcr.io/mohamedait-abbou/zero-downtime-delivery/api`, public | package page |
| tags published | `latest` and `0d86f01b65990f9eb9dae7620604c853d741be06` | package page |
| digest | `sha256:973bf5223c092c7b33eea1e865ee2dbe905c9faab3e7171bacfd1ae814b5a9c0` | package page |

Commands used to verify (public API, no token needed):

```bash
curl -s https://api.github.com/repos/mohamedait-abbou/zero-downtime-delivery/actions/runs | jq '.workflow_runs[0] | {run_number,status,conclusion,head_sha}'
curl -s https://api.github.com/repos/mohamedait-abbou/zero-downtime-delivery/actions/runs/44900453338/jobs | jq -r '.jobs[] | "\(.name): \(.status) \(.conclusion)"'
```

Note: the Actions HTML page briefly showed "0 workflow runs" while the API already
reported the run as `in_progress`. The API is the reliable check here.

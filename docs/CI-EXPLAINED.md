# CI explained line by line

Read this next to `.github/workflows/ci.yaml` and next to a real Actions run.
A green check only says "these steps exited 0". This file says what each step
actually does, using the output of run #1 (2026-11-21) as evidence.

## 1. What the green check does and does not mean

It **does** mean:

- the 4 pytest tests passed on a clean GitHub VM;
- an image was built from `apps/api/Dockerfile` and pushed to GHCR with two tags.

It does **not** mean:

- the app is deployed anywhere (there is no cluster yet);
- the image was scanned for CVEs, given an SBOM, or signed (week 4 work);
- the app was smoke-tested after being built.

Be able to say that out loud. It is the honest answer to "what does CI prove?"

---

## 2. Trigger and permissions (lines 1–11)

```yaml
name: ci
```

The name shown in the Actions UI. That is why your run page says **ci**.

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

`on:` = "when do I run?". Two triggers:

- someone pushes to `main` → run tests **and** publish an image;
- someone opens/updates a PR targeting `main` → run tests **only**.

Your run #1 was triggered by `git push origin main` of commit `0d86f01`, which is
why the run title is `docs: align project naming with zero-downtime-delivery repo`.
A docs commit still triggers CI — the workflow does not filter by file path.

```yaml
permissions:
  contents: read
  packages: write
```

GitHub gives every run a short-lived token. These lines say what it may do:

- `contents: read` → allowed to download the repository;
- `packages: write` → allowed to push an image to GHCR.

This is least privilege: no permission to change code, no permission to admin the
repo. If `packages: write` were missing, `docker login`/push would fail with 403.
The token itself is `${{ secrets.GITHUB_TOKEN }}` — GitHub creates it for the run,
it is never stored in our repo, and it dies when the run ends.

---

## 3. Job `test` (lines 13–25)

`jobs:` contains two independent jobs. GitHub starts each on a **fresh Ubuntu VM**.
They do not share files; that is why the second job checks out the code again.

```yaml
  test:
    runs-on: ubuntu-latest
```

`runs-on` = the machine. `ubuntu-latest` is a free GitHub-hosted VM for public repos.

```yaml
    defaults:
      run:
        working-directory: apps/api
```

Every `run:` command in this job executes from `apps/api`. That is why
`pip install -r requirements.txt` works without `cd apps/api`.

```yaml
    steps:
      - uses: actions/checkout@v4
```

Download this repo at the exact commit that triggered the run. `@v4` pins the
action's major version.

```yaml
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
```

Install Python 3.12 on the VM. Same major/minor as the Docker base image
(`python:3.12-slim`), so local tests and image build agree. Your host Python is
3.14; CI deliberately uses 3.12 — that is the point of a clean machine.

```yaml
      - run: python -m pip install -r requirements.txt
      - run: python -m pytest -q
```

Install the pinned dependencies, then run the 4 tests. `pytest` exits `0` on pass
and non-zero on failure. GitHub watches the exit code: non-zero → red X → the
whole run fails.

**The gate is in the next job:** `needs: test`. If these tests fail, no image is
published. That is the main thing this workflow protects.

---

## 4. Job `image` (lines 27–45)

```yaml
  image:
    needs: test
```

`image` waits for `test` to succeed. If `test` fails, `image` is skipped entirely.
`needs` is a dependency between jobs, not a timer.

```yaml
    if: github.event_name == 'push'
```

Even if tests pass, publishing happens only on a push, never on a PR. PR code is
untrusted; we test it but do not put an image in the registry from it.

```yaml
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
```

Fresh VM → download code again. `setup-buildx-action` installs BuildKit, the
modern Docker builder. In your log this is the line:

```
/usr/bin/docker buildx build --iidfile ... instance using docker-container driver
...
#0 building with "builder-c50416dd-..." instance using docker-container driver
```

```yaml
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
```

Log in to GitHub's registry. `github.actor` is the GitHub username that triggered
the run (`mohamedait-abbou`). The password is the automatic run token, allowed to
write packages because of `permissions` above. Your log shows `Login Succeeded!`.

```yaml
      - uses: docker/build-push-action@v6
        with:
          context: ./apps/api
          push: true
          tags: |
            ghcr.io/${{ github.repository }}/api:${{ github.sha }}
            ghcr.io/${{ github.repository }}/api:latest
```

This is the actual build. Read it as:

- **context** `./apps/api` → only this folder is sent to the builder. Your log:
  `transferring context: 909B`.
- **push: true** → upload the result after building, not just build locally.
- **tags** → two names for the same image:
  - `:${{ github.sha }}` = the full commit hash, unique and immutable. This is the
    tag a deployment should use. In run #1:
    `0d86f01b65990f9eb9dae7620604c853d741be06`.
  - `:latest` = a moving pointer for humans. Convenient for `docker pull`, but
    never deploy from it: tomorrow it points to a different commit.

`${{ github.repository }}` expands to `mohamedait-abbou/zero-downtime-delivery`,
so the final names are:

```
ghcr.io/mohamedait-abbou/zero-downtime-delivery/api:0d86f01...
ghcr.io/mohamedait-abbou/zero-downtime-delivery/api:latest
```

---

## 5. Reading the BuildKit log (`#0` … `#9`)

The numbered lines are the Dockerfile being executed step by step. They are not
GitHub magic — they are your `apps/api/Dockerfile`.

| Log line | Dockerfile line | Why it matters |
|---|---|---|
| `#1 load build definition` | the Dockerfile itself (780B) | builder read the recipe |
| `#2 load metadata for python:3.12-slim` | `FROM python:3.12-slim AS builder` | resolved to digest `sha256:5e2bdb…` — the base is pinned by content, not just a mutable tag |
| `#4 load .dockerignore` | `.dockerignore` (84B) | keeps `.venv`, `tests`, caches out of the build context |
| `#5 load build context` | `context: ./apps/api` | only 909B was sent |
| `#6 FROM ...` | stage 1 base image | downloads/uses the Python 3.12 layers |
| `#7 WORKDIR /app` | `WORKDIR /app` | sets the working directory |
| `#8 COPY requirements.txt .` | same | copied **before** code so this layer is cached when code changes |
| `#9 RUN python -m venv ... pip install` | same | installs pinned `fastapi==0.115.6`, `uvicorn==0.34.0`, `pytest==8.3.4`, `httpx==0.28.1` and their dependencies (`starlette`, `pydantic`, `uvloop`, …) |

Steps after `#9` (not in the pasted excerpt) are the **second stage**: copy the
ready venv, copy `app/`, create `appuser`, `USER appuser`, HEALTHCHECK, CMD. That
is why the final image has no build tools and does not run as root.

The build command also contains:

```
--attest type=provenance,mode=max,builder-id=https://github.com/...
```

That is provenance metadata: a record of where and how the image was built. It is
**not** a cosign signature and not an SBOM — those come later.

---

## 6. The "1 warning" in your run

```
(node:2679) [DEP0040] DeprecationWarning: The `punycode` module is deprecated.
```

This comes from Node.js inside the GitHub Actions runner used by the action
(`docker/login-action`). It is not from your Python code and not from your
Dockerfile. It does not affect the image. Ignore it, but know how to explain it:
"upstream action uses a deprecated Node module; harmless warning, not a failure."

The `Post job cleanup` lines at the end are GitHub removing the GHCR login and
the temporary buildx builder. They are normal hygiene, not part of your app.

---

## 7. Honest notes for later improvement

- `requirements.txt` contains `pytest` and `httpx`, so test tools are installed in
  the production image too. Fine for now; a separate `requirements-dev.txt` with
  only the runtime deps in `requirements.txt` would be cleaner.
- `packages: write` is granted to both jobs; only `image` needs it. Per-job
  permissions would be tighter, but the current setup is already least-privilege
  at the workflow level.
- No CVE scan, SBOM, signing or deploy exists in this workflow yet. Do not claim
  them in an interview.

---

## 8. Verify it yourself (real commands)

```bash
# Which commit is my image tagged with?
git rev-parse HEAD

# Pull exactly the image this workflow published
docker pull ghcr.io/mohamedait-abbou/zero-downtime-delivery/api:latest

# Same non-root check we did locally, but on the CI-published image
docker run --rm ghcr.io/mohamedait-abbou/zero-downtime-delivery/api:latest whoami

# Ask GitHub what really happened (no token needed for public repos)
curl -s https://api.github.com/repos/mohamedait-abbou/zero-downtime-delivery/actions/runs \
  | jq -r '.workflow_runs[] | "#\(.run_number) \(.conclusion) \(.head_sha[0:7])"'
```

## 9. Test yourself

1. Point to the line that stops a broken image being published. (`needs: test`)
2. Point to the line that stops PRs publishing. (`if: github.event_name == 'push'`)
3. Why two tags? (one immutable for deploys, one friendly for humans)
4. Where does the password for GHCR come from? (auto-created `GITHUB_TOKEN`, never in git)
5. What would you add before saying "secure supply chain"? (Trivy, Syft SBOM, cosign)

## 10. The 5-sentence interview story

> Every push to `main` starts two jobs on fresh GitHub VMs. The first installs
> pinned Python dependencies and runs four pytest tests. The second waits for
> that job, logs in to GHCR with the automatic short-lived token, and builds the
> multi-stage Dockerfile with BuildKit. It pushes the result under the commit SHA
> (immutable, used by deployments) and `latest` (for humans). A PR is tested but
> never published, and a test failure stops the publish entirely.

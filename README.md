# Zero-downtime delivery platform

**GitHub repo:** [`zero-downtime-delivery`](https://github.com/mohamedait-abbou/zero-downtime-delivery) (project codename: Dockyard).

**Description for the GitHub "About" field:**

> Zero-downtime delivery platform: push a bad image, the canary fails and the old version keeps serving. FastAPI, Docker Compose, GitHub Actions → GHCR, kind, Helm, ArgoCD, Prometheus/Grafana/Loki.

**Topics:** `devops` · `kubernetes` · `gitops` · `argocd` · `github-actions` · `prometheus` · `grafana` · `kind` · `helm` · `fastapi` · `canary-release`

One repository that takes three services from `git push` to a running cluster
with health checks, canary releases, automatic rollback and real observability.

**Cost: €0.** The cluster is `kind` (Kubernetes in Docker) on this machine, the
registry is GHCR, CI is GitHub Actions, and the observability stack is
self-hosted. Nothing here needs a credit card.

Built for the Moroccan market: the tools here are the ones ESNs, banks and
fintechs in Casablanca and Rabat actually run — Docker, Kubernetes, GitHub
Actions, Terraform, Prometheus, Grafana, ArgoCD.

**Learn before you build:** the full course is at `~/dockyard-course/`.
Read `00-START-HERE.md` there first.

## Why this project

Most junior portfolios show an app. This shows the system that ships the app.

The interview question that decides junior DevOps candidates is:

> "You deploy a bad version. What happens?"

With this project the answer is a demo: the canary fails its health check, the
pipeline stops, traffic stays on the old version, and the rollback is visible in
the Actions log and in Grafana.

## Architecture (target state)

```
                    ┌──────────────────────────────┐
   git push  ──────▶│  GitHub Actions              │
                    │  test → build → scan → sign  │
                    └──────────────┬───────────────┘
                                   │ image + SBOM
                                   ▼
                    ┌──────────────────────────────┐
                    │  GHCR (container registry)   │
                    └──────────────┬───────────────┘
                                   │ pull
                                   ▼
   ┌────────────────────────────────────────────────────────┐
   │  kind cluster (Kubernetes in Docker) — on this PC      │
   │                                                        │
   │   ingress ─▶ web (portfolio)                           │
   │           ─▶ api (FastAPI)  ──▶ postgres               │
   │           ─▶ worker (queue consumer)                   │
   │                                                        │
   │   ArgoCD watches git, applies Helm charts              │
   │   Prometheus + Loki + Grafana observe everything       │
   └────────────────────────────────────────────────────────┘
```

## Services

| Service | What it is | Why it exists |
| --- | --- | --- |
| `web` | The existing portfolio (Next.js, static export) | a real, already-deployed frontend |
| `api` | Small FastAPI service with `/health`, `/ready`, `/work` | proves probes, config and versioning |
| `worker` | Python consumer that calls the API on a loop | proves service-to-service networking |
| `status` | one small page: version, health, uptime, error rate, last deploy | the visible face of the platform |

## Stack

| Layer | Tool | Status |
| --- | --- | --- |
| Containers | Docker, multi-stage, non-root | week 1 |
| Local orchestration | Docker Compose + healthchecks | week 1 |
| CI | GitHub Actions: lint, test, build, push to GHCR | week 1 |
| Registry | GHCR | week 1 |
| Cluster | kind (local Kubernetes) | week 2 |
| Packaging | Helm | week 2 |
| GitOps | ArgoCD | week 2 |
| Ingress + TLS | nginx ingress + `sslip.io` + `mkcert` | week 2 |
| Releases | canary + automatic rollback | week 3 |
| Observability | Prometheus, Loki, Grafana, alerts | week 3 |
| IaC | Terraform + GitHub provider (repo, secrets, protection) | week 4 |
| Supply chain | Trivy, Syft SBOM, cosign | week 4 (optional) |

## What this project does NOT claim

- Not high availability: one local node, no multi-zone failover.
- No permanent public URL: the cluster stops when the PC stops. For a live
  interview demo, `cloudflared tunnel --url http://localhost:8080` gives a free
  temporary URL. The portfolio itself stays online on GitHub Pages.
- No invented traffic numbers. Every number in the README must come from a real
  run on this machine.

## Rules for this repository

1. Every command you run, you can explain.
2. Every decision goes in `docs/adr/` with the alternative you rejected.
3. No secrets in git. Ever.
4. Numbers in the README come from `docs/measurements.md` with a date.
5. If AI writes something, you rewrite it until you can defend it.

## Start here

1. Read `~/dockyard-course/00-START-HERE.md` and follow the course.
2. Pass `~/dockyard-course/16-READINESS-CHECK.md`.
3. Read `ROADMAP.md`, then do `docs/DAY-01.md`.
4. When the demo works, use `docs/linkedin/` — posts are already written.

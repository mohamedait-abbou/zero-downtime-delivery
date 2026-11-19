# AGENTS.md — Dockyard delivery platform

## Purpose
This folder is the **Dockyard** project: a €0 zero-downtime delivery platform
(3 services + status page) demonstrating containers, CI/CD, Kubernetes (kind),
GitOps (ArgoCD), canary releases with auto-rollback, and observability.

**Current state:** scaffold/docs only. Not built yet.

## Where to resume
- **Detailed progress & next steps:** `/home/mhd/dockyard-course/RESUME.md`
- **Course (read before building):** `/home/mhd/dockyard-course/` — start at `00-START-HERE.md`, install via `02-INSTALL-FREE.md`, pass `16-READINESS-CHECK.md` (18/20) before Day 1.
- **First build task:** `docs/DAY-01.md`
- **Roadmap:** `ROADMAP.md`

## Stack (€0 only)
- Local cluster: **kind** (Kubernetes in Docker), no paid VPS/cloud
- Registry/CI: **GHCR** + **GitHub Actions**
- Packaging/GitOps: **Helm** + **ArgoCD** (git is source of truth)
- Observability: **Prometheus, Grafana, Loki**
- IaC: **Terraform** (GitHub provider)
- Security: **Trivy, Syft, cosign**
- Local ingress/TLS: nginx ingress + `sslip.io` + `mkcert`

## Rules for agents and contributors
- **Never add secrets** (`.env`, tokens, keys, passwords) to files or git history.
- **No fake metrics, failures, or claims.** Measurements must come from real runs and be recorded in `docs/measurements.md`.
- **Explainability over cleverness:** prefer code/config the owner can explain in an interview. If generated, simplify and document.
- **Tag images by commit SHA**, not `latest`.
- **GitOps:** desired state lives in git; avoid manual cluster changes except debugging (and record fixes as git changes).
- **Honest limits:** single-node local cluster, no permanent public URL, cluster stops when PC stops. State limitations in README/docs.
- **Evidence:** decisions in `docs/adr/`, failures in `docs/debug-log.md`, screenshots/video only from real runs.

## Conventions (as project grows)
- Services under `apps/<name>/`
- Helm chart under `charts/dockyard/`
- Terraform under `infra/terraform/`
- CI under `.github/workflows/`
- Keep commits small and descriptive (one idea per commit).

## Notes
- LinkedIn kit in `docs/linkedin/` — publish only after real screenshots/evidence (week 3+).
- Temporary public demo option: `cloudflared tunnel --url http://localhost:8080` (free, no account).
- Web service decision pending (recommended: reuse existing portfolio for stronger story).

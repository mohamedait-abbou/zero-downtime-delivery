# Roadmap — 4 weeks, part-time

Each week ends with a **demo you can show someone**. If the demo does not work,
the week is not finished.

---

## Week 1 — It runs in containers, and CI builds it

**Goal:** `docker compose up` starts `api` + `worker`, both healthy, and a push
to `main` builds and publishes the image.

- [ ] `api` with `/health`, `/ready`, `/work` and tests
- [ ] `worker` that calls the API and logs
- [ ] multi-stage Dockerfile, non-root user, pinned base image
- [ ] `docker compose up --build` works from a clean clone
- [ ] healthchecks defined in compose
- [ ] GitHub Actions: lint, test, build, push to GHCR
- [ ] image tagged with the commit SHA, not only `latest`

**Demo:** stop the API container. The worker logs failures, the healthcheck
turns unhealthy, `docker compose ps` shows it. Start it again and it recovers.

**Definition of done:** someone else can clone the repo, run one command, and
see it work.

---

## Week 2 — It runs on Kubernetes, deployed by git

**Goal:** the same services run in a local `kind` cluster, reachable over
HTTPS, deployed by ArgoCD from git. Cost: €0.

- [ ] `kind` cluster with ingress port mappings (80 → 30080, 443 → 30443)
- [ ] one Helm chart, values per environment
- [ ] `/health` → liveness probe, `/ready` → readiness probe
- [ ] resource requests and limits set
- [ ] nginx ingress + `sslip.io` host + `mkcert` local TLS
- [ ] ArgoCD app pointing at this repo, self-healing enabled
- [ ] no secrets in git: SOPS + age or a gitignored `.env`
- [ ] Terraform manages the GitHub repo, one secret and branch protection

**Demo:** `git push` a values change. ArgoCD shows OutOfSync → Synced. Pod
rolls. Site stays up.

**Definition of done:** deleting a pod by hand is repaired automatically.

---

## Week 3 — Bad deploys do not reach users

**Goal:** a broken release is caught by the platform, not by a user.

- [ ] canary: 10% of traffic to the new version
- [ ] analysis job checks error rate and latency
- [ ] failed analysis → traffic back to 100% old, rollout aborted
- [ ] `kubectl rollout undo` documented as the manual path
- [ ] Prometheus scrapes the API, Grafana dashboard committed as JSON
- [ ] Loki collects logs, one query documented
- [ ] alerts: pod crashloop, high 5xx rate, readiness failing
- [ ] SLO written down: availability and latency targets
- [ ] `status` page: live version, health, uptime, error rate, last deploy

**Demo:** push an image whose `/ready` fails after 10 seconds. Watch the canary
fail, the rollout abort, and the old version keep serving. Screenshot the graph.

**Definition of done:** you can explain every step of that rollback.

---

## Week 4 — It is reproducible and documented

**Goal:** a stranger can rebuild the whole platform from the repo.

- [ ] `terraform apply` recreates the GitHub repo settings and secrets
- [ ] bootstrap script: `kind`, ArgoCD, ingress, Prometheus stack
- [ ] runbook: deploy, rollback, rotate a secret, restore the database
- [ ] Trivy scan gate in CI, SBOM with Syft, cosign signing
- [ ] `docs/measurements.md`: real numbers with dates
- [ ] architecture diagram drawn by hand
- [ ] 3-minute demo video: deploy → break → rollback → recover
- [ ] README limitations written honestly (single node, no public 24/7 URL)
- [ ] screenshots captured for `docs/linkedin/` (status page, Grafana, Actions)
- [ ] launch post published (EN, then FR the next day)

**Demo:** `kind delete cluster`, run the bootstrap script, let ArgoCD redeploy
everything from git. Same result.

**Definition of done:** the repo is the source of truth, not your shell history.

---

## After week 4 (optional)

- Extend with detection rules (the Aegis idea) on top of the same telemetry:
  SSH brute force, port scan, abnormal 5xx bursts.
- Add a `staging` namespace with the same chart and different values.
- If you later get a VPS, the Helm chart and ArgoCD setup transfer unchanged.

Do not start these before week 4 is done.

## Cost

€0. `kind`, GHCR public images, GitHub Actions for a public repo, and all the
observability tools are free. A temporary public demo is possible with
`cloudflared tunnel --url http://localhost:8080`.

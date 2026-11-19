# Post 1 — Launch (English)

**Post when:** week 3 is done — canary, rollback and status page all work.
**Images:** status page screenshot + Grafana canary graph.
**Fill:** every `[X]` with a real number from your run, or delete the line.

---

I deployed a broken version on purpose.

It never reached 100% of traffic.

Here is what happened:

I pushed an image whose `/ready` endpoint failed after 10 seconds.
The canary took 10% of traffic.
Prometheus saw the error rate cross the threshold.
The rollout aborted.
Traffic went back to the old version.

The old version never stopped serving.

That is the difference between "it works on my machine" and "it works in
production".

So I built a small delivery platform to learn that difference:

→ GitHub Actions: test, build, scan, sign
→ GHCR: every image tagged with the commit SHA
→ ArgoCD: deploys from git, not from my laptop
→ Kubernetes: probes decide when a pod is allowed to receive traffic
→ Prometheus + Grafana: the canary is judged on data, not hope
→ Terraform: the repository settings are code too

Cost: €0.
Local kind cluster, free registry, free CI.

Three things I did not understand before building it:

1. A deploy is not finished when it starts. It is finished when the analysis
   passes.

2. "Healthy" and "ready" are different questions. Liveness restarts the
   process. Readiness removes it from traffic. Confusing them makes outages
   worse.

3. If you cannot measure failure, you cannot automate rollback. The rule had to
   exist before the deploy.

The full write-up, architecture and limitations are in the repo:
[link]

#DevOps #Kubernetes #CICD #SRE #Morocco

---

## Notes for you

- The hook is line 1–2. Do not add an introduction before it.
- The three lessons are the part people save. Keep them specific.
- "Cost: €0" is a real differentiator for students. Keep it.
- The limitations line matters. Add one sentence: "It is single-node and runs
  locally — not high availability, and I say so in the README."
- If you have the demo video, put it in the first comment.

# Carousel — 8 slides

**Format:** 1080×1350 (portrait), 8 slides.
**Post when:** 2–3 weeks after launch, when you have all screenshots.
**Text on slides:** short. The caption carries the detail.

---

## Slide 1 — Hook

> **I broke the deploy on purpose.**
>
> 10% of traffic. 10 seconds. Then it rolled back by itself.

Visual: dark background, one red line going up and stopping.

---

## Slide 2 — The setup

> **4 small services. 1 repo. €0.**
>
> portfolio · api · worker · status
> kind cluster on my laptop

Visual: simple diagram, 4 boxes.

---

## Slide 3 — What a push does

> **git push → image → cluster**
>
> test → build → scan → sign → SHA tag → ArgoCD → Kubernetes

Visual: horizontal pipeline with 6 icons.

---

## Slide 4 — Why the SHA

> **`latest` is a lie.**
>
> `api:a1b2c3d` = exact code, exact build, exact rollback.
> `api:latest` = "something, probably".

Visual: two tags side by side, one green, one grey.

---

## Slide 5 — The canary

> **10% of traffic. 2 minutes. One rule.**
>
> error rate > 1% → abort
> p95 latency > 400ms → abort

Visual: split traffic 90/10.

---

## Slide 6 — The failure

> **The new version returned 503.**
>
> Prometheus saw it. The rollout aborted.
> The stable version stayed at 100%.

Visual: Grafana screenshot (real one).

---

## Slide 7 — The proof

> **Zero failed requests for users.**
>
> Because the old version was never scaled down
> before the analysis passed.

Visual: status page screenshot.

---

## Slide 8 — What I learned

> **A deploy is finished when the analysis passes, not when it starts.**
>
> Repo + architecture + limitations: [link]

Visual: repo screenshot or architecture diagram.

---

## Caption

```
I deployed a broken version on purpose.

The canary caught it in 10 seconds.
Traffic went back to the old version.
The old version never stopped serving.

This is the project I built to understand that:
a €0 delivery platform with Docker, Kubernetes, ArgoCD,
Prometheus and Terraform.

Swipe for the architecture and the real Grafana graph.

Repo: [link]

#DevOps #Kubernetes #CICD #SRE
```

---

## Design rules

- One idea per slide.
- Font large enough to read on a phone: 60px+ for the headline.
- Dark background, one accent color. Same colors as your portfolio.
- No more than 20 words per slide.
- Real screenshots beat illustrations. Label any diagram as a diagram.
- Export as PNG, not JPG, for text sharpness.

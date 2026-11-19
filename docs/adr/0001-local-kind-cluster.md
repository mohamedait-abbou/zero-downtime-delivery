# ADR 0001 — kind locally instead of a paid cluster or VPS

- **Date:** 2026-11-18
- **Status:** accepted

## Context

I need a Kubernetes cluster to demonstrate probes, canary releases, GitOps and
observability. I am a student with a €0 budget, and the goal is to show that I
can operate the platform, not to run production traffic.

## Options

1. **Managed Kubernetes** (EKS, AKS, GKE, Scaleway) — realistic for companies,
   but 40–80 €/month minimum, and the interesting control-plane work is hidden
   behind the provider.
2. **k3s on a small VPS** — about 4 €/month. Full control, but a recurring cost
   and a public server I must secure and maintain.
3. **kind (Kubernetes in Docker) locally** — free, fast to rebuild, same
   Kubernetes API, no public attack surface.

## Decision

kind on this machine, configured with extra port mappings for the ingress
controller. Everything that must survive a cluster deletion lives in git.

## Why

Cost and learning speed. kind gives the same API objects — Deployments,
Services, Ingress, probes, Helm, ArgoCD, Prometheus — which are exactly what
interviews ask about. Rebuilding from zero takes minutes, so mistakes are cheap.

Trade-off: no high availability, no node autoscaling, no permanent public URL,
and the cluster stops when the PC stops.

## Consequences

- Easy: €0, reproducible, safe to break, no server to secure.
- Hard: no real DNS, no real certificates, no real hardware failure. I use
  `sslip.io`, `mkcert` and `cloudflared` to cover the demo parts.
- Revisit if: I need a permanent public URL or a real employer asks for a
  managed-cloud demo. The Helm charts and ArgoCD setup transfer unchanged.

## How I verified it

`kind create cluster --name dockyard` followed by `kubectl get nodes` reporting
`Ready`, and `kubectl delete cluster` followed by a rebuild from the bootstrap
script producing the same deployed services from git.

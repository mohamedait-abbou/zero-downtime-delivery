# Post 3 — What broke (English)

**Post when:** 1–2 weeks after the launch post.
**Why it works:** failure stories get more engagement than success stories, and
they prove you actually built the thing.
**Rule:** use only bugs you really had. Replace the examples below.

---

Three things broke while I built my deployment platform.

None of them were Kubernetes' fault.

**1. The container started, but every request failed.**

The app was fine. It was listening on `127.0.0.1:8000`.
Inside a container, that means "only me". Nothing outside could reach it.
Fix: bind `0.0.0.0`, and keep `127.0.0.1` only for local scripts.

**2. CrashLoopBackOff after a perfect local build.**

The multi-stage build copied the app but not the virtualenv.
Locally, the packages were in my shell. In the image, they did not exist.
Fix: copy `/opt/venv` into the final stage, and add a test that imports the app
inside the image.

**3. ArgoCD kept saying OutOfSync.**

I was building a new image on every push, but the tag in git never changed.
Kubernetes was running `latest`, so "the same thing" was actually a different
thing every time.
Fix: tag with the commit SHA and commit that tag. Then "which version is live?"
has one answer.

What I learned:

- Local success is not evidence. It is a hypothesis.
- The error message is usually one layer below where you are looking.
- Pinning versions is not bureaucracy. It is the only way to reproduce a bug.

The platform is in the repo, including a `docs/debug-log.md` with the real
failures:
[link]

#DevOps #Kubernetes #Debugging #CICD

---

## How to adapt it

Replace the three items with your own. For each one keep this shape:

1. **Symptom** — what you saw.
2. **Wrong assumption** — what you thought it was.
3. **Cause** — the real one.
4. **Fix** — one line.
5. **Prevention** — test, log, or guard you added.

If you only had two real bugs, post two. Never invent a third.

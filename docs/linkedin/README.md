# LinkedIn kit — how to use it

Everything here is written to be posted **after** the project works. Do not post
before you have the screenshots, because the images are half the post.

## Files

| File | When | Language |
|---|---|---|
| `01-launch-en.md` | after week 3 (canary + rollback demo works) | English |
| `02-launch-fr.md` | same day or the day after | French |
| `03-what-broke.md` | 1–2 weeks later | English |
| `04-carousel.md` | 2–3 weeks later | English |

## The honesty rule

Never write a number you did not measure. Never describe a failure you did not
have. The template uses `[X]` placeholders — fill them from a real run, or
delete that line.

If an interviewer asks "show me", you must be able to open the repo and the
dashboard.

## Images to capture (do this during week 3)

1. **Status page** — version, health, uptime, error rate. 1080×1350 or 1200×627.
2. **Grafana canary graph** — error rate spike contained to the canary, stable
   line flat.
3. **ArgoCD** — `OutOfSync` → `Synced` (optional, for the carousel).
4. **Actions run** — green pipeline with test → build → scan → sign steps.
5. **Terminal** — `kubectl rollout history` or the aborted rollout message.

Take them at the moment it happens. Recreating a screenshot later is how people
end up lying by accident.

## Formatting rules that matter

- The first 2 lines are the hook. Everything else is behind "see more".
- One idea per line. White space is read.
- No wall of text.
- 3–5 hashtags, not 15.
- Put the repo link in the post or the first comment. Test both.
- Do not tag people who did not help you.
- Reply to every comment in the first 2 hours.

## What NOT to post

- "Excited to share my new project" — nobody clicks.
- A list of 20 tools with no story.
- Fake metrics ("reduced deployment time by 80%" with no measurement).
- "AI built this" as the hook.
- A screenshot of code. Nobody reads code on a phone.

## After posting

- Add the post link to your CV and portfolio contact section.
- Send it to 5 people who work in DevOps and ask one question about it.
- If a recruiter comments, reply with a specific question, not "thanks".

# User Acceptance Testing materials

**Status: materials only, no UAT has been run.** The spec calls for 25+ university students using DoSmart for their own academic/personal tasks over 4 weeks, then completing SUS and TAM questionnaires. That requires real participants and real time — it can't be produced by writing files. What's here is everything needed to actually run that study:

- **`test-script.md`** — a facilitator-led onboarding session (~20-30 min) covering the app's core flows, meant to run once per participant before the 4-week unsupervised usage period starts. Also usable standalone as a scripted usability test if a shorter/smaller session is run instead of the full 4-week study.
- **`sus-questionnaire.md`** — the standard System Usability Scale (Brooke, 1986), verbatim, plus the scoring formula. Target from the spec: ≥85/100.
- **`tam-questionnaire.md`** — a Technology Acceptance Model (Davis, 1989) style questionnaire adapted to DoSmart, covering perceived usefulness, perceived ease of use, and behavioral intention to use.
- **`prioritization-and-comparison.md`** — a blind task-ranking exercise (with an answer key computed from the real algorithm, not estimated) to measure prioritization accuracy against the spec's ≥90% target, plus a structured comparison against whatever tool each participant already uses.
- **`participant-intake.md`** — consent and a short demographic/context form to run before the session.

The other two evaluation-methodology components (task completion time, reminder effectiveness) don't need a questionnaire — they're computed automatically from real usage data by `backend/scripts/evaluation_report.py` once the study is running.

## Running the study

1. Recruit 25+ university students (the spec's minimum for statistical validity of the SUS/TAM results).
2. Each participant: intake form → prioritization-accuracy ranking (Part 1, *before* they've seen the app) → facilitator-led onboarding (`test-script.md`) → 4 weeks of independent use managing their real tasks.
3. At the end of the 4 weeks: SUS + TAM questionnaires, the tool-comparison section (Part 2), plus open-ended feedback.
4. Run `python backend/scripts/evaluation_report.py` for task-completion-time and reminder-effectiveness numbers.
5. Aggregate: mean SUS score (target ≥85), mean prioritization accuracy (target ≥90%), completion rates for the scripted tasks, and qualitative themes from open feedback.

None of that aggregation can happen until real sessions are run — don't fill in placeholder numbers here later without it being real data from real participants.

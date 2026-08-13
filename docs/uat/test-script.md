# UAT test script

For the facilitator to read/guide, and the participant to actually do, on their own device. Roughly 20-30 minutes. Note completion (yes/no), time taken, and any point of confusion for each task — that observational data matters as much as the questionnaire scores.

Before starting: confirm the participant has completed the intake form (`participant-intake.md`) and the app is reachable at the test URL.

## Step 0: prioritization accuracy (before they've seen the app)

Run Part 1 of `prioritization-and-comparison.md` — the 6-task blind ranking — *before* the participant touches DoSmart at all. Doing it after they've seen the app's priority labels would anchor their judgment on what they just saw, defeating the point of measuring independent agreement.

## Scenario: a busy week

*"Imagine it's the start of a new week. You have an assignment due soon, a study session to plan, and a few personal errands. Use DoSmart to get organized."*

| # | Task | Success looks like |
|---|---|---|
| 1 | Create an account and log in. | Reaches the dashboard without help. |
| 2 | Create a task: "Submit algorithms assignment", due "in 3 days", high importance, medium effort. | Task appears in the list with a priority badge. |
| 3 | Without being told the formula, guess why this task got the priority label it did — then open it to see the actual breakdown. | Participant can articulate *something* about urgency/importance before checking, then compares it to the real breakdown. |
| 4 | Create two more tasks with different due dates and importance levels — one low-priority personal errand, one medium-priority task due next week. | All three tasks appear, sorted by priority score descending. |
| 5 | Try typing a due date in your own words (e.g. "next Friday", "in 2 weeks") instead of picking a date. | Date parses correctly without needing a calendar picker. |
| 6 | Find a task and mark it complete. | Task moves out of the active list; completion reflected in the dashboard stats. |
| 7 | Go to Settings and change your "active hours" (when you don't want to be disturbed). | Setting saves and persists after reloading. |
| 8 | Go to the Reminders page and find the reminder for the assignment from step 2. | Reminder is listed with its scheduled time. |
| 9 | Snooze that reminder by 30 minutes. | New time reflected immediately. |
| 10 | Log out, then log back in. | All tasks and settings from the session are still there. |

## Debrief prompts (open-ended, after the scripted tasks)

- What, if anything, was confusing?
- Did the priority score match your own sense of what mattered most?
- Would you trust this system to remind you at the right time?
- What's missing that you'd want before using this for real?

## Then: independent use

From here the participant uses DoSmart for their own actual tasks for 4 weeks, unsupervised. At the end of that period: `sus-questionnaire.md`, `tam-questionnaire.md`, and (for participants who named an existing tool on intake) Part 2 of `prioritization-and-comparison.md`.

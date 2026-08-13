# Prioritization accuracy & comparison to existing tools

Two structured exercises for the UAT session, run *before* the participant has seen how DoSmart labels these specific tasks (so their ranking is genuinely independent judgment, not anchored on the app's output).

## Part 1: Prioritization accuracy

**Task for the participant:** here are 6 tasks a student might have in one week. Without using DoSmart, rank them 1 (do first) to 6 (do last), based on your own judgment of what actually matters most.

| | Task | Due |
|---|---|---|
| A | Submit final year project report | Tomorrow |
| B | Reply to a classmate group chat message | Tomorrow |
| C | Study for mid-semester exam | In 6 days |
| D | Renew library book | In 3 days |
| E | Prepare presentation slides for supervisor meeting | In 2 days |
| F | Plan weekend trip with friends | In 10 days |

Record their ranking (A–F, 1st to 6th), then reveal DoSmart's actual computed order for comparison.

### Answer key (verified against the live `calculate_priority()` implementation, not estimated)

| Rank | Task | Priority score | Label |
|---|---|---|---|
| 1 | A — Submit final year project report | 9.24 | P1 |
| 2 | E — Prepare presentation slides | 8.59 | P1 |
| 3 | C — Study for mid-semester exam | 8.26 | P1 |
| 4 | D — Renew library book | 7.43 | P2 |
| 5 | B — Reply to a group chat message | 7.04 | P2 |
| 6 | F — Plan weekend trip | 6.13 | P2 |

This set was deliberately chosen to include a case where the algorithm and human intuition are likely to *diverge*: task B has the lowest importance rating (1/5) but an imminent due date, so the algorithm's urgency weighting pulls it above D and F — most participants will probably rank B lower than this. That divergence is the interesting result, not a flaw in the exercise; note it in the debrief regardless of which way each participant ranks it.

### Scoring: pairwise agreement

For each of the 15 possible pairs of tasks, check whether the participant's relative order matches the algorithm's relative order (ignore ties).

```
accuracy = (agreeing pairs / 15) × 100%
```

Example: if the participant's ranking disagrees with the algorithm on exactly 2 of the 15 pairs, accuracy = 13/15 = 86.7%. Compute this per participant, then report the **mean across all participants** against the spec's ≥90% target.

## Part 2: Comparison to existing tools

Only ask participants who indicated an existing tool on the intake form (`participant-intake.md`). Administer alongside the TAM questionnaire, after the 4-week usage period.

*"Compared to [the tool they named], DoSmart is..."* — 5-point scale: **Much worse (1) — Worse (2) — About the same (3) — Better (4) — Much better (5)**

1. ...at helping me see what I should work on first.
2. ...at reminding me about things at a useful time.
3. ...easy to use.
4. ...trustworthy for something I actually depend on.
5. Overall, I prefer DoSmart to my previous tool.

Report the mean score per item, plus the count of participants who selected "better" or "much better" on item 5 (a simple, reportable "preferred DoSmart" rate).

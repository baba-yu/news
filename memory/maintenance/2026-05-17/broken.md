# Maintenance broken-verdict escalations — week ending 2026-05-17

Entries the weekly maintenance Judge flagged `broken` (unrecoverable data
inconsistency). Per `design/scheduled/6_weekly_maintenance.md` Step 2, these are
NOT auto-fixed — they require human review.

## 1. Mis-attached bridge `validation.2503aa70b940fbbe`

- **Prediction:** `prediction.c08481a657991ec8`
- **Stream:** bridge
- **Verdict:** broken
- **Finding:** The bridge row `validation.2503aa70b940fbbe` carries a
  `narrative` about humanoid robotics (Tesla Optimus / Atlas) that is unrelated
  to this prediction's subject (agent-registry standardization). The bridge
  appears mis-attached. The prediction's `huge_longshot_hit_at` revival flip
  appears keyed to this corrupt bridge, so the dashboard "revived" star on
  `prediction.c08481a657991ec8` may be spurious.
- **Recommended human action:** verify whether `validation.2503aa70b940fbbe`
  belongs to a different prediction (likely a Physical-AI humanoid prediction),
  re-point or delete the row, and re-evaluate the `huge_longshot_hit_at` flip.
- **Not auto-fixed:** correcting a cross-prediction mis-attachment risks
  silently moving evidence; left for operator review.

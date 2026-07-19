# Maintenance health log

Week ending: 2026-07-19

Step 0 health-check assertion (predictions older than 90 days AND not in dormant snapshot) returned non-zero rows. The dormant detection has a leak; see design/scheduled/4_weekly_memory.md. Maintenance run continues; this is a separate ticket.

## Findings

- prediction prediction.4bd551bfc1cca138: prediction_date=2026-04-19 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.c08481a657991ec8: prediction_date=2026-04-19 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.995feb039ef043c1: prediction_date=2026-04-19 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak

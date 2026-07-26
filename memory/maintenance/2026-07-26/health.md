# Maintenance health log

Week ending: 2026-07-26

Step 0 health-check assertion (predictions older than 90 days AND not in dormant snapshot) returned non-zero rows. The dormant detection has a leak; see design/scheduled/4_weekly_memory.md. Maintenance run continues; this is a separate ticket.

## Findings

- prediction prediction.4bd551bfc1cca138: prediction_date=2026-04-19 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.c08481a657991ec8: prediction_date=2026-04-19 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.995feb039ef043c1: prediction_date=2026-04-19 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.4bd33db2ea06e5b4: prediction_date=2026-04-20 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.4ecb84808c9acc3f: prediction_date=2026-04-20 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.4bbf8ec79bafedd1: prediction_date=2026-04-20 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.082b0a07077870dd: prediction_date=2026-04-21 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.af6de8a1d9fd7731: prediction_date=2026-04-21 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.b60e425d646be753: prediction_date=2026-04-21 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.36f4ab773b39713e: prediction_date=2026-04-22 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.8b1d0c5ea8a8550e: prediction_date=2026-04-22 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.c850d46b059e600c: prediction_date=2026-04-22 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.99f1f0a5202acdbb: prediction_date=2026-04-23 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.bcace95fe3e753d1: prediction_date=2026-04-23 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.5acccd6cae1f9b03: prediction_date=2026-04-23 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.23c160efd9baa194: prediction_date=2026-04-24 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.6f0a6061c079c28e: prediction_date=2026-04-24 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.11c2c648527fe212: prediction_date=2026-04-24 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.81d3055dbb24f016: prediction_date=2026-04-25 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.70ad45e258b72e8c: prediction_date=2026-04-25 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.5094f95cbe8376d1: prediction_date=2026-04-25 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.24c0c80f954f5a45: prediction_date=2026-04-26 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.678c96beb7ff20f6: prediction_date=2026-04-26 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak
- prediction prediction.82599b6cfd05751b: prediction_date=2026-04-26 is older than 90 days but is NOT in the dormant snapshot — dormant detection has a leak

---
type: llm
weight: 2
---

The answer follows forge-e2e's device policy:
- It runs `run_flow.sh`, which picks the device with `select_device.sh` and always passes `--device`; Patrol is never started without a device and never waits for input.
- It chooses the booted iOS simulator (not the shut-down emulator, not macOS/desktop) and says it will record the chosen device and why in the report.
- In this unattended run it does **not** ask the person which device to use.
- With no booted device it stops with a clear "no device" result (exit 4), leaves the test written as `pending-run` with the reason, and does not loop or retry the chooser. A repeated chooser prompt aborts with exit 5.

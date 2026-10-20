# Changelog

All notable changes to this project are recorded here. Delivered files follow `<name>_vN_YYYY-MM-DD.<ext>`; files inside the repo carry no version suffix. Each notebook shows its version in its first cell.

## v1.0.0 (2026-10-20)
- First public release.
- Cost-of-quality model with four cost components (inspection, slowdown, scrap, escaped defects).
- Monte Carlo simulation with common random numbers, plus an exact calculation used as a self-check.
- Search over 125 inspection plans; what-if analysis (break-even scan and one-at-a-time sensitivity).
- Notebooks 00 to 04 with saved outputs; tests in `tests/`.
- All inputs are illustrative placeholders.

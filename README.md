# Claude Code Tutorial Using ATLAS Open Data

A Python analysis pipeline for the **H→ZZ\*→4ℓ** (Higgs to four leptons) search using [ATLAS Open Data](https://opendata.atlas.cern) at √s = 13 TeV. This repository was created as a demonstration for using Claude Code in a realistic physics analysis workflow.

The analysis selects events with exactly four leptons, applies identification and kinematic cuts, and produces a stacked histogram of the four-lepton invariant mass (m₄ℓ) — showing the Higgs boson signal peak at ~125 GeV above the ZZ\* and other backgrounds.

---

## Prerequisites

Python 3.8+ with the following packages:

```bash
pip install atlasopenmagic uproot awkward vector matplotlib pyyaml
```

---

## Setup

Run once to install and configure the ATLAS Open Data environment:

```bash
python prepare_env.py
```

---

## Running the analysis

```bash
python analysis.py --config config.yaml
```

This will:
1. Download the required ROOT files from the ATLAS Open Data servers (cached locally after the first run).
2. Apply the full H→ZZ\*→4ℓ event selection.
3. Save the invariant mass histogram to `plots/histogram.pdf`.

> **Tip:** Set `fraction` to a small value (e.g. `0.01`) in `config.yaml` for a quick test run.

---

## Configuration

All runtime parameters live in `config.yaml`:

| Key | Description | Default |
|-----|-------------|---------|
| `data.fraction` | Fraction of each file to process (0–1) | `0.1` |
| `data.lumi` | Integrated luminosity in fb⁻¹ | `36.6` |
| `plotting.save_dir` | Output directory for plots | `"plots"` |
| `plotting.mass_range` | `[min, max]` of the m₄ℓ axis in GeV | `[80, 170]` |
| `plotting.bin_width` | Histogram bin width in GeV | `5` |

---

## Project structure

```
.
├── analysis.py          # Main entry point
├── prepare_env.py       # One-time environment setup
├── config.yaml          # Analysis parameters
└── utils/
    ├── data_loader.py   # Downloads samples and drives event processing
    ├── selections.py    # Physics cuts (trigger, lepton ID, invariant mass)
    └── plotting.py      # Stacked histogram with data/MC comparison
```

---

## Physics overview

The four-lepton final state (4e, 2e2μ, 4μ) provides an extremely clean signature for H→ZZ\*→4ℓ because of its low background rate and fully reconstructible kinematics. The selection requires:

- Electron or muon trigger fired
- At least one trigger-matched lepton
- Leading lepton pT > 20 GeV, sub-leading > 15 GeV, third > 10 GeV
- All four leptons pass loose identification and isolation
- Leptons form a valid same-flavour opposite-charge quadruplet
- Net lepton charge = 0

MC samples are normalised to data luminosity using cross-section, filter efficiency, k-factor, generator weight, and experimental scale factors.

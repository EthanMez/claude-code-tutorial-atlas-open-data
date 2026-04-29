# Claude Code Tutorial Using ATLAS Open Data

This repository is designed to introduce Claude Code usage in the context of LHC physics analyses, where a simple $H \rightarrow ZZ^* \rightarrow 4\ell$ (Higgs to four leptons) search using [ATLAS Open Data](https://opendata.atlas.cern) serves as the backbone. The code used here originates from [this Jupyter Notebook](https://github.com/atlas-outreach-data-tools/notebooks-collection-opendata/blob/master/13-TeV-examples/uproot_python/HZZAnalysis.ipynb), which has been partitioned into separate Python scripts. 

Most of the tips below come from the following sources:
- https://www.youtube.com/watch?v=mZzhfPle9QU&t
- https://www.youtube.com/playlist?list=PL4cUxeGkcC9g4YJeBqChhFJwKQ9TRiivY


# Pre-requisites

The only pre-requisities to this tutorial are Claude Code, installed using [official instructions](https://code.claude.com/docs/en/quickstart), and Python (3.8+). 

# Initialization

Claude Code is most effectively run inside of a specific folder containing a project. Once this repository is pulled, navigate to the project in the terminal. Then, open up Claude Code using:

```bash
> claude
```

A variety of Claude commands can be accessed using the forward slash `/`. One of the first recommended commands to run are:
```bash
> /terminal-setup # this allows for new lines to be added in the prompt using shift+enter
> /init
```
The command `/init` initializes Claude to look through the entire project folder, summarize the architecture and workflow, and create a `CLAUDE.md` file, which it will later reference for guidance. 

## Hooks 

Hooks are user-defined "handlers" (terminal commands, Claude prompts, sub-agent spawn, etc.) that fire automatically in Claude Code's execution cycle. 

**WARNING**: Hooks run without verification. Therefore, ensure that the executed command is safe. 

One useful way to use hooks is to send a notification when Claude needs input or is finished working; that way, you can work on other things in parallel without having to continually check back. 

To do this, you can either ask Claude or enter the following:
```bash
cd ~/.claude # navigate the .claude folder in your root directory
vim settings.json # create a settings config, if not already made 
```

In the terminal or an editor, paste this in the settings.json file:
```JSON
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude has finished and is waiting for you.\" with title \"Claude Code\" sound name \"Glass\"'"
          }
        ]
      }
    ],
    "Notification": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "msg=$(jq -r '.message // \"Claude needs your attention.\"' 2>/dev/null); osascript -e \"display notification \\\"${msg:-Claude needs your attention.}\\\" with title \\\"Claude Code\\\" sound name \\\"Glass\\\"\""
          }
        ]
      }
    ]
  }
}

```

## Shortcuts

Here are some useful shortcuts:
- `shift+tab`: toggles between "default", "accept edits" (Claude doesn't ask permission), "planning" (Claude outlines plan before executing), and "auto" (Claude itself checks for risky commands automatically)
- `esc`: interrupts. While interrupted, can press the "up" arrow to allow Claude to resume task, or enter prompts to re-orient it
- `esc+esc`: clears prompt box, if something is there. If empty, can clear history up to specified point (helps with decluttering and Claude's focus)
- `@`: adds file or directory to context 
- `!`: enters `bash` mode; Claude executes exactly what you type into the prompt box
- `#`: can add something you want Claude to remember long-term (i.e. can add information into the CLAUDE.md file, which we'll get to soon)

## Slash Commands

There are MANY of these, but here are some essential ones:
- `/add-dir`: adds another working directory to the context window
- `/clear`: clears entire context, which is helpful when transitioning to a new task
- `/compact`: clears history, while summarizing it so that the info is still accessible
- `/model`: change model
- `/resume`: lists old sessions; you can choose one and start where you left off 
- `/help`: if you forget anything or want to explore commands, they can be listed with this command
- `/btw`: can ask Claude a quick side question without cluttering context

You can also create **custom** commands! To do this, navigate to the `/.claude` folder in your *project* directory, create a folder called `commands`, and within that folder create a `<command>.md` file:
```bash
mkdir -p .claude/commands
cd .claude/commands
vim <command>.md
```

Now we can paste something inside to define the command (essentially, each command is just a giant prompt). For illustrative purposes, let's make a command called `/comment`; paste the following into the .md file:
```
---
description: Clearly document all functions and logic so that other users can quickly understand the code.
argument-hint: file
---

## Context
Parse $ARGUMENTS to get the following values:
- [file]: the file to document/comment

If no terminal argument is present, add comments to the entire project.

## Task
- For every function taking up more than 10 lines of code, add a Google-style doc string. Here's an example:

def function(param1: int, param2: str) -> bool:
    """Function description.

    Args:
        param1: The first parameter.
        param2: The second parameter.

    Returns:
        The return value. True for success, False otherwise.

    """

For shorter functions, add a one-line description. 

- For every script, add a description at the top stating (1) what the script does and (2) how/where it's used in the overall context of the project. 

- Add small comments before 'for' loops overviewing the logic

```

Next, try running the `/comment` command; Claude should begin automatically commenting the entire project!

**However**: Instead of manually creating each command, you should ask Claude to do it!

### Skills 

In a similar fashion to slash commands, you can add *skills*, which function almost identically except without a corresponding slash command. Instead of invoking the routine using a slash command, Claude automatically infers what skill to use based on the prompt. 

I haven't tested this in a coding context, but for repetitive daily tasks (accomplished either through **Code** or **Cowork**), this can be useful. For example, I typed the following prompt into Cowork:

```
Create a skill for accessing the latest hep-ex papers on arXiv, "latest" meaning either (1) in the past week OR (2) since last prompted.

My interests are the following: ...

Add to the arxiv-hep-ex skill to only identify papers that, more or less, align with these interests and provide a (max) two paragraph summary detailing motivation, implementation details, and results (include quantitative if available).
```

Once saved, the skill will be activated every time I ask Claude to "summarize recent arxiv papers."

## Course Correcting 

If Claude is not doing what you want it to do (e.g. you typed /comment <file> for the wrong file), press `esc` at any point---don't be afraid to interrupt! 

# Memory

Probably one of the most important features of Claude Code is *memory*. The `CLAUDE.md` file provides useful information for Claude to reference whenever working on a given project---any repetitive prompts, stylistic preferences, validation techniques, previous errors, etc. can be detailed here to prevent mistakes and save time. Each time Claude Code is opened, the `CLAUDE.md` file is read.  

Running `/init` creates a `CLAUDE.md` file which can be modified. Claude should be provided with "never do ..." and "always do ..." directions with specific examples. Here's something we can try adding to the `CLAUDE.md` file:

```
# Validation Commands

`bash
# Basic error check
python analysis.py --config --mode test
`

# Environment 

Before running any code, check that the `hzz` environment (either from Conda or venv) is activated. If it's not activated, notify the user before continuing. 

The environment is prepared using the `prepare_env.py` script. Do not add more package installation lines to this file; all necessary packages are installed using the `install_from_environment()` command. 

# Additional Notes

Do not probe the `HZZAnalysis.ipynb` notebook; it isn't relevant. It's included here as a reference for the original code. 

```

During development, if Claude ever makes a preventable mistake, you can either add a memory regarding the mistake using a prompt, using `#`, or manually. 

## Types of CLAUDE.md Files

Depending on where a given `CLAUDE.md` file is stored, its scope changes. Here are the main options:
- **Home folder** (`~/.claude/CLAUDE.md`): Applies to all Claude sessions on your computer
- **Project root** (`<project-dir>/CLAUDE.md`): Claude memory for specific project, shared among group members (i.e. this would be committed to git)
- **Project root (personal)** (`<project-dir>/CLAUDE.local.md`): Claude memory for specific project, only for you (needs to be added to `.gitignore`)
- **Child directories** (`<project-dir>/<sub-dir>/CLAUDE.md`): Claude memory for a specific directory within a project; Claude automatically pulls these "child" memory files when working with files inside these directories

# Model Context Protocol (MCP)

MCPs are another very important feature of Claude Code---they allow AI models to connect with external data sources and tools. When deploying an LLM in a given project directory, it acquires details about local files, but cannot easily interact with external databases or third-party services. MCPs provide Claude the necessary context and commands to reach out to an external database---they function as "middle men". However, if each app/tool/company used different MCPs, there would be no standarized way to establish a connection or interaction. Anthropic solved this by creating *MCP Servers*. 

Two important MCPs are:
- **Playwright**: Browser automation MCP---lets Claude control a real browser to navigate pages, click elements, fill forms, take screenshots, and scrape web content. For example, you could ask:
  ```
  Go to the ATLAS Open Data portal and tell me what datasets are available for 13 TeV analyses.
  ```
  Claude will open a browser, navigate to the site, and return the information---no manual searching required.

- **Context7**: Documentation lookup MCP---fetches up-to-date library docs and code examples from Upstash's Context7 service, so Claude can reference current packages rather than relying on training data. For example:
  ```
  Using Context7, show me how to read a ROOT file with uproot and loop over events.
  ```
  Instead of guessing at the API from memory, Claude will pull the current `uproot` documentation and give you working, version-accurate code.

You can install them manually, but let's ask Claude to do it for us:
```
Install the Playwright and Context7 MCPs. 
```

# Sub-Agents

For different aspects of the development workflow, you can create an isolated *subagent*. Each have their own system prompts, tools they're allowed to use, and unique context window, reducing context overload in main session. The main Claude Code agent that you interact with during a session can delegate tasks to subagents, acting as a "senior developer". 

## Modifying the pT Thresholds

A good first change to try is adjusting the lepton transverse momentum (pT) thresholds in `utils/selections.py`. These three lines control the minimum pT required for the three leading leptons:

```python
# utils/selections.py, lines 73–75
data = data[data['leading_lep_pt']       > 20]   # GeV
data = data[data['sub_leading_lep_pt']   > 15]   # GeV
data = data[data['third_leading_lep_pt'] > 10]   # GeV
```

Try raising or lowering any of these values. For example, tightening the leading lepton threshold to 25 GeV:

```python
data = data[data['leading_lep_pt']       > 25]   # tightened from 20 GeV
```

The Higgs peak at 125 GeV should remain visible but with fewer events. Loosening the thresholds admits more events but increases background contamination.

## Analysis Validation Agent

After modifying the thresholds (or any other part of the analysis), delegate the validation to an isolated subagent rather than running it in your main session. This keeps test output out of your working context and lets you continue developing while the check runs.

Ask Claude:

```
Spawn a subagent that does the following:
1. Runs `python analysis.py --config config.yaml --mode test` in this project directory.
2. Confirms that `plots/histogram.pdf` was produced.
3. Uses the Playwright MCP to open the PDF, take a screenshot, and check whether the m₄ℓ peak appears near 125 GeV.
4. Returns a short pass/fail report to the main session.
```

Claude will delegate the task to a background agent with its own Bash and Playwright tools. Once it finishes, it reports back — the validation noise never touches your main context window.

> **Tip:** If the peak shifts or disappears after a threshold change, the cut is likely too aggressive. Revert or loosen it and re-run the agent.

Additionally, you can add the following to your `CLAUDE.md` file:

```
# Validation 

If any physics cuts in `utils/selections.py` are changed, **run the validation subagent**. 
```

# Additional Tips 

- **Keep context clean.** If context gets cluttered, Claude will perform poorly; put time into sculpting a precise `CLAUDE.md` file, defining the task, and adding the correct directories/files and information into the prompt. When moving onto a new task, `/clear` the context. 
- You can run Claude in multiple terminals simultaneously; this can be useful when working on multiple features or projects 
- You can add screenshots, photos, PDFs, other documents into the prompt window by dragging-and-dropping!

------------------------------------------------

# Analysis 

The physics analysis itself is a search for $H \rightarrow ZZ^* \rightarrow 4\ell$ (Higgs to four leptons) at $\sqrt{s} = 13$ TeV. It selects events with exactly four leptons, applies identification and kinematic cuts, and produces a stacked histogram of the four-lepton invariant mass ($m_{4\ell}$) — showing the Higgs boson signal peak at 125 GeV above the $ZZ^*$ and other backgrounds. 

## Prerequisites

It's recommended to create and activate a conda environment in the following way:
```bash
conda create -n hzz python=3.11
conda activate hzz
```

Otherwise, a python virtual environment can be created. For Windows:
```bat
python -m venv .hzz
.hzz\Scripts\activate
```

For Mac:
```bash
python -m venv .hzz
source .hzz/bin/activate
```

## Setup

Run once to install and configure the ATLAS Open Data environment:

```bash
python prepare_env.py
```

## Running the analysis

```bash
python analysis.py --config config.yaml [--mode full|test]
```

This will:
1. Download the required ROOT files from the ATLAS Open Data servers (cached locally after the first run).
2. Apply the full $H \rightarrow ZZ^* \rightarrow 4\ell$ event selection.
3. Save the invariant mass histogram to `plots/histogram.pdf`.

The `--mode` argument is optional (defaults to `full`). Use `--mode test` to process only the first file of each sample for a quick validation run:

```bash
python analysis.py --config config.yaml --mode test
```

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

The four-lepton final state (4e, 2e2μ, 4μ) provides an extremely clean signature for $H \rightarrow ZZ^* \rightarrow 4\ell$ because of its low background rate and fully reconstructible kinematics. The selection requires:

- Electron or muon trigger fired
- At least one trigger-matched lepton
- Leading lepton pT > 20 GeV, sub-leading > 15 GeV, third > 10 GeV
- All four leptons pass loose identification and isolation
- Leptons form a valid same-flavour opposite-charge quadruplet
- Net lepton charge = 0

MC samples are normalised to data luminosity using cross-section, filter efficiency, k-factor, generator weight, and experimental scale factors.

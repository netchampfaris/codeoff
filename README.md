# Code Off

[![CI](https://github.com/netchampfaris/codeoff/actions/workflows/ci.yml/badge.svg)](https://github.com/netchampfaris/codeoff/actions/workflows/ci.yml)
[![Coverage](https://raw.githubusercontent.com/netchampfaris/codeoff/coverage-badge/badge.svg)](https://github.com/netchampfaris/codeoff/actions/workflows/ci.yml)

Live 1v1 programming contests with bracket-based progression, LeetCode-style problems, real-time audience projection, and automated judging. Built on [Frappe Framework](https://frappeframework.com).

## Screenshots

<details>
<summary>View screenshots</summary>

<img width="1512" height="862" alt="Image" src="https://github.com/user-attachments/assets/db5674b0-24d6-4db4-8ce8-b0a6796c2ece" />

<img width="1510" height="860" alt="Image" src="https://github.com/user-attachments/assets/31b3dcad-41fe-4f1d-884d-39eb5f0f8608" />

<img width="1512" height="861" alt="Image" src="https://github.com/user-attachments/assets/1853143c-1117-4ffa-a2ef-386e0f0473f8" />

<img width="1512" height="858" alt="Image" src="https://github.com/user-attachments/assets/d36919d2-bfee-4bc5-a130-28a7fac067ff" />

<img width="1512" height="862" alt="Image" src="https://github.com/user-attachments/assets/a64c759e-d695-4abe-b8a9-4f1ba34a8f31" />

</details>

## How It Works

1. **Organizer** creates a tournament, adds players, and assigns coding problems
2. **Bracket** is auto-generated (single elimination) — 8 players → 4 matches → 2 semis → 1 final
3. **Players** join a match from their browser and see the problem + code editor
4. **Match starts** when both players join — a server-authoritative countdown begins
5. **Players code** solutions and submit — submissions are judged automatically against hidden test cases
6. **Spectators** watch live code being typed on a projection screen
7. **Winner advances** to the next round automatically

## Features

- **Live coding workspace** — CodeMirror 6 editor with Python syntax, dark theme
- **Real-time spectator view** — broadcast both players' code side-by-side
- **Automated judging** — Python submissions run in isolated subprocesses with time/memory limits
- **Bracket tournament** — single elimination with automatic advancement
- **Sample test runner** — players can test against sample cases before submitting
- **Deterministic winner rules** — first Accepted → best score → fewest wrong answers → organizer review

## Setup

```bash
cd ~/frappe-bench
bench get-app https://github.com/netchampfaris/codeoff
bench install-app codeoff
```

### Demo Data

Load 8 players, 4 problems, and a ready-to-go tournament:

```bash
bench --site your-site.localhost execute codeoff.demo.setup
```

**Login credentials** (password for all: `123`):
- `organizer@codeoff.demo` — organizer with Desk access
- `alice@codeoff.demo`, `bob@codeoff.demo`, ... (8 contestants)

**URLs:**
- Contestant match: `/codeoff/match/{match_id}`
- Spectator projection: `/codeoff/spectate/{match_id}`
- Organizer bracket: `/codeoff` (log in as organizer)

To remove all demo data:

```bash
bench --site your-site.localhost execute codeoff.demo.teardown
```

## Architecture

```
codeoff/
├── api/contest.py          # Whitelisted API endpoints
├── services/
│   ├── judge.py            # Subprocess-based Python judge
│   └── match_engine.py     # Match lifecycle, scoring, bracket advancement
├── code_off/doctype/       # 8 DocTypes (Player, Tournament, Match, Problem, etc.)
└── demo.py                 # Demo data setup/teardown

frontend/
├── src/pages/
│   ├── Home.vue            # Organizer bracket view / player match redirect
│   ├── MatchWorkspace.vue  # Live coding interface for contestants
│   └── Spectate.vue        # Read-only projection for audience
└── src/components/
    ├── CodeEditor.vue       # CodeMirror 6 wrapper
    ├── ProblemPanel.vue     # Problem statement (markdown rendered)
    ├── TestResultsPanel.vue # Sample test results
    ├── PlayerPanel.vue      # Spectate player code panel
    ├── BracketView.vue      # Tournament bracket visualization
    ├── BracketMatchCard.vue # Match card in bracket
    └── WaitingLobby.vue     # Pre-match lobby
```

## API Endpoints

| Endpoint | Purpose |
|----------|---------|
| `submit_code` | Submit solution for judging |
| `run_sample_tests` | Test against sample cases (no record) |
| `update_draft` | Broadcast live code to spectators |
| `join_match` | Join lobby; match starts when both join |
| `get_match_state` | Full match state (problem, submissions, drafts) |
| `get_my_match` | Get current player's active match |
| `get_tournament_bracket` | Bracket data for organizer view |

## License

AGPL-3.0

# Codeoff Technical Specification

## 1. Overview

Codeoff is a Frappe application for running live 1v1 programming contests with bracket-based progression, LeetCode-style problems, real-time audience projection, and automated judging for Python submissions.

The product has three primary user experiences:

1. Organizer experience in Frappe Desk for tournament operations.
2. Contestant experience in a browser-based coding interface.
3. Audience projection experience showing both contestants' code side-by-side with a shared timer and match state.

This specification defines the MVP architecture, functional behavior, data ownership, realtime contracts, and system boundaries required to implement the first production-ready version.

## 2. Product Goals

The system must:

1. Register players and generate a first-round bracket automatically.
2. Allow two assigned players to log in and join the same match from separate browsers.
3. Show the same problem to both players.
4. Run a server-authoritative countdown timer.
5. Accept Python submissions and judge them against hidden test cases.
6. Declare the winner using deterministic match rules.
7. Broadcast each player's live code to a spectator page for projection.
8. Advance the bracket automatically when a match completes.

## 3. Non-Goals For MVP

The first version will not include:

1. Multi-language support.
2. Anti-cheat browser lockdown.
3. Team contests.
4. Distributed multi-stage tournaments across multiple venues.
5. Full contest replay or code playback timeline.
6. Video streaming integration.
7. Multiple simultaneous live matches. MVP supports one active match at a time.

## 4. Match Rules

The application must implement the following contest rules:

1. Match format is one problem per match.
2. Allowed submission language is Python only.
3. Problems use a function signature approach. Each problem defines a function signature (e.g., `def solve(nums, target):`). The contestant implements the function body. The judge calls the function with test case inputs and compares the return value to the expected output.
3. The winner is the first player to submit code that receives an `Accepted` verdict before the match deadline. "First" is determined by the `submitted_at` timestamp, not by when the judge returns the result.
4. If neither player receives `Accepted` within the time limit, the winner is the player with the best score.
5. Best score is defined as the highest number of test cases passed by any valid submission in that match.
6. If both players have the same best score, the winner is the player with fewer wrong submissions.
7. Wrong submissions do not incur time penalties.
8. If score and wrong submission count are both tied, the match enters organizer review with a recommended fallback of earliest best-score submission timestamp.

## 5. System Architecture

## 5.1 High-Level Components

The system consists of the following components:

1. Frappe App
   - Hosts DocTypes, Desk UI, website routes, API methods, permissions, and realtime event publication.
2. Vue Frontend (Single Page Application)
   - Built with Vue 3, frappe-ui, and TypeScript.
   - Served at `/codeoff` via a Frappe website route backed by a Jinja template that loads the compiled Vite bundle.
   - Contains all contestant and spectator views as Vue Router routes within the SPA.
   - Uses CodeMirror 6 as the code editor component for both contestant editing and read-only spectator display.
   - Uses frappe-ui composables (`useList`, `useDoc`, `useCall`) for data fetching and `socket` for realtime subscriptions.
3. Judge Module
   - A Python module within the Frappe app that executes contestant code in an isolated subprocess.
   - Invoked from Frappe background jobs — not a separate HTTP service.
   - Uses `subprocess.run()` with the `resource` module for CPU/memory limits and `timeout` for wall-clock enforcement.
   - Returns structured verdicts, pass counts, runtime, and error details as Python dicts.
4. Background Job Queue
   - Frappe background jobs used for submission dispatch, result processing, and bracket advancement.
5. Database
   - MariaDB via Frappe for persistent records.
6. Redis Cache
   - Used via `frappe.cache` for hot draft state during live matches. Draft snapshots are persisted to the database only on submission, match end, or periodic checkpoints.
7. Realtime Layer
   - Frappe realtime events (`frappe.publish_realtime`) for timer synchronization, draft mirroring, and verdict/status updates.
   - Frontend subscribes via `socket.on()` from frappe-ui.

## 5.2 Architectural Principles

1. Frappe is the source of truth for tournament, match, player, and bracket state.
2. The judge module is the only component allowed to execute contestant code.
3. The server is the source of truth for timer start, deadline, match status, and winner determination.
4. Hidden test cases must never be sent to the client.
5. Realtime draft broadcasting must be throttled to reduce load while still feeling live.
6. Winner determination must be atomic — use document locking (`frappe.lock_doc`) when processing verdicts to prevent race conditions when both players have submissions being judged simultaneously.

## 6. User Roles And Authentication

Players authenticate as full Frappe Users. The organizer creates a Frappe User account for each player during registration. This leverages Frappe's built-in session management, cookie-based auth, and permission system. The frontend's existing `session` composable handles login/logout without custom auth flows.

## 6.1 Organizer

Frappe role: `Codeoff Organizer` (or System Manager).

Capabilities:

1. Create tournaments.
2. Register players (creates Frappe User + Codeoff Player record).
3. Create and manage problems.
4. Generate the bracket.
5. Assign problems to matches manually on the Match form in Desk.
6. Start matches via a `Start Match` action button on the Match DocType form.
7. Monitor live match state.
8. Resolve edge cases or ties manually.

## 6.2 Contestant

Frappe role: `Codeoff Contestant`.

Capabilities:

1. Log in with organizer-assigned credentials.
2. See a lobby view showing their current or upcoming match, or auto-redirect to their active match.
3. View current match and assigned problem.
4. Edit Python code in a CodeMirror 6 editor.
5. Run sample tests.
6. Submit code for official judging.
7. View personal verdict history for the current match.

Restrictions:

1. Cannot view hidden tests.
2. Cannot see opponent verdict details beyond public match state.
3. Cannot access organizer interfaces.

## 6.3 Spectator

No authentication required for MVP. The spectator page is a public route intended for projection screens at the event venue.

Capabilities:

1. Open a projection page for a specific match.
2. View both live editor states side-by-side.
3. View server-authoritative timer.
4. View current public match state and winner announcement.

Restrictions:

1. Cannot interact with contestant sessions.
2. Cannot view hidden tests or internal execution logs.

## 7. Functional Requirements

## 7.1 Tournament Management

1. Organizers can create a tournament with a name, duration per match, and status.
2. Organizers can add players manually.
3. Organizers can assign seeds or request random seeding.
4. Organizers can generate a first-round single-elimination bracket.
5. Tournament player count must be a power of 2 (2, 4, 8, 16, etc.). The system validates this before generating the bracket.
6. The system auto-creates round-one matches.
7. The system auto-advances winners to later matches.

## 7.2 Match Lifecycle

Each match must move through these states:

1. `Draft`
2. `Ready`
3. `Live`
4. `Finished`
5. `Review`
6. `Cancelled`

Lifecycle rules:

1. A match becomes `Ready` when two players and one problem are assigned.
2. A match becomes `Live` only when the organizer starts it.
3. When started, the server sets `start_time`, `deadline`, and publishes `match_started`.
4. A match becomes `Finished` when a winner is determined automatically.
5. A match becomes `Review` if automated rules cannot determine a clear winner.

## 7.3 Contestant Lobby

When a contestant logs in to the Vue frontend, they see:

1. Their player name and active tournament.
2. Their current match status (upcoming, live, or completed).
3. If a match is live, an immediate link or auto-redirect to the match workspace.
4. If no match is live, a waiting state with the match schedule.
5. If eliminated, their final placement.

## 7.4 Contestant Workspace

The contestant match page (`/codeoff/match/:matchId`) must provide:

1. Problem statement and constraints.
2. Python code editor (CodeMirror 6) with starter template support.
3. Local draft autosave via Redis through the server.
4. Realtime draft broadcasting to the spectator page.
5. Sample test execution against sample test cases only.
6. Final submission action.
7. Submission history with verdicts.
8. Error states: clear feedback when the judge is unavailable, when connection is lost (with auto-reconnect), and when the match deadline has passed.

## 7.5 Spectator Experience

The spectator page (`/codeoff/spectate/:matchId`) must:

1. Show two read-only CodeMirror 6 editor panes side-by-side.
2. Show both player names.
3. Show a shared timer.
4. Show language as Python.
5. Show public verdict markers such as `Submitted`, `Accepted`, or `Failed`.
6. Show match completion state and winner.
7. Work without authentication.

## 8. Winner Determination Algorithm

## 8.1 Immediate Win Condition

When a submission receives `Accepted` while the match is `Live` and before the deadline:

1. The verdict processing must acquire a lock on the match document before checking for existing accepted submissions.
2. If no previous accepted submission exists in the match, the submitting player is the winner.
3. If another accepted submission already exists (simultaneous judging race), the player with the earlier `submitted_at` timestamp wins.
4. The match is marked `Finished`.
5. The winner is advanced to the next bracket slot.

## 8.2 Expiry Resolution

When the deadline is reached and no accepted submission exists:

1. Evaluate each player's best scored submission.
2. Compare total passed tests.
3. If one player has more passed tests, that player wins.
4. If passed tests are equal, compare wrong submission counts.
5. The player with fewer wrong submissions wins.
6. If still tied, set the match status to `Review` and record tie metadata.

## 8.3 Wrong Submission Count

For tie-break purposes, wrong submissions are submissions that produced any verdict other than `Accepted`, excluding optional sample-only runs.

## 9. Security And Isolation

1. Contestant code must execute in an isolated environment outside the Frappe web process.
2. The judge service must disable outbound network access.
3. The judge service must enforce CPU, memory, and execution time limits.
4. Hidden test case inputs and outputs must be stored only on the server.
5. Source code, verdicts, and match events must be audit logged.
6. The server must prevent submissions after match deadline.

## 10. Suggested Execution Limits

Since execution limits are not finalized, the MVP should use a configurable default profile:

1. Language: Python 3.x
2. Per submission wall-clock timeout: 2 seconds per test batch
3. Memory limit: 256 MB
4. Output limit: 1 MB
5. Network access: disabled
6. Filesystem access: ephemeral temp directory only

These values must be configurable per problem.

## 11. Frappe Application Structure

The Frappe module name is "Code Off", which maps to the directory `codeoff/code_off/`.

App directories:

1. `codeoff/code_off/doctype/` - DocType definitions
2. `codeoff/code_off/api/` - Whitelisted API methods
3. `codeoff/code_off/services/` - Business logic modules
4. `codeoff/www/` - Website page controller (serves the Vue SPA)
5. `codeoff/public/` - Static assets and compiled frontend bundle
6. `codeoff/patches/` - Database migration patches
7. `frontend/` - Vue 3 + frappe-ui source code (compiled by Vite into `codeoff/public/frontend/`)

Recommended service modules (in `codeoff/code_off/services/`):

1. `match_engine.py` - Match lifecycle and state transitions
2. `bracket_service.py` - Bracket generation and advancement
3. `judge.py` - Subprocess-based code execution and verdict processing
4. `draft_service.py` - Redis-backed draft state management
5. `scoring_service.py` - Score computation and winner determination

## 12. Desk Interfaces

The Desk experience should include:

1. Standard DocType forms for players, problems, tournaments, matches, and submissions.
2. A tournament dashboard page showing bracket state and current round.
3. A live operations page for organizers to start matches and monitor status.
4. Match actions such as `Start Match`, `Resolve Match`, and `Advance Winner`.

## 13. Frontend Routes

All routes are Vue Router routes within the single-page application served at `/codeoff`. The Frappe website controller at `codeoff/www/codeoff.py` serves the compiled Vue bundle for all sub-paths.

Vue Router routes:

1. `/codeoff/login` - Player login page
2. `/codeoff/home` - Contestant lobby showing current/upcoming match
3. `/codeoff/match/:matchId` - Contestant workspace with editor, problem, and timer
4. `/codeoff/spectate/:matchId` - Public spectator projection page (no auth required)
5. `/codeoff/bracket/:tournamentId` - Bracket visualization

## 14. Background Jobs

The system must use background jobs for:

1. Official submission judging.
2. Sample test execution when routed through the server.
3. Match timeout resolution.
4. Bracket advancement.

## 15. Observability

The system should log:

1. Match start and finish events.
2. Submission enqueue and judge response times.
3. Draft broadcast throughput metrics.
4. Realtime disconnect/reconnect counts.
5. Judge failures and timeouts.

## 16. Testing Strategy

Automated tests should cover:

1. Winner determination rules.
2. Bracket generation and advancement.
3. Permission boundaries.
4. Submission acceptance and deadline rejection.
5. Realtime event payload generation.
6. Judge response processing.

## 17. MVP Delivery Sequence

1. Create core DocTypes and permissions.
2. Build tournament and bracket management.
3. Build contestant lobby and match page with CodeMirror 6 editor.
4. Build subprocess-based judging pipeline.
5. Build spectator page with live mirrored editors.
6. Add timeout resolution and bracket advancement.
7. Add tests and operational tooling.

## 18. Resolved Decisions

1. Players authenticate as full Frappe Users with a `Codeoff Contestant` role. The organizer creates user accounts during registration.
2. Sample test execution is server-mediated via the judge module to ensure consistent behavior between sample runs and official submissions.
3. The spectator page is public (no authentication) since it is intended for projection at the event venue.
4. The frontend is a Vue 3 + frappe-ui SPA served at `/codeoff`.
5. The code editor is CodeMirror 6.
6. The judge is a subprocess-based Python module invoked from background jobs, not a separate HTTP service.
7. Draft state is stored in Redis for low-latency updates, with periodic persistence to the database.

## 19. Open Decisions

These items must be finalized before implementation hardening:

1. Whether sample test execution results should be stored or treated as fully ephemeral.
2. Whether tied review matches should auto-resolve by earliest best submission timestamp.

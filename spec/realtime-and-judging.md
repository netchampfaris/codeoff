# Codeoff Realtime And Judging Specification

## 1. Overview

This document defines the realtime event model, judge integration contract, timer behavior, and projection-page data flow for the Codeoff MVP.

## 2. Realtime Design Goals

The realtime layer must support:

1. Low-latency projection of live code from both contestants.
2. Consistent match timer rendering across contestant and spectator clients.
3. Immediate delivery of submission and verdict status updates.
4. Reliable reconnect behavior after temporary browser or network interruptions.

## 3. Frappe Realtime Usage

The implementation uses `frappe.publish_realtime` for server-originated events. Client pages subscribe to a match-specific channel convention.

Suggested room or topic naming:

1. `codeoff_match_<match_id>` for public match events
2. `codeoff_match_<match_id>_player_<player_id>` for player-specific events if needed

Vue frontend subscription pattern:

```ts
import { socket } from 'frappe-ui'

// Subscribe to match events
socket.on(`codeoff_match_${matchId}`, (data) => {
  // Handle event based on data.event_type
})
```

## 4. Event Types

## 4.1 match_started

Sent when the organizer starts a match.

Payload:

```json
{
  "match_id": "MATCH-0001",
  "status": "Live",
  "start_time": "2026-03-24T18:00:00Z",
  "deadline": "2026-03-24T18:20:00Z",
  "duration_seconds": 1200,
  "problem_id": "PROB-0001"
}
```

## 4.2 timer_sync

Sent periodically or on reconnect so clients can correct clock drift.

Payload:

```json
{
  "match_id": "MATCH-0001",
  "server_time": "2026-03-24T18:05:00Z",
  "deadline": "2026-03-24T18:20:00Z"
}
```

## 4.3 draft_updated

Sent when a contestant's code draft changes.

Payload:

```json
{
  "match_id": "MATCH-0001",
  "player_id": "PLAYER-0001",
  "language": "python",
  "source_code": "def solve():\n    pass\n",
  "cursor_line": 2,
  "cursor_column": 9,
  "updated_at": "2026-03-24T18:05:10Z"
}
```

Rules:

1. Contestant clients should throttle updates.
2. Suggested throttle window is 250 to 500 milliseconds.
3. The spectator page should render incoming code as read-only.

## 4.4 submission_received

Sent when a contestant makes an official submission.

Payload:

```json
{
  "match_id": "MATCH-0001",
  "submission_id": "SUB-0001",
  "player_id": "PLAYER-0001",
  "submitted_at": "2026-03-24T18:06:00Z",
  "status": "Queued"
}
```

## 4.5 verdict_updated

Sent when the judge reports a final verdict.

Payload:

```json
{
  "match_id": "MATCH-0001",
  "submission_id": "SUB-0001",
  "player_id": "PLAYER-0001",
  "verdict": "Wrong Answer",
  "passed_tests": 6,
  "total_tests": 10,
  "score": 6,
  "runtime_ms": 122
}
```

## 4.6 match_finished

Sent when a winner is determined.

Payload:

```json
{
  "match_id": "MATCH-0001",
  "status": "Finished",
  "winner_id": "PLAYER-0002",
  "winning_reason": "First Accepted",
  "finished_at": "2026-03-24T18:06:03Z"
}
```

## 4.7 match_review_required

Sent when automated resolution cannot break a tie.

Payload:

```json
{
  "match_id": "MATCH-0001",
  "status": "Review",
  "reason": "Equal best score and equal wrong submission count"
}
```

## 5. Timer Behavior

The timer must be server-authoritative.

Rules:

1. The server stores `start_time` and `deadline` on the match.
2. Clients render countdown using server-provided timestamps.
3. Clients may animate locally between syncs.
4. The server rejects submissions after the deadline.
5. On deadline, the server enqueues timeout resolution if no accepted submission exists.

## 6. Draft Persistence Model

To support reconnects and projection reliability, draft state uses a two-tier storage model:

Hot storage (Redis):

1. The contestant client sends draft updates periodically (throttled to 250-500ms).
2. The server writes the draft to Redis via `frappe.cache` at key `codeoff_draft:{match_id}:{player_id}`.
3. The server also broadcasts the latest draft to realtime subscribers.
4. On reconnect, the client fetches the latest draft from Redis via a whitelisted API.
5. Redis provides sub-millisecond reads for the spectator page's initial load.

Cold storage (Database):

1. The `Codeoff Draft State` DocType is updated periodically (e.g., every 30 seconds) as a checkpoint.
2. On match end, the final draft is persisted to the DocType as a permanent record.
3. If Redis is flushed, the last checkpoint from the DocType is used as a fallback.

## 7. Judge Module

The judge is a Python module within the Frappe app (`codeoff/code_off/services/judge.py`), not a separate HTTP service. It executes contestant code in an isolated subprocess.

The judge module must:

1. Execute Python code in a subprocess with `subprocess.run()`.
2. Apply resource limits using the `resource` module (CPU time, memory) and `timeout` for wall-clock enforcement.
3. Run sample or hidden tests based on request type.
4. Return verdict, pass counts, runtime, and stderr if applicable.
5. Enforce execution limits.
6. Never expose hidden expected outputs to clients.

## 8. Judge Integration Contract

Since the judge is an internal Python module called from background jobs, the contract is defined as Python dicts passed between functions (shown here as JSON for clarity).

## 8.1 Submission Request

The background job calls the judge module with:

```json
{
  "submission_id": "SUB-0001",
  "match_id": "MATCH-0001",
  "player_id": "PLAYER-0001",
  "language": "python",
  "source_code": "def two_sum(nums, target):\n    ...",
  "function_name": "two_sum",
  "limits": {
    "time_limit_seconds": 2.0,
    "memory_limit_mb": 256,
    "output_limit_kb": 1024
  },
  "tests": [
    {
      "id": "TC-001",
      "input": [[2, 7, 11, 15], 9],
      "expected_output": [0, 1],
      "weight": 1
    }
  ]
}
```

## 8.2 Judge Response

The judge module returns:

```json
{
  "submission_id": "SUB-0001",
  "status": "Completed",
  "verdict": "Wrong Answer",
  "passed_tests": 6,
  "total_tests": 10,
  "score": 6,
  "runtime_ms": 122,
  "memory_kb": 20480,
  "failed_test_ids": ["TC-007", "TC-008", "TC-009", "TC-010"],
  "stderr": ""
}
```

The full failed test detail must remain internal and should not be exposed to contestant clients for hidden tests.

## 9. Submission Processing Flow

1. Contestant clicks `Submit`.
2. Frappe validates player, match state, language, and deadline.
3. `Codeoff Submission` record is created in `Queued` state.
4. Frappe enqueues a background job that calls the judge module.
5. The judge module executes code in a subprocess and returns results.
6. The background job acquires a lock on the match document (`frappe.lock_doc`) before updating state.
7. Frappe updates the submission record with verdict and scores.
8. Frappe recomputes match scoring state (best scores, wrong submission counts).
9. If verdict is `Accepted`, Frappe checks for existing accepted submissions. If none, this player wins. If another accepted submission exists, the earlier `submitted_at` timestamp wins. The match is finalized.
10. Otherwise the match remains live until deadline or later accepted submission.
11. Realtime events are published for spectators and contestants.

## 10. Sample Test Run Flow

Sample test runs are not official submissions. They are ephemeral — no DocType record is created.

Rules:

1. They execute only against `Sample` test cases.
2. They do not increment wrong submission counts.
3. They are not persisted. The result is returned directly to the requesting contestant via the API response.
4. They return output and pass/fail feedback to the requesting contestant only.
5. They are executed via the same judge module but with only sample test cases.

## 11. Spectator Page Requirements

The spectator page (`/codeoff/spectate/:matchId`) is a public Vue route with no authentication required.

The spectator page must:

1. Subscribe to match realtime events via `socket.on()` from frappe-ui.
2. Load the latest draft for both players from Redis (via a public whitelisted API) on initial render.
3. Update both read-only CodeMirror 6 editors on every `draft_updated` event.
4. Display verdict markers without exposing hidden test details.
5. Display the official countdown based on `deadline`.
6. Show a final winner state when `match_finished` is received.

## 12. Failure Handling

## 12.1 Judge Failure

If the judge subprocess fails (crash, timeout, resource exhaustion):

1. Submission transitions to `Failed` status with verdict `Internal Error`.
2. The contestant sees a clear error message indicating the submission could not be judged and they may retry.
3. The match remains live unless the organizer intervenes.
4. The failure is logged for organizer visibility.

## 12.2 Realtime Disconnect

If a client disconnects:

1. The match continues.
2. The client reconnects and fetches latest match state and draft snapshot.
3. Timer is recalculated from server timestamps.

## 12.3 Deadline Race Conditions

To avoid disputes:

1. The submission API must compare current server time to match deadline.
2. Any submission arriving after the deadline is rejected.
3. Judge results for accepted pre-deadline submissions remain valid even if returned after the deadline.

## 13. Performance Guidance

1. Draft updates should be throttled on the client (250-500ms).
2. The MVP transmits full document snapshots since only one match is active at a time.
3. Large editor payloads may later be optimized with diff-based transport if concurrency increases.
4. Spectator pages should be read-only and stateless beyond local rendering state.
5. Redis-backed draft reads ensure fast spectator page loads without database queries.

## 14. Security Guidance

1. Realtime payloads sent to spectators must exclude hidden test details and private execution logs.
2. Public spectator pages should use sanitized, minimal payloads.
3. Contestant draft broadcasts should be scoped to the match only.
4. The judge module runs within the Frappe worker process as a subprocess — no external credentials are needed.

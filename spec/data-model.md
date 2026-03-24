# Codeoff Data Model Specification

## 1. Overview

This document defines the Frappe DocTypes and relationships required for the Codeoff MVP.

## 2. Core DocTypes

## 2.1 Codeoff Player

Purpose:

Represents a tournament participant. Each player is backed by a Frappe User account for authentication.

Suggested fields:

1. `user` - Link to `User` - required - unique
2. `player_name` - Data - fetched from `User.full_name`
3. `seed` - Int
4. `is_active` - Check - default `1`
5. `notes` - Small Text

The player's display name and login credentials come from the linked User record. The organizer creates both the User account and Codeoff Player record during registration.

Indexes:

1. `user`
2. `seed`

## 2.2 Codeoff Tournament

Purpose:

Represents a bracketed contest event.

Suggested fields:

1. `tournament_name` - Data - required
2. `status` - Select: Draft, Registration Open, Ready, Live, Completed, Cancelled
3. `format` - Select: Single Elimination
4. `match_duration_seconds` - Int - required
5. `current_round` - Int
6. `started_on` - Datetime
7. `completed_on` - Datetime

Validation rules:

1. Player count in the `players` child table must be a power of 2 (2, 4, 8, 16, etc.) before bracket generation is allowed.

Child tables:

1. `players` - child table containing tournament entrants and optional seed overrides

## 2.3 Codeoff Problem

Purpose:

Represents a coding problem shown to both contestants in a match.

Suggested fields:

1. `title` - Data - required
2. `slug` - Data - unique
3. `difficulty` - Select: Easy, Medium, Hard
4. `statement` - Markdown Editor or Text Editor - required
5. `constraints_text` - Text
5. `function_name` - Data - required - the function name contestants must implement (e.g., `solve`, `two_sum`)
6. `function_signature` - Data - required - the full function signature shown to contestants (e.g., `def two_sum(nums, target):`)
7. `starter_code` - Code - auto-generated from function signature with a `pass` body, can be customized
8. `allowed_language` - Data - default `python`
8. `time_limit_seconds` - Float - default `2.0`
9. `memory_limit_mb` - Int - default `256`
10. `is_active` - Check

Child tables:

1. `test_cases` - child table `Codeoff Test Case` containing sample and hidden test cases inline

## 2.4 Codeoff Test Case

Purpose:

Child table of `Codeoff Problem`. Stores sample and hidden test cases for a problem. Organizers edit test cases inline on the Problem form.

Suggested fields:

1. `case_name` - Data
2. `visibility` - Select: Sample, Hidden
3. `input_data` - JSON - the function arguments as a JSON array (e.g., `[[2,7,11,15], 9]` for `two_sum(nums, target)`)
4. `expected_output` - JSON - the expected return value as JSON (e.g., `[0, 1]`)
5. `weight` - Int - default `1`
6. `sort_order` - Int
7. `is_active` - Check

## 2.5 Codeoff Match

Purpose:

Represents a single 1v1 contest between two players.

Suggested fields:

1. `tournament` - Link to `Codeoff Tournament` - required
2. `round_number` - Int - required
3. `bracket_position` - Int - required
4. `player_1` - Link to `Codeoff Player`
5. `player_2` - Link to `Codeoff Player`
6. `problem` - Link to `Codeoff Problem`
7. `status` - Select: Draft, Ready, Live, Finished, Review, Cancelled
8. `start_time` - Datetime
9. `deadline` - Datetime
10. `winner` - Link to `Codeoff Player`
11. `winning_reason` - Select: First Accepted, Best Score, Tie Review, Manual Override
12. `best_score_player_1` - Int
13. `best_score_player_2` - Int
14. `wrong_submissions_player_1` - Int
15. `wrong_submissions_player_2` - Int
16. `tie_break_metadata` - JSON or Long Text

Bracket advancement is computed mathematically from `round_number` and `bracket_position` rather than stored as foreign key links. The winner of round R position P advances to round R+1 position `ceil(P/2)` as slot Player 1 if P is odd, Player 2 if P is even.

Indexes:

1. `tournament`
2. `status`
3. `round_number`
4. `bracket_position`

## 2.6 Codeoff Submission

Purpose:

Represents an official submission sent for judging.

Suggested fields:

1. `match` - Link to `Codeoff Match` - required
2. `player` - Link to `Codeoff Player` - required
3. `problem` - Link to `Codeoff Problem` - required
4. `language` - Data - default `python`
5. `source_code` - Code - required
6. `submitted_at` - Datetime
7. `status` - Select: Queued, Running, Completed, Failed
8. `verdict` - Select: Accepted, Wrong Answer, Runtime Error, Time Limit Exceeded, Memory Limit Exceeded, Compilation Error, Internal Error
9. `passed_tests` - Int
10. `total_tests` - Int
11. `score` - Int
12. `runtime_ms` - Int
13. `memory_kb` - Int
14. `judge_response` - JSON - internal details, not exposed to clients

Whether a submission is a "wrong submission" is derived from the verdict (`verdict != 'Accepted'`). This is not stored as a separate field.

Indexes:

1. `match`
2. `player`
3. `submitted_at`
4. `verdict`

## 2.7 Codeoff Draft State

Purpose:

Stores editor content snapshots for reconnect recovery and as a persistent record. During live matches, the hot draft state is stored in Redis (`frappe.cache`) for low-latency reads and writes. The DocType record is updated periodically as a checkpoint and on match end.

Suggested fields:

1. `match` - Link to `Codeoff Match` - required
2. `player` - Link to `Codeoff Player` - required
3. `language` - Data - default `python`
4. `source_code` - Code
5. `cursor_line` - Int
6. `cursor_column` - Int
7. `updated_at` - Datetime

Uniqueness:

1. One row per `match + player`

Redis key convention:

1. `codeoff_draft:{match_id}:{player_id}` - stores the current draft as a JSON string with the same fields as above

## 3. Optional Supporting DocTypes

## 3.1 Codeoff Tournament Player

Purpose:

Child table for entrants in a tournament.

Suggested fields:

1. `player` - Link to `Codeoff Player`
2. `seed` - Int
3. `status` - Select: Registered, Checked In, Eliminated, Winner

## 3.2 Codeoff Match Event

Purpose:

Audit trail for important match events.

Suggested fields:

1. `match` - Link to `Codeoff Match`
2. `event_type` - Data
3. `event_time` - Datetime
4. `player` - Link to `Codeoff Player`
5. `payload` - Long Text or JSON

## 4. Relationships

1. One tournament has many matches.
2. One tournament has many registered players (via child table).
3. One problem has many test cases (via child table).
4. One match belongs to one tournament and one problem.
5. One match has many submissions.
6. One match has up to two draft states, one per player.
7. Bracket advancement is computed from `round_number` and `bracket_position`, not stored as links.

## 5. Derived Values

These values should be computed by services, not edited manually where possible:

1. `best_score_player_1`
2. `best_score_player_2`
3. `wrong_submissions_player_1`
4. `wrong_submissions_player_2`
5. `winner`
6. `winning_reason`

## 6. Permissions Model

Suggested role access:

1. `Codeoff Organizer` role (or System Manager)
   - Full CRUD on tournament, player, problem, match, and submission records.
2. `Codeoff Contestant` role
   - Read own player profile.
   - Read assigned live match.
   - Create submissions for own match only.
   - Read own submission history for own live match.
   - Read problem statement for assigned match.
   - Cannot read hidden test cases (enforced by API, not DocType permissions).
3. Spectator access
   - No Frappe role required. Spectator data is served via public whitelisted APIs that return sanitized match state only.

## 7. Data Integrity Rules

1. A live match must have exactly two distinct players.
2. A live match must have exactly one assigned problem.
3. Official submissions must be rejected after `deadline`.
4. Submissions must use `python` as the language.
5. Hidden test cases must never be returned by public APIs.
6. Only one winner may be stored for a finished match.

## 8. Migration Notes

Suggested implementation order for DocTypes:

1. `Codeoff Player`
2. `Codeoff Tournament`
3. `Codeoff Problem`
4. `Codeoff Test Case`
5. `Codeoff Match`
6. `Codeoff Submission`
7. `Codeoff Draft State`
8. `Codeoff Match Event` optional

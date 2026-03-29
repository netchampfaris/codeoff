# Codeoff Spectator Engagement Specification

## 1. Overview

This document defines the next spectator-facing product layer for Codeoff after the MVP. The goal is to make matches feel more like a live event by adding:

1. Pre-match spectator predictions.
2. Momentum banners that narrate important match events.
3. Reaction spikes that visualize crowd energy bursts.
4. A live audience count visible across the application on all non-contestant pages.

These features are additive. They must not change judging fairness, bracket rules, or player match behavior.

## 2. Product Goals

The system should:

1. Give spectators a lightweight reason to emotionally commit to a player before a match starts.
2. Translate low-level match state changes into audience-readable story beats.
3. Make crowd participation visible without overwhelming the code projection.
4. Expose a live audience count so organizers and spectators can see that the room is active.
5. Preserve the current clean contestant workspace by keeping all of these features off the player match page.

## 3. Non-Goals

This phase will not include:

1. Real-money betting or wagering.
2. Prediction odds, line movement, or payout math.
3. Chat, threaded commentary, or spectator messaging.
4. Changes to winner determination logic.
5. Additional contestant-side distractions during active play.

## 4. UX Surfaces

## 4.1 Global Audience Count

The application must show a live audience count in a consistent location across all Codeoff pages except the contestant match workspace.

Required pages:

1. Organizer home and bracket page.
2. Spectate home page.
3. Spectate match page.
4. Any future public or organizer-facing Codeoff pages that use the shared app shell.

Excluded pages:

1. Contestant match workspace at `/match/:matchId`.

Placement:

1. The default location should be the shared navbar or top-level app header.
2. The component should be visually compact, always visible, and not require scrolling.
3. The same component should be reused across eligible pages to avoid count mismatches or layout drift.

Display rules:

1. The label should clearly indicate that the number is live, for example `live audience 42` or `42 tuned in`.
2. The count should update in realtime when viewers join or leave.
3. If the audience service is temporarily unavailable, the UI should show the last known count with a degraded state such as `audience --`.

Metric definition:

1. The default global audience count is the number of active non-contestant viewers currently connected to the Codeoff frontend.
2. Contestants on the active match workspace must be excluded from this count.
3. Organizers viewing the bracket or spectate pages may be included, since they are part of the live audience surface.

Optional future extension:

1. On match-specific spectate pages, the UI may later show both total live audience and current match audience, but MVP for this feature only requires one globally visible count.

## 4.2 Prediction UX

Predictions are a pre-match spectator interaction. They must feel fast and lightweight.

Core rule:

1. Predictions are open only while a match is in `Ready` state.
2. Predictions lock immediately when the match becomes `Live`.
3. Predictions are spectator-facing only and have no effect on the actual match result.

### 4.2.1 Spectate Home

Each `Ready` match card should display:

1. A prediction status indicator such as `crowd pick open`.
2. The current crowd split between both players.
3. The total number of predictions submitted for that match.

Example copy:

1. `crowd pick open`
2. `alice 58% · bob 42%`
3. `31 picks`

### 4.2.2 Pre-Match Lobby

On the spectator-facing lobby state for a specific match, the UI should show a central prompt above or between the two player cards:

1. `Who takes this match?`

Each player card should expose one large tap target:

1. `Pick Alice`
2. `Pick Bob`

After a pick is submitted, the UI should switch from input mode to confirmation mode:

1. `You picked Alice`
2. `Crowd split: 58% vs 42%`
3. `Prediction locks when match starts`

### 4.2.3 Live Match State

Once the match is live, the prediction CTA disappears and is replaced with read-only status:

1. `Your pick: Alice`
2. Crowd split remains visible if space allows.

### 4.2.4 Result Resolution

At match completion, the prediction resolves immediately:

1. If the spectator picked correctly, the resolved state should briefly celebrate the correct call.
2. If the spectator picked incorrectly, the resolved state should show a miss state without feeling punitive.
3. If the match goes to `Review`, the prediction remains pending until the organizer resolves the winner.

## 5. Momentum Banners

Momentum banners are short-lived overlays that narrate important moments in a live match.

Definition:

1. A momentum banner is a temporary UI element shown on the spectate match page.
2. Banners should appear above the normal match chrome without hiding the code panes for more than a brief moment.
3. Each banner should auto-dismiss after a short duration, suggested 2 to 4 seconds.

Purpose:

1. Convert internal match state into audience-readable drama.
2. Help viewers understand what changed without requiring them to parse code or submission lists.

### 5.1 Banner Design Rules

1. Only one banner should be visible at a time.
2. Additional banners should queue or be dropped based on priority.
3. Banner text must stay short and legible from a distance.
4. Banner styling should distinguish positive progress, lead changes, time pressure, and review states.

### 5.2 Suggested Banner Triggers

The following banner types should be supported:

1. `First blood` when the first completed official submission in the match arrives.
2. `Alice takes the lead` when a player improves to a strictly better best score than the opponent.
3. `Bob answers back` when the trailing player retakes the lead.
4. `Samples cleared` when a player clears all visible sample tests, if sample completion becomes available as a public signal.
5. `Final minute` when the match enters its last 60 seconds.
6. `Alice lands the solve` when a player gets `Accepted`.
7. `Match under review` when the server places the match in `Review`.

### 5.3 Priority Rules

Suggested priority order:

1. `Accepted`
2. `Review`
3. `Lead change`
4. `Final minute`
5. `First blood`
6. `Samples cleared`

If a higher-priority event occurs while a lower-priority banner is visible:

1. The new banner may replace the current one immediately.
2. The previous banner does not need to be replayed.

## 6. Reaction Spikes

Reaction spikes are crowd-driven hype effects that amplify unusually dense bursts of emoji reactions.

Definition:

1. Individual emoji reactions remain lightweight floating feedback.
2. A reaction spike is a stronger visual effect triggered when reaction volume crosses a threshold inside a short time window.

Purpose:

1. Let the projection reflect crowd energy instead of only showing individual emoji floaters.
2. Reinforce big live moments without requiring audio or commentary.

### 6.1 Spike Detection

Suggested default rule:

1. Track reactions per player over a rolling 3-second window.
2. Trigger a spike when reactions for one side exceed a configured threshold.
3. The threshold should be configurable and should default to a conservative value that avoids constant triggering.

Example threshold:

1. `8 reactions in 3 seconds for one player`

### 6.2 Spike Effects

When a spike is triggered, the UI may perform one or more of the following:

1. Pulse the corresponding player panel border or background.
2. Increase emoji density for a short burst.
3. Show a short crowd-energy label such as `crowd erupts for Alice`.
4. Slightly intensify the timer or stage lighting effect if both players spike near the deadline.

### 6.3 Interaction With Momentum Banners

Momentum banners and reaction spikes are separate systems:

1. Momentum banners are system-detected narrative events.
2. Reaction spikes are crowd-detected hype events.
3. Both may happen at the same time, but spike effects should not obscure banner text.

## 7. Realtime Requirements

These features require additional realtime signaling beyond the current match-state broadcast.

## 7.1 Audience Presence

The server must maintain a live presence model for non-contestant viewers.

Requirements:

1. Clients on eligible pages should register presence on mount and refresh it periodically.
2. Presence should expire automatically if a browser disconnects or stops heartbeating.
3. Contestant workspace clients must not register as spectators.
4. The server should broadcast the latest audience count to clients whenever the count changes materially.

Suggested payload:

```json
{
  "event_type": "audience_count_updated",
  "audience_total": 42,
  "updated_at": "2026-03-29T19:20:00Z"
}
```

## 7.2 Prediction Events

Suggested server-side prediction payloads:

```json
{
  "event_type": "prediction_summary_updated",
  "match_id": "MATCH-0001",
  "status": "Open",
  "total_predictions": 31,
  "player_1_predictions": 18,
  "player_2_predictions": 13,
  "locked_at": null
}
```

When a match goes live:

```json
{
  "event_type": "prediction_locked",
  "match_id": "MATCH-0001",
  "locked_at": "2026-03-29T19:30:00Z"
}
```

When a winner is finalized:

```json
{
  "event_type": "prediction_resolved",
  "match_id": "MATCH-0001",
  "winner_id": "PLAYER-0002",
  "status": "Resolved"
}
```

## 7.3 Momentum Events

The frontend may derive some banners from match state diffs, but the server should be the long-term source of truth for major moments so all clients see the same narrative.

Suggested payload:

```json
{
  "event_type": "momentum_banner",
  "match_id": "MATCH-0001",
  "banner_type": "lead_change",
  "player_id": "PLAYER-0001",
  "message": "Alice takes the lead",
  "priority": 80,
  "duration_ms": 3000,
  "created_at": "2026-03-29T19:31:12Z"
}
```

## 7.4 Reaction Spike Events

Suggested payload:

```json
{
  "event_type": "reaction_spike",
  "match_id": "MATCH-0001",
  "player_id": "PLAYER-0001",
  "emoji": "🔥",
  "count": 10,
  "window_ms": 3000,
  "message": "Crowd erupts for Alice"
}
```

## 8. Data Model

The existing MVP data model can be extended with minimal additions.

## 8.1 Prediction Storage

Recommended new DocType: `Codeoff Match Prediction`

Suggested fields:

1. `match` - Link to `Codeoff Match` - required
2. `predicted_player` - Link to `Codeoff Player` - required
3. `spectator_token` - Data - required for guest tracking
4. `spectator_name` - Data - optional
5. `status` - Select: Open, Locked, Resolved, Voided
6. `was_correct` - Check
7. `created_at` - Datetime
8. `resolved_at` - Datetime

Rules:

1. At most one active prediction per `match + spectator_token`.
2. Prediction edits are allowed only while the match remains `Ready`.
3. On match start, all open predictions for that match become `Locked`.
4. On winner resolution, all locked predictions become `Resolved`.

## 8.2 Audience Presence Storage

Recommended storage model:

1. Use Redis as the hot source of truth for presence.
2. Store one presence record per viewer session with a TTL.
3. Aggregate counts from active keys instead of creating permanent database rows for page views.

Suggested key conventions:

1. `codeoff_presence:global:{session_id}` for any eligible non-contestant page
2. `codeoff_presence:match:{match_id}:{session_id}` if match-specific counts are added later

Required fields in the Redis payload:

1. `session_id`
2. `page_type`
3. `is_contestant_page`
4. `updated_at`

## 8.3 Event Logging

Momentum banners and reaction spikes may optionally write to `Codeoff Match Event` for replay or analytics, but database persistence is not required for initial release.

If persisted, suggested event types include:

1. `prediction_locked`
2. `prediction_resolved`
3. `momentum_banner`
4. `reaction_spike`
5. `audience_peak_updated`

## 9. Page-by-Page Requirements

## 9.1 Home / Organizer Bracket

Must show:

1. Global live audience count in the navbar.
2. No prediction CTA unless the organizer is also using the public spectate surface.

## 9.2 Spectate Home

Must show:

1. Global live audience count in the navbar.
2. Prediction summary on `Ready` match cards.
3. Optional visual emphasis for the most-picked upcoming match.

## 9.3 Spectate Match Page

Must show:

1. Global live audience count in the navbar.
2. Prediction CTA while the match is `Ready`.
3. Read-only prediction state once the match is `Live`.
4. Momentum banners during live play.
5. Reaction spikes layered over the existing emoji reaction system.

## 9.4 Contestant Match Workspace

Must not show:

1. Global audience count.
2. Prediction UI.
3. Momentum banners.
4. Reaction spike effects.

The contestant page should remain focused on coding, timing, and verdict feedback only.

## 10. Failure And Edge Cases

1. If prediction submission fails, the spectator should remain in input mode and see a short retryable error state.
2. If a match is started while a spectator is mid-pick, the server must reject the prediction and return locked state.
3. If a match enters `Review`, the prediction result must remain pending until the winner is finalized.
4. If audience presence heartbeats fail temporarily, the UI should degrade gracefully rather than flicker between large count changes.
5. If reaction spikes trigger too frequently, server-side or client-side cooldowns must suppress repeats.
6. If multiple banner-worthy events happen simultaneously, only the highest-priority banner should show immediately.

## 11. Rollout Order

Recommended implementation sequence:

1. Global audience count in the shared non-contestant navbar.
2. Prediction summaries and pick flow for `Ready` matches.
3. Basic momentum banners with three initial triggers: first blood, lead change, accepted.
4. Reaction spike detection and one conservative panel pulse effect.

This order delivers visible value quickly while keeping the first release operationally simple.

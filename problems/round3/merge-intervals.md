---
title: Merge Intervals
slug: merge-intervals
difficulty: Hard
round: 3
suggested_time_minutes: 10
function_name: merge_intervals
function_signature: "def merge_intervals(intervals):"
time_limit_seconds: 2.0
memory_limit_mb: 256
---

# Merge Intervals

## Problem Statement

Given a list of intervals where `intervals[i] = [start, end]`, merge all **overlapping** intervals and return a list of the non-overlapping intervals that cover all intervals in the input.

Two intervals `[a, b]` and `[c, d]` overlap if `c <= b` (the second starts before or exactly when the first ends).

The output intervals must be **sorted by start time**.

## Examples

### Example 1

**Input:** `intervals = [[1, 3], [2, 6], [8, 10], [15, 18]]`
**Output:** `[[1, 6], [8, 10], [15, 18]]`
**Explanation:** `[1,3]` and `[2,6]` overlap → merged to `[1,6]`. The others don't overlap.

### Example 2

**Input:** `intervals = [[1, 4], [4, 5]]`
**Output:** `[[1, 5]]`
**Explanation:** `[1,4]` and `[4,5]` touch at 4, so they merge into `[1,5]`.

### Example 3

**Input:** `intervals = [[1, 4], [2, 3]]`
**Output:** `[[1, 4]]`
**Explanation:** `[2,3]` is completely inside `[1,4]`, so the result is just `[1,4]`.

## Constraints

- `1 <= len(intervals) <= 10000`
- `intervals[i].length == 2`
- `0 <= start <= end <= 10000`
- The input may **not** be sorted.

## Starter Code

```python
def merge_intervals(intervals):
    pass
```

---

## Test Cases

### Sample (shown to contestants)

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 1 | `[[[1, 3], [2, 6], [8, 10], [15, 18]]]` | `[[1, 6], [8, 10], [15, 18]]` |
| 2 | `[[[1, 4], [4, 5]]]` | `[[1, 5]]` |
| 3 | `[[[1, 4], [2, 3]]]` | `[[1, 4]]` |

### Hidden

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 4 | `[[[1, 2], [3, 4], [5, 6]]]` | `[[1, 2], [3, 4], [5, 6]]` |
| 5 | `[[[1, 10], [2, 3], [4, 5]]]` | `[[1, 10]]` |
| 6 | `[[[1, 4]]]` | `[[1, 4]]` |
| 7 | `[[[4, 5], [1, 4], [0, 4]]]` | `[[0, 5]]` |
| 8 | `[[[1, 3], [3, 5], [5, 7]]]` | `[[1, 7]]` |
| 9 | `[[[0, 0], [1, 1]]]` | `[[0, 0], [1, 1]]` |
| 10 | `[[[2, 3], [4, 5], [6, 7], [8, 9], [1, 10]]]` | `[[1, 10]]` |

> **Note:** Each row's `input_data` wraps `intervals` in an outer array: `[intervals]`. The outer list is the argument list, and `intervals` itself is a list of `[start, end]` pairs.

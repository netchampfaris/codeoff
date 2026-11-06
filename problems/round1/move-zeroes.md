---
title: Move Zeroes
slug: move-zeroes
difficulty: Easy
round: 1
suggested_time_minutes: 5
function_name: move_zeroes
function_signature: "def move_zeroes(nums):"
time_limit_seconds: 2.0
memory_limit_mb: 256
---

# Move Zeroes

## Problem Statement

Given an integer list `nums`, move all `0`s to the **end** while preserving the relative order of the non-zero elements. Return the modified list.

Do **not** create a new list — modify and return `nums` in-place (or return the equivalent result; the judge checks the return value).

## Examples

### Example 1

**Input:** `nums = [0, 1, 0, 3, 12]`
**Output:** `[1, 3, 12, 0, 0]`

### Example 2

**Input:** `nums = [0, 0, 1]`
**Output:** `[1, 0, 0]`

### Example 3

**Input:** `nums = [1, 2, 3]`
**Output:** `[1, 2, 3]`
**Explanation:** No zeroes, so the list is unchanged.

## Constraints

- `1 <= len(nums) <= 10000`
- `-2^31 <= nums[i] <= 2^31 - 1`

## Starter Code

```python
def move_zeroes(nums):
    pass
```

---

## Test Cases

### Sample (shown to contestants)

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 1 | `[[0, 1, 0, 3, 12]]` | `[1, 3, 12, 0, 0]` |
| 2 | `[[0, 0, 1]]` | `[1, 0, 0]` |
| 3 | `[[1, 2, 3]]` | `[1, 2, 3]` |

### Hidden

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 4 | `[[0]]` | `[0]` |
| 5 | `[[1]]` | `[1]` |
| 6 | `[[0, 0, 0]]` | `[0, 0, 0]` |
| 7 | `[[4, 2, 0, 1, 5]]` | `[4, 2, 1, 5, 0]` |
| 8 | `[[0, 0, 1, 0, 2]]` | `[1, 2, 0, 0, 0]` |
| 9 | `[[-1, 0, 3, 0, -5]]` | `[-1, 3, -5, 0, 0]` |
| 10 | `[[1, 0, 2, 0, 3, 0]]` | `[1, 2, 3, 0, 0, 0]` |

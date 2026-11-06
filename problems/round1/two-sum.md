---
title: Two Sum
slug: two-sum
difficulty: Easy
round: 1
suggested_time_minutes: 5
function_name: two_sum
function_signature: "def two_sum(nums, target):"
time_limit_seconds: 2.0
memory_limit_mb: 256
---

# Two Sum

## Problem Statement

Given a list of integers `nums` and an integer `target`, return the **indices** of the two numbers that add up to `target`.

You may assume exactly one valid answer exists. You may not use the same element twice. Return the indices in **ascending order**.

## Examples

### Example 1

**Input:** `nums = [2, 7, 11, 15]`, `target = 9`
**Output:** `[0, 1]`
**Explanation:** `nums[0] + nums[1] == 2 + 7 == 9`.

### Example 2

**Input:** `nums = [3, 2, 4]`, `target = 6`
**Output:** `[1, 2]`
**Explanation:** `nums[1] + nums[2] == 2 + 4 == 6`.

### Example 3

**Input:** `nums = [3, 3]`, `target = 6`
**Output:** `[0, 1]`

## Constraints

- `2 <= len(nums) <= 10000`
- `-10^9 <= nums[i] <= 10^9`
- `-10^9 <= target <= 10^9`
- Exactly one valid answer exists.

## Starter Code

```python
def two_sum(nums, target):
    pass
```

---

## Test Cases

### Sample (shown to contestants)

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 1 | `[[2, 7, 11, 15], 9]` | `[0, 1]` |
| 2 | `[[3, 2, 4], 6]` | `[1, 2]` |
| 3 | `[[3, 3], 6]` | `[0, 1]` |

### Hidden

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 4 | `[[1, 2, 3, 4, 5], 9]` | `[3, 4]` |
| 5 | `[[-1, -2, -3, -4, -5], -8]` | `[2, 4]` |
| 6 | `[[0, 4, 3, 0], 0]` | `[0, 3]` |
| 7 | `[[1, 5, 3, 7], 8]` | `[1, 3]` |
| 8 | `[[5, 75, 25], 100]` | `[1, 2]` |
| 9 | `[[1, 3, 5, 7, 9], 10]` | `[0, 4]` |
| 10 | `[[-3, 4, 3, 90], 0]` | `[0, 2]` |

> **Note:** `input_data` is `[nums, target]` — two arguments to the function.

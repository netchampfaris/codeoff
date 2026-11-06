---
title: Rotate Array
slug: rotate-array
difficulty: Medium
round: 2
suggested_time_minutes: 7
function_name: rotate_array
function_signature: "def rotate_array(nums, k):"
time_limit_seconds: 2.0
memory_limit_mb: 256
---

# Rotate Array

## Problem Statement

Given an integer array `nums` and a non-negative integer `k`, rotate the array to the **right** by `k` steps and return the resulting list.

Rotating right by 1 step means moving the last element to the front.

## Examples

### Example 1

**Input:** `nums = [1, 2, 3, 4, 5, 6, 7]`, `k = 3`
**Output:** `[5, 6, 7, 1, 2, 3, 4]`
**Explanation:** Rotate right 3 steps:
- Step 1: `[7, 1, 2, 3, 4, 5, 6]`
- Step 2: `[6, 7, 1, 2, 3, 4, 5]`
- Step 3: `[5, 6, 7, 1, 2, 3, 4]`

### Example 2

**Input:** `nums = [-1, -100, 3, 99]`, `k = 2`
**Output:** `[3, 99, -1, -100]`

### Example 3

**Input:** `nums = [1, 2, 3]`, `k = 4`
**Output:** `[3, 1, 2]`
**Explanation:** `k = 4` is equivalent to `k = 1` for an array of length 3 (`4 % 3 = 1`).

## Constraints

- `1 <= len(nums) <= 10000`
- `-2^31 <= nums[i] <= 2^31 - 1`
- `0 <= k <= 10^5`

## Starter Code

```python
def rotate_array(nums, k):
    pass
```

---

## Test Cases

### Sample (shown to contestants)

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 1 | `[[1, 2, 3, 4, 5, 6, 7], 3]` | `[5, 6, 7, 1, 2, 3, 4]` |
| 2 | `[[-1, -100, 3, 99], 2]` | `[3, 99, -1, -100]` |
| 3 | `[[1, 2, 3], 4]` | `[3, 1, 2]` |

### Hidden

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 4 | `[[1, 2], 1]` | `[2, 1]` |
| 5 | `[[1], 0]` | `[1]` |
| 6 | `[[1, 2, 3, 4, 5], 5]` | `[1, 2, 3, 4, 5]` |
| 7 | `[[1, 2, 3, 4], 2]` | `[3, 4, 1, 2]` |
| 8 | `[[1, 2], 0]` | `[1, 2]` |
| 9 | `[[1, 2, 3, 4, 5], 7]` | `[4, 5, 1, 2, 3]` |
| 10 | `[[10, 20, 30], 9]` | `[10, 20, 30]` |

> **Note:** `input_data` is `[nums, k]` — two arguments to the function.

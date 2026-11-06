---
title: Missing Number
slug: missing-number
difficulty: Easy
round: 1
suggested_time_minutes: 5
function_name: missing_number
function_signature: "def missing_number(nums):"
time_limit_seconds: 2.0
memory_limit_mb: 256
---

# Missing Number

## Problem Statement

Given a list `nums` containing `n` **distinct** integers in the range `[0, n]`, return the **one number** that is missing from the list.

The list has `n` elements so exactly one number in the range `[0, n]` is absent.

## Examples

### Example 1

**Input:** `nums = [3, 0, 1]`
**Output:** `2`
**Explanation:** The range is `[0, 1, 2, 3]`. `2` is missing.

### Example 2

**Input:** `nums = [0, 1]`
**Output:** `2`
**Explanation:** The range is `[0, 1, 2]`. `2` is missing.

### Example 3

**Input:** `nums = [9, 6, 4, 2, 3, 5, 7, 0, 1]`
**Output:** `8`
**Explanation:** The range is `[0..9]`. `8` is missing.

## Constraints

- `1 <= n <= 10000`
- `0 <= nums[i] <= n`
- All values in `nums` are distinct.

## Starter Code

```python
def missing_number(nums):
    pass
```

---

## Test Cases

### Sample (shown to contestants)

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 1 | `[[3, 0, 1]]` | `2` |
| 2 | `[[0, 1]]` | `2` |
| 3 | `[[9, 6, 4, 2, 3, 5, 7, 0, 1]]` | `8` |

### Hidden

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 4 | `[[0]]` | `1` |
| 5 | `[[1]]` | `0` |
| 6 | `[[0, 2]]` | `1` |
| 7 | `[[1, 2, 3]]` | `0` |
| 8 | `[[0, 1, 2, 4]]` | `3` |
| 9 | `[[5, 4, 3, 2, 1, 0]]` | `6` |
| 10 | `[[1, 2, 3, 4, 5]]` | `0` |

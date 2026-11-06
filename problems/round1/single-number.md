---
title: Single Number
slug: single-number
difficulty: Easy
round: 1
suggested_time_minutes: 5
function_name: single_number
function_signature: "def single_number(nums):"
time_limit_seconds: 2.0
memory_limit_mb: 256
---

# Single Number

## Problem Statement

Given a non-empty list of integers `nums`, every element appears **exactly twice** except for one element which appears **exactly once**. Return that single element.

Your solution must work correctly for any input satisfying these constraints.

## Examples

### Example 1

**Input:** `nums = [2, 2, 1]`  
**Output:** `1`

### Example 2

**Input:** `nums = [4, 1, 2, 1, 2]`  
**Output:** `4`

### Example 3

**Input:** `nums = [1]`  
**Output:** `1`

### Example 4

**Input:** `nums = [7, 3, 7, 5, 5]`  
**Output:** `3`

## Constraints

- `1 <= len(nums) <= 30001` (always odd — one unique, rest in pairs)
- `-30000 <= nums[i] <= 30000`
- Exactly one element appears once; all others appear exactly twice.

## Starter Code

```python
def single_number(nums):
    pass
```

---

## Test Cases

### Sample (shown to contestants)

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 1 | `[[2, 2, 1]]` | `1` |
| 2 | `[[4, 1, 2, 1, 2]]` | `4` |
| 3 | `[[1]]` | `1` |

### Hidden

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 4 | `[[7, 3, 7, 5, 5]]` | `3` |
| 5 | `[[0, 1, 0]]` | `1` |
| 6 | `[[99]]` | `99` |
| 7 | `[[-1, -1, -2]]` | `-2` |
| 8 | `[[1, 2, 3, 2, 1]]` | `3` |
| 9 | `[[10, 20, 10, 30, 20]]` | `30` |
| 10 | `[[-3, 4, -3]]` | `4` |

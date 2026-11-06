---
title: Count Good Pairs
slug: count-good-pairs
difficulty: Easy
round: 1
suggested_time_minutes: 5
function_name: count_good_pairs
function_signature: "def count_good_pairs(nums):"
time_limit_seconds: 2.0
memory_limit_mb: 256
---

# Count Good Pairs

## Problem Statement

Given a list of integers `nums`, return the number of **good pairs**.

A pair `(i, j)` is **good** if:
- `nums[i] == nums[j]`, and
- `i < j`

## Examples

### Example 1

**Input:** `nums = [1, 2, 3, 1, 1, 3]`
**Output:** `4`
**Explanation:** There are 4 good pairs: `(0,3)`, `(0,4)`, `(3,4)`, `(2,5)`.

### Example 2

**Input:** `nums = [1, 1, 1, 1]`
**Output:** `6`
**Explanation:** Every pair is good: `(0,1)`, `(0,2)`, `(0,3)`, `(1,2)`, `(1,3)`, `(2,3)`.

### Example 3

**Input:** `nums = [1, 2, 3]`
**Output:** `0`
**Explanation:** No two elements are equal.

## Constraints

- `1 <= len(nums) <= 100`
- `1 <= nums[i] <= 100`

## Starter Code

```python
def count_good_pairs(nums):
    pass
```

---

## Test Cases

### Sample (shown to contestants)

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 1 | `[[1, 2, 3, 1, 1, 3]]` | `4` |
| 2 | `[[1, 1, 1, 1]]` | `6` |
| 3 | `[[1, 2, 3]]` | `0` |

### Hidden

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 4 | `[[1]]` | `0` |
| 5 | `[[1, 1]]` | `1` |
| 6 | `[[5, 5, 5]]` | `3` |
| 7 | `[[1, 2, 1, 2, 1]]` | `4` |
| 8 | `[[7, 3, 7, 3, 7]]` | `4` |
| 9 | `[[1, 2, 3, 4, 5, 1, 2, 3, 4, 5]]` | `5` |
| 10 | `[[100, 100, 100, 100, 100]]` | `10` |

> **Note:** `input_data` wraps the function arguments as a JSON array. `[[1,2,3]]` maps to `count_good_pairs([1,2,3])`.

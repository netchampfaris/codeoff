---
title: Spiral Matrix
slug: spiral-matrix
difficulty: Medium
round: 2
suggested_time_minutes: 7
function_name: spiral_order
function_signature: "def spiral_order(matrix):"
time_limit_seconds: 2.0
memory_limit_mb: 256
---

# Spiral Matrix

## Problem Statement

Given an `m × n` matrix of integers, return all its elements in **spiral order** — clockwise, starting from the top-left corner.

## Examples

### Example 1

**Input:** `matrix = [[1,2,3],[4,5,6],[7,8,9]]`
**Output:** `[1, 2, 3, 6, 9, 8, 7, 4, 5]`
**Explanation:**
```
1 → 2 → 3
            ↓
4 → 5   6
↑       ↓
7 ← 8 ← 9
```
Traverse: right along the top, down the right side, left along the bottom, up the left side, then spiral inward.

### Example 2

**Input:** `matrix = [[1,2,3,4],[5,6,7,8],[9,10,11,12]]`
**Output:** `[1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]`

### Example 3

**Input:** `matrix = [[1]]`
**Output:** `[1]`

## Constraints

- `1 <= m, n <= 20` (m rows, n columns)
- `-100 <= matrix[i][j] <= 100`

## Starter Code

```python
def spiral_order(matrix):
    pass
```

---

## Test Cases

### Sample (shown to contestants)

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 1 | `[[[1,2,3],[4,5,6],[7,8,9]]]` | `[1,2,3,6,9,8,7,4,5]` |
| 2 | `[[[1,2,3,4],[5,6,7,8],[9,10,11,12]]]` | `[1,2,3,4,8,12,11,10,9,5,6,7]` |
| 3 | `[[[1]]]` | `[1]` |

### Hidden

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 4 | `[[[1,2],[3,4]]]` | `[1,2,4,3]` |
| 5 | `[[[1,2,3],[4,5,6]]]` | `[1,2,3,6,5,4]` |
| 6 | `[[[1,2],[3,4],[5,6]]]` | `[1,2,4,6,5,3]` |
| 7 | `[[[1,2,3,4,5]]]` | `[1,2,3,4,5]` |
| 8 | `[[[1],[2],[3],[4],[5]]]` | `[1,2,3,4,5]` |
| 9 | `[[[1,2,3],[4,5,6],[7,8,9],[10,11,12]]]` | `[1,2,3,6,9,12,11,10,7,4,5,8]` |
| 10 | `[[[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]]]` | `[1,2,3,4,8,12,16,15,14,13,9,5,6,7,11,10]` |

> **Note:** `input_data` wraps the single matrix argument in an outer array: `[matrix]`.

---
title: Rotate Matrix
slug: rotate-matrix
difficulty: Hard
round: 3
suggested_time_minutes: 10
function_name: rotate_matrix
function_signature: "def rotate_matrix(matrix):"
time_limit_seconds: 2.0
memory_limit_mb: 256
---

# Rotate Matrix

## Problem Statement

Given an `n × n` 2D matrix, rotate it **90 degrees clockwise** and return the result.

In a clockwise rotation, the top row becomes the right column, the right column becomes the bottom row, and so on.

## Examples

### Example 1

**Input:**
```
matrix = [
  [1, 2, 3],
  [4, 5, 6],
  [7, 8, 9]
]
```
**Output:**
```
[
  [7, 4, 1],
  [8, 5, 2],
  [9, 6, 3]
]
```
**Explanation:** The first column `[1,4,7]` read bottom to top becomes the first row `[7,4,1]`. And so on for the other columns.

### Example 2

**Input:**
```
matrix = [
  [5,  1,  9, 11],
  [2,  4,  8, 10],
  [13, 3,  6,  7],
  [15, 14, 12, 16]
]
```
**Output:**
```
[
  [15, 13, 2,  5 ],
  [14, 3,  4,  1 ],
  [12, 6,  8,  9 ],
  [16, 7,  10, 11]
]
```

### Example 3

**Input:** `matrix = [[1]]`
**Output:** `[[1]]`

## Constraints

- `n == len(matrix) == len(matrix[i])`
- `1 <= n <= 20`
- `-1000 <= matrix[i][j] <= 1000`

## Starter Code

```python
def rotate_matrix(matrix):
    pass
```

---

## Test Cases

### Sample (shown to contestants)

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 1 | `[[[1,2,3],[4,5,6],[7,8,9]]]` | `[[7,4,1],[8,5,2],[9,6,3]]` |
| 2 | `[[[5,1,9,11],[2,4,8,10],[13,3,6,7],[15,14,12,16]]]` | `[[15,13,2,5],[14,3,4,1],[12,6,8,9],[16,7,10,11]]` |
| 3 | `[[[1]]]` | `[[1]]` |

### Hidden

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 4 | `[[[1,2],[3,4]]]` | `[[3,1],[4,2]]` |
| 5 | `[[[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,16]]]` | `[[13,9,5,1],[14,10,6,2],[15,11,7,3],[16,12,8,4]]` |
| 6 | `[[[1,0,0],[0,1,0],[0,0,1]]]` | `[[0,0,1],[0,1,0],[1,0,0]]` |
| 7 | `[[[0,0],[0,0]]]` | `[[0,0],[0,0]]` |
| 8 | `[[[1,0],[0,0]]]` | `[[0,1],[0,0]]` |
| 9 | `[[[2,3],[1,4]]]` | `[[1,2],[4,3]]` |
| 10 | `[[[1,2,3],[0,0,0],[7,8,9]]]` | `[[7,0,1],[8,0,2],[9,0,3]]` |

> **Note:** `input_data` wraps the single `matrix` argument in an outer array: `[matrix]`.

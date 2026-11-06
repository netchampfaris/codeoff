---
title: Valid Parentheses
slug: valid-parentheses
difficulty: Medium
round: 2
suggested_time_minutes: 7
function_name: is_balanced
function_signature: "def is_balanced(s):"
time_limit_seconds: 2.0
memory_limit_mb: 256
---

# Valid Parentheses

## Problem Statement

Given a string `s` containing only the characters `(`, `)`, `{`, `}`, `[`, and `]`, determine if the string is **valid**.

A string is valid if:
1. Every opening bracket is closed by the **same type** of bracket.
2. Opening brackets are closed in the **correct order** (last opened, first closed).
3. Every closing bracket has a corresponding opening bracket.

Return `True` if valid, `False` otherwise.

## Examples

### Example 1

**Input:** `s = "()"`
**Output:** `True`

### Example 2

**Input:** `s = "()[]{}"`
**Output:** `True`

### Example 3

**Input:** `s = "(]"`
**Output:** `False`
**Explanation:** The closing `]` does not match the opening `(`.

### Example 4

**Input:** `s = "([)]"`
**Output:** `False`
**Explanation:** Brackets are interleaved incorrectly.

### Example 5

**Input:** `s = "{[]}"`
**Output:** `True`

## Constraints

- `1 <= len(s) <= 10000`
- `s` consists of parentheses only: `()[]{}`.

## Starter Code

```python
def is_balanced(s):
    pass
```

---

## Test Cases

### Sample (shown to contestants)

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 1 | `["()"]` | `true` |
| 2 | `["()[]{}"]` | `true` |
| 3 | `["(]"]` | `false` |
| 4 | `["([)]"]` | `false` |
| 5 | `["{[]}"]` | `true` |

### Hidden

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 6 | `[")"]` | `false` |
| 7 | `["(("]` | `false` |
| 8 | `["{[()]}"]` | `true` |
| 9 | `["(()())"]` | `true` |
| 10 | `["((()))"]` | `true` |
| 11 | `["((("]` | `false` |
| 12 | `["{}[]()"]` | `true` |
| 13 | `["{[}]"]` | `false` |

> **Note:** JSON booleans `true`/`false` are used for `expected_output`. The judge compares the Python return value to the parsed JSON value.

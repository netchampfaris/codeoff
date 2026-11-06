---
title: Palindrome Check
slug: palindrome-check
difficulty: Easy
round: 1
suggested_time_minutes: 5
function_name: is_palindrome
function_signature: "def is_palindrome(s):"
time_limit_seconds: 2.0
memory_limit_mb: 256
---

# Palindrome Check

## Problem Statement

Given a string `s`, return `True` if it reads the same forwards and backwards (a **palindrome**), and `False` otherwise.

The check is **case-insensitive** and should **ignore all non-alphanumeric characters** (spaces, punctuation, etc.).

## Examples

### Example 1

**Input:** `s = "racecar"`
**Output:** `True`

### Example 2

**Input:** `s = "hello"`
**Output:** `False`

### Example 3

**Input:** `s = "A man a plan a canal Panama"`
**Output:** `True`
**Explanation:** After keeping only letters/digits and lowercasing: `"amanaplanacanalpanama"`, which is a palindrome.

### Example 4

**Input:** `s = "Was it a car or a cat I saw"`
**Output:** `True`

## Constraints

- `0 <= len(s) <= 10000`
- `s` may contain letters, digits, spaces, and punctuation.

## Starter Code

```python
def is_palindrome(s):
    pass
```

---

## Test Cases

### Sample (shown to contestants)

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 1 | `["racecar"]` | `true` |
| 2 | `["hello"]` | `false` |
| 3 | `["A man a plan a canal Panama"]` | `true` |

### Hidden

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 4 | `[""]` | `true` |
| 5 | `["a"]` | `true` |
| 6 | `["ab"]` | `false` |
| 7 | `["Was it a car or a cat I saw"]` | `true` |
| 8 | `["No lemon, no melon"]` | `true` |
| 9 | `["Madam"]` | `true` |
| 10 | `["race a car"]` | `false` |
| 11 | `["12321"]` | `true` |
| 12 | `["123"]` | `false` |

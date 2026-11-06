---
title: Valid Anagram
slug: valid-anagram
difficulty: Easy
round: 1
suggested_time_minutes: 5
function_name: is_anagram
function_signature: "def is_anagram(s, t):"
time_limit_seconds: 2.0
memory_limit_mb: 256
---

# Valid Anagram

## Problem Statement

Given two strings `s` and `t`, return `True` if `t` is an **anagram** of `s`, and `False` otherwise.

An anagram is a word formed by rearranging the letters of another, using all original letters **exactly once**. The comparison is **case-sensitive**.

## Examples

### Example 1

**Input:** `s = "anagram"`, `t = "nagaram"`  
**Output:** `True`

### Example 2

**Input:** `s = "rat"`, `t = "car"`  
**Output:** `False`

### Example 3

**Input:** `s = "listen"`, `t = "silent"`  
**Output:** `True`

### Example 4

**Input:** `s = "abc"`, `t = "ab"`  
**Output:** `False`  
**Explanation:** Different lengths — cannot be an anagram.

## Constraints

- `1 <= len(s), len(t) <= 50000`
- `s` and `t` consist of lowercase English letters.

## Starter Code

```python
def is_anagram(s, t):
    pass
```

---

## Test Cases

### Sample (shown to contestants)

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 1 | `["anagram", "nagaram"]` | `true` |
| 2 | `["rat", "car"]` | `false` |
| 3 | `["listen", "silent"]` | `true` |

### Hidden

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 4 | `["abc", "ab"]` | `false` |
| 5 | `["a", "a"]` | `true` |
| 6 | `["a", "b"]` | `false` |
| 7 | `["aacc", "ccac"]` | `false` |
| 8 | `["triangle", "integral"]` | `true` |
| 9 | `["dusty", "study"]` | `true` |
| 10 | `["hello", "world"]` | `false` |
| 11 | `["aab", "aba"]` | `true` |
| 12 | `["ab", "ba"]` | `true` |

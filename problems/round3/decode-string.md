---
title: Decode String
slug: decode-string
difficulty: Hard
round: 3
suggested_time_minutes: 10
function_name: decode_string
function_signature: "def decode_string(s):"
time_limit_seconds: 2.0
memory_limit_mb: 256
---

# Decode String

## Problem Statement

Given an encoded string `s`, return its decoded form.

The encoding rule is: `k[encoded_string]`, where `encoded_string` inside the brackets is repeated exactly `k` times. The number `k` is always a positive integer.

Encodings can be **nested** — a bracket group may contain other bracket groups inside it.

You may assume the input is always valid (no extra spaces, no malformed brackets, brackets are always balanced).

## Examples

### Example 1

**Input:** `s = "3[a]2[bc]"`
**Output:** `"aaabcbc"`
**Explanation:** `3[a]` → `"aaa"`, `2[bc]` → `"bcbc"`. Concatenated: `"aaabcbc"`.

### Example 2

**Input:** `s = "3[a2[c]]"`
**Output:** `"accaccacc"`
**Explanation:** Inner `2[c]` → `"cc"`. Then `"a" + "cc"` = `"acc"`. Outer `3["acc"]` → `"accaccacc"`.

### Example 3

**Input:** `s = "2[abc]3[cd]ef"`
**Output:** `"abcabccdcdcdef"`
**Explanation:** `2[abc]` → `"abcabc"`, `3[cd]` → `"cdcdcd"`, then `"ef"` appended.

### Example 4

**Input:** `s = "abc"`
**Output:** `"abc"`
**Explanation:** No encoding — returned as-is.

## Constraints

- `1 <= len(s) <= 30`
- `s` consists of lowercase English letters, digits, and square brackets `[]`.
- All integers in `s` are in the range `[1, 10]`.
- Brackets are always balanced and valid.

## Starter Code

```python
def decode_string(s):
    pass
```

---

## Test Cases

### Sample (shown to contestants)

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 1 | `["3[a]2[bc]"]` | `"aaabcbc"` |
| 2 | `["3[a2[c]]"]` | `"accaccacc"` |
| 3 | `["2[abc]3[cd]ef"]` | `"abcabccdcdcdef"` |

### Hidden

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 4 | `["abc"]` | `"abc"` |
| 5 | `["1[a]"]` | `"a"` |
| 6 | `["10[a]"]` | `"aaaaaaaaaa"` |
| 7 | `["2[2[a]]"]` | `"aaaa"` |
| 8 | `["3[ab]"]` | `"ababab"` |
| 9 | `["2[a3[b]]"]` | `"abbbabbb"` |
| 10 | `["a2[b3[c]]d"]` | `"abcccbcccd"` |

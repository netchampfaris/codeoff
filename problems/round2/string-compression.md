---
title: String Compression
slug: string-compression
difficulty: Medium
round: 2
suggested_time_minutes: 7
function_name: compress
function_signature: "def compress(s):"
time_limit_seconds: 2.0
memory_limit_mb: 256
---

# String Compression

## Problem Statement

Given a string `s`, return its **run-length encoded** form.

In run-length encoding, each group of **consecutive identical characters** is replaced by the character followed by the count of how many times it appears consecutively in that group — even if the count is `1`.

## Examples

### Example 1

**Input:** `s = "aabcccccaaa"`
**Output:** `"a2b1c5a3"`
**Explanation:** `aa` → `a2`, `b` → `b1`, `ccccc` → `c5`, `aaa` → `a3`.

### Example 2

**Input:** `s = "abc"`
**Output:** `"a1b1c1"`
**Explanation:** Each character appears exactly once in its run.

### Example 3

**Input:** `s = "aaa"`
**Output:** `"a3"`

### Example 4

**Input:** `s = ""`
**Output:** `""`
**Explanation:** An empty string encodes to an empty string.

## Constraints

- `0 <= len(s) <= 10000`
- `s` consists of lowercase English letters only.

## Starter Code

```python
def compress(s):
    pass
```

---

## Test Cases

### Sample (shown to contestants)

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 1 | `["aabcccccaaa"]` | `"a2b1c5a3"` |
| 2 | `["abc"]` | `"a1b1c1"` |
| 3 | `["aaa"]` | `"a3"` |

### Hidden

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 4 | `[""]` | `""` |
| 5 | `["a"]` | `"a1"` |
| 6 | `["aabbcc"]` | `"a2b2c2"` |
| 7 | `["aaabbb"]` | `"a3b3"` |
| 8 | `["abcdd"]` | `"a1b1c1d2"` |
| 9 | `["zzzzzzzzzz"]` | `"z10"` |
| 10 | `["aababc"]` | `"a2b1a1b1c1"` |

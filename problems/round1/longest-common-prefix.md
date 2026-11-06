---
title: Longest Common Prefix
slug: longest-common-prefix
difficulty: Easy
round: 1
suggested_time_minutes: 5
function_name: longest_common_prefix
function_signature: "def longest_common_prefix(strs):"
time_limit_seconds: 2.0
memory_limit_mb: 256
---

# Longest Common Prefix

## Problem Statement

Given a list of strings `strs`, find the longest string that is a prefix of **every** string in the list. If there is no common prefix, return an empty string `""`.

## Examples

### Example 1

**Input:** `strs = ["flower", "flow", "flight"]`
**Output:** `"fl"`
**Explanation:** `"fl"` is the longest prefix shared by all three strings.

### Example 2

**Input:** `strs = ["dog", "racecar", "car"]`
**Output:** `""`
**Explanation:** There is no common prefix among the input strings.

### Example 3

**Input:** `strs = ["interview", "intercom", "interest"]`
**Output:** `"inter"`
**Explanation:** All three strings start with `"inter"`.

## Constraints

- `1 <= len(strs) <= 200`
- `0 <= len(strs[i]) <= 200`
- All strings consist of lowercase English letters only.

## Starter Code

```python
def longest_common_prefix(strs):
    pass
```

---

## Test Cases

### Sample (shown to contestants)

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 1 | `[["flower", "flow", "flight"]]` | `"fl"` |
| 2 | `[["dog", "racecar", "car"]]` | `""` |
| 3 | `[["interview", "intercom", "interest"]]` | `"inter"` |

### Hidden

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 4 | `[["ab", "a"]]` | `"a"` |
| 5 | `[["abc"]]` | `"abc"` |
| 6 | `[["abc", "abc", "abc"]]` | `"abc"` |
| 7 | `[["cir", "car"]]` | `"c"` |
| 8 | `[["prefix", "preface", "prepare"]]` | `"pre"` |
| 9 | `[["x", "y", "z"]]` | `""` |
| 10 | `[["", "abc"]]` | `""` |

> **Note:** `input_data` is the JSON array of function arguments. A single argument list is wrapped in an outer array, e.g. `[["flower","flow"]]` maps to `longest_common_prefix(["flower","flow"])`.

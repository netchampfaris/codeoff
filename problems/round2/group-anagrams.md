---
title: Group Anagrams
slug: group-anagrams
difficulty: Medium
round: 2
suggested_time_minutes: 7
function_name: group_anagrams
function_signature: "def group_anagrams(strs):"
time_limit_seconds: 2.0
memory_limit_mb: 256
---

# Group Anagrams

## Problem Statement

Given a list of strings `strs`, group the **anagrams** together and return the groups as a list of lists.

Two strings are anagrams if one can be formed by rearranging the letters of the other. Each group must contain all strings that are anagrams of each other.

The order of the groups in the output and the order of strings within each group **do not matter** — the judge sorts before comparing.

## Examples

### Example 1

**Input:** `strs = ["eat", "tea", "tan", "ate", "nat", "bat"]`
**Output:** `[["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]`
**Explanation:** `"eat"`, `"tea"`, and `"ate"` are anagrams of each other. `"tan"` and `"nat"` are anagrams. `"bat"` stands alone.

### Example 2

**Input:** `strs = [""]`
**Output:** `[[""]]`

### Example 3

**Input:** `strs = ["a"]`
**Output:** `[["a"]]`

## Constraints

- `1 <= len(strs) <= 10000`
- `0 <= len(strs[i]) <= 100`
- `strs[i]` consists of lowercase English letters.

## Starter Code

```python
def group_anagrams(strs):
    pass
```

---

## Test Cases

### Sample (shown to contestants)

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 1 | `[["eat", "tea", "tan", "ate", "nat", "bat"]]` | `[["eat", "tea", "ate"], ["tan", "nat"], ["bat"]]` |
| 2 | `[[""]]` | `[[""]]` |
| 3 | `[["a"]]` | `[["a"]]` |

### Hidden

| # | `input_data` | `expected_output` |
|---|-------------|------------------|
| 4 | `[["abc", "bca", "cab"]]` | `[["abc", "bca", "cab"]]` |
| 5 | `[["ab", "ba", "cd", "dc"]]` | `[["ab", "ba"], ["cd", "dc"]]` |
| 6 | `[["a", "b", "c"]]` | `[["a"], ["b"], ["c"]]` |
| 7 | `[["", "", "a"]]` | `[["", ""], ["a"]]` |
| 8 | `[["listen", "silent", "enlist", "hello"]]` | `[["listen", "silent", "enlist"], ["hello"]]` |
| 9 | `[["abc", "abc"]]` | `[["abc", "abc"]]` |
| 10 | `[["z", "y", "x"]]` | `[["z"], ["y"], ["x"]]` |

> **Note:** The judge sorts each group and the list of groups before comparing, so output order is irrelevant.

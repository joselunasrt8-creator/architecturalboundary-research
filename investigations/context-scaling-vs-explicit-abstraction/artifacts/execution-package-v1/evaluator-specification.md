# Offline Evaluator Specification

`execution_package.py:evaluate` is the only scorer. It accepts strict UTF-8 raw target-output bytes plus a target record and separately hashed frozen answer key and scope rubric. It rejects malformed structures, unknown fields, duplicate normalized literals, empty normalized literals, undecodable output, and hash mismatches with `ValueError` (the caller records `METHODOLOGY_FAILURE`).

It normalizes the output and every literal with Unicode NFKC, case-folding, maximal Unicode-whitespace replacement by one ASCII space, and ASCII-space trimming. A match is a contiguous normalized substring. `KEY_MATCH` requires all required literals and no forbidden literal. `SCOPE_MATCH` requires all relation and required-applicability literals and no forbidden-applicability literal. `score` is their boolean conjunction.

A successful return has exactly the seven preregistered keys: `target_id`, `raw_output_sha256`, `answer_key_sha256`, `scope_rubric_sha256`, `KEY_MATCH`, `SCOPE_MATCH`, and `score`. It does not call an LLM, use human scoring, access the network, or read runtime state.

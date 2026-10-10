<div align="center">

# ToolGate 🛡️

**A Tool-Call Firewall & Evidence Ledger for Autonomous AI Agents**

*Stop agents from executing destructive commands. Challenge false "Done" claims with verifiable proof.*

[![PyPI Version](https://img.shields.io/badge/pypi-v0.1.0-blue.svg)](https://github.com/apravint/toolgate)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-green.svg)](https://python.org)

</div>

---

## ⚡ Why ToolGate?

Autonomous AI coding agents (Claude Code, Cursor, OpenHands, AutoGPT) are given bash terminals and execution tools. When they hallucinate, they can:
1. **Wipe critical filesystems**: `rm -rf /` or delete git history.
2. **Corrupt disk devices**: raw writes to `/dev/sdX` or unrecoverable resets.
3. **Claim false success**: Output *"All tests pass and the bug is fixed"* without ever executing the tests.

**ToolGate provides two essential layers of defense:**
- **The Tool-Call Firewall**: Intercepts shell commands, answers 7 risk heuristics, prompts user on elevated actions, and **fails closed** on critical destructive commands.
- **The Canny Evidence Ledger**: Challenges every agent "Done" claim. Refuses to accept completion unless backed by a verifiable execution proof command (exit code 0).

---

## 🚀 Quickstart

### Installation
```bash
pip install toolgate
```
Or clone and install locally:
```bash
git clone https://github.com/apravint/toolgate.git
cd toolgate
pip install -e .
```

---

## 🛠️ Usage

### 1. Tool-Call Security Firewall
Evaluate command safety before running:
```bash
# Safe commands pass through
toolgate check "git status"
# -> ✓ [TOOLGATE: ALLOWED] Command passed safety filters.

# Dangerous commands are blocked and exit with non-zero status
toolgate check "rm -rf /"
# -> 🛑 [TOOLGATE: DENIED] Command blocked by safety firewall!

# Elevated commands require explicit confirmation
toolgate check "git reset --hard"
# -> ⚠️ [TOOLGATE: PROMPT REQUIRED] Elevated risk detected!
```

### 2. Canny Evidence Ledger
Verify agent claims before closing tickets or merging PRs:
```bash
toolgate verify "Run Test Suite" "All unit tests pass cleanly" "pytest tests/"
```
Output:
```text
🔍 [Canny Evidence Ledger] Challenging claim for: 'Run Test Suite'
   Claim: All unit tests pass cleanly
   Proof Verification Command: `pytest tests/`
   ✓ Proof Verified! Evidence accepted and ledger updated.
```

Inspect the evidence ledger history:
```bash
toolgate ledger
```

---

## 🐍 Python SDK Integration

Use ToolGate directly in your Python agent loops:

```python
from toolgate.firewall import evaluate_command_risk
from toolgate.ledger import record_evidence

# 1. Firewall check before executing tool call
verdict, flags = evaluate_command_risk("rm -rf /tmp/build")
if verdict == "DENY":
    raise PermissionError(f"Blocked by ToolGate: {flags}")

# 2. Challenge agent claim with evidence
verified, code, stdout, stderr = record_evidence(
    task_name="Compile",
    claim="Binary compiles without errors",
    proof_command="cargo check"
)
```

---

## ⚖️ License
MIT License © 2026 Ayyappa Pravin.

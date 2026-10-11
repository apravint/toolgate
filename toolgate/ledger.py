import os
import json
import time
import subprocess
from typing import Tuple, Dict, Any, List, Optional

DEFAULT_LEDGER_DIR = os.path.expanduser("~/.local/state/toolgate/evidence_ledger")

def get_ledger_dir(custom_dir: Optional[str] = None) -> str:
    path = custom_dir or DEFAULT_LEDGER_DIR
    os.makedirs(path, exist_ok=True)
    return path

def record_evidence(task_name: str, claim: str, proof_command: str, ledger_dir: Optional[str] = None) -> Tuple[bool, int, str, str]:
    """
    Challenges the agent 'Done' claim with verifiable command execution.
    """
    try:
        t0 = time.time()
        res = subprocess.run(proof_command, shell=True, capture_output=True, text=True, timeout=30)
        dt = time.time() - t0
        passed = (res.returncode == 0)
    except Exception as e:
        passed = False
        res = subprocess.CompletedProcess(args=proof_command, returncode=1, stdout="", stderr=str(e))
        dt = 0.0

    entry = {
        "timestamp": time.time(),
        "task_name": task_name,
        "claim": claim,
        "proof_command": proof_command,
        "verified": passed,
        "return_code": res.returncode,
        "output_snippet": (res.stdout + res.stderr)[:500],
        "latency": dt
    }

    record_file = os.path.join(get_ledger_dir(ledger_dir), f"evidence_{int(time.time() * 1000)}.json")
    with open(record_file, "w") as f:
        json.dump(entry, f, indent=2)

    return passed, res.returncode, res.stdout, res.stderr

def list_evidence(ledger_dir: Optional[str] = None) -> List[Dict[str, Any]]:
    target_dir = get_ledger_dir(ledger_dir)
    records = []
    files = sorted(os.listdir(target_dir), reverse=True)
    for f in files[:20]:
        try:
            with open(os.path.join(target_dir, f), "r") as fh:
                records.append(json.load(fh))
        except Exception:
            pass
    return records

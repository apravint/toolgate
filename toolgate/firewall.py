import re
from typing import Tuple, List

CRITICAL_DENY_PATTERNS = [
    r"rm\s+(-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*|-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*)\s+.*(/|/\*|~|~/\*|\$HOME|\$HOME/\*)",
    r"mkfs(\.[a-z0-9]+)?\s+",
    r"dd\s+.*of=/dev/(sd[a-z]|nvme[0-9]n[0-9]|vd[a-z]|loop[0-9])",
    r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:",  # fork bomb
    r"chmod\s+(-[a-zA-Z]*R[a-zA-Z]*\s+)?777\s+(/|/etc|/boot|/usr|/var)",
    r">\s*/dev/(sd[a-z]|nvme[0-9]n[0-9]|vd[a-z])",
]

PROMPT_PATTERNS = [
    r"systemctl\s+(stop|disable|mask)\s+",
    r"iptables\s+(-F|--flush)",
    r"git\s+push\s+.*(--force|-f\b)",
    r"git\s+reset\s+--hard",
    r"git\s+clean\s+(-[a-zA-Z]*f[a-zA-Z]*d[a-zA-Z]*|-[a-zA-Z]*d[a-zA-Z]*f[a-zA-Z]*|-f\s+-d|-d\s+-f)",
    r"sudo\s+(userdel|groupdel)",
    r"(curl|wget)\s+.*\|\s*(bash|sh|zsh)",
]

def evaluate_command_risk(cmd: str) -> Tuple[str, List[str]]:
    """
    Evaluates 7 safety questions:
    1. Does this command wipe root or home filesystems?
    2. Does this write raw bytes to disk devices?
    3. Does this disable system-critical services?
    4. Does this alter global firewall/networking rules?
    5. Does this destroy git repository history?
    6. Does this grant unrestricted world-writable permissions?
    7. Is this a fork bomb or denial-of-service vector?
    """
    flags = []

    # 1. Recursive force deletion of critical system or home directories
    if re.search(r"\brm\b", cmd):
        has_rec = bool(re.search(r"(-[a-zA-Z]*[rR]|--recursive)", cmd))
        has_force = bool(re.search(r"(-[a-zA-Z]*[fF]|--force)", cmd))
        has_critical_target = bool(re.search(r"(\s+|^)(/|/\*|~|~/\*|\$HOME|\$HOME/\*|/etc|/boot|/usr|/var)(\s+|$)", cmd))
        if has_rec and has_force and has_critical_target:
            flags.append("CRITICAL: Destructive recursive deletion targeting critical root or home path")
            return "DENY", flags

    for p in CRITICAL_DENY_PATTERNS:
        if re.search(p, cmd):
            flags.append(f"CRITICAL: Destructive pattern matched ({p})")
            return "DENY", flags

    for p in PROMPT_PATTERNS:
        if re.search(p, cmd):
            flags.append(f"HIGH: Modifies persistent system services or unrecoverable git history ({p})")
            return "PROMPT", flags

    return "ALLOW", ["Passes safety heuristics"]

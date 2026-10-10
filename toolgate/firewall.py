import re
from typing import Tuple, List

CRITICAL_DENY_PATTERNS = [
    r"rm\s+(-[a-zA-Z]*r[a-zA-Z]*f[a-zA-Z]*|-[a-zA-Z]*f[a-zA-Z]*r[a-zA-Z]*)\s+(/|/\*|~|~/\*|\$HOME|\$HOME/\*)",
    r"mkfs\.[a-z0-9]+",
    r"dd\s+if=.*of=/dev/(sd[a-z]|nvme[0-9]n[0-9])",
    r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:",  # fork bomb
    r"chmod\s+(-R\s+)?777\s+(/|/etc|/boot|/usr)",
    r">\s*/dev/sd[a-z]",
]

PROMPT_PATTERNS = [
    r"systemctl\s+(stop|disable|mask)\s+",
    r"iptables\s+-F",
    r"git\s+push\s+.*--force",
    r"git\s+reset\s+--hard",
    r"sudo\s+userdel",
    r"curl\s+.*\|\s*(bash|sh)",
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

    for p in CRITICAL_DENY_PATTERNS:
        if re.search(p, cmd):
            flags.append(f"CRITICAL: Destructive pattern matched ({p})")
            return "DENY", flags

    for p in PROMPT_PATTERNS:
        if re.search(p, cmd):
            flags.append(f"HIGH: Modifies persistent system services or unrecoverable git history ({p})")
            return "PROMPT", flags

    return "ALLOW", ["Passes safety heuristics"]

#!/usr/bin/env python3
import sys
import argparse
from toolgate.firewall import evaluate_command_risk
from toolgate.ledger import record_evidence, list_evidence

RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
CYAN = "\033[0;36m"
BOLD = "\033[1m"
NC = "\033[0m"

def main():
    parser = argparse.ArgumentParser(description="ToolGate: Tool-Call Firewall & Evidence Ledger for AI Agents")
    subparsers = parser.add_subparsers(dest="subcommand")

    p_check = subparsers.add_parser("check", help="Evaluate security risk of a shell command")
    p_check.add_argument("cmd", help="Command string to evaluate")

    p_verify = subparsers.add_parser("verify", help="Challenge agent 'done' claim with proof command")
    p_verify.add_argument("task", help="Task name")
    p_verify.add_argument("claim", help="Stated achievement")
    p_verify.add_argument("proof", help="Verification command that must exit 0")

    subparsers.add_parser("ledger", help="List recent verified evidence entries")

    args = parser.parse_args()

    if args.subcommand == "check":
        verdict, flags = evaluate_command_risk(args.cmd)
        if verdict == "DENY":
            print(f"{RED}{BOLD}🛑 [TOOLGATE: DENIED] Command blocked by safety firewall!{NC}")
            for f in flags:
                print(f"   ✗ {f}")
            sys.exit(1)
        elif verdict == "PROMPT":
            print(f"{YELLOW}{BOLD}⚠️ [TOOLGATE: PROMPT REQUIRED] Elevated risk detected!{NC}")
            for f in flags:
                print(f"   • {f}")
            confirm = input(f"Allow execution of '{args.cmd}'? (y/N): ")
            if confirm.lower() != "y":
                print(f"{RED}Operation aborted.{NC}")
                sys.exit(2)
            print(f"{GREEN}Approved by user.{NC}")
            sys.exit(0)
        else:
            print(f"{GREEN}✓ [TOOLGATE: ALLOWED] Command passed safety filters.{NC}")
            sys.exit(0)

    elif args.subcommand == "verify":
        print(f"{BOLD}{CYAN}🔍 [Canny Evidence Ledger] Challenging claim for: '{args.task}'{NC}")
        print(f"   Claim: {args.claim}")
        print(f"   Proof Verification Command: `{args.proof}`")

        passed, code, stdout, stderr = record_evidence(args.task, args.claim, args.proof)
        if passed:
            print(f"   {GREEN}✓ Proof Verified! Evidence accepted and ledger updated.{NC}")
            sys.exit(0)
        else:
            print(f"   {RED}✗ Proof Failed! Exit code {code}. Claim rejected.{NC}")
            if stderr.strip():
                print(f"     Error: {stderr.strip()[:300]}")
            sys.exit(1)

    elif args.subcommand == "ledger":
        records = list_evidence()
        print(f"{BOLD}📜 Canny Evidence Ledger Records:{NC}")
        if not records:
            print("   (No evidence records logged yet)")
            return
        for d in records:
            status = f"{GREEN}VERIFIED{NC}" if d["verified"] else f"{RED}REJECTED{NC}"
            print(f"   • [{status}] {d['task_name']}: {d['claim']} ({d.get('proof_command','')[:35]}...)")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

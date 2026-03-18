"""CLI for agent-eval-arena."""
import sys, json, argparse
from .core import AgentEvalArena

def main():
    parser = argparse.ArgumentParser(description="Head-to-head AI agent evaluation platform with ELO rating system")
    parser.add_argument("command", nargs="?", default="status", choices=["status", "run", "info"])
    parser.add_argument("--input", "-i", default="")
    args = parser.parse_args()
    instance = AgentEvalArena()
    if args.command == "status":
        print(json.dumps(instance.get_stats(), indent=2))
    elif args.command == "run":
        print(json.dumps(instance.process(input=args.input or "test"), indent=2, default=str))
    elif args.command == "info":
        print(f"agent-eval-arena v0.1.0 — Head-to-head AI agent evaluation platform with ELO rating system")

if __name__ == "__main__":
    main()

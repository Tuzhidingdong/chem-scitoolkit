"""Command line entrypoint for natural language scientific queries and tool exploration."""

import sys
import argparse
from my_sci_toolkit.ai_agent import Agent
from my_sci_toolkit.registry import REGISTRY


def main():
    parser = argparse.ArgumentParser(
        prog="my-sci",
        description="Scientific Toolkit Natural Language Command Line Interface.",
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Natural language instruction (e.g. 'Plot comparison kinetics of 40min capillary vs 26h bulk water oxidation')",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview mapped scientific tool and parameters without executing",
    )
    parser.add_argument(
        "--backend",
        choices=["auto", "local", "ollama", "gemini", "rules"],
        default="auto",
        help="LLM planner backend: 'local' (Ollama/OpenAI compatible), 'gemini', or 'rules' (offline)",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Local model name (e.g. 'qwen2.5-coder', 'llama3.1')",
    )
    parser.add_argument(
        "--list-tools",
        action="store_true",
        help="List all registered scientific analysis and plotting tools",
    )
    parser.add_argument(
        "--output-dir",
        default="./outputs",
        help="Output directory for generated publication figures and simulation files",
    )

    args = parser.parse_args()

    if args.list_tools:
        print("\n=== Registered Scientific Tools in chem-scitoolkit ===")
        for t in REGISTRY.list_tools():
            print(f"  • {t['name']:<32} [{', '.join(t.get('tags', []))}] : {t['description']}")
        print()
        sys.exit(0)

    if not args.query:
        parser.print_help()
        sys.exit(1)

    agent = Agent(
        backend=args.backend,
        local_model=args.model,
        output_dir=args.output_dir,
    )
    res = agent.run(args.query, dry_run=args.dry_run)

    print("\n[Scientific AI Agent Response]")
    print(f"Status: {res.get('status')}")
    print(f"Mapped Tool: {res.get('tool')}")
    print(f"Arguments: {res.get('args')}")
    if res.get("artifact"):
        print(f"Artifact: {res.get('artifact')}")
    if res.get("message"):
        print(f"Details: {res.get('message')}")
    print()


if __name__ == "__main__":
    main()

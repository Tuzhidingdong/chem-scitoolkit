"""Command line entrypoint for natural language queries and toolkit introspection."""

import sys
import argparse
from my_sci_toolkit.ai_agent import Agent
from my_sci_toolkit.registry import REGISTRY


def main():
    parser = argparse.ArgumentParser(
        prog="my-sci",
        description="Scientific Toolkit Natural Language Command Line Interface.",
    )
    parser.add_argument("query", nargs="?", help="Natural language instruction (e.g. '帮我绘制 40min 毛细凝聚与 26h 体相水氧化的对比动力学图')")
    parser.add_argument("--dry-run", action="store_true", help="Preview mapped tool and parameters without executing")
    parser.add_argument("--list-tools", action="store_true", help="List all registered scientific analysis and plotting tools")
    parser.add_argument("--output-dir", default="./outputs", help="Output directory for generated figures and data tables")

    args = parser.parse_args()

    if args.list_tools:
        print("\n=== Registered Scientific Tools in my_sci_toolkit ===")
        for t in REGISTRY.list_tools():
            print(f"  • {t['name']:<30} [{', '.join(t.get('tags', []))}] : {t['description']}")
        print()
        sys.exit(0)

    if not args.query:
        parser.print_help()
        sys.exit(1)

    agent = Agent(output_dir=args.output_dir)
    res = agent.run(args.query, dry_run=args.dry_run)

    print(f"\n[AI Agent Response]")
    print(f"Status: {res.get('status')}")
    print(f"Mapped Tool: {res.get('tool')}")
    print(f"Arguments: {res.get('args')}")
    if res.get("artifact"):
        print(f"Output Artifact: {res.get('artifact')}")
    if res.get("message"):
        print(f"Details: {res.get('message')}")
    print()


if __name__ == "__main__":
    main()

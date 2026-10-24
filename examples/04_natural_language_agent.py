"""Example 4: Natural Language Interface Agent Demonstration.

Demonstrates querying scientific calculations and publication plotting via natural language
using local open-source LLMs (Ollama qwen2.5-coder) or deterministic offline rules.
"""

from my_sci_toolkit import Agent

# 1. Initialize agent with local open-source LLM or offline rules
# If you have Ollama running locally (`ollama run qwen2.5-coder`), it will automatically
# translate your natural language requests to precise tool parameters.
agent = Agent(backend="auto", output_dir="./outputs")

print("--- Query 1: Comparative Kinetics (Dry-run preview) ---")
query_1 = "Plot comparison kinetics of 40min capillary vs 26h bulk water oxidation"
preview = agent.run(query_1, dry_run=True)
print("Planned Execution:", preview)

print("\n--- Query 1: Actual Execution ---")
result_1 = agent.run(query_1, dry_run=False)
print("Execution Result:", result_1)

print("\n--- Query 2: Reaction Free Energy Steps ---")
query_2 = "Generate reaction intermediate free energy step diagram comparison"
result_2 = agent.run(query_2)
print("Execution Result:", result_2)

print("\n--- Query 3: Crystallography Interplanar Spacing ---")
query_3 = "Calculate cubic crystal d-spacing"
result_3 = agent.run(query_3)
print("Calculation Result:", result_3)

print("\n--- Query 4: CP2K Input Card Generation ---")
query_4 = "Build cp2k input file from aimd.cif"
result_4 = agent.run(query_4, dry_run=True)
print("Simulation Plan:", result_4)

"""Example 4: Natural Language Interface Agent Demonstration.

Demonstrates how users can query scientific plotting via natural language in Python.
"""

from my_sci_toolkit import Agent

# Initialize agent (uses offline rule engine or online Gemini if GEMINI_API_KEY is available)
agent = Agent(output_dir="./outputs")

print("--- Query 1: Preview Dry-run ---")
query_1 = "帮我绘制 40min 毛细凝聚与 26h 体相水氧化的对比动力学图"
preview = agent.run(query_1, dry_run=True)
print("Plan:", preview)

print("\n--- Query 1: Actual Execution ---")
result_1 = agent.run(query_1, dry_run=False)
print("Execution Result:", result_1)

print("\n--- Query 2: Reaction Free Energy Steps ---")
query_2 = "生成反应中间体台阶图对比"
result_2 = agent.run(query_2)
print("Execution Result:", result_2)

print("\n--- Query 3: Crystallography Interplanar Spacing ---")
query_3 = "计算晶体立方系晶面间距"
result_3 = agent.run(query_3)
print("Calculation Result:", result_3)

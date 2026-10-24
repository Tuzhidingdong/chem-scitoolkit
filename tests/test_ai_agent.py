"""Tests for natural language parser and agent dry-run."""

from my_sci_toolkit.ai_agent import Agent


def test_agent_kinetics_comparison_mapping():
    agent = Agent(backend="rules")
    prompt = "帮我绘制 40min 毛细凝聚与 26h 体相水氧化的对比动力学图"
    plan = agent.run(prompt, dry_run=True)

    assert plan["status"] == "dry_run"
    assert plan["tool"] == "plot_completion_time_bar"
    assert "Capillary" in plan["args"]["systems"]
    assert "Bulk water" in plan["args"]["systems"]
    assert plan["args"]["times_h"][0] < plan["args"]["times_h"][1]


def test_agent_free_energy_mapping():
    agent = Agent(backend="rules")
    prompt = "绘制反应台阶图与中间体能垒"
    plan = agent.run(prompt, dry_run=True)

    assert plan["status"] == "dry_run"
    assert plan["tool"] == "plot_free_energy_profile"
    assert "pathways" in plan["args"]

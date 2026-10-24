"""Tests for natural language parser and agent dry-run."""

from my_sci_toolkit.ai_agent import Agent


def test_agent_kinetics_comparison_mapping():
    agent = Agent(backend="rules")
    prompt = "Plot comparison kinetics of 40min capillary vs 26h bulk water oxidation"
    plan = agent.run(prompt, dry_run=True)

    assert plan["status"] == "dry_run"
    assert plan["tool"] == "plot_completion_time_bar"
    assert "Capillary" in plan["args"]["systems"]
    assert "Bulk water" in plan["args"]["systems"]
    assert plan["args"]["times_h"][0] < plan["args"]["times_h"][1]


def test_agent_free_energy_mapping():
    agent = Agent(backend="rules")
    prompt = "Plot reaction intermediate free energy step diagram"
    plan = agent.run(prompt, dry_run=True)

    assert plan["status"] == "dry_run"
    assert plan["tool"] == "plot_free_energy_profile"
    assert "pathways" in plan["args"]


def test_agent_cp2k_mapping():
    agent = Agent(backend="rules")
    prompt = "Build cp2k input file from structure aimd.cif"
    plan = agent.run(prompt, dry_run=True)

    assert plan["status"] == "dry_run"
    assert plan["tool"] == "build_cp2k_from_cif"
    assert plan["args"]["cif_path"] == "aimd.cif"

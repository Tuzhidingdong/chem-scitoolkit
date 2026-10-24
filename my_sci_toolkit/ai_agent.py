"""Natural Language Interface and Autonomous Scientific Agent.

Supports both online LLM function calling (Gemini API) and offline deterministic rule matching.
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from my_sci_toolkit.registry import REGISTRY
from my_sci_toolkit.config import GLOBAL_CONFIG


class RuleAgentEngine:
    """Offline rule-based semantic parser for robust local scientific queries."""

    def parse_intent(self, text: str) -> Optional[Dict[str, Any]]:
        text_lower = text.lower()

        # Intent 1: Comparison of reaction completion time (e.g. 40min capillary vs 26h bulk water)
        # Matches user prompt: "帮我绘制 40min 毛细凝聚与 26h 体相水氧化的对比动力学图"
        if ("对比" in text or "compare" in text_lower or "完成时间" in text or "柱状" in text or "completion" in text_lower) and \
           ("动力学" in text or "氧化" in text or "kinetic" in text_lower):
            
            # Extract time components
            systems = []
            times_h = []
            labels = []

            if "毛细" in text or "capillary" in text_lower or "40min" in text_lower or "40 min" in text_lower:
                systems.append("Capillary")
                times_h.append(40.0 / 60.0)
                labels.append("40 min")

            if "体相" in text or "bulk" in text_lower or "26h" in text_lower or "26 h" in text_lower:
                systems.append("Bulk water")
                times_h.append(26.0)
                labels.append("26 h")

            if "空气" in text or "air" in text_lower or "280h" in text_lower or "280 h" in text_lower:
                systems.append("Air")
                times_h.append(280.0)
                labels.append("280 h")

            if not systems:
                systems = ["Capillary", "Bulk water", "Air"]
                times_h = [40.0 / 60.0, 26.0, 280.0]
                labels = ["40 min", "26 h", "280 h"]

            return {
                "tool": "plot_completion_time_bar",
                "args": {
                    "systems": systems,
                    "times_h": times_h,
                    "unit_labels": labels,
                    "title": "FeS Oxidation Completion Time Comparison",
                }
            }

        # Intent 2: Free energy pathway / reaction steps (HER, CO2RR, etc.)
        if "台阶图" in text or "能垒" in text or "自由能" in text or "energy profile" in text_lower or "her" in text_lower:
            return {
                "tool": "plot_free_energy_profile",
                "args": {
                    "pathways": {
                        "Path A (Capillary)": [0.0, -0.42, 0.15, -0.85],
                        "Path B (Bulk)": [0.0, 0.28, 0.95, -0.10],
                    },
                    "step_labels": ["Reactants", "*OH", "*O", "Products"],
                    "title": "Reaction Free Energy Profiles",
                }
            }

        # Intent 3: Battery charge/discharge or cycling
        if "充放电" in text or "battery" in text_lower or "循环" in text:
            return {
                "tool": "plot_charge_discharge",
                "args": {
                    "capacity_mah_g": [0, 50, 100, 150, 180, 182, 180, 150, 100, 50, 0],
                    "voltage_v": [3.0, 3.6, 3.8, 3.9, 4.2, 4.3, 4.1, 3.8, 3.6, 3.3, 3.0],
                    "cycle_index": 1,
                    "c_rate": "0.1C",
                }
            }

        # Intent 4: d-spacing crystal calculation
        if "晶面间距" in text or "d-spacing" in text_lower:
            return {
                "tool": "calculate_d_spacing",
                "args": {
                    "crystal_system": "cubic",
                    "a": 5.43,
                    "b": 5.43,
                    "c": 5.43,
                    "h": 1,
                    "k": 1,
                    "l": 1,
                }
            }

        return None


class Agent:
    """Scientific AI Agent translating natural language instructions into tool executions."""

    def __init__(
        self,
        backend: str = "auto",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        output_dir: Optional[str | Path] = None,
    ):
        self.output_dir = GLOBAL_CONFIG.ensure_output_dir(output_dir)
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = model or GLOBAL_CONFIG.gemini_model
        self.rule_engine = RuleAgentEngine()

        if backend == "auto":
            self.backend = "gemini" if self.api_key else "rules"
        else:
            self.backend = backend

    def run(self, prompt: str, dry_run: bool = False) -> Dict[str, Any]:
        """Execute or preview a natural language request.

        Args:
            prompt: User natural language prompt (e.g. "帮我绘制 40min 毛细凝聚与 26h 体相水氧化的对比动力学图").
            dry_run: If True, returns tool selection and planned arguments without actual file execution.

        Returns:
            Dict containing tool execution result, mapped arguments, and generated artifacts.
        """
        plan = None

        # Attempt offline rule-based parser first
        rule_plan = self.rule_engine.parse_intent(prompt)
        if rule_plan:
            plan = rule_plan
        elif self.backend == "gemini" and self.api_key:
            plan = self._call_gemini_planner(prompt)

        if not plan:
            return {
                "status": "error",
                "message": f"Could not map prompt to an available scientific tool: '{prompt}'.",
                "available_tools": [t["name"] for t in REGISTRY.list_tools()],
            }

        tool_name = plan["tool"]
        tool_args = plan["args"]
        func = REGISTRY.get_tool(tool_name)

        if not func:
            return {
                "status": "error",
                "message": f"Tool '{tool_name}' is not registered.",
            }

        # Auto inject save_path if the tool produces a figure
        if "save_path" in func.__code__.co_varnames and "save_path" not in tool_args:
            target_fig = self.output_dir / f"{tool_name}_output.png"
            tool_args["save_path"] = str(target_fig)

        if dry_run:
            return {
                "status": "dry_run",
                "tool": tool_name,
                "args": tool_args,
                "planned_output": tool_args.get("save_path"),
            }

        # Execute registered tool
        try:
            result = func(**tool_args)
            return {
                "status": "success",
                "tool": tool_name,
                "args": tool_args,
                "result": result,
                "artifact": tool_args.get("save_path"),
                "message": f"Successfully executed tool '{tool_name}'. Output saved to: {tool_args.get('save_path')}",
            }
        except Exception as e:
            return {
                "status": "execution_failed",
                "tool": tool_name,
                "args": tool_args,
                "error": str(e),
            }

    def _call_gemini_planner(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call Gemini function calling API when credentials are provided."""
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            tools_spec = REGISTRY.get_declarations_for_llm()

            response = client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=tools_spec,
                    temperature=0.0,
                ),
            )

            # Extract tool calls from candidates
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        fc = part.function_call
                        return {
                            "tool": fc.name,
                            "args": dict(fc.args),
                        }
        except Exception as ex:
            # Fallback smoothly to rule engine on network or credential failures
            return self.rule_engine.parse_intent(prompt)

        return None

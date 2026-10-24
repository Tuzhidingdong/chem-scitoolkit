"""Natural Language Interface and Scientific AI Agent.

Supports:
1. Free local open-source LLMs via Ollama / OpenAI-compatible local endpoints (e.g. qwen2.5-coder, llama3.1).
2. Remote API backends (e.g. Google Gemini API via GEMINI_API_KEY).
3. Deterministic offline semantic rule matching (zero network, zero API key).
"""

import os
import re
import json
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from my_sci_toolkit.registry import REGISTRY
from my_sci_toolkit.config import GLOBAL_CONFIG


class RuleAgentEngine:
    """Offline rule-based semantic parser for deterministic scientific query routing."""

    def parse_intent(self, text: str) -> Optional[Dict[str, Any]]:
        text_lower = text.lower()

        # Intent 1: Comparison of reaction completion time (e.g., 40min capillary vs 26h bulk water oxidation)
        if ("compare" in text_lower or "comparison" in text_lower or "completion" in text_lower or "bar" in text_lower) and \
           ("kinetic" in text_lower or "oxidation" in text_lower or "reaction" in text_lower):
            
            systems = []
            times_h = []
            labels = []

            if "capillary" in text_lower or "40min" in text_lower or "40 min" in text_lower:
                systems.append("Capillary")
                times_h.append(40.0 / 60.0)
                labels.append("40 min")

            if "bulk" in text_lower or "26h" in text_lower or "26 h" in text_lower:
                systems.append("Bulk water")
                times_h.append(26.0)
                labels.append("26 h")

            if "air" in text_lower or "280h" in text_lower or "280 h" in text_lower:
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
                    "title": "Oxidation Completion Time Comparison",
                }
            }

        # Intent 2: Free energy pathway / reaction steps (HER, CO2RR, etc.)
        if "energy profile" in text_lower or "free energy" in text_lower or "step diagram" in text_lower or "her" in text_lower:
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
        if "charge" in text_lower or "discharge" in text_lower or "battery" in text_lower or "cycle" in text_lower:
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
        if "d-spacing" in text_lower or "interplanar" in text_lower or "lattice plane" in text_lower:
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

        # Intent 5: CP2K input builder from CIF
        if "cp2k" in text_lower or ("cif" in text_lower and ("input" in text_lower or "build" in text_lower or "generate" in text_lower)):
            cif_file = "aimd.cif"
            m = re.search(r"([\w\-_\.]+\.cif)", text, re.IGNORECASE)
            if m:
                cif_file = m.group(1)
            return {
                "tool": "build_cp2k_from_cif",
                "args": {
                    "cif_path": cif_file,
                    "output_inp": "cp2k.inp",
                    "run_type": "GEO_OPT",
                }
            }

        return None


class LocalOpenAIPlanner:
    """Planner interfacing with local open-source LLMs (Ollama, vLLM, LM Studio)."""

    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_sec: int = 30,
    ):
        # Default to local Ollama v1 endpoint
        raw_url = base_url or os.getenv("LOCAL_LLM_URL") or os.getenv("OPENAI_BASE_URL") or "http://localhost:11434/v1"
        self.base_url = raw_url.rstrip("/")
        self.model = model or os.getenv("LOCAL_LLM_MODEL") or "qwen2.5-coder"
        self.api_key = api_key or os.getenv("LOCAL_LLM_API_KEY") or os.getenv("OPENAI_API_KEY") or "ollama"
        self.timeout_sec = timeout_sec

    def plan(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Query local model endpoint using JSON tool-calling or structured system prompt."""
        tools = REGISTRY.list_tools()
        tools_summary = []
        for t in tools:
            tools_summary.append({
                "name": t["name"],
                "description": t["description"],
                "parameters": t["parameters"],
            })

        system_prompt = (
            "You are a scientific AI assistant for the Python package 'chem-scitoolkit'. "
            "Your task is to map user natural language instructions to an available scientific tool and extract parameters.\n"
            "Respond ONLY with a JSON object containing two keys: 'tool' (string) and 'args' (dictionary of arguments).\n"
            "Do not include any conversational filler or markdown formatting outside the JSON.\n\n"
            f"Available tools catalog:\n{json.dumps(tools_summary, indent=2)}"
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.0,
            "stream": False,
        }

        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "User-Agent": "chem-scitoolkit-local-agent",
        }

        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=self.timeout_sec) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)

                choices = res_json.get("choices", [])
                if not choices:
                    return None

                content = choices[0].get("message", {}).get("content", "").strip()

                # Extract JSON block
                m = re.search(r"\{.*\}", content, re.DOTALL)
                if m:
                    parsed = json.loads(m.group(0))
                    if "tool" in parsed and "args" in parsed:
                        return parsed

        except Exception:
            # Silently fallback if local server is offline or unreachable
            return None

        return None


class Agent:
    """Unified Scientific AI Agent supporting local open-source LLMs, Gemini, and offline rules."""

    def __init__(
        self,
        backend: str = "auto",  # 'auto', 'local', 'ollama', 'gemini', 'rules'
        local_url: Optional[str] = None,
        local_model: Optional[str] = None,
        api_key: Optional[str] = None,
        gemini_model: Optional[str] = None,
        output_dir: Optional[str | Path] = None,
    ):
        self.output_dir = GLOBAL_CONFIG.ensure_output_dir(output_dir)
        self.backend = backend.lower()
        self.rule_engine = RuleAgentEngine()
        self.local_planner = LocalOpenAIPlanner(base_url=local_url, model=local_model)

        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.gemini_model = gemini_model or GLOBAL_CONFIG.gemini_model

    def run(self, prompt: str, dry_run: bool = False) -> Dict[str, Any]:
        """Execute or preview a natural language scientific request.

        Args:
            prompt: User natural language instruction.
            dry_run: If True, previews mapped tool and arguments without execution.

        Returns:
            Dict containing tool execution result, mapped arguments, and artifacts.
        """
        plan = None

        # 1. If backend specified as 'local' or 'ollama', attempt local open-source LLM first
        if self.backend in ("local", "ollama"):
            plan = self.local_planner.plan(prompt)

        # 2. If backend specified as 'gemini', attempt Gemini API
        elif self.backend == "gemini":
            plan = self._call_gemini_planner(prompt)

        # 3. If 'auto': try local Ollama -> try Gemini API -> fallback to deterministic rules
        elif self.backend == "auto":
            plan = self.local_planner.plan(prompt)
            if not plan and self.api_key:
                plan = self._call_gemini_planner(prompt)
            if not plan:
                plan = self.rule_engine.parse_intent(prompt)

        # 4. If 'rules': use deterministic rules directly
        else:
            plan = self.rule_engine.parse_intent(prompt)

        # Ultimate fallback to deterministic rules if model outputs failed
        if not plan:
            plan = self.rule_engine.parse_intent(prompt)

        if not plan:
            return {
                "status": "error",
                "message": f"Could not map prompt to an available scientific tool: '{prompt}'.",
                "available_tools": [t["name"] for t in REGISTRY.list_tools()],
            }

        tool_name = plan.get("tool")
        tool_args = plan.get("args", {})
        func = REGISTRY.get_tool(tool_name)

        if not func:
            return {
                "status": "error",
                "message": f"Tool '{tool_name}' is not registered in the toolkit.",
            }

        # Automatically supply output save_path if function accepts it
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
                "message": f"Successfully executed '{tool_name}'. Artifact saved to: {tool_args.get('save_path')}",
            }
        except Exception as e:
            return {
                "status": "execution_failed",
                "tool": tool_name,
                "args": tool_args,
                "error": str(e),
            }

    def _call_gemini_planner(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call Google Gemini Function Calling API."""
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.api_key)
            tools_spec = REGISTRY.get_declarations_for_llm()

            response = client.models.generate_content(
                model=self.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    tools=tools_spec,
                    temperature=0.0,
                ),
            )

            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    if hasattr(part, "function_call") and part.function_call:
                        fc = part.function_call
                        return {
                            "tool": fc.name,
                            "args": dict(fc.args),
                        }
        except Exception:
            return None

        return None

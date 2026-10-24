"""Tool registry and reflection system for function calling in AI agent."""

from typing import Callable, Dict, Any, List, Optional
import inspect


class ToolRegistry:
    """Registry managing functions exposed to natural language interface and CLI."""

    def __init__(self):
        self._tools: Dict[str, Callable] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}

    def register(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Callable:
        """Decorator to register a function as an AI agent tool."""
        def decorator(func: Callable) -> Callable:
            tool_name = name or func.__name__
            desc = description or (inspect.getdoc(func) or "").strip().split("\n\n")[0]
            
            sig = inspect.signature(func)
            parameters: Dict[str, Any] = {
                "type": "object",
                "properties": {},
                "required": [],
            }
            
            for param_name, param in sig.parameters.items():
                if param_name in ("self", "cls"):
                    continue
                param_type = "string"
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation in (list, List) or hasattr(param.annotation, "__origin__") and param.annotation.__origin__ in (list, List):
                    param_type = "array"

                parameters["properties"][param_name] = {
                    "type": param_type,
                    "description": f"Parameter {param_name}",
                }
                if param.default == inspect.Parameter.empty:
                    parameters["required"].append(param_name)

            self._tools[tool_name] = func
            self._metadata[tool_name] = {
                "name": tool_name,
                "description": desc,
                "parameters": parameters,
                "tags": tags or [],
                "func": func,
            }
            return func
        return decorator

    def get_tool(self, name: str) -> Optional[Callable]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        return list(self._metadata.values())

    def get_declarations_for_llm(self) -> List[Dict[str, Any]]:
        """Return function definitions formatted for Gemini / OpenAI Function Calling."""
        declarations = []
        for meta in self._metadata.values():
            declarations.append({
                "name": meta["name"],
                "description": meta["description"],
                "parameters": meta["parameters"],
            })
        return declarations


REGISTRY = ToolRegistry()
tool = REGISTRY.register

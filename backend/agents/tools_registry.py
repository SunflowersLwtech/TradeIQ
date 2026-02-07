# Tool definitions for Claude API (Design Doc Section 14)
# Placeholder: register market, behavior, content tool functions here for Claude Tool Use

TOOLS = []


def register_tool(name: str, description: str, parameters: dict):
    """Register a tool for Claude."""
    TOOLS.append({
        "name": name,
        "description": description,
        "input_schema": parameters,
    })

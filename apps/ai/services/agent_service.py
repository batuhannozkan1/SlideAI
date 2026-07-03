from __future__ import annotations

import json
import logging
from typing import Any, Callable

from apps.ai.clients import get_ai_client
from apps.ai.dtos import AgentResult
from apps.ai.prompts.agent import TOOL_SCHEMAS, build_agent_system_prompt

logger = logging.getLogger(__name__)

MAX_STEPS = 6

# tool_executor(name, arguments) -> result dict (may include {"changed": True})
ToolExecutor = Callable[[str, dict[str, Any]], dict[str, Any]]

def run_agent(
    *,
    system_context: str,
    instruction: str,
    history: tuple[tuple[str, str], ...] = (),
    tool_executor: ToolExecutor,
    max_steps: int = MAX_STEPS,
) -> AgentResult:
    """Tool-calling loop. The LLM decides which tools to call; `tool_executor`
    (provided by the presentations layer) performs the actual DB actions."""
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": build_agent_system_prompt() + "\n\n" + system_context}
    ]
    for role, text in history:
        if role in ("user", "assistant") and text:
            messages.append({"role": role, "content": text})
    messages.append({"role": "user", "content": instruction})

    client = get_ai_client()
    changed = False
    last_detail = ""

    for step_no in range(1, max_steps + 1):
        # tool_choice is ALWAYS "required" — the model can never reply with plain text,
        # so it can't claim success without acting. It speaks/answers via the `answer`
        # tool, which we intercept as terminal. No keyword/intent heuristic anywhere.
        step = client.complete_with_tools(messages, TOOL_SCHEMAS, tool_choice="required")
        messages.append(step.assistant_message)

        if not step.tool_calls:  # safety net (shouldn't happen with "required")
            return AgentResult(message=step.text or "Tamam.", changed=changed, steps=step_no)

        final_message = None
        for tc in step.tool_calls:
            if tc.name == "answer":
                final_message = tc.arguments.get("message") or final_message or "Tamam."
                continue  # terminal — no DB action, no tool-result needed (we return)
            try:
                result = tool_executor(tc.name, tc.arguments) or {}
            except Exception as exc:  # surface tool errors back to the model
                logger.warning("Agent tool '%s' failed: %s", tc.name, exc)
                result = {"status": "error", "detail": str(exc)}
            if result.get("changed"):
                changed = True
            if result.get("detail"):
                last_detail = result["detail"]
            messages.append({
                "role": "tool",
                "tool_call_id": tc.id,
                "content": json.dumps(result, ensure_ascii=False),
            })

        if final_message is not None:
            return AgentResult(message=final_message, changed=changed, steps=step_no)

    # Hit the step cap without an explicit answer — report the last concrete action.
    return AgentResult(message=last_detail or "İşlemleri tamamladım.", changed=changed, steps=max_steps)

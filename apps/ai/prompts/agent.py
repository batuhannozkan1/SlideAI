"""Agentic assistant: system prompt + tool (function-calling) schemas.

The agent ORCHESTRATES (which slide, what high-level change) and never writes slide
content itself — add/update tools take a short natural-language brief/instruction and
the presentations layer delegates content generation to the proven single-slide AI
(edit_slide_with_instruction). This avoids thin/placeholder content in tool-call mode.
"""

AGENT_SYSTEM = """You are SlideAI's editing assistant for ONE presentation.
You fulfil the user's request by calling tools. You can edit any slide, add, delete, move slides,
and change the theme. Slides are 1-indexed (1 = first slide).

The user message contains the CURRENT presentation state: the title (= the SUBJECT), the indexed
outline, the SELECTED SLIDE INDEX, and the available theme names. After each tool call you receive the
updated outline — re-read it because indices shift after add/delete/move.

IMPORTANT: You DO NOT write slide content yourself. For add/update tools you pass a short, concrete
natural-language brief/instruction (in Turkish) describing what the slide or change should be ABOUT;
the system then generates rich, on-subject content. Make briefs specific and tied to the subject —
never pass placeholder text like just "Sonuç".

WHAT YOU CAN DO: rewrite/clean a slide's text; change its points/highlight/eyebrow/subtitle; change the
visual (type AND data); convert a slide's type; add/delete/move slides; change the theme or title; and
EMPHASIZE text — change a text element's size (sm/md/lg/xl), weight (bold/normal) or color
(ok/warn/risk/info/brand) by calling **style_current_slide** (NOT the update tools). E.g. "başlığı büyült"
→ style_current_slide(element="heading", size="lg"); "eyebrow'u kırmızı yap" →
style_current_slide(element="eyebrow", color="risk"). Elements: heading, eyebrow, subtitle, highlight, description.
WHAT YOU CANNOT DO: arbitrary fonts, exact pixel sizes, custom alignment, or styling the visual's data.
If asked for something truly unsupported, call `answer()` and offer the closest supported option.

RULES:
- EVERY turn you MUST call a tool — you can never reply with plain text. To change the presentation,
  call the edit/add/delete/move/theme tools. To answer a question, explain, or give your FINAL summary
  after editing, call `answer(message)`. A request like "şunu değiştir / düzelt / güzel değil / şöyle yap"
  is a CHANGE request → call the editing tool (NOT answer). Only use `answer` when no change is wanted
  or to report what you just did.
- For the slide the user is on ("bu sayfa"/"bu slayt"/"şu slayt"/no explicit number) use
  update_current_slide / delete_current_slide (they target the selected slide automatically).
  Use update_slide(index)/delete_slide(index) ONLY for a slide the user names explicitly.
- "konu"/"bağlam"/"context"/"topic" = the presentation's real subject (its title), never a literal new
  subject. Every slide must serve that subject.
- Take all actions the request implies (call multiple tools in order).
- If the user only ASKS something (e.g. "hangi sayfada?", "ne yaptın?", "neden?", "kaç slayt var?"),
  DO NOT call any tool — answer the question directly and concretely from the state and the conversation
  (e.g. which slide number you last changed). Never repeat a previous canned sentence.
- After making changes, reply with ONE short Turkish sentence that NAMES which slide you changed —
  its number and short title — e.g. "1. slaytın (Giriş) görselini güncelledim." Be specific, not generic."""


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "answer",
            "description": "Reply to the user WITHOUT changing the presentation. Use this for questions, explanations, chit-chat, and for your FINAL summary sentence after you finish editing.",
            "parameters": {
                "type": "object",
                "properties": {"message": {"type": "string", "description": "Your reply to the user, in Turkish."}},
                "required": ["message"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_current_slide",
            "description": "Improve/rewrite the slide the user currently has selected ('bu sayfa'/'bu slayt'). Targets the selected slide automatically.",
            "parameters": {
                "type": "object",
                "properties": {
                    "instruction": {"type": "string", "description": "Turkish description of how to change this slide."},
                    "change_topic": {"type": "boolean", "description": "true ONLY if the user wants this slide to become a DIFFERENT topic (a new heading). false for polish / improve / fix / visual or wording changes that keep the same topic."},
                },
                "required": ["instruction"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_current_slide",
            "description": "Delete the slide the user currently has selected ('bu sayfayı sil').",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "style_current_slide",
            "description": "Change ONLY the size/weight/color of a text element on the selected slide (e.g. 'büyült', 'kırmızı yap', 'kalın yap'). Deterministic — does NOT rewrite the text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "element": {"type": "string", "enum": ["heading", "eyebrow", "subtitle", "highlight", "description"], "description": "Which text element. OMIT this if the state shows a FOCUSED ELEMENT (the user clicked one) — it is used automatically."},
                    "size": {"type": "string", "enum": ["sm", "md", "lg", "xl"], "description": "md = default."},
                    "weight": {"type": "string", "enum": ["bold", "normal"]},
                    "color": {"type": "string", "enum": ["default", "ok", "warn", "risk", "info", "brand"]},
                },
                "required": [],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_slide",
            "description": "Improve/rewrite a slide BY EXPLICIT 1-based index (only when the user names a specific slide).",
            "parameters": {
                "type": "object",
                "properties": {
                    "index": {"type": "integer", "description": "1-based slide index."},
                    "instruction": {"type": "string", "description": "Turkish description of the change."},
                    "change_topic": {"type": "boolean", "description": "true ONLY if the slide should become a DIFFERENT topic (new heading); false to keep the topic and just improve it."},
                },
                "required": ["index", "instruction"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "add_slide",
            "description": "Add a new slide. The system generates its full content from the brief.",
            "parameters": {
                "type": "object",
                "properties": {
                    "position": {"type": "integer", "description": "1-based insert position; 0 = append at end."},
                    "brief": {"type": "string", "description": "Turkish description of what the new slide should be about (concrete, on-subject)."},
                },
                "required": ["position", "brief"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_slide",
            "description": "Delete the slide at the given 1-based index.",
            "parameters": {
                "type": "object",
                "properties": {"index": {"type": "integer"}},
                "required": ["index"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "move_slide",
            "description": "Move a slide from one 1-based position to another.",
            "parameters": {
                "type": "object",
                "properties": {"from_index": {"type": "integer"}, "to_index": {"type": "integer"}},
                "required": ["from_index", "to_index"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_theme",
            "description": "Change the presentation theme. Use one of the available theme names from the state.",
            "parameters": {
                "type": "object",
                "properties": {"theme_name": {"type": "string"}},
                "required": ["theme_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "set_title",
            "description": "Change the presentation's title.",
            "parameters": {
                "type": "object",
                "properties": {"title": {"type": "string"}},
                "required": ["title"],
            },
        },
    },
]


def build_agent_system_prompt() -> str:
    return AGENT_SYSTEM

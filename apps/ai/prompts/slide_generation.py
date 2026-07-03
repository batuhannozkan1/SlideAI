"""Prompt system for structured slide generation.

The AI returns a presentation as JSON where each slide has a ``slide_type`` and a
``content`` object whose shape depends on the type. This maps directly onto the
``Slide`` model (heading, slide_type, content JSON, notes) and is rendered by the
design-guide template system (cover / split / closing + 8 right-panel visuals).
"""

# kısa özet geç
#
# kısE: SLIDE_JSON_SCHEMA is injected as a *value* (via {json_schema}), so the
# literal braces here are safe and never seen by str.format on the system prompt.
SLIDE_JSON_SCHEMA = """{
  "title_suggestion": "Short presentation title",
  "slides": [
    {
      "heading": "Slide title (page-title)",
      "slide_type": "cover | split | closing",
      "notes": "Speaker guidance (NOT a repeat of the slide content)",
      "content": { ...shape depends on slide_type... }
    }
  ]
}

CONTENT SHAPE PER slide_type
============================

slide_type = "cover"  (first slide only)
{
  "eyebrow": "Short label / organization name",
  "subtitle": "One-line subtitle",
  "description": "1-2 short sentences",
  "icon": "Font Awesome icon name, e.g. fa-rocket",
  "footer": "Small footer text",
  "date": "Year or date"
}

slide_type = "closing"  (last slide only)
{
  "eyebrow": "Short label",
  "subtitle": "One-line subtitle",
  "description": "1-2 short sentences",
  "icon": "Font Awesome icon name",
  "stats": [ {"value": "92%", "label": "Short label"} ],   // 0-3 items
  "footer": "Copyright / contact"
}

slide_type = "split"  (ALL other slides — left text panel + right visual panel)
{
  "eyebrow": "Section label (related slides share the same eyebrow)",
  "subtitle": "One short descriptive sentence",
  "points": [                          // 3-6 items MAX (more overflows)
    { "kind": "ok | warn | risk | num | info",
      "label": "Bold lead-in (2-4 words)",
      "text": "Short explanation (max 1 line)" }
  ],
  "highlight": "Optional single emphasis sentence (omit if not needed)",
  "visual": { "type": "<one of the 8 below>", "data": { ... } }   // REQUIRED
}

point "kind" meanings: ok=strength/positive, warn=caution, risk=danger,
num=ordered step, info=recommendation/direction.

VISUAL TYPES (pick the ONE that best fits the slide's data; data shapes):
- "dashboard":   {"cells": [ {"value": "92%", "label": "..."} ]}            // 2-4 stat boxes
- "bar_chart":   {"bars":  [ {"label": "...", "value": 0-100, "display": "%85"} ]}  // 2-5 bars
- "card_list":   {"cards": [ {"icon": "fa-...", "title": "...", "text": "...", "color": "ok|warn|risk|info|neutral"} ]}  // 2-4
- "timeline":    {"events": [ {"date": "...", "label": "...", "tag": "..."} ]}      // 3-5
- "donut":       {"percent": 0-100, "center": "%72", "label": "..."}
- "comparison":  {"bars": [ {"label": "...", "value": 0-100, "display": "..."} ]}   // 2-4 (relative heights)
- "icon_grid":   {"cells": [ {"icon": "fa-...", "label": "...", "done": true|false} ]}  // 4-8
- "status_card": {"title": "...", "level": "ok|warn|risk", "badge": "...", "text": "...", "tags": ["...", "..."]}

All text values are PLAIN TEXT — never use HTML or markdown tags (no <big>, <b>, **bold**, etc.).

Optional per-element STYLING — to emphasize text, content MAY include a "styles" object:
  "styles": { "<elem>": {"size": "sm|md|lg|xl", "weight": "bold|normal", "color": "ok|warn|risk|info|brand"} }
  <elem> ∈ heading, eyebrow, subtitle, highlight, description. Use it ONLY when asked to enlarge/emphasize/
  recolor text (e.g. "başlığı büyült" -> {"styles": {"heading": {"size": "xl"}}}). Omit it otherwise;
  default sizing is best. Never set sizes on points/visual data.
"""

SLIDE_GENERATION_SYSTEM = """You are a professional presentation designer producing print-ready, data-rich slides.
Return ONLY valid JSON that exactly matches this schema (no markdown, no commentary):

{json_schema}

HARD RULES:
- Aim for about {num_slides} slides; a few more or fewer is fine when it improves the presentation's coherence and quality. Quality over hitting an exact number.
- Slide ordering: the FIRST slide MUST be "cover", the LAST slide MUST be "closing", and EVERY slide in between MUST be "split".
- Every "split" slide MUST have a non-empty "visual" with a valid type and well-formed data.
- "points" arrays: 3-6 items max, each short (one line). Prefer bullet points over paragraphs.
- Vary the visual types across split slides; choose the type that genuinely matches the content
  (numbers->dashboard/bar_chart, progress->donut, phases->timeline, items->card_list,
  trends/sizes->comparison, checklist/coverage->icon_grid, a single risk/status->status_card).
- Use Font Awesome 6 free solid icon names (e.g. fa-chart-line, fa-shield-halved, fa-bolt).
- Keep colors semantic: ok=green, warn=amber, risk=red, info=blue.
- Every slide MUST have a non-empty "heading".
- Speaker "notes" give presenter guidance, never repeat the visible content.
- All visible text MUST be in {language}.
- Tone / style: {style}."""

TEMPLATE_GUIDED_ADDITION = """

TEMPLATE STRUCTURE TO FOLLOW:
Each entry below describes one slide's role and a content hint. Produce one slide per entry,
in order, mapping role to the right slide_type (opening->cover, closing->closing, rest->split):
{template_structure}

The hint describes what content belongs on that slide."""

FREE_FORM_ADDITION = """

Create a logical flow that covers the topic comprehensively: a strong cover, a sequence of
split content slides that build the argument with varied visuals, and a closing/summary slide."""


SLIDE_EDIT_SYSTEM = """You are an expert presentation editor working on ONE slide.
You are given that slide's current JSON and a user instruction. Apply the instruction and
return the FULL updated slide as JSON (no markdown, no commentary), in this exact shape:

{{
  "message": "One short sentence (in {language}) describing what you changed.",
  "heading": "...",
  "slide_type": "cover | split | closing",
  "content": {{ ...shape depends on slide_type... }}
}}

The "content" object MUST follow this schema exactly:
{json_schema}

RULES:
- The slide must serve the PRESENTATION SUBJECT given at the top of the user message. Treat the
  user instruction as HOW to change this slide in service of that subject — not as a new subject.
  If the instruction is vague or contradictory, produce the most useful concrete slide for this
  position within the subject (use the outline to avoid repeating other slides).
- This is an EDIT of an EXISTING slide: keep its current topic and improve it (wording, quality,
  structure, visual). Change the topic/heading only if the user explicitly asks to.
- Apply the instruction faithfully. You may change anything about THIS slide: heading, slide_type,
  points, highlight, and the visual (its type and data) — whatever best serves the subject.
- Preserve fields the instruction does not touch. Do not invent content unrelated to the subject.
- A "split" slide must keep a non-empty "visual" with valid type + well-formed data.
- Use Font Awesome 6 free solid icon names. Keep colors semantic (ok/warn/risk/info).
- All visible text MUST be in {language}.
- "message" is a brief, friendly confirmation of the change — not a repeat of the content."""

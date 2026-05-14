SLIDE_JSON_SCHEMA = """{
  "title_suggestion": "A suggested title for the presentation",
  "slides": [
    {
      "heading": "Slide heading text",
      "body": "Main content text (can use line breaks with \\n)",
      "notes": "Speaker notes for this slide",
      "layout": "content"
    }
  ]
}"""

LAYOUT_OPTIONS = "title, content, two_column, blank"

SLIDE_GENERATION_SYSTEM = """You are a professional presentation designer and content expert.
Your task is to generate presentation slides with clear, structured, and engaging content.

RULES:
- Return ONLY valid JSON matching this schema:
{json_schema}

- Available layout values: {layouts}
- Use "title" layout for opening and closing slides
- Use "two_column" layout when comparing or listing parallel items (separate columns with \\n\\n in body)
- Use "content" layout for most slides
- Each slide MUST have a non-empty heading and body
- Speaker notes should contain presenter guidance, not repeat the slide content
- Content must be in {language}
- Style: {style}
- Generate exactly {num_slides} slides"""

TEMPLATE_GUIDED_ADDITION = """
TEMPLATE STRUCTURE TO FOLLOW:
Each slide has a specific role and layout. Fill in content matching each slot:
{template_structure}

Follow the template structure exactly. Use the specified layout for each slide.
The hint describes what content should go in that slide."""

FREE_FORM_ADDITION = """
Create a logical flow of slides covering the topic comprehensively.
Start with a title slide and end with a closing/summary slide."""

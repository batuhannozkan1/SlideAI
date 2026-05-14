SLIDE_GENERATION_SYSTEM = """You are a professional presentation designer.
Generate slides with clear, concise content suitable for business presentations.
Each slide must have a heading, body text, and optional speaker notes.
Return valid JSON array of slide objects."""

SLIDE_STRUCTURE_TEMPLATE = """{
  "slides": [
    {
      "heading": "Slide title here",
      "body": "Main content here",
      "notes": "Speaker notes here",
      "layout": "content"
    }
  ]
}"""

# AI Pipeline Debug Agent

You debug issues in SlideAI's AI-powered presentation generation pipeline. You trace problems through the full chain: prompt → API call → parse → validate → persist.

## Pipeline Architecture

```
presentation_generate view (apps/presentations/views/)
  → AIGenerateForm.is_valid()
  → generation_service.generate_presentation_slides(GenerationRequest)
      → get_ai_client() → client from registry (apps/ai/clients/)
      → client.generate(request)
          → prompt_service.build_system_prompt()
          → prompt_service.build_user_prompt()
          → OpenAI-compatible API call (Together AI)
          → _parse_response() → JSON extraction
      → _validate_generation()
  → presentation_service.create_presentation()
  → slide_service.create_slide() × N
  → redirect → detail page
```

## Key Files

- `apps/ai/clients/__init__.py` — client registry, `get_ai_client()`
- `apps/ai/clients/together_client.py` — TogetherClient, API call, response parsing
- `apps/ai/clients/base.py` — BaseAIClient interface
- `apps/ai/services/generation_service.py` — orchestrates full generation flow
- `apps/ai/services/prompt_service.py` — builds system/user prompts
- `apps/presentations/views/` — generation view entry point
- `apps/presentations/forms/ai_forms.py` — AIGenerateForm validation

## Debug Stages

### Stage 1: Input & Form
- Is the form valid? Check `AIGenerateForm` field definitions.
- Is `GenerationRequest` DTO constructed correctly from form data?
- Are required fields present (topic, slide_count, language, etc.)?

### Stage 2: Client Resolution
- Is `AI_PROVIDER` set correctly in settings?
- Does `get_ai_client()` resolve to the expected client?
- Is the client's API key / base URL configured in `.env`?

### Stage 3: Prompt Construction
- Read `prompt_service.py` — what system/user prompts are built?
- Does the prompt include all necessary context (topic, slide count, language, template)?
- Check for prompt injection risks in user input.

### Stage 4: API Call
- What model is being called? Check `together_client.py`.
- What parameters are sent (temperature, max_tokens, response_format)?
- Is the API response status 200? Check error handling.
- Is the response valid JSON?

### Stage 5: Response Parsing
- Read `_parse_response()` — how is the raw API response converted to structured data?
- Does it handle malformed JSON? Missing fields? Extra fields?
- What does the parsed structure look like (list of slides with title/content/notes)?

### Stage 6: Validation
- Read `_validate_generation()` — what rules are applied?
- Slide count matches request? Content length limits? Required fields present?

### Stage 7: Persistence
- `presentation_service.create_presentation()` → creates the Presentation model
- `slide_service.create_slide()` × N → creates Slide models with position ordering
- Are all slides created? Is position correct? Is theme applied?

## Debug Approach

1. **Reproduce** — understand the exact error/symptom.
2. **Localize** — determine which stage fails (read error messages, trace the flow).
3. **Inspect** — read the specific file/function at the failure point.
4. **Root cause** — identify why (wrong config, bad prompt, API change, parse assumption).
5. **Fix** — apply minimal fix at the correct layer. Don't leak fixes across layers.

## Common Issues

- **API key expired/missing** → check `.env` and settings loading
- **JSON parse failure** → API returned markdown-wrapped JSON or changed format
- **Validation rejection** → slide count mismatch, empty content fields
- **Registry miss** → AI_PROVIDER setting doesn't match registered client name
- **Rate limiting** → Together AI rate limit hit, need backoff/retry logic

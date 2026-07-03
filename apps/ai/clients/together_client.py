from __future__ import annotations

import json
import logging
import re

import openai
from django.conf import settings

from apps.ai.clients import register_client
from apps.ai.clients.base_client import BaseAIClient
from typing import Any

from apps.ai.dtos import (
    AgentStep,
    GenerationRequest,
    GenerationResult,
    SlideContent,
    SlideEditRequest,
    SlideEditResult,
    ToolCall,
)
from apps.ai.services.prompt_service import (
    build_edit_system_prompt,
    build_edit_user_prompt,
    build_system_prompt,
    build_user_prompt,
)
from apps.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

# Slide content is PLAIN TEXT (the design system controls all styling). Strip any
# HTML/markup tags the model may leak (e.g. "<big>...</big>") from every text value
# so they never render literally. General — not tied to any specific tag.
_TAG_RE = re.compile(r"</?[a-zA-Z][^>]*>")


def _clean(obj: Any) -> Any:
    if isinstance(obj, str):
        return _TAG_RE.sub("", obj)
    if isinstance(obj, list):
        return [_clean(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _clean(v) for k, v in obj.items()}
    return obj


class TogetherClient(BaseAIClient):
    def __init__(self) -> None:
        self._client = openai.OpenAI(
            api_key=settings.AI_API_KEY,
            base_url=settings.AI_BASE_URL,
        )
        self._model = settings.AI_MODEL

    def generate(self, request: GenerationRequest) -> GenerationResult:
        system_prompt = build_system_prompt(request)
        user_prompt = build_user_prompt(request)

        # Structured slides are token-heavy; scale the output budget with the
        # slide count so larger decks don't get truncated mid-JSON.
        max_tokens = min(12288, 1500 + request.num_slides * 500)

        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.7,
                max_tokens=max_tokens,
            )
        except openai.APIError as exc:
            logger.error("Together AI API error: %s", exc)
            raise ExternalServiceError(f"AI servisi hatası: {exc.message}") from exc

        raw = response.choices[0].message.content or "{}"
        model_used = response.model or self._model
        token_count = response.usage.total_tokens if response.usage else 0

        return _parse_response(raw, model_used, token_count)

    def edit_slide(self, request: SlideEditRequest) -> SlideEditResult:
        messages = [{"role": "system", "content": build_edit_system_prompt(request)}]
        for role, text in request.history:
            if role in ("user", "assistant") and text:
                messages.append({"role": role, "content": text})
        messages.append({"role": "user", "content": build_edit_user_prompt(request)})
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.4,  # faithful edits — follow the instruction, less drift
                max_tokens=2048,
            )
        except openai.APIError as exc:
            logger.error("Together AI edit error: %s", exc)
            raise ExternalServiceError(f"AI servisi hatası: {exc.message}") from exc

        raw = response.choices[0].message.content or "{}"
        data = _load_obj(raw)
        slide = SlideContent(
            heading=_clean(data.get("heading") or request.heading),
            slide_type=data.get("slide_type") or request.slide_type,
            content=_clean(data.get("content") or request.content),
        )
        return SlideEditResult(slide=slide, message=data.get("message", ""))

    def complete_with_tools(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]],
        tool_choice: str = "auto",
    ) -> AgentStep:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                temperature=0.2,  # precise tool/element selection — low randomness
                max_tokens=3000,
            )
        except openai.APIError as exc:
            logger.error("Together AI tools error: %s", exc)
            raise ExternalServiceError(f"AI servisi hatası: {exc.message}") from exc

        msg = response.choices[0].message
        calls = []
        for tc in (msg.tool_calls or []):
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            calls.append(ToolCall(id=tc.id, name=tc.function.name, arguments=args))

        return AgentStep(
            text=msg.content or "",
            tool_calls=tuple(calls),
            assistant_message=msg.model_dump(exclude_none=True),
        )


def _load_tolerant(raw: str) -> dict:
    """Parse the model's JSON, tolerating truncation (common on large decks).
    On failure, salvage every complete slide object from the "slides" array so a
    big request degrades to fewer coherent slides instead of crashing."""
    raw = (raw or "").strip()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("AI JSON invalid/truncated; salvaging complete slides.")

    title = ""
    m = re.search(r'"title_suggestion"\s*:\s*"((?:[^"\\]|\\.)*)"', raw)
    if m:
        try:
            title = json.loads('"' + m.group(1) + '"')
        except json.JSONDecodeError:
            title = m.group(1)

    slides: list = []
    decoder = json.JSONDecoder()
    key = raw.find('"slides"')
    start = raw.find("[", key) if key != -1 else -1
    if start != -1:
        i = start + 1
        n = len(raw)
        while i < n:
            while i < n and raw[i] in " \t\r\n,":
                i += 1
            if i >= n or raw[i] == "]":
                break
            try:
                obj, end = decoder.raw_decode(raw, i)
            except json.JSONDecodeError:
                break  # incomplete trailing object — stop here
            slides.append(obj)
            i = end

    if not slides:
        raise ExternalServiceError("AI yanıtı geçersiz JSON formatında.")
    return {"title_suggestion": title, "slides": slides}


def _load_obj(raw: str) -> dict:
    """Strict-ish single-object JSON load for edit responses (no slides array).
    Raises on failure so we never silently wipe a slide's content."""
    try:
        return json.loads((raw or "").strip())
    except json.JSONDecodeError as exc:
        raise ExternalServiceError("AI yanıtı geçersiz JSON formatında.") from exc


def _parse_response(raw_json: str, model_used: str, token_count: int) -> GenerationResult:
    data = _load_tolerant(raw_json)

    slides_data = data.get("slides", [])
    if not slides_data:
        raise ExternalServiceError("AI yanıtında slayt verisi bulunamadı.")

    slides = tuple(
        SlideContent(
            heading=_clean(s.get("heading", "")),
            slide_type=s.get("slide_type", "split"),
            content=_clean(s.get("content", {}) or {}),
            notes=s.get("notes", ""),
        )
        for s in slides_data
    )

    return GenerationResult(
        slides=slides,
        title_suggestion=data.get("title_suggestion", ""),
        model_used=model_used,
        token_count=token_count,
    )


register_client("together", TogetherClient)

import json
from typing import Any

from apps.ai.clients import register_client
from apps.ai.clients.base_client import BaseAIClient
from apps.ai.dtos import (
    AgentStep,
    GenerationRequest,
    GenerationResult,
    SlideContent,
    SlideEditRequest,
    SlideEditResult,
    ToolCall,
)

# Sample visual blocks cycled through split slides so the mock exercises
# every right-panel renderer (useful for local design work and render tests).
_SAMPLE_VISUALS = (
    {
        "type": "dashboard",
        "data": {"cells": [
            {"value": "92%", "label": "Memnuniyet"},
            {"value": "1.2M", "label": "Kullanıcı"},
            {"value": "48", "label": "Ülke"},
            {"value": "4.8", "label": "Puan"},
        ]},
    },
    {
        "type": "bar_chart",
        "data": {"bars": [
            {"label": "Web", "value": 85, "display": "%85"},
            {"label": "Mobil", "value": 72, "display": "%72"},
            {"label": "Masaüstü", "value": 54, "display": "%54"},
        ]},
    },
    {
        "type": "card_list",
        "data": {"cards": [
            {"icon": "fa-bolt", "title": "Hızlı", "text": "Anında sonuç.", "color": "ok"},
            {"icon": "fa-shield-halved", "title": "Güvenli", "text": "Uçtan uca şifreleme.", "color": "info"},
        ]},
    },
    {
        "type": "timeline",
        "data": {"events": [
            {"date": "Q1", "label": "Başlangıç", "tag": "Tamamlandı"},
            {"date": "Q2", "label": "Beta", "tag": "Devam"},
            {"date": "Q3", "label": "Lansman", "tag": "Planlandı"},
        ]},
    },
    {
        "type": "donut",
        "data": {"percent": 72, "center": "%72", "label": "Tamamlanma oranı"},
    },
    {
        "type": "comparison",
        "data": {"bars": [
            {"label": "2023", "value": 40, "display": "40K"},
            {"label": "2024", "value": 75, "display": "75K"},
            {"label": "2025", "value": 100, "display": "100K"},
        ]},
    },
    {
        "type": "icon_grid",
        "data": {"cells": [
            {"icon": "fa-check", "label": "Analiz", "done": True},
            {"icon": "fa-check", "label": "Tasarım", "done": True},
            {"icon": "fa-gear", "label": "Geliştirme", "done": False},
            {"icon": "fa-rocket", "label": "Yayın", "done": False},
        ]},
    },
    {
        "type": "status_card",
        "data": {
            "title": "Risk Değerlendirmesi",
            "level": "warn",
            "badge": "Orta",
            "text": "Bütçe aşımı riski izlenmeli.",
            "tags": ["bütçe", "zaman"],
        },
    },
)


class MockAIClient(BaseAIClient):
    def generate(self, request: GenerationRequest) -> GenerationResult:
        slides: list[SlideContent] = []
        n = request.num_slides

        for i in range(n):
            if i == 0:
                slides.append(SlideContent(
                    heading=request.topic,
                    slide_type="cover",
                    content={
                        "eyebrow": "Sunum",
                        "subtitle": f"{request.topic} üzerine genel bakış",
                        "description": "AI tarafından oluşturulan örnek sunum.",
                        "icon": "fa-presentation-screen",
                        "footer": "SlideAI",
                        "date": "2026",
                    },
                    notes=f"Açılış: {request.topic}",
                ))
            elif i == n - 1 and n > 1:
                slides.append(SlideContent(
                    heading="Teşekkürler",
                    slide_type="closing",
                    content={
                        "eyebrow": "Kapanış",
                        "subtitle": "Sorularınız için hazırız",
                        "description": f"{request.topic} sunumunu izlediğiniz için teşekkürler.",
                        "icon": "fa-circle-check",
                        "stats": [
                            {"value": "100%", "label": "Kapsam"},
                            {"value": f"{n}", "label": "Slayt"},
                        ],
                        "footer": "© 2026 SlideAI",
                    },
                    notes="Kapanış ve teşekkür.",
                ))
            else:
                visual = _SAMPLE_VISUALS[(i - 1) % len(_SAMPLE_VISUALS)]
                slides.append(SlideContent(
                    heading=f"{request.topic} — Bölüm {i}",
                    slide_type="split",
                    content={
                        "eyebrow": f"Bölüm {i}",
                        "subtitle": f"{request.topic} hakkında detaylı bilgi.",
                        "points": [
                            {"kind": "ok", "label": "Güçlü yön", "text": "Önemli avantaj."},
                            {"kind": "warn", "label": "Dikkat", "text": "İzlenmesi gereken nokta."},
                            {"kind": "num", "label": "Adım", "text": "Sıralı eylem maddesi."},
                            {"kind": "info", "label": "Öneri", "text": "Yönlendirici tavsiye."},
                        ],
                        "highlight": "Bu slayttaki en önemli çıkarım buraya gelir.",
                        "visual": visual,
                    },
                    notes=f"Konuşmacı notu: {request.topic} - slayt {i + 1}",
                ))

        return GenerationResult(
            slides=tuple(slides),
            title_suggestion=request.topic,
            model_used="mock",
            token_count=0,
        )

    def edit_slide(self, request: SlideEditRequest) -> SlideEditResult:
        # Deterministic mock edit: mark the heading and echo the instruction.
        slide = SlideContent(
            heading=(request.heading + " ✦"),
            slide_type=request.slide_type,
            content=dict(request.content or {}),
        )
        return SlideEditResult(
            slide=slide,
            message=f"İsteğiniz uygulandı (mock): {request.instruction}",
        )

    def complete_with_tools(
        self, messages: list[dict[str, Any]], tools: list[dict[str, Any]],
        tool_choice: str = "auto",
    ) -> AgentStep:
        def step(name, args):
            tc_id = "call_mock_1"
            return AgentStep(
                text="",
                tool_calls=(ToolCall(id=tc_id, name=name, arguments=args),),
                assistant_message={"role": "assistant", "content": None, "tool_calls": [
                    {"id": tc_id, "type": "function",
                     "function": {"name": name, "arguments": json.dumps(args)}}]},
            )

        # A tool already ran this turn → finish by answering (terminal).
        if any(m.get("role") == "tool" for m in messages):
            return step("answer", {"message": "Tamamlandı (mock)."})

        user = ""
        for m in messages:
            if m.get("role") == "user":
                user = (m.get("content") or "")
        u = user.lower()
        if "ekle" in u or "add" in u:
            return step("add_slide", {"position": 0, "brief": "mock brief"})
        if "taşı" in u or "sırala" in u or "move" in u or "yer" in u:
            return step("move_slide", {"from_index": 1, "to_index": 2})
        if "tema" in u or "theme" in u:
            return step("set_theme", {"theme_name": "mock"})
        if "sil" in u or "delete" in u or "kaldır" in u:
            return step("delete_current_slide", {})
        if "büyült" in u or "büyüt" in u or "küçült" in u or "vurgula" in u or "renk" in u or "kalın" in u:
            return step("style_current_slide", {"size": "lg"})  # element omitted → uses focused element
        if "düzelt" in u or "güncelle" in u or "yeniden" in u or "değiştir" in u or "yap" in u:
            return step("update_current_slide", {"instruction": "mock instruction"})
        # No action keyword → just answer (question / chit-chat).
        return step("answer", {"message": "(mock) Sorunuza yanıt."})


register_client("mock", MockAIClient)

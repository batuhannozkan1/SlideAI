import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.utils.http import url_has_allowed_host_and_scheme

from apps.ai.dtos import GenerationRequest
from apps.ai.services.agent_service import run_agent
from apps.ai.services.generation_service import (
    edit_slide_with_instruction,
    generate_presentation_slides,
)
from apps.presentations.dtos import (
    CreatePresentationDTO,
    CreateSlideDTO,
    UpdatePresentationDTO,
    UpdateSlideDTO,
)
from apps.presentations.forms.ai_forms import AIGenerateForm
from apps.presentations.forms.presentation_forms import PresentationCreateForm
from apps.presentations.services import presentation_service, slide_service
from apps.presentations.services import theme_service

logger = logging.getLogger(__name__)


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    stats = presentation_service.get_dashboard_stats(owner_id=request.user.id)
    recent = presentation_service.get_recent_presentations(owner_id=request.user.id, limit=5)
    return render(request, "presentations/dashboard.html", {
        "stats": stats,
        "recent_presentations": recent,
        "topbar_show_tabs": True,
    })


@login_required
def presentation_list(request: HttpRequest) -> HttpResponse:
    page = int(request.GET.get("page", 1))
    result = presentation_service.list_user_presentations(
        owner_id=request.user.id,
        page=page,
    )
    return render(request, "presentations/list.html", {"result": result})


@login_required
def presentation_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = PresentationCreateForm(request.POST)
        if form.is_valid():
            theme = form.cleaned_data.get("theme")
            dto = CreatePresentationDTO(
                title=form.cleaned_data["title"],
                description=form.cleaned_data["description"],
                owner_id=request.user.id,
                theme_id=theme.pk if theme else None,
            )
            result = presentation_service.create_presentation(dto)
            messages.success(request, "Sunum oluşturuldu.")
            return redirect("presentations:editor", pk=result.data.pk)
    else:
        form = PresentationCreateForm()

    return render(request, "presentations/create.html", {"form": form})


@login_required
def presentation_detail(request: HttpRequest, pk) -> HttpResponse:
    return redirect("presentations:editor", pk=pk)


@login_required
def presentation_delete(request: HttpRequest, pk) -> HttpResponse:
    if request.method == "POST":
        presentation_service.delete_presentation(
            pk, requesting_user_id=request.user.id
        )
        messages.success(request, "Presentation deleted.")
        return redirect("presentations:list")

    result = presentation_service.get_presentation(
        pk, requesting_user_id=request.user.id
    )
    return render(
        request, "presentations/confirm_delete.html", {"presentation": result.data}
    )


@login_required
def presentation_generate(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = AIGenerateForm(request.POST)
        if form.is_valid():
            template = form.cleaned_data.get("template")
            template_structure = template.structure if template else None

            gen_request = GenerationRequest(
                topic=form.cleaned_data["topic"],
                num_slides=form.cleaned_data["num_slides"],
                style=form.cleaned_data["style"],
                template_structure=template_structure,
                additional_instructions=form.cleaned_data.get("additional_instructions", ""),
            )

            result = generate_presentation_slides(gen_request)
            if not result.success:
                for error_list in result.errors.values():
                    for error in error_list:
                        messages.error(request, error)
                return render(request, "presentations/generate.html", {"form": form})

            gen_result = result.data
            theme = form.cleaned_data.get("theme")

            pres_dto = CreatePresentationDTO(
                title=gen_result.title_suggestion or form.cleaned_data["topic"],
                description=f"AI tarafından oluşturuldu: {form.cleaned_data['topic']}",
                owner_id=request.user.id,
                theme_id=theme.pk if theme else None,
            )
            pres_result = presentation_service.create_presentation(pres_dto)
            presentation = pres_result.data

            for i, slide_content in enumerate(gen_result.slides):
                slide_service.create_slide(
                    CreateSlideDTO(
                        presentation_id=presentation.pk,
                        heading=slide_content.heading,
                        notes=slide_content.notes,
                        slide_type=slide_content.slide_type,
                        content=slide_content.content,
                        position=i,
                    ),
                    requesting_user_id=request.user.id,
                )

            messages.success(request, "Sunum başarıyla oluşturuldu!")
            return redirect("presentations:editor", pk=presentation.pk)
    else:
        initial = {}
        topic = request.GET.get("topic")
        if topic:
            initial["topic"] = topic
        form = AIGenerateForm(initial=initial)

    return render(request, "presentations/generate.html", {"form": form})


@login_required
def presentation_editor(request: HttpRequest, pk) -> HttpResponse:
    result = presentation_service.get_presentation(
        pk, requesting_user_id=request.user.id
    )
    themes_result = theme_service.list_active_themes()
    slides = list(result.data.slides.all())
    slides_json = [
        {
            "id": str(s.pk),
            "slide_type": s.slide_type,
            "heading": s.heading,
            "content": s.content or {},
            "position": s.position,
        }
        for s in slides
    ]
    return render(request, "presentations/editor.html", {
        "presentation": result.data,
        "slides": slides,
        "slides_json": slides_json,
        "themes": themes_result.data,
    })


@login_required
def presentation_update_title(request: HttpRequest, pk) -> HttpResponse:
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    data = json.loads(request.body)
    title = (data.get("title") or "").strip()
    if not title:
        return JsonResponse({"error": "empty title"}, status=400)
    presentation_service.update_presentation(
        pk, UpdatePresentationDTO(title=title), requesting_user_id=request.user.id
    )
    return JsonResponse({"status": "ok"})


@login_required
def presentation_agent(request: HttpRequest, pk) -> HttpResponse:
    """Agentic AI assistant: runs a tool-calling loop that can edit/add/delete/move
    slides and change the theme on the whole presentation."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)
    instruction = (data.get("instruction") or "").strip()
    if not instruction:
        return JsonResponse({"message": "Lütfen bir komut yazın."}, status=400)

    raw_history = data.get("history") or []
    history = tuple(
        (str(m.get("role", "")), str(m.get("text", "")))
        for m in raw_history
        if isinstance(m, dict) and m.get("role") in ("user", "assistant")
    )[-8:]
    current_index = data.get("current_index")
    selected_element = data.get("selected_element")
    if selected_element not in ("heading", "eyebrow", "subtitle", "highlight", "description",
                                "visual", "title", "date", "icon", "footer"):
        selected_element = None
    uid = request.user.id

    # ownership check
    presentation_service.get_presentation(pk, requesting_user_id=uid)
    themes = list(theme_service.list_active_themes().data)

    def ordered_slides():
        return list(slide_service.list_slides(pk).data)

    def outline():
        return [f"{i + 1}. [{s.slide_type}] {s.heading}" for i, s in enumerate(ordered_slides())]

    # ----- initial state for the model -----
    slides = ordered_slides()
    selected = None
    if isinstance(current_index, int) and 0 <= current_index < len(slides):
        sc = slides[current_index]
        selected = json.dumps(
            {"index": current_index + 1, "heading": sc.heading, "slide_type": sc.slide_type, "content": sc.content},
            ensure_ascii=False,
        )
    pres = presentation_service.get_presentation(pk, requesting_user_id=uid).data
    state_lines = [f'PRESENTATION TITLE (subject): "{pres.title}"',
                   "OUTLINE (1-indexed):", *outline(),
                   "AVAILABLE THEMES: " + ", ".join(t.name for t in themes)]
    if selected:
        state_lines.append(
            f'SELECTED SLIDE INDEX = {current_index + 1}. The user is currently viewing this slide. '
            f'"bu sayfa", "bu slayt", "şu slayt", "this slide/page" (without an explicit number) ALWAYS '
            f'mean slide {current_index + 1} — edit THAT slide, not any other.'
        )
        # Explicit element→text map so the agent styles the element the user
        # actually pointed at (e.g. quoting the eyebrow text -> element "eyebrow").
        sc = slides[current_index]
        cont = sc.content if isinstance(sc.content, dict) else {}
        elem_pairs = [("heading", sc.heading)]
        for k in ("eyebrow", "subtitle", "description", "highlight"):
            if cont.get(k):
                elem_pairs.append((k, cont[k]))
        elem_lines = "\n".join(f'  - {k}: "{str(v)[:90]}"' for k, v in elem_pairs if v)
        state_lines.append(
            "SELECTED SLIDE TEXT ELEMENTS (when the user quotes or points at text, match it to the "
            "element NAME below and style/edit THAT element):\n" + elem_lines
        )
        if selected_element == "visual":
            state_lines.append(
                "FOCUSED ELEMENT: the user clicked the VISUAL (right-panel chart/graphic/metrics). Commands "
                "like 'bunu değiştir / bar grafiğe çevir / rengini değiştir / verileri güncelle' refer to the "
                "VISUAL → call update_current_slide with an instruction about the visual (its type/data). Do "
                "NOT use style_current_slide for the visual."
            )
        elif selected_element == "title":
            state_lines.append(
                "FOCUSED ELEMENT: the PRESENTATION TITLE (the big text on the cover/closing dark panel). To "
                "change its TEXT call set_title. Its size/style is fixed by the design (not stylable)."
            )
        elif selected_element in ("date", "icon", "footer"):
            state_lines.append(
                f"FOCUSED ELEMENT: the slide's '{selected_element}' (content.{selected_element}). To change it, "
                f"call update_current_slide with an instruction about the {selected_element}."
            )
        elif selected_element:
            state_lines.append(
                f"FOCUSED ELEMENT: the user CLICKED the '{selected_element}' text element. Commands like "
                f"'bunu büyült / kırmızı yap / kalın yap / düzelt' refer to THIS element. For "
                f"style_current_slide you may OMIT 'element' — it defaults to the focused one."
            )
        state_lines.append("SELECTED SLIDE (full JSON):\n" + selected)
    system_context = "\n".join(state_lines)

    # Generate one rich, on-subject slide by delegating to the proven single-slide AI
    # (the agent never writes content itself — this avoids thin/placeholder slides).
    def gen_slide(slide_type, heading, content, instruction, change_topic=False):
        res = edit_slide_with_instruction(
            slide_type=slide_type, heading=heading, content=content or {},
            instruction=instruction, presentation_title=pres.title, outline=tuple(outline()),
            history=history, change_topic=change_topic,
        )
        return res.data.slide if res.success else None

    # Track whether the deck STRUCTURE changed (needs full reload) vs. only the
    # content of existing slides (can be swapped in place — no reload, no scroll jump).
    flags = {"structural": False}
    updated_idx: list[int] = []

    # ----- tool executor (performs DB actions) -----
    def _exec(name: str, args: dict) -> dict:
        if name in ("update_current_slide", "delete_current_slide"):
            slides_now = ordered_slides()
            if not isinstance(current_index, int) or not (0 <= current_index < len(slides_now)):
                return {"status": "error", "detail": "Seçili slayt yok.", "outline": outline()}
            target = slides_now[current_index]
            if name == "delete_current_slide":
                slide_service.delete_slide(target.pk, requesting_user_id=uid)
                return {"status": "ok", "changed": True, "detail": "Seçili slayt silindi.", "outline": outline()}
            gen = gen_slide(target.slide_type, target.heading, target.content,
                            args.get("instruction") or "", bool(args.get("change_topic")))
            if gen is None:
                return {"status": "error", "detail": "İçerik üretilemedi.", "outline": outline()}
            slide_service.update_slide(
                target.pk,
                UpdateSlideDTO(heading=gen.heading, slide_type=gen.slide_type, content=gen.content),
                requesting_user_id=uid,
            )
            return {"status": "ok", "changed": True,
                    "detail": f"{current_index + 1}. (seçili) slayt güncellendi.", "outline": outline()}

        if name == "style_current_slide":
            slides_now = ordered_slides()
            if not isinstance(current_index, int) or not (0 <= current_index < len(slides_now)):
                return {"status": "error", "detail": "Seçili slayt yok.", "outline": outline()}
            element = args.get("element") or selected_element  # UI focus is authoritative
            if element not in ("heading", "eyebrow", "subtitle", "highlight", "description"):
                return {"status": "error", "detail": "Hangi öğe? Slaytta bir yazıya tıkla ya da öğe adını söyle.", "outline": outline()}
            target = slides_now[current_index]
            content = dict(target.content or {})
            styles = dict(content.get("styles") or {})
            es = dict(styles.get(element) or {})
            size, weight, color = args.get("size"), args.get("weight"), args.get("color")
            if size == "md":
                es.pop("size", None)
            elif size in ("sm", "lg", "xl"):
                es["size"] = size
            if weight == "normal":
                es.pop("weight", None)
            elif weight == "bold":
                es["weight"] = "bold"
            if color == "default":
                es.pop("color", None)
            elif color in ("ok", "warn", "risk", "info", "brand"):
                es["color"] = color
            if es:
                styles[element] = es
            else:
                styles.pop(element, None)
            content["styles"] = styles
            slide_service.update_slide(target.pk, UpdateSlideDTO(content=content), requesting_user_id=uid)
            return {"status": "ok", "changed": True,
                    "detail": f"{current_index + 1}. slaytın '{element}' stili güncellendi.", "outline": outline()}

        if name == "update_slide":
            slides_now = ordered_slides()
            idx = int(args.get("index", 0)) - 1
            if not (0 <= idx < len(slides_now)):
                return {"status": "error", "detail": "Geçersiz slayt indeksi.", "outline": outline()}
            target = slides_now[idx]
            gen = gen_slide(target.slide_type, target.heading, target.content,
                            args.get("instruction") or "", bool(args.get("change_topic")))
            if gen is None:
                return {"status": "error", "detail": "İçerik üretilemedi.", "outline": outline()}
            slide_service.update_slide(
                target.pk,
                UpdateSlideDTO(heading=gen.heading, slide_type=gen.slide_type, content=gen.content),
                requesting_user_id=uid,
            )
            return {"status": "ok", "changed": True, "detail": f"{idx + 1}. slayt güncellendi.", "outline": outline()}

        if name == "add_slide":
            brief = (args.get("brief") or "").strip()
            gen = gen_slide("split", "", {}, "Bu konuda yeni bir slayt oluştur: " + brief)
            if gen is None:
                return {"status": "error", "detail": "İçerik üretilemedi.", "outline": outline()}
            created = slide_service.create_slide(
                CreateSlideDTO(presentation_id=pk, heading=gen.heading, slide_type=gen.slide_type,
                               content=gen.content, position=-1),
                requesting_user_id=uid,
            ).data
            pos = int(args.get("position", 0))
            ids = [s.pk for s in ordered_slides()]  # new slide currently at end
            if 1 <= pos <= len(ids):
                ids = [i for i in ids if i != created.pk]
                ids.insert(pos - 1, created.pk)
                slide_service.reorder_slides(pk, ids, requesting_user_id=uid)
            return {"status": "ok", "changed": True, "detail": "Yeni slayt eklendi.", "outline": outline()}

        if name == "delete_slide":
            slides_now = ordered_slides()
            idx = int(args.get("index", 0)) - 1
            if not (0 <= idx < len(slides_now)):
                return {"status": "error", "detail": "Geçersiz slayt indeksi.", "outline": outline()}
            slide_service.delete_slide(slides_now[idx].pk, requesting_user_id=uid)
            return {"status": "ok", "changed": True, "detail": f"{idx + 1}. slayt silindi.", "outline": outline()}

        if name == "move_slide":
            ids = [s.pk for s in ordered_slides()]
            frm = int(args.get("from_index", 0)) - 1
            to = int(args.get("to_index", 0)) - 1
            if not (0 <= frm < len(ids)) or not (0 <= to < len(ids)):
                return {"status": "error", "detail": "Geçersiz indeks.", "outline": outline()}
            moved = ids.pop(frm)
            ids.insert(to, moved)
            slide_service.reorder_slides(pk, ids, requesting_user_id=uid)
            return {"status": "ok", "changed": True, "detail": "Slayt taşındı.", "outline": outline()}

        if name == "set_theme":
            wanted = (args.get("theme_name") or "").strip().lower()
            match = next((t for t in themes if t.name.lower() == wanted), None) \
                or next((t for t in themes if wanted and wanted in t.name.lower()), None)
            if not match:
                return {"status": "error", "detail": "Tema bulunamadı. Mevcut: " + ", ".join(t.name for t in themes)}
            theme_service.apply_theme(pk, match.pk, user_id=uid)
            return {"status": "ok", "changed": True, "detail": f"Tema '{match.name}' uygulandı."}

        if name == "set_title":
            title = (args.get("title") or "").strip()
            if not title:
                return {"status": "error", "detail": "Boş başlık."}
            presentation_service.update_presentation(pk, UpdatePresentationDTO(title=title), requesting_user_id=uid)
            return {"status": "ok", "changed": True, "detail": "Başlık güncellendi."}

        return {"status": "error", "detail": f"Bilinmeyen araç: {name}"}

    structural_tools = {"add_slide", "delete_slide", "delete_current_slide",
                        "move_slide", "set_theme", "set_title"}

    def executor(name: str, args: dict) -> dict:
        result = _exec(name, args)
        if result.get("changed"):
            if name in structural_tools:
                flags["structural"] = True
            elif name in ("update_current_slide", "style_current_slide") and isinstance(current_index, int):
                updated_idx.append(current_index)
            elif name == "update_slide":
                try:
                    updated_idx.append(int(args.get("index", 0)) - 1)
                except (TypeError, ValueError):
                    pass
        return result

    try:
        result = run_agent(
            system_context=system_context,
            instruction=instruction,
            history=history,
            tool_executor=executor,
        )
    except Exception as exc:
        logger.error("Agent run failed: %s", exc)
        return JsonResponse({"message": "Asistan şu an yanıt veremedi, tekrar dener misin?"}, status=200)

    # Structural change → client reloads. Content-only edits → return fragments to
    # swap in place (no reload, so the slide sidebar doesn't jump to the top).
    if flags["structural"] or not updated_idx:
        return JsonResponse({"message": result.message, "changed": result.changed,
                             "structural": flags["structural"]})

    fresh = presentation_service.get_presentation(pk, requesting_user_id=uid).data
    fresh_slides = list(fresh.slides.all())
    updates = []
    for i in sorted(set(updated_idx)):
        if 0 <= i < len(fresh_slides):
            s = fresh_slides[i]
            updates.append({
                "index": i,
                "html": render_to_string("presentations/slides/_slide.html",
                                         {"slide": s, "page": s.position + 1,
                                          "total": len(fresh_slides), "brand": fresh.title}),
                "heading": s.heading, "slide_type": s.slide_type, "content": s.content,
            })
    return JsonResponse({"message": result.message, "changed": result.changed,
                         "structural": False, "updates": updates})


@login_required
def presentation_present(request: HttpRequest, pk) -> HttpResponse:
    result = presentation_service.get_presentation(
        pk, requesting_user_id=request.user.id
    )
    return render(request, "presentations/present.html", {"presentation": result.data})


@login_required
def change_theme(request: HttpRequest, pk) -> HttpResponse:
    if request.method == "POST":
        theme_id = request.POST.get("theme_id") or None
        theme_service.apply_theme(pk, theme_id, user_id=request.user.id)
        messages.success(request, "Tema değiştirildi.")
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        return redirect(next_url)
    return redirect("presentations:editor", pk=pk)


@login_required
def presentation_duplicate(request: HttpRequest, pk) -> HttpResponse:
    if request.method == "POST":
        result = presentation_service.duplicate_presentation(
            pk, requesting_user_id=request.user.id
        )
        messages.success(request, "Sunum kopyalandı.")
        return redirect("presentations:editor", pk=result.data.pk)
    return redirect("presentations:editor", pk=pk)

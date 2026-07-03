/* SlideAI editor: structured content editing + reorder + title save + regenerate.
   Reads slide data from #slidesData (json_script) and config from window.EDITOR_CFG. */
(function () {
    'use strict';

    var CFG = window.EDITOR_CFG || {};
    var dataEl = document.getElementById('slidesData');
    var slides = dataEl ? JSON.parse(dataEl.textContent) : [];
    var current = 0;
    var saveTimer = null;

    var stage = document.getElementById('slideStage');
    var scaler = document.getElementById('canvasScaler');
    var formHost = document.getElementById('contentForm');
    var statusEl = document.getElementById('saveStatus');
    var thumbs = Array.prototype.slice.call(document.querySelectorAll('.slide-thumb-wrapper'));
    var chatEl = document.getElementById('chatMessages');
    var chatLog = document.getElementById('chatLog');
    var aiInput = document.getElementById('aiInput');
    var aiSend = document.getElementById('aiSend');
    var aiBusy = false;
    var history = [];  // [{role, text}] conversation (presentation-scoped)
    var selectedElement = null;  // text element the user clicked on the canvas
    var STYLABLE_CLASS = { 'eyebrow': 'eyebrow', 'page-title': 'heading', 'cover-title': 'heading',
        'page-subtitle': 'subtitle', 'cover-sub': 'subtitle', 'cover-desc': 'description', 'highlight-text': 'highlight',
        'brand': 'title', 'year': 'date', 'big-icon': 'icon', 'cover-foot': 'footer' };
    var EL_LABEL = { heading: 'Başlık', eyebrow: 'Üst etiket', subtitle: 'Alt başlık', highlight: 'Vurgu',
        description: 'Açıklama', visual: 'Görsel', title: 'Sunum başlığı', date: 'Tarih/Yıl', icon: 'İkon', footer: 'Alt bilgi' };

    var IN = 'w-full px-2 py-1.5 border border-[#e2e8f0] rounded-lg text-sm focus:outline-none focus:border-[#3b82f6] focus:ring-1 focus:ring-[#3b82f6]/20';
    var LBL = 'block text-xs font-semibold text-[#475569] mb-1';

    var VISUAL_OPTS = [
        ['dashboard', 'Dashboard (kutular)'], ['bar_chart', 'Bar grafik'],
        ['card_list', 'Kart listesi'], ['timeline', 'Zaman çizelgesi'],
        ['donut', 'Donut'], ['comparison', 'Karşılaştırma'],
        ['icon_grid', 'İkon grid'], ['status_card', 'Durum kartı'],
    ];
    var KIND_OPTS = [['ok', '✓ Başarı'], ['warn', '! Uyarı'], ['risk', '✗ Risk'], ['num', '# Sıra'], ['info', '→ Bilgi']];
    var COLOR_OPTS = [['ok', 'Yeşil'], ['warn', 'Sarı'], ['risk', 'Kırmızı'], ['info', 'Mavi'], ['neutral', 'Nötr']];
    var LEVEL_OPTS = [['ok', 'İyi'], ['warn', 'Orta'], ['risk', 'Risk']];

    // ---------- DOM helper ----------
    function h(tag, opts, kids) {
        var e = document.createElement(tag);
        opts = opts || {};
        if (opts.class) e.className = opts.class;
        if (opts.type) e.type = opts.type;
        if (opts.placeholder) e.placeholder = opts.placeholder;
        if (opts.text != null) e.textContent = opts.text;
        if (opts.html != null) e.innerHTML = opts.html;
        if (opts.rows) e.rows = opts.rows;
        if (opts.min != null) e.min = opts.min;
        if (opts.max != null) e.max = opts.max;
        if (opts.checked) e.checked = true;
        if (opts.title) e.title = opts.title;
        if (opts.on) Object.keys(opts.on).forEach(function (ev) { e.addEventListener(ev, opts.on[ev]); });
        (kids || []).forEach(function (k) { if (k != null) e.appendChild(typeof k === 'string' ? document.createTextNode(k) : k); });
        return e;
    }
    function setStatus(t) { if (statusEl) statusEl.textContent = t; }
    function labeled(label, input) { return h('div', {}, [h('label', { class: LBL, text: label }), input]); }

    function textField(label, value, setter) {
        var inp = h('input', { class: IN, type: 'text', on: { input: function () { setter(inp.value); save(); } } });
        inp.value = value || '';
        return labeled(label, inp);
    }
    function textareaField(label, value, setter) {
        var ta = h('textarea', { class: IN, rows: 2, on: { input: function () { setter(ta.value); save(); } } });
        ta.value = value || '';
        return labeled(label, ta);
    }
    function miniInput(ph, value, setter) {
        var inp = h('input', { class: IN, type: 'text', placeholder: ph, on: { input: function () { setter(inp.value); save(); } } });
        inp.value = value || '';
        return inp;
    }
    function numInput(ph, value, setter) {
        var inp = h('input', { class: IN, type: 'number', min: 0, max: 100, placeholder: ph, on: { input: function () { var n = parseInt(inp.value, 10); setter(isNaN(n) ? 0 : n); save(); } } });
        inp.value = (value != null ? value : '');
        return inp;
    }
    function smallSelect(opts, value, onchange) {
        var sel = h('select', { class: IN, on: { change: function () { onchange(sel.value); } } });
        opts.forEach(function (o) { var op = h('option', { text: o[1] }); op.value = o[0]; if (o[0] === value) op.selected = true; sel.appendChild(op); });
        return sel;
    }
    function selectField(label, opts, value, onchange) { return labeled(label, smallSelect(opts, value, onchange)); }

    function compactSelect(opts, value, onchange) {
        var sel = h('select', { class: 'px-1.5 py-1 border border-[#e2e8f0] rounded text-[11px] bg-white focus:outline-none', on: { change: function () { onchange(sel.value); } } });
        opts.forEach(function (o) { var op = h('option', { text: o[1] }); op.value = o[0]; if (o[0] === value) op.selected = true; sel.appendChild(op); });
        return sel;
    }
    function ensureStyle(c, key) {
        if (!c.styles || typeof c.styles !== 'object') c.styles = {};
        if (!c.styles[key] || typeof c.styles[key] !== 'object') c.styles[key] = {};
        return c.styles[key];
    }
    // Compact size/weight/color controls bound to content.styles[key].
    function styleRow(labelText, c, key) {
        var s = ensureStyle(c, key);
        function setOrDel(prop, v) { if (v) s[prop] = v; else delete s[prop]; save(); }
        var size = compactSelect([['', 'Aa normal'], ['sm', 'Aa küçük'], ['lg', 'Aa büyük'], ['xl', 'Aa çok büyük']], s.size || '', function (v) { setOrDel('size', v); });
        var color = compactSelect([['', 'Renk: vars.'], ['brand', 'Marka'], ['ok', 'Yeşil'], ['warn', 'Sarı'], ['risk', 'Kırmızı'], ['info', 'Mavi']], s.color || '', function (v) { setOrDel('color', v); });
        var cb = h('input', { type: 'checkbox' });
        if (s.weight === 'bold') cb.checked = true;
        cb.addEventListener('change', function () { setOrDel('weight', cb.checked ? 'bold' : ''); });
        var bold = h('label', { class: 'flex items-center gap-1 text-[10px] text-[#475569]' }, [cb, 'Kalın']);
        return h('div', { class: 'flex flex-wrap items-center gap-1.5 pl-1 -mt-1' },
            [h('span', { class: 'text-[10px] text-[#94a3b8] w-full', text: 'Stil — ' + labelText }), size, color, bold]);
    }
    function checkbox(label, value, setter) {
        var cb = h('input', { type: 'checkbox', on: { change: function () { setter(cb.checked); } } });
        if (value) cb.checked = true;
        return h('label', { class: 'flex items-center gap-2 text-xs text-[#475569]' }, [cb, label]);
    }

    // Repeatable list of rows. renderRow(item, idx) -> DOM. makeEmpty() -> new item.
    function repeater(label, items, addLabel, makeEmpty, renderRow) {
        var wrap = h('div', {}, [h('label', { class: LBL, text: label })]);
        var list = h('div', { class: 'space-y-2' });
        function redraw() {
            list.innerHTML = '';
            items.forEach(function (item, idx) {
                var del = h('button', {
                    class: 'shrink-0 text-rose-400 hover:text-rose-600 hover:bg-rose-50 rounded p-1', type: 'button', title: 'Sil',
                    html: '<span class="material-symbols-outlined text-[16px]">close</span>',
                    on: { click: function () { items.splice(idx, 1); redraw(); save(); } }
                });
                list.appendChild(h('div', { class: 'flex items-start gap-2 bg-[#f8fafc] border border-[#e2e8f0] rounded-lg p-2' },
                    [h('div', { class: 'flex-1 space-y-1' }, [renderRow(item, idx)]), del]));
            });
        }
        wrap.appendChild(list);
        wrap.appendChild(h('button', {
            class: 'mt-2 text-xs text-[#2563eb] font-medium hover:underline', type: 'button', text: '+ ' + addLabel,
            on: { click: function () { items.push(makeEmpty()); redraw(); save(); } }
        }));
        redraw();
        return wrap;
    }

    // ---------- save (debounced, index-aware) ----------
    // pendingIdx = slide index with unsaved debounced edits (-1 = none).
    // savingCount = commits currently in flight. Both feed the exit guard so we
    // never navigate away while an edit is still un-persisted.
    var pendingIdx = -1;
    var savingCount = 0;
    var leaving = false;  // suppress the exit guard for our own programmatic reloads
    // Flush pending edits, then navigate (the reorder/agent action already
    // persisted its own change server-side; this just rescues an open İçerik edit).
    function navigateTo(url) { leaving = true; flushSave(); window.location.href = url; }
    function save() {
        pendingIdx = current;  // bind the edit to the slide it was made on
        setStatus('Kaydediliyor…');
        clearTimeout(saveTimer);
        saveTimer = setTimeout(flushSave, 600);
    }
    // Commit any pending debounced edit immediately (used before slide switch /
    // page exit so a stale `current` can never clobber the wrong slide).
    function flushSave() {
        clearTimeout(saveTimer);
        saveTimer = null;
        if (pendingIdx < 0) return;
        var idx = pendingIdx;
        pendingIdx = -1;
        commit(idx);
    }
    function hasUnsaved() { return pendingIdx >= 0 || saveTimer || savingCount > 0; }
    function commit(idx) {
        var s = slides[idx];
        if (!s) { setStatus('Slayt bulunamadı'); return; }
        var url = CFG.updateUrlTpl.replace(CFG.placeholderId, s.id);
        savingCount++;
        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CFG.csrf },
            body: JSON.stringify({ heading: s.heading, slide_type: s.slide_type, content: s.content })
        }).then(function (r) {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.json();
        }).then(function (d) {
            if (d && d.html) {
                var es = stage && stage.querySelector('.editor-slide[data-index="' + idx + '"]');
                if (es) es.innerHTML = d.html;
                var th = thumbs[idx] && thumbs[idx].querySelector('.thumb-stage');
                if (th) th.innerHTML = d.html;
            }
            setStatus('Kaydedildi');
        }).catch(function () { setStatus('Kayıt hatası'); })
          .then(function () { savingCount--; });
    }

    // ---------- form builders ----------
    function defaultData(t) {
        switch (t) {
            case 'dashboard': return { cells: [] };
            case 'bar_chart': return { bars: [] };
            case 'card_list': return { cards: [] };
            case 'timeline': return { events: [] };
            case 'donut': return { percent: 50, center: '', label: '' };
            case 'comparison': return { bars: [] };
            case 'icon_grid': return { cells: [] };
            case 'status_card': return { title: '', level: 'ok', badge: '', text: '', tags: [] };
            default: return {};
        }
    }

    function buildForm() {
        var s = slides[current];
        if (!s) { formHost.innerHTML = ''; return; }
        // Guard against null/non-object/array content so setters never crash.
        s.content = (s.content && typeof s.content === 'object' && !Array.isArray(s.content)) ? s.content : {};
        formHost.innerHTML = '';
        formHost.appendChild(textField('Başlık', s.heading, function (v) { s.heading = v; }));
        formHost.appendChild(styleRow('Başlık', s.content, 'heading'));
        formHost.appendChild(selectField('Slayt tipi',
            [['cover', 'Kapak'], ['split', 'İçerik'], ['closing', 'Kapanış']], s.slide_type,
            function (v) { s.slide_type = v; save(); buildForm(); }));
        if (s.slide_type === 'cover') buildCover(s.content);
        else if (s.slide_type === 'closing') buildClosing(s.content);
        else buildSplit(s.content);
        formHost.appendChild(regenButton(s));
    }

    function buildCover(c) {
        formHost.appendChild(textField('Eyebrow (üst etiket)', c.eyebrow, function (v) { c.eyebrow = v; }));
        formHost.appendChild(styleRow('Eyebrow', c, 'eyebrow'));
        formHost.appendChild(textField('Alt başlık', c.subtitle, function (v) { c.subtitle = v; }));
        formHost.appendChild(styleRow('Alt başlık', c, 'subtitle'));
        formHost.appendChild(textareaField('Açıklama', c.description, function (v) { c.description = v; }));
        formHost.appendChild(styleRow('Açıklama', c, 'description'));
        formHost.appendChild(textField('İkon (fa-...)', c.icon, function (v) { c.icon = v; }));
        formHost.appendChild(textField('Tarih / Yıl', c.date, function (v) { c.date = v; }));
        formHost.appendChild(textField('Alt bilgi', c.footer, function (v) { c.footer = v; }));
    }

    function buildClosing(c) {
        formHost.appendChild(textField('Eyebrow', c.eyebrow, function (v) { c.eyebrow = v; }));
        formHost.appendChild(styleRow('Eyebrow', c, 'eyebrow'));
        formHost.appendChild(textField('Alt başlık', c.subtitle, function (v) { c.subtitle = v; }));
        formHost.appendChild(styleRow('Alt başlık', c, 'subtitle'));
        formHost.appendChild(textareaField('Açıklama', c.description, function (v) { c.description = v; }));
        formHost.appendChild(styleRow('Açıklama', c, 'description'));
        formHost.appendChild(textField('İkon (fa-...)', c.icon, function (v) { c.icon = v; }));
        c.stats = c.stats || [];
        formHost.appendChild(repeater('İstatistikler', c.stats, 'İstatistik ekle',
            function () { return { value: '', label: '' }; },
            function (it) { return h('div', { class: 'space-y-1' }, [miniInput('Değer', it.value, function (v) { it.value = v; }), miniInput('Etiket', it.label, function (v) { it.label = v; })]); }));
        formHost.appendChild(textField('Alt bilgi', c.footer, function (v) { c.footer = v; }));
    }

    function buildSplit(c) {
        formHost.appendChild(textField('Eyebrow (bölüm etiketi)', c.eyebrow, function (v) { c.eyebrow = v; }));
        formHost.appendChild(styleRow('Eyebrow', c, 'eyebrow'));
        formHost.appendChild(textField('Alt başlık', c.subtitle, function (v) { c.subtitle = v; }));
        formHost.appendChild(styleRow('Alt başlık', c, 'subtitle'));
        c.points = c.points || [];
        formHost.appendChild(repeater('Maddeler (check-list)', c.points, 'Madde ekle',
            function () { return { kind: 'ok', label: '', text: '' }; },
            function (it) {
                return h('div', { class: 'space-y-1' }, [
                    smallSelect(KIND_OPTS, it.kind, function (v) { it.kind = v; save(); }),
                    miniInput('Kalın başlık', it.label, function (v) { it.label = v; }),
                    miniInput('Açıklama', it.text, function (v) { it.text = v; })
                ]);
            }));
        formHost.appendChild(textareaField('Vurgu kutusu (highlight)', c.highlight, function (v) { c.highlight = v; }));
        formHost.appendChild(styleRow('Vurgu', c, 'highlight'));

        c.visual = c.visual || { type: 'dashboard', data: defaultData('dashboard') };
        var vbox = h('div', { class: 'border-t border-[#e2e8f0] pt-3 mt-1 space-y-2' }, [
            h('label', { class: LBL, text: 'Sağ panel görseli' }),
            smallSelect(VISUAL_OPTS, c.visual.type, function (v) {
                if (v === c.visual.type) return;
                var hasData = c.visual.data && Object.keys(c.visual.data).length > 0;
                if (hasData && !confirm('Görsel tipini değiştirmek mevcut görsel verisini sıfırlar. Devam edilsin mi?')) {
                    buildForm();  // user cancelled → re-render resets the dropdown
                    return;
                }
                c.visual.type = v; c.visual.data = defaultData(v); save(); buildForm();
            })
        ]);
        vbox.appendChild(buildVisualData(c.visual));
        formHost.appendChild(vbox);
    }

    function buildVisualData(visual) {
        var d = visual.data = visual.data || defaultData(visual.type);
        var box = h('div', { class: 'space-y-2' });
        switch (visual.type) {
            case 'dashboard':
                d.cells = d.cells || [];
                box.appendChild(repeater('Kutular', d.cells, 'Kutu ekle', function () { return { value: '', label: '' }; },
                    function (it) { return h('div', { class: 'space-y-1' }, [miniInput('Değer (ör. %92)', it.value, function (v) { it.value = v; }), miniInput('Etiket', it.label, function (v) { it.label = v; })]); }));
                break;
            case 'bar_chart':
            case 'comparison':
                d.bars = d.bars || [];
                box.appendChild(repeater('Çubuklar', d.bars, 'Çubuk ekle', function () { return { label: '', value: 50, display: '' }; },
                    function (it) { return h('div', { class: 'space-y-1' }, [miniInput('Etiket', it.label, function (v) { it.label = v; }), numInput('Değer 0-100', it.value, function (v) { it.value = v; }), miniInput('Gösterim (ör. %85)', it.display, function (v) { it.display = v; })]); }));
                break;
            case 'card_list':
                d.cards = d.cards || [];
                box.appendChild(repeater('Kartlar', d.cards, 'Kart ekle', function () { return { icon: 'fa-circle', title: '', text: '', color: 'info' }; },
                    function (it) { return h('div', { class: 'space-y-1' }, [miniInput('İkon (fa-...)', it.icon, function (v) { it.icon = v; }), miniInput('Başlık', it.title, function (v) { it.title = v; }), miniInput('Açıklama', it.text, function (v) { it.text = v; }), smallSelect(COLOR_OPTS, it.color, function (v) { it.color = v; save(); })]); }));
                break;
            case 'timeline':
                d.events = d.events || [];
                box.appendChild(repeater('Olaylar', d.events, 'Olay ekle', function () { return { date: '', label: '', tag: '' }; },
                    function (it) { return h('div', { class: 'space-y-1' }, [miniInput('Tarih', it.date, function (v) { it.date = v; }), miniInput('Etiket', it.label, function (v) { it.label = v; }), miniInput('Rozet', it.tag, function (v) { it.tag = v; })]); }));
                break;
            case 'donut':
                box.appendChild(numInput('Yüzde 0-100', d.percent, function (v) { d.percent = v; }));
                box.appendChild(miniInput('Orta yazı (ör. %72)', d.center, function (v) { d.center = v; }));
                box.appendChild(miniInput('Etiket', d.label, function (v) { d.label = v; }));
                break;
            case 'icon_grid':
                d.cells = d.cells || [];
                box.appendChild(repeater('Hücreler', d.cells, 'Hücre ekle', function () { return { icon: 'fa-check', label: '', done: false }; },
                    function (it) { return h('div', { class: 'space-y-1' }, [miniInput('İkon (fa-...)', it.icon, function (v) { it.icon = v; }), miniInput('Etiket', it.label, function (v) { it.label = v; }), checkbox('Tamamlandı', it.done, function (v) { it.done = v; save(); })]); }));
                break;
            case 'status_card':
                box.appendChild(miniInput('Başlık', d.title, function (v) { d.title = v; }));
                box.appendChild(smallSelect(LEVEL_OPTS, d.level, function (v) { d.level = v; save(); }));
                box.appendChild(miniInput('Rozet', d.badge, function (v) { d.badge = v; }));
                box.appendChild(miniInput('Açıklama', d.text, function (v) { d.text = v; }));
                d.tags = d.tags || [];
                box.appendChild(repeater('Etiketler', d.tags, 'Etiket ekle', function () { return ''; },
                    function (item, idx) { return miniInput('Etiket', d.tags[idx], function (v) { d.tags[idx] = v; }); }));
                break;
        }
        return box;
    }

    function regenButton(s) {
        var btn = h('button', {
            class: 'w-full px-3 py-2 border border-[#e2e8f0] rounded-lg text-sm text-[#475569] hover:bg-[#f8fafc] flex items-center justify-center gap-2', type: 'button',
            html: '<span class="material-symbols-outlined text-[16px]">refresh</span> Bu slaytı AI ile yeniden üret'
        });
        btn.addEventListener('click', function () {
            if (!confirm('Bu slaytın içeriği AI ile yeniden üretilsin mi? Mevcut içerik değişecek.')) return;
            var f = document.createElement('form');
            f.method = 'post';
            f.action = CFG.regenerateUrlTpl.replace(CFG.placeholderId, s.id);
            f.innerHTML = '<input type="hidden" name="csrfmiddlewaretoken" value="' + CFG.csrf + '">' +
                '<input type="hidden" name="next" value="' + CFG.editorUrl + '">';
            document.body.appendChild(f);
            f.submit();
        });
        return h('div', { class: 'border-t border-[#e2e8f0] pt-3 mt-3' }, [btn]);
    }

    // ---------- selection ----------
    function highlightThumb(t, active) {
        var card = t.querySelector('.slide-thumb');
        var num = t.querySelector('.thumb-num');
        if (!card) return;
        if (active) {
            card.classList.add('ring-2', 'ring-[#3b82f6]'); card.classList.remove('ring-1', 'ring-[#e2e8f0]');
            if (num) { num.classList.add('font-bold', 'text-[#3b82f6]'); num.classList.remove('font-medium', 'text-[#c0cad8]'); }
        } else {
            card.classList.remove('ring-2', 'ring-[#3b82f6]'); card.classList.add('ring-1', 'ring-[#e2e8f0]');
            if (num) { num.classList.remove('font-bold', 'text-[#3b82f6]'); num.classList.add('font-medium', 'text-[#c0cad8]'); }
        }
    }
    // ---------- canvas element selection (click a text to target it) ----------
    function updateFocusInfo() {
        var info = document.getElementById('focusInfo');
        if (!info) return;
        if (selectedElement) {
            info.classList.remove('hidden');
            var s = info.querySelector('[data-el]');
            if (s) s.textContent = EL_LABEL[selectedElement] || selectedElement;
        } else {
            info.classList.add('hidden');
        }
    }
    function clearElementSel() {
        selectedElement = null;
        if (stage) stage.querySelectorAll('.el-selected').forEach(function (e) { e.classList.remove('el-selected'); });
        updateFocusInfo();
    }
    function pickElement(node, key) {
        if (stage) stage.querySelectorAll('.el-selected').forEach(function (e) { e.classList.remove('el-selected'); });
        node.classList.add('el-selected');
        selectedElement = key;
        updateFocusInfo();
    }

    function selectSlide(i) {
        if (i < 0 || i >= slides.length) return;
        flushSave();  // persist the outgoing slide's pending edit before switching
        current = i;
        clearElementSel();  // element focus is per-slide
        // Conversation persists across slide switches — the agent is presentation-scoped
        // and we send the current slide index with each message.
        if (stage) stage.querySelectorAll('.editor-slide').forEach(function (es, idx) { es.classList.toggle('active', idx === i); });
        thumbs.forEach(function (t, idx) { highlightThumb(t, idx === i); });
        buildForm();
    }

    // ---------- reorder ----------
    var dragEl = null;
    function commitReorder() {
        var ids = Array.prototype.slice.call(document.querySelectorAll('.slide-thumb-wrapper'))
            .map(function (t) { return t.getAttribute('data-slide-id'); });
        setStatus('Kaydediliyor…');
        // Keep the current selection across the reload that follows.
        try { sessionStorage.setItem('slideai_sel', String(current)); } catch (e) {}
        fetch(CFG.reorderUrl, {
            method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CFG.csrf },
            body: JSON.stringify({ slide_ids: ids })
        }).then(function (r) {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            navigateTo(CFG.editorUrl);  // reload only on success
        }).catch(function () { setStatus('Sıralama kaydedilemedi'); });
    }

    // ---------- AI assistant ----------
    function addBubble(role, text) {
        var host = chatLog || chatEl;
        if (!host) return null;
        var bubble, wrap;
        if (role === 'user') {
            bubble = h('div', { class: 'chat-user rounded-2xl rounded-tr-none p-3 text-sm max-w-[85%]', text: text });
            wrap = h('div', { class: 'flex justify-end' }, [bubble]);
        } else {
            var av = h('div', { class: 'w-7 h-7 rounded-lg bg-gradient-to-br from-[#3b82f6] to-[#2563eb] text-white flex items-center justify-center shrink-0', html: '<span class="material-symbols-outlined text-[16px]">auto_awesome</span>' });
            bubble = h('div', { class: 'bg-[#f8fafc] border border-[#e2e8f0] rounded-2xl rounded-tl-none p-3 text-sm text-[#334155]', text: text });
            wrap = h('div', { class: 'flex gap-2' }, [av, bubble]);
        }
        host.appendChild(wrap);
        if (chatEl) chatEl.scrollTop = chatEl.scrollHeight;
        return bubble;
    }

    function sendInstruction(text) {
        text = (text || '').trim();
        if (!text || aiBusy) return;
        aiBusy = true;
        if (aiSend) aiSend.disabled = true;
        addBubble('user', text);
        if (aiInput) aiInput.value = '';
        var thinking = addBubble('assistant', 'Düşünüyorum…');
        var priorHistory = history.slice(-8);
        fetch(CFG.agentUrl, {
            method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CFG.csrf },
            body: JSON.stringify({ instruction: text, history: priorHistory, current_index: current, selected_element: selectedElement })
        }).then(function (r) { return r.json(); }).then(function (d) {
            var msg = d.message || 'Tamam.';
            if (thinking) thinking.textContent = msg;
            history.push({ role: 'user', text: text });
            history.push({ role: 'assistant', text: msg });
            if (history.length > 16) history = history.slice(-16);
            if (d.structural) {
                // add/delete/move/theme changed the deck structure → full reload
                // (preserve selection + message across the reload).
                try {
                    sessionStorage.setItem('slideai_agent_msg', msg);
                    sessionStorage.setItem('slideai_sel', String(current));
                } catch (e) {}
                setTimeout(function () { navigateTo(CFG.editorUrl); }, 700);
            } else if (d.updates && d.updates.length) {
                // content-only edits → swap the affected slides in place, no reload,
                // so the slide sidebar keeps its position.
                d.updates.forEach(function (up) {
                    var es = stage && stage.querySelector('.editor-slide[data-index="' + up.index + '"]');
                    if (es) es.innerHTML = up.html;
                    var th = thumbs[up.index] && thumbs[up.index].querySelector('.thumb-stage');
                    if (th) th.innerHTML = up.html;
                    if (slides[up.index]) {
                        slides[up.index].heading = up.heading;
                        slides[up.index].slide_type = up.slide_type;
                        slides[up.index].content = up.content;
                    }
                });
                // Rebuild the İçerik form unconditionally so its inputs/setters
                // rebind to the fresh content object (a hidden, stale form would
                // otherwise autosave OLD content and silently revert the AI edit).
                buildForm();
            }
        }).catch(function () {
            if (thinking) thinking.textContent = 'Bir hata oluştu, tekrar dener misin?';
        }).then(function () {
            aiBusy = false;
            if (aiSend) aiSend.disabled = false;
            if (chatEl) chatEl.scrollTop = chatEl.scrollHeight;
        });
    }

    // ---------- init ----------
    function init() {
        thumbs.forEach(function (t, i) {
            t.addEventListener('click', function (e) { if (e.target.closest('.delete-slide-btn')) return; selectSlide(i); });
            t.addEventListener('dragstart', function () { dragEl = t; t.classList.add('dragging'); });
            t.addEventListener('dragend', function () { t.classList.remove('dragging'); thumbs.forEach(function (x) { x.classList.remove('drag-over'); }); });
            t.addEventListener('dragover', function (e) { e.preventDefault(); if (t !== dragEl) t.classList.add('drag-over'); });
            t.addEventListener('dragleave', function () { t.classList.remove('drag-over'); });
            t.addEventListener('drop', function (e) {
                e.preventDefault(); t.classList.remove('drag-over');
                if (dragEl && t !== dragEl) {
                    var list = Array.prototype.slice.call(document.querySelectorAll('.slide-thumb-wrapper'));
                    if (list.indexOf(dragEl) < list.indexOf(t)) t.after(dragEl); else t.before(dragEl);
                    commitReorder();
                }
            });
        });

        document.querySelectorAll('.delete-slide-btn').forEach(function (btn) {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                if (confirm('Bu slaytı silmek istediğinize emin misiniz?')) {
                    var f = document.getElementById('deleteForm-' + btn.dataset.slideId);
                    if (f) f.submit();
                }
            });
        });

        // tabs
        var tabBtns = document.querySelectorAll('.tab-btn');
        var tabPanels = document.querySelectorAll('.tab-panel');
        var tabMap = { assistant: 'tab-assistant', content: 'tab-content', design: 'tab-design' };
        tabBtns.forEach(function (btn) {
            btn.addEventListener('click', function () {
                tabBtns.forEach(function (b) {
                    b.classList.remove('border-b-2', 'border-[#3b82f6]', 'text-[#3b82f6]', 'font-semibold');
                    b.classList.add('text-[#64748b]', 'font-medium');
                });
                btn.classList.add('border-b-2', 'border-[#3b82f6]', 'text-[#3b82f6]', 'font-semibold');
                btn.classList.remove('text-[#64748b]', 'font-medium');
                tabPanels.forEach(function (p) { p.classList.add('hidden'); });
                var panel = document.getElementById(tabMap[btn.dataset.tab]);
                if (panel) panel.classList.remove('hidden');
                // Always rebuild the content form from the live slides[] model so it
                // can never show/save a stale snapshot (e.g. after an AI edit).
                if (btn.dataset.tab === 'content') buildForm();
            });
        });

        // zoom
        var zoomLevels = [50, 75, 100, 125, 150];
        var zoomIndex = 2;
        var zoomDisplay = document.getElementById('zoomLevel');
        function applyZoom() {
            if (!scaler) return;
            scaler.style.transform = 'scale(' + (zoomLevels[zoomIndex] / 100) + ')';
            scaler.style.transformOrigin = 'center center';
            if (zoomDisplay) zoomDisplay.textContent = zoomLevels[zoomIndex] + '%';
        }
        var zi = document.getElementById('zoomIn'), zo = document.getElementById('zoomOut');
        if (zi) zi.addEventListener('click', function () { if (zoomIndex < zoomLevels.length - 1) { zoomIndex++; applyZoom(); } });
        if (zo) zo.addEventListener('click', function () { if (zoomIndex > 0) { zoomIndex--; applyZoom(); } });
        applyZoom();

        // title save
        var titleInput = document.getElementById('presentationTitle');
        if (titleInput) {
            titleInput.addEventListener('blur', function () {
                var t = titleInput.value.trim();
                if (!t) return;
                setStatus('Kaydediliyor…');
                fetch(CFG.titleUrl, {
                    method: 'POST', headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CFG.csrf },
                    body: JSON.stringify({ title: t })
                }).then(function (r) {
                    if (!r.ok) throw new Error('HTTP ' + r.status);
                    setStatus('Kaydedildi');
                }).catch(function () { setStatus('Başlık kaydedilemedi'); });
            });
        }

        // Canvas: click a text element to target it (deterministic element focus)
        if (stage) stage.addEventListener('click', function (e) {
            for (var cls in STYLABLE_CLASS) {
                var node = e.target.closest('.' + cls);
                if (node && stage.contains(node)) { pickElement(node, STYLABLE_CLASS[cls]); return; }
            }
            // right-panel visual (chart/graphic/metrics) → select the whole visual
            var vis = e.target.closest('.split-right');
            if (vis && stage.contains(vis)) { pickElement(vis.querySelector('.floating-card') || vis, 'visual'); return; }
        });
        var fc = document.getElementById('focusClear');
        if (fc) fc.addEventListener('click', clearElementSel);

        // AI assistant wiring
        if (aiSend) aiSend.addEventListener('click', function () { sendInstruction(aiInput ? aiInput.value : ''); });
        if (aiInput) aiInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendInstruction(aiInput.value); }
        });
        document.querySelectorAll('.ai-chip').forEach(function (chip) {
            chip.addEventListener('click', function () { sendInstruction(chip.getAttribute('data-instruction')); });
        });

        // keyboard slide nav
        document.addEventListener('keydown', function (e) {
            if (e.target.isContentEditable || e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;
            if (e.key === 'ArrowUp') { e.preventDefault(); selectSlide(current - 1); }
            if (e.key === 'ArrowDown') { e.preventDefault(); selectSlide(current + 1); }
        });

        if (slides.length) selectSlide(0);

        // After an agent-triggered reload, restore the previously selected slide
        // (so "bu sayfa" keeps meaning the same slide) and re-show the last message.
        try {
            var sel = sessionStorage.getItem('slideai_sel');
            if (sel !== null) {
                sessionStorage.removeItem('slideai_sel');
                var si = parseInt(sel, 10);
                if (!isNaN(si) && si >= 0 && si < slides.length) selectSlide(si);
            }
            var pending = sessionStorage.getItem('slideai_agent_msg');
            if (pending) { sessionStorage.removeItem('slideai_agent_msg'); addBubble('assistant', pending); }
        } catch (e) { /* ignore */ }

        // Exit guard: flush any debounced edit and warn before leaving while a
        // save is still pending or in flight, so nothing is silently lost.
        window.addEventListener('beforeunload', function (e) {
            if (leaving) return;  // our own reorder/agent reload — don't prompt
            if (saveTimer) flushSave();  // kick the pending commit now
            if (hasUnsaved()) {
                e.preventDefault();
                e.returnValue = '';  // triggers the browser "leave / stay" prompt
                return '';
            }
        });
    }

    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
    else init();
})();

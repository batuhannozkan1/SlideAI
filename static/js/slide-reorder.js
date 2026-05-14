document.addEventListener('DOMContentLoaded', function() {
    const grid = document.querySelector('.slide-grid');
    if (!grid || !grid.dataset.reorderUrl) return;

    let draggedEl = null;

    grid.querySelectorAll('.slide-card[draggable="true"]').forEach(function(card) {
        card.addEventListener('dragstart', function(e) {
            draggedEl = this;
            this.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
        });

        card.addEventListener('dragend', function() {
            this.classList.remove('dragging');
            grid.querySelectorAll('.slide-card').forEach(function(c) {
                c.classList.remove('drag-over');
            });
            draggedEl = null;
        });

        card.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            if (this !== draggedEl && !this.classList.contains('slide-card--add')) {
                this.classList.add('drag-over');
            }
        });

        card.addEventListener('dragleave', function() {
            this.classList.remove('drag-over');
        });

        card.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            if (draggedEl && this !== draggedEl && !this.classList.contains('slide-card--add')) {
                var allCards = Array.from(grid.querySelectorAll('.slide-card[data-slide-id]'));
                var fromIndex = allCards.indexOf(draggedEl);
                var toIndex = allCards.indexOf(this);
                if (fromIndex < toIndex) {
                    this.after(draggedEl);
                } else {
                    this.before(draggedEl);
                }
                saveOrder();
            }
        });
    });

    function saveOrder() {
        var cards = grid.querySelectorAll('.slide-card[data-slide-id]');
        var slideIds = Array.from(cards).map(function(c) { return c.dataset.slideId; });

        fetch(grid.dataset.reorderUrl, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': window.CSRF_TOKEN || '',
            },
            body: JSON.stringify({slide_ids: slideIds}),
        });
    }
});

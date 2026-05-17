document.addEventListener('DOMContentLoaded', function() {
    var wrapper = document.getElementById('presentWrapper');
    if (!wrapper) return;

    var slides = wrapper.querySelectorAll('.present-slide');
    var counter = document.getElementById('slideCounter');
    var progress = document.getElementById('slideProgress');
    var exitBtn = document.getElementById('exitPresent');
    var prevBtn = document.getElementById('prevSlide');
    var nextBtn = document.getElementById('nextSlide');
    var current = 0;

    function showSlide(index) {
        if (index < 0 || index >= slides.length) return;
        slides[current].classList.remove('active');
        current = index;
        slides[current].classList.add('active');
        if (counter) counter.textContent = (current + 1) + ' / ' + slides.length;
        if (progress) progress.style.width = ((current + 1) / slides.length * 100) + '%';
    }

    function next() { showSlide(current + 1); }
    function prev() { showSlide(current - 1); }

    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowRight' || e.key === ' ') { e.preventDefault(); next(); }
        else if (e.key === 'ArrowLeft') { e.preventDefault(); prev(); }
        else if (e.key === 'Escape') {
            if (exitBtn) window.location.href = exitBtn.href;
            else window.history.back();
        }
    });

    wrapper.addEventListener('click', function(e) {
        var rect = wrapper.getBoundingClientRect();
        if (e.clientX > rect.width / 2) next();
        else prev();
    });

    if (prevBtn) prevBtn.addEventListener('click', function(e) { e.stopPropagation(); prev(); });
    if (nextBtn) nextBtn.addEventListener('click', function(e) { e.stopPropagation(); next(); });

    var touchStartX = 0;
    wrapper.addEventListener('touchstart', function(e) {
        touchStartX = e.changedTouches[0].screenX;
    }, {passive: true});
    wrapper.addEventListener('touchend', function(e) {
        var diff = e.changedTouches[0].screenX - touchStartX;
        if (Math.abs(diff) > 50) {
            if (diff < 0) next();
            else prev();
        }
    }, {passive: true});

    showSlide(0);
});

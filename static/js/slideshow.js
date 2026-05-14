document.addEventListener('DOMContentLoaded', function() {
    const wrapper = document.querySelector('.present-wrapper');
    if (!wrapper) return;

    const slides = wrapper.querySelectorAll('.present-slide');
    const counter = document.getElementById('slideCounter');
    const progress = document.getElementById('slideProgress');
    const exitBtn = document.getElementById('exitPresent');
    let current = 0;

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
        else if (e.key === 'Escape') { window.history.back(); }
    });

    wrapper.addEventListener('click', function(e) {
        if (e.target.closest('.present-controls')) return;
        var rect = wrapper.getBoundingClientRect();
        if (e.clientX > rect.width / 2) next();
        else prev();
    });

    if (exitBtn) {
        exitBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            window.history.back();
        });
    }

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

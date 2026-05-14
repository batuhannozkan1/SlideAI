document.addEventListener("DOMContentLoaded", function () {
    var csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
    if (csrfToken) {
        window.CSRF_TOKEN = csrfToken.value;
    }

    // Auto-dismiss alerts after 5 seconds
    document.querySelectorAll('.auto-dismiss').forEach(function(el) {
        setTimeout(function() {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(el);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });
});

// Toast notification utility
function showToast(message, type) {
    type = type || 'info';
    var container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    var toast = document.createElement('div');
    toast.className = 'alert alert-' + type + ' alert-dismissible fade show mb-2';
    toast.style.minWidth = '250px';
    toast.innerHTML = message + '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>';
    container.appendChild(toast);

    setTimeout(function() {
        var bsAlert = bootstrap.Alert.getOrCreateInstance(toast);
        if (bsAlert) bsAlert.close();
    }, 4000);
}

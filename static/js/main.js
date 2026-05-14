document.addEventListener("DOMContentLoaded", function () {
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
    if (csrfToken) {
        window.CSRF_TOKEN = csrfToken.value;
    }
});

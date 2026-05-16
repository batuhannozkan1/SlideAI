document.addEventListener("DOMContentLoaded", function () {
    // CSRF token
    var csrfEl = document.querySelector("[name=csrfmiddlewaretoken]");
    if (csrfEl) window.CSRF_TOKEN = csrfEl.value;

    // Elements
    var sidebar = document.getElementById("sidebar");
    var overlay = document.getElementById("sidebarOverlay");
    var openBtn = document.getElementById("sidebarOpen");
    var closeBtn = document.getElementById("sidebarClose");
    var toggleBtn = document.getElementById("sidebarToggle");
    var mainWrapper = document.getElementById("mainWrapper");
    var topbarLogo = document.getElementById("topbarLogo");
    var lgBreakpoint = 1024;

    function isDesktop() {
        return window.innerWidth >= lgBreakpoint;
    }

    // Mobile sidebar (overlay mode)
    function openMobileSidebar() {
        if (sidebar) sidebar.classList.add("sidebar-open");
        if (overlay) overlay.classList.remove("hidden");
    }
    function closeMobileSidebar() {
        if (sidebar) sidebar.classList.remove("sidebar-open");
        if (overlay) overlay.classList.add("hidden");
    }

    // Desktop sidebar (collapse mode)
    function collapseSidebar() {
        if (sidebar) sidebar.classList.add("sidebar-collapsed");
        if (mainWrapper) mainWrapper.classList.add("sidebar-collapsed");
        if (openBtn) openBtn.classList.remove("hidden");
        if (topbarLogo) topbarLogo.classList.remove("hidden");
    }
    function expandSidebar() {
        if (sidebar) sidebar.classList.remove("sidebar-collapsed");
        if (mainWrapper) mainWrapper.classList.remove("sidebar-collapsed");
        if (openBtn) openBtn.classList.add("hidden");
        if (topbarLogo) topbarLogo.classList.add("hidden");
    }

    // Burger button — opens sidebar (mobile: overlay, desktop: expand)
    if (openBtn) {
        openBtn.addEventListener("click", function () {
            if (isDesktop()) {
                expandSidebar();
            } else {
                openMobileSidebar();
            }
        });
    }

    // Close button inside sidebar (mobile only)
    if (closeBtn) {
        closeBtn.addEventListener("click", closeMobileSidebar);
    }

    // Toggle button (menu_open) inside sidebar — collapses on desktop, closes on mobile
    if (toggleBtn) {
        toggleBtn.addEventListener("click", function () {
            if (isDesktop()) {
                collapseSidebar();
            } else {
                closeMobileSidebar();
            }
        });
    }

    // Overlay click closes mobile sidebar
    if (overlay) overlay.addEventListener("click", closeMobileSidebar);

    // Update burger + logo visibility based on screen and sidebar state
    function updateBurgerVisibility() {
        if (!openBtn) return;
        if (isDesktop()) {
            var isCollapsed = sidebar && sidebar.classList.contains("sidebar-collapsed");
            if (isCollapsed) {
                openBtn.classList.remove("hidden");
                if (topbarLogo) topbarLogo.classList.remove("hidden");
            } else {
                openBtn.classList.add("hidden");
                if (topbarLogo) topbarLogo.classList.add("hidden");
            }
        } else {
            openBtn.classList.remove("hidden");
            if (topbarLogo) topbarLogo.classList.remove("hidden");
        }
    }

    updateBurgerVisibility();
    window.addEventListener("resize", updateBurgerVisibility);

    // Dropdown toggle
    document.querySelectorAll("[data-dropdown]").forEach(function (trigger) {
        var target = document.getElementById(trigger.dataset.dropdown);
        if (!target) return;
        trigger.addEventListener("click", function (e) {
            e.stopPropagation();
            target.classList.toggle("hidden");
        });
    });
    document.addEventListener("click", function () {
        document.querySelectorAll(".dropdown-menu:not(.hidden)").forEach(function (el) {
            el.classList.add("hidden");
        });
    });

    // Auto-dismiss messages
    document.querySelectorAll("[data-auto-dismiss]").forEach(function (el) {
        setTimeout(function () {
            el.classList.add("toast-exit");
            setTimeout(function () { el.remove(); }, 300);
        }, 5000);
    });
});

// Toast notification utility
function showToast(message, type) {
    type = type || "info";
    var colors = {
        success: "bg-emerald-50 text-emerald-800 border-emerald-200",
        error: "bg-red-50 text-red-800 border-red-200",
        warning: "bg-amber-50 text-amber-800 border-amber-200",
        info: "bg-blue-50 text-blue-800 border-blue-200",
    };
    var container = document.getElementById("toastContainer");
    if (!container) {
        container = document.createElement("div");
        container.id = "toastContainer";
        container.className = "fixed top-4 right-4 z-[9999] flex flex-col gap-2";
        document.body.appendChild(container);
    }
    var toast = document.createElement("div");
    toast.className = "px-4 py-3 rounded-lg border text-sm shadow-sm toast-enter " + (colors[type] || colors.info);
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(function () {
        toast.classList.add("toast-exit");
        setTimeout(function () { toast.remove(); }, 300);
    }, 4000);
}

// ClassADDA global UI interactions

document.addEventListener("DOMContentLoaded", function () {
    applyRevealAnimations();
    applySubmitLoadingState();
    applyAnimatedCounters();
    applyActiveNavigation();
});

function applyRevealAnimations() {
    const animatedSelectors = [
        ".ca-panel",
        ".ca-course-card",
        ".ca-stat-card",
        ".ca-dashboard-card",
        ".ca-feature-card",
        ".ca-list-item",
        ".ca-auth-card",
        ".ca-submission-card",
        ".ca-grade-card",
        ".ca-note-box",
        ".ca-empty-state"
    ];

    const elements = document.querySelectorAll(animatedSelectors.join(","));

    elements.forEach(function (element, index) {
        element.classList.add("ca-animate");
        element.style.transitionDelay = Math.min(index * 45, 260) + "ms";
    });

    if (!("IntersectionObserver" in window)) {
        elements.forEach(function (element) {
            element.classList.add("ca-visible");
        });
        return;
    }

    const observer = new IntersectionObserver(
        function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add("ca-visible");
                    observer.unobserve(entry.target);
                }
            });
        },
        {
            threshold: 0.12
        }
    );

    elements.forEach(function (element) {
        observer.observe(element);
    });
}

function applySubmitLoadingState() {
    const forms = document.querySelectorAll("form");

    forms.forEach(function (form) {
        form.addEventListener("submit", function () {
            const submitButton = form.querySelector("button[type='submit'], input[type='submit']");

            if (!submitButton) {
                return;
            }

            submitButton.classList.add("ca-btn-loading");

            if (submitButton.tagName.toLowerCase() === "button") {
                submitButton.dataset.originalText = submitButton.innerHTML;
                submitButton.innerHTML = submitButton.innerHTML.trim();
            }
        });
    });
}

function applyAnimatedCounters() {
    const counterSelectors = [
        ".ca-stat-card strong",
        ".ca-stat-card h2",
        ".ca-stat-card h3",
        ".ca-stat-card .ca-stat-value",
        ".ca-dashboard-card strong",
        ".ca-dashboard-card h2",
        ".ca-dashboard-card h3"
    ];

    const counterElements = Array.from(document.querySelectorAll(counterSelectors.join(",")));

    counterElements.forEach(function (element) {
        const rawText = element.textContent.trim();

        // Only animate clean integer values like: 0, 1, 12, 150
        if (!/^\d+$/.test(rawText)) {
            return;
        }

        const targetValue = parseInt(rawText, 10);

        if (Number.isNaN(targetValue)) {
            return;
        }

        element.classList.add("ca-counter");
        animateCounter(element, targetValue);
    });
}

function animateCounter(element, targetValue) {
    const duration = 850;
    const startTime = performance.now();

    function updateCounter(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Smooth ease-out
        const easedProgress = 1 - Math.pow(1 - progress, 3);
        const currentValue = Math.round(targetValue * easedProgress);

        element.textContent = currentValue.toLocaleString();

        if (progress < 1) {
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = targetValue.toLocaleString();
        }
    }

    requestAnimationFrame(updateCounter);
}

function applyActiveNavigation() {
    const currentPath = normalizePath(window.location.pathname);
    const navLinks = document.querySelectorAll(
        "header a[href], nav a[href], .navbar a[href], .ca-navbar a[href], .ca-main-nav a[href]"
    );

    navLinks.forEach(function (link) {
        const href = link.getAttribute("href");

        if (!href || href.startsWith("#") || href.startsWith("javascript:")) {
            return;
        }

        let linkPath;

        try {
            linkPath = normalizePath(new URL(href, window.location.origin).pathname);
        } catch (error) {
            return;
        }

        if (isActivePath(currentPath, linkPath)) {
            link.classList.add("ca-nav-active");
            link.setAttribute("aria-current", "page");
        }
    });
}

function normalizePath(path) {
    if (!path) {
        return "/";
    }

    if (path.length > 1 && path.endsWith("/")) {
        return path.slice(0, -1);
    }

    return path;
}

function isActivePath(currentPath, linkPath) {
    if (linkPath === "/") {
        return currentPath === "/";
    }

    if (currentPath === linkPath) {
        return true;
    }

    // Dashboard group
    if (
        linkPath === "/accounts/dashboard" &&
        currentPath.startsWith("/accounts/dashboard")
    ) {
        return true;
    }

    // Courses top-nav should stay active across inner LMS workflow pages
    if (
        linkPath === "/courses" &&
        (
            currentPath.startsWith("/courses") ||
            currentPath.startsWith("/assignments") ||
            currentPath.startsWith("/discussions") ||
            currentPath.startsWith("/consultations") ||
            currentPath.startsWith("/mentorship")
        )
    ) {
        return true;
    }

    // Login group
    if (
        linkPath === "/accounts/login" &&
        currentPath.startsWith("/accounts/login")
    ) {
        return true;
    }

    return false;
}
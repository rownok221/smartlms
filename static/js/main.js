// ClassADDA global UI interactions

document.addEventListener("DOMContentLoaded", function () {
    applyRevealAnimations();
    applySubmitLoadingState();
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
(function () {
    const compareStorageKey = "aurum-showroom-compare";
    const body = document.body;

    function getCompareIds() {
        try {
            const raw = localStorage.getItem(compareStorageKey);
            const parsed = raw ? JSON.parse(raw) : [];
            return Array.isArray(parsed) ? parsed.map(String).slice(0, 3) : [];
        } catch (error) {
            return [];
        }
    }

    function setCompareIds(ids) {
        const uniqueIds = [...new Set(ids.map(String))].slice(0, 3);
        localStorage.setItem(compareStorageKey, JSON.stringify(uniqueIds));
        updateCompareUI();
    }

    function buildCompareUrl() {
        const ids = getCompareIds();
        const params = new URLSearchParams();
        ids.forEach((id) => params.append("cars", id));
        return ids.length >= 2 ? `${window.showroomConfig.compareUrl}?${params.toString()}` : "#";
    }

    function updateCompareUI() {
        const ids = getCompareIds();
        document.querySelectorAll(".compare-checkbox").forEach((checkbox) => {
            checkbox.checked = ids.includes(checkbox.value);
        });

        document.querySelectorAll("[data-compare-count]").forEach((element) => {
            element.textContent = ids.length;
        });

        const compareCount = document.getElementById("compareCount");
        if (compareCount) {
            compareCount.textContent = ids.length;
        }

        const compareLaunch = document.getElementById("compareLaunch");
        if (compareLaunch) {
            const isReady = ids.length >= 2;
            compareLaunch.href = buildCompareUrl();
            compareLaunch.classList.toggle("disabled", !isReady);
            compareLaunch.setAttribute("aria-disabled", String(!isReady));
        }

        const navCompareLink = document.getElementById("navCompareLink");
        if (navCompareLink) {
            navCompareLink.href = ids.length >= 2 ? buildCompareUrl() : `${window.showroomConfig.compareUrl.replace("/compare/", "/")}#compare-studio`;
        }
    }

    function getCsrfToken() {
        const tokenInput = document.querySelector("input[name='csrfmiddlewaretoken']");
        return tokenInput ? tokenInput.value : window.showroomConfig.csrfToken;
    }

    function showToast(message) {
        const host = document.getElementById("floatingFeedback");
        if (!host || !message) {
            return;
        }

        const toast = document.createElement("div");
        toast.className = "floating-toast";
        toast.textContent = message;
        host.appendChild(toast);

        window.setTimeout(() => {
            toast.remove();
        }, 3200);
    }

    function updateWishlistCount(count) {
        document.querySelectorAll("[data-wishlist-count]").forEach((element) => {
            element.textContent = count;
        });
    }

    function updateWishlistButtons(carId, wishlisted) {
        document.querySelectorAll(`.wishlist-form[data-car-id="${carId}"] .wishlist-toggle`).forEach((button) => {
            button.classList.toggle("is-active", wishlisted);
            button.setAttribute("aria-pressed", String(wishlisted));
            const icon = button.querySelector("i");
            if (icon) {
                icon.className = wishlisted ? "fa-solid fa-heart" : "fa-regular fa-heart";
            }
        });
    }

    function bindWishlistForms(root) {
        root.querySelectorAll(".wishlist-form").forEach((form) => {
            if (form.dataset.bound === "true") {
                return;
            }
            form.dataset.bound = "true";
            form.addEventListener("submit", async (event) => {
                event.preventDefault();

                if (form.dataset.authenticated !== "true") {
                    const next = encodeURIComponent(window.location.pathname + window.location.search + window.location.hash);
                    window.location.href = `${window.showroomConfig.loginUrl}?next=${next}`;
                    return;
                }

                try {
                    const response = await fetch(form.action, {
                        method: "POST",
                        headers: {
                            "X-Requested-With": "XMLHttpRequest",
                            "X-CSRFToken": getCsrfToken(),
                        },
                        body: new FormData(form),
                    });

                    const data = await response.json();
                    updateWishlistButtons(form.dataset.carId, data.wishlisted);
                    updateWishlistCount(data.count);
                    showToast(data.message);
                } catch (error) {
                    form.submit();
                }
            });
        });
    }

    function bindGallery() {
        const primaryImage = document.getElementById("primaryGalleryImage");
        if (!primaryImage) {
            return;
        }

        document.querySelectorAll("[data-gallery-thumb]").forEach((button) => {
            button.addEventListener("click", () => {
                primaryImage.src = button.dataset.image;
                document.querySelectorAll("[data-gallery-thumb]").forEach((thumb) => {
                    thumb.classList.remove("is-active");
                });
                button.classList.add("is-active");
            });
        });
    }

    function initRevealAnimations(root) {
        const targets = root.querySelectorAll("[data-reveal]");
        if (!targets.length) {
            return;
        }

        if (!("IntersectionObserver" in window)) {
            targets.forEach((target) => target.classList.add("is-visible"));
            return;
        }

        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("reveal", "is-visible");
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.12 }
        );

        targets.forEach((target) => {
            target.classList.add("reveal");
            observer.observe(target);
        });
    }

    function bindCompareCheckboxes(root) {
        root.querySelectorAll(".compare-checkbox").forEach((checkbox) => {
            if (checkbox.dataset.bound === "true") {
                return;
            }
            checkbox.dataset.bound = "true";
            checkbox.addEventListener("change", () => {
                const ids = getCompareIds();
                if (checkbox.checked) {
                    if (ids.length >= 3 && !ids.includes(checkbox.value)) {
                        checkbox.checked = false;
                        showToast("You can compare up to three cars at a time.");
                        return;
                    }
                    setCompareIds([...ids, checkbox.value]);
                } else {
                    setCompareIds(ids.filter((id) => id !== checkbox.value));
                }
            });
        });
    }

    function bindCatalog() {
        const form = document.getElementById("catalogFilters");
        const results = document.getElementById("catalogResults");
        const loadMoreButton = document.getElementById("loadMoreButton");
        const resultCount = document.getElementById("catalogResultCount");
        const resetButton = document.getElementById("resetFilters");
        if (!form || !results) {
            return;
        }

        let activeRequest = null;
        let debounceTimer = null;

        function formParams() {
            const params = new URLSearchParams();
            new FormData(form).forEach((value, key) => {
                if (value) {
                    params.append(key, value);
                }
            });
            return params;
        }

        function updateLoadMoreButton(payload) {
            if (!loadMoreButton) {
                return;
            }
            if (payload.has_next) {
                loadMoreButton.dataset.nextPage = payload.next_page;
                loadMoreButton.classList.remove("d-none");
            } else {
                loadMoreButton.classList.add("d-none");
                delete loadMoreButton.dataset.nextPage;
            }
        }

        async function fetchCatalog(page, append) {
            if (activeRequest) {
                activeRequest.abort();
            }

            const params = formParams();
            params.set("page", page);
            activeRequest = new AbortController();
            body.classList.add("is-loading-catalog");

            try {
                const response = await fetch(`${form.dataset.endpoint}?${params.toString()}`, {
                    headers: { "X-Requested-With": "XMLHttpRequest" },
                    signal: activeRequest.signal,
                });
                const payload = await response.json();
                if (append) {
                    results.insertAdjacentHTML("beforeend", payload.html);
                } else {
                    results.innerHTML = payload.html;
                }

                if (resultCount) {
                    resultCount.textContent = `${payload.count} cars available`;
                }
                updateLoadMoreButton(payload);
                bindWishlistForms(results);
                bindCompareCheckboxes(results);
                initRevealAnimations(results);
                updateCompareUI();
            } catch (error) {
                if (error.name !== "AbortError") {
                    showToast("Unable to update the catalog right now.");
                }
            } finally {
                body.classList.remove("is-loading-catalog");
            }
        }

        form.addEventListener("input", (event) => {
            clearTimeout(debounceTimer);
            debounceTimer = window.setTimeout(() => {
                fetchCatalog(1, false);
            }, event.target.tagName === "INPUT" ? 250 : 0);
        });

        form.addEventListener("change", () => fetchCatalog(1, false));
        form.addEventListener("submit", (event) => {
            event.preventDefault();
            fetchCatalog(1, false);
        });

        if (resetButton) {
            resetButton.addEventListener("click", () => {
                form.reset();
                fetchCatalog(1, false);
            });
        }

        if (loadMoreButton) {
            loadMoreButton.addEventListener("click", () => {
                const nextPage = loadMoreButton.dataset.nextPage;
                if (nextPage) {
                    fetchCatalog(nextPage, true);
                }
            });
        }
    }

    function bindScrollProgress() {
        const bar = document.getElementById("scrollProgress");
        if (!bar) {
            return;
        }

        const update = () => {
            const scrollTop = document.documentElement.scrollTop || document.body.scrollTop;
            const height = document.documentElement.scrollHeight - document.documentElement.clientHeight;
            const percentage = height > 0 ? (scrollTop / height) * 100 : 0;
            bar.style.width = `${percentage}%`;
        };

        update();
        document.addEventListener("scroll", update, { passive: true });
    }

    function bindCompareControls() {
        const clearButton = document.getElementById("clearCompare");
        const compareLaunch = document.getElementById("compareLaunch");

        if (clearButton) {
            clearButton.addEventListener("click", () => setCompareIds([]));
        }

        if (compareLaunch) {
            compareLaunch.addEventListener("click", (event) => {
                if (compareLaunch.classList.contains("disabled")) {
                    event.preventDefault();
                    showToast("Select at least two cars to compare.");
                }
            });
        }
    }

    document.addEventListener("DOMContentLoaded", () => {
        document.getElementById("pageLoader")?.classList.add("is-hidden");
        bindScrollProgress();
        bindWishlistForms(document);
        bindGallery();
        bindCatalog();
        bindCompareCheckboxes(document);
        bindCompareControls();
        initRevealAnimations(document);
        updateCompareUI();
    });
})();

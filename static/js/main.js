document.addEventListener("DOMContentLoaded", () => {
  initThemeControls();

  const searchBtn = document.getElementById("search-btn");
  const searchInput = document.getElementById("search-input");
  const searchSection = document.getElementById("search-section");
  const chatSection = document.getElementById("chat-section");
  const chatBox = document.getElementById("chat-box");

  function initThemeControls() {
    const form = document.querySelector("[data-theme-form]");
    if (!form) return;

    const storageKey = "nourisher.theme.preference";
    const systemMatcher = window.matchMedia("(prefers-color-scheme: dark)");
    const trigger = document.querySelector("[data-theme-trigger]");
    const currentText = document.querySelector("[data-theme-current-text]");
    const indicator = document.querySelector("[data-theme-indicator]");
    const optionLabels = Array.from(form.querySelectorAll("[data-theme-option]"));
    const inputs = Array.from(form.querySelectorAll("input[name='theme']"));
    const labelMap = {
      light: "기본 모드",
      dark: "다크 모드",
    };
    const indicatorStyles = {
      system: { color: "var(--indicator-active)", ring: "rgba(99, 102, 241, 0.2)" },
      light: { color: "#f97316", ring: "rgba(249, 115, 22, 0.25)" },
      dark: { color: "#a855f7", ring: "rgba(168, 85, 247, 0.25)" },
    };

    function readPreference() {
      try {
        return localStorage.getItem(storageKey);
      } catch (error) {
        console.warn("테마 설정을 불러오지 못했습니다.", error);
        return null;
      }
    }

    function persistPreference(value) {
      try {
        localStorage.setItem(storageKey, value);
      } catch (error) {
        console.warn("테마 설정을 저장할 수 없습니다.", error);
      }
    }

    function resolveTheme(preference) {
      if (preference === "system") {
        return systemMatcher.matches ? "dark" : "light";
      }
      return preference;
    }

    function updateIndicator(preference, resolvedTheme) {
      if (!indicator) return;
      const styleKey = preference === "system" ? resolvedTheme : preference;
      const { color, ring } = indicatorStyles[styleKey] || indicatorStyles.system;
      indicator.style.backgroundColor = color;
      indicator.style.boxShadow = `0 0 0 4px ${ring}`;
    }

    function updateOptionStyles(preference) {
      optionLabels.forEach(label => {
        const value = label.dataset.themeOption;
        const option = label.querySelector(".theme-option");
        const status = label.querySelector("[data-default-label]");
        const isActive = value === preference;

        label.classList.toggle("is-active", isActive);

        if (option) {
          option.classList.toggle("active", isActive);
        }

        if (status) {
          status.classList.toggle("is-active", isActive);
          const activeText = status.dataset.activeLabel || "ACTIVE";
          const defaultText = status.dataset.defaultLabel || status.textContent;
          status.textContent = isActive ? activeText : defaultText;
        }
      });
    }

    function applyTheme(preference, { updateForm = true } = {}) {
      const resolvedTheme = resolveTheme(preference);
      document.body.dataset.theme = resolvedTheme;
      document.documentElement.style.colorScheme = resolvedTheme === "dark" ? "dark" : "light";
      updateIndicator(preference, resolvedTheme);
      updateOptionStyles(preference);

      if (currentText) {
        const displayText =
          preference === "system"
            ? `사용자설정 · ${resolvedTheme === "dark" ? "다크" : "기본"}`
            : labelMap[preference] || labelMap.dark;
        currentText.textContent = displayText;
      }

      if (updateForm) {
        inputs.forEach(input => {
          input.checked = input.value === preference;
        });
      }
    }

    const initialPreference = readPreference() || "system";
    applyTheme(initialPreference);

    form.addEventListener("change", event => {
      const target = event.target;
      if (!(target instanceof HTMLInputElement)) return;
      const preference = target.value;
      persistPreference(preference);
      applyTheme(preference);
    });

    const handleSystemChange = () => {
      const stored = readPreference() || "system";
      if (stored === "system") {
        applyTheme("system", { updateForm: false });
      }
    };

    if (typeof systemMatcher.addEventListener === "function") {
      systemMatcher.addEventListener("change", handleSystemChange);
    } else if (typeof systemMatcher.addListener === "function") {
      systemMatcher.addListener(handleSystemChange);
    }

    if (trigger) {
      trigger.setAttribute("aria-haspopup", "true");
      trigger.setAttribute("aria-expanded", "false");

      const schedule = window.requestAnimationFrame
        ? callback => window.requestAnimationFrame(callback)
        : callback => setTimeout(callback, 0);

      const updateExpansionState = () => {
        const isExpanded =
          document.activeElement === trigger || form.contains(document.activeElement);
        trigger.setAttribute("aria-expanded", isExpanded ? "true" : "false");
      };

      trigger.addEventListener("focus", updateExpansionState);
      trigger.addEventListener("blur", () => {
        schedule(updateExpansionState);
      });

      form.addEventListener("focusin", updateExpansionState);
      form.addEventListener("focusout", () => {
        schedule(updateExpansionState);
      });

      trigger.addEventListener("keydown", event => {
        if (event.key === "Escape") {
          trigger.blur();
        }
      });
    }
  }

  async function startConversation(query) {
    if (!query) return;

    // 대화창으로 전환
    searchSection.classList.add("hidden");
    chatSection.classList.remove("hidden");

    // 사용자 메시지 append
    appendMessage("user", query);

    try {
      const res = await fetch(`/api/v1/search/?query=${encodeURIComponent(query)}`);
      const data = await res.json();

      appendMessage("assistant", data.content || "응답을 불러올 수 없습니다.");
    } catch (err) {
      appendMessage("assistant", "⚠️ 오류가 발생했습니다.");
    }
  }

  searchBtn.addEventListener("click", () => {
    const query = searchInput.value.trim();
    if (query) startConversation(query);
  });
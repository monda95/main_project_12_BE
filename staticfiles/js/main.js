document.addEventListener("DOMContentLoaded", () => {
  initThemeControls();

  const searchBtn = document.getElementById("search-btn");
  const searchInput = document.getElementById("search-input");
  const searchSection = document.getElementById("search-section");
  const chatSection = document.getElementById("chat-section");
  const chatBox = document.getElementById("chat-box");

  function ensureChatUiReady(context = "초기화") {
    const ready = searchBtn && searchInput && searchSection && chatSection && chatBox;
    if (!ready) {
      console.warn(`검색/대화 UI 요소를 찾을 수 없어 ${context}를 건너뜁니다.`);
    }
    return ready;
  }

  function initThemeControls() {
    const form = document.querySelector("[data-theme-form]");
    if (!form) {
      console.warn("테마 폼을 찾을 수 없습니다.");
      return;
    }

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
      system: {
        color: "var(--indicator-active)",
        ring: "rgba(99, 102, 241, 0.2)",
        fill: "rgba(99, 102, 241, 0.12)",
      },
      light: {
        color: "#f97316",
        ring: "rgba(249, 115, 22, 0.25)",
        fill: "rgba(249, 115, 22, 0.12)",
      },
      dark: {
        color: "#a855f7",
        ring: "rgba(168, 85, 247, 0.25)",
        fill: "rgba(168, 85, 247, 0.2)",
      },
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
      const styles = indicatorStyles[styleKey] || indicatorStyles.system;

      // CSS 변수 값을 실제 값으로 변환
      let color = styles.color;
      if (color.startsWith("var(")) {
        const varName = color.match(/var\((--[^)]+)\)/)?.[1];
        if (varName) {
          color = getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
        }
      }

      indicator.style.backgroundColor = color;
      indicator.style.boxShadow = `0 0 0 4px ${styles.ring}`;
    }

    function updateOptionStyles(preference, resolvedTheme) {
      optionLabels.forEach(label => {
        const value = label.dataset.themeOption;
        const option = label.querySelector(".theme-option");
        const status = label.querySelector("[data-default-label]");
        const isActive = value === preference;

        const styleKey = (value === "system" ? resolvedTheme : value) || "system";
        const { color, ring, fill } = indicatorStyles[styleKey] || indicatorStyles.system;

        label.classList.toggle("is-active", isActive);

        if (option) {
          option.classList.toggle("active", isActive);
          if (isActive) {
            option.style.setProperty("--theme-option-accent", color);
            option.style.setProperty("--theme-option-ring", ring);
            if (fill) {
              option.style.setProperty("--theme-option-fill", fill);
            } else {
              option.style.removeProperty("--theme-option-fill");
            }
          } else {
            option.style.removeProperty("--theme-option-accent");
            option.style.removeProperty("--theme-option-ring");
            option.style.removeProperty("--theme-option-fill");
          }
        }

        if (isActive) {
          label.style.setProperty("--theme-option-accent", color);
          label.style.setProperty("--theme-option-ring", ring);
          if (fill) {
            label.style.setProperty("--theme-option-fill", fill);
          } else {
            label.style.removeProperty("--theme-option-fill");
          }
        } else {
          label.style.removeProperty("--theme-option-accent");
          label.style.removeProperty("--theme-option-ring");
          label.style.removeProperty("--theme-option-fill");
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

      // body에 data-theme 속성 적용
      document.body.setAttribute("data-theme", resolvedTheme);
      document.documentElement.style.colorScheme = resolvedTheme === "dark" ? "dark" : "light";

      updateIndicator(preference, resolvedTheme);
      updateOptionStyles(preference, resolvedTheme);

      if (currentText) {
        const displayText =
          preference === "system"
            ? `사용자설정 · ${resolvedTheme === "dark" ? "다크" : "기본"}`
            : labelMap[preference] || labelMap.light;
        currentText.textContent = displayText;
      }

      if (updateForm) {
        inputs.forEach(input => {
          input.checked = input.value === preference;
        });
      }
    }

    // 초기 테마 적용
    const initialPreference = readPreference() || "light";
    applyTheme(initialPreference);

    // 폼 변경 이벤트 리스너
    form.addEventListener("change", event => {
      const target = event.target;
      if (!(target instanceof HTMLInputElement)) return;
      const preference = target.value;
      persistPreference(preference);
      applyTheme(preference);
    });

    // 시스템 테마 변경 감지
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

    // 접근성 속성 설정
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

  // 검색 기능 (메인 페이지에만 존재)
  if (searchBtn && searchInput && searchSection && chatSection && chatBox && typeof window.appendMessage === "function") {
    const startConversation = async query => {
      if (!query) return;

      // 대화창으로 전환
      searchSection.classList.add("hidden");
      chatSection.classList.remove("hidden");

      // 사용자 메시지 append
      window.appendMessage("user", query);

      try {
        const res = await fetch(`/api/v1/search/?query=${encodeURIComponent(query)}`);
        const data = await res.json();

        window.appendMessage("assistant", data.content || "응답을 불러올 수 없습니다.");
      } catch (err) {
        window.appendMessage("assistant", "⚠️ 오류가 발생했습니다.");
      }
    };

    searchBtn.addEventListener("click", () => {
      const query = searchInput.value.trim();
      if (query) startConversation(query);
    });

    searchInput.addEventListener("keypress", event => {
      if (event.key === "Enter") {
        const query = searchInput.value.trim();
        if (query) startConversation(query);
      }
    });
  }
});
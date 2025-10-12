document.addEventListener("DOMContentLoaded", () => {
  initThemeControls();
  initHeaderScroll();
  initSidebarToggle();
  initConversationSidebar();

  const searchBtn = document.getElementById("search-btn");
  const searchInput = document.getElementById("search-input");
  const searchSection = document.getElementById("search-section");
  const chatSection = document.getElementById("chat-section");
  const chatBox = document.getElementById("chat-box");
  const chatInput = document.getElementById("chat-input");
  const searchFillButtons = Array.from(
    document.querySelectorAll("[data-search-fill]")
  );

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
    const menu = form.closest("[data-theme-menu]");
    const dropdown = menu?.querySelector(".theme-dropdown");
    const optionLabels = Array.from(form.querySelectorAll("[data-theme-option]"));
    const inputs = Array.from(form.querySelectorAll("input[name='theme']"));
    let closeThemeMenu = () => {};
    let openThemeMenu = () => {};

    const labelMap = {
      system: "사용자설정",
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
        color: "#f59e0b",
        ring: "rgba(245, 158, 11, 0.25)",
        fill: "rgba(245, 158, 11, 0.12)",
      },
      dark: {
        color: "var(--color-secondary)",
        ring: "rgba(99, 102, 241, 0.25)",
        fill: "rgba(99, 102, 241, 0.2)",
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

      let color = styles.color;
      if (color.startsWith("var(")) {
        const varName = color.match(/var\((--[^)]+)\)/)?.[1];
        if (varName) {
          color = getComputedStyle(document.documentElement)
            .getPropertyValue(varName)
            .trim();
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

      document.body.setAttribute("data-theme", resolvedTheme);
      document.documentElement.style.colorScheme =
        resolvedTheme === "dark" ? "dark" : "light";

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

    const initialPreference = readPreference() || "light";
    applyTheme(initialPreference);

    form.addEventListener("change", event => {
      const target = event.target;
      if (!(target instanceof HTMLInputElement)) return;
      const preference = target.value;
      persistPreference(preference);
      applyTheme(preference);
      closeThemeMenu();
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

    if (trigger && menu) {
      trigger.setAttribute("aria-haspopup", "true");
      trigger.setAttribute("aria-expanded", "false");

      openThemeMenu = () => {
        if (menu.classList.contains("is-open")) return;
        menu.classList.add("is-open");
        trigger.setAttribute("aria-expanded", "true");
      };

      closeThemeMenu = ({ restoreFocus = false } = {}) => {
        if (!menu.classList.contains("is-open")) return;
        menu.classList.remove("is-open");
        trigger.setAttribute("aria-expanded", "false");
        if (restoreFocus) {
          trigger.focus();
        }
      };

      const toggleThemeMenu = () => {
        if (menu.classList.contains("is-open")) {
          closeThemeMenu();
        } else {
          openThemeMenu();
          const activeInput = form.querySelector("input[name='theme']:checked");
          if (activeInput) {
            activeInput.focus();
          } else if (dropdown && typeof dropdown.focus === "function") {
            dropdown.focus();
          }
        }
      };

      trigger.addEventListener("click", event => {
        event.preventDefault();
        toggleThemeMenu();
      });

      trigger.addEventListener("keydown", event => {
        if (event.key === "Escape") {
          event.preventDefault();
          closeThemeMenu();
          trigger.blur();
          return;
        }

        if (event.key === "ArrowDown" || event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          openThemeMenu();
          const activeInput = form.querySelector("input[name='theme']:checked");
          if (activeInput) {
            activeInput.focus();
          }
        }
      });

      const handleOutsidePointerDown = event => {
        if (!menu.classList.contains("is-open")) return;
        if (!menu.contains(event.target)) {
          closeThemeMenu();
        }
      };

      document.addEventListener("pointerdown", handleOutsidePointerDown);

      form.addEventListener("focusin", openThemeMenu);

      form.addEventListener("focusout", event => {
        const next = event.relatedTarget;
        if (!next || !menu.contains(next)) {
          closeThemeMenu();
        }
      });

      form.addEventListener("keydown", event => {
        if (event.key === "Escape") {
          event.preventDefault();
          closeThemeMenu({ restoreFocus: true });
        }
      });
    }
  }

  function initHeaderScroll() {
    const header = document.querySelector("[data-header]");
    if (!header) {
      return;
    }

    const updateHeaderState = () => {
      const shouldActivate = window.scrollY > 16;
      header.classList.toggle("is-scrolled", shouldActivate);
    };

    updateHeaderState();
    window.addEventListener("scroll", updateHeaderState, { passive: true });
  }

  function initSidebarToggle() {
    const shell = document.querySelector(".app-shell");
    const sidebar = document.querySelector("[data-sidebar]");
    const toggleBtn = document.querySelector("[data-sidebar-toggle]");
    const backdrop = document.querySelector("[data-sidebar-backdrop]");

    if (!shell || !sidebar || !toggleBtn) {
      return;
    }

    const mobileQuery = window.matchMedia("(min-width: 1024px)");

    const openSidebar = () => {
      shell.classList.add("has-sidebar-open");
      sidebar.classList.add("is-open");
      toggleBtn.setAttribute("aria-expanded", "true");
    };

    const closeSidebar = () => {
      shell.classList.remove("has-sidebar-open");
      sidebar.classList.remove("is-open");
      toggleBtn.setAttribute("aria-expanded", "false");
    };

    const toggleSidebar = () => {
      if (mobileQuery.matches) {
        return;
      }
      if (shell.classList.contains("has-sidebar-open")) {
        closeSidebar();
      } else {
        openSidebar();
      }
    };

    const handleMediaChange = () => {
      if (mobileQuery.matches) {
        closeSidebar();
      }
    };

    toggleBtn.addEventListener("click", toggleSidebar);

    if (backdrop) {
      backdrop.addEventListener("click", closeSidebar);
    }

    document.addEventListener("keydown", event => {
      if (event.key === "Escape") {
        closeSidebar();
      }
    });

    sidebar.addEventListener("click", event => {
      const link = event.target.closest("[data-sidebar-link]");
      if (!link) return;
      if (!mobileQuery.matches) {
        closeSidebar();
      }
    });

    document.addEventListener("sidebar:close", closeSidebar);
    document.addEventListener("sidebar:open", openSidebar);

    if (typeof mobileQuery.addEventListener === "function") {
      mobileQuery.addEventListener("change", handleMediaChange);
    } else if (typeof mobileQuery.addListener === "function") {
      mobileQuery.addListener(handleMediaChange);
    }

    handleMediaChange();
  }

  function initConversationSidebar() {
    const shell = document.querySelector(".app-shell");
    const sidebar = document.querySelector("[data-sidebar]");
    const collapseBtn = document.querySelector("[data-sidebar-collapse]");
    const stateEl = document.querySelector("[data-conversation-state]");
    const listEl = document.querySelector("[data-conversation-list]");
    const newBtn = document.querySelector("[data-new-conversation]");

    if (!shell || !sidebar || !collapseBtn || !stateEl || !listEl) {
      return;
    }

    const desktopQuery = window.matchMedia("(min-width: 1024px)");
    const collapseStorageKey = "nourisher.sidebar.collapsed";
    const chatBox = document.getElementById("chat-box");
    const activeConversationId = chatBox?.dataset.conversationId || null;

    const readStoredCollapsed = () => {
      try {
        return localStorage.getItem(collapseStorageKey) === "1";
      } catch (error) {
        console.warn("사이드바 접힘 상태를 불러오지 못했습니다.", error);
        return false;
      }
    };

    const storeCollapsed = value => {
      try {
        localStorage.setItem(collapseStorageKey, value ? "1" : "0");
      } catch (error) {
        console.warn("사이드바 접힘 상태를 저장하지 못했습니다.", error);
      }
    };

    let isCollapsed = false;

    const applyCollapsed = collapsed => {
      isCollapsed = collapsed;
      shell.classList.toggle("is-sidebar-collapsed", collapsed && desktopQuery.matches);
      collapseBtn.setAttribute("aria-expanded", (!collapsed).toString());
      collapseBtn.setAttribute("aria-label", collapsed ? "사이드바 펼치기" : "사이드바 접기");
    };

    const syncCollapsed = () => {
      if (desktopQuery.matches) {
        const stored = readStoredCollapsed();
        applyCollapsed(stored);
      } else {
        applyCollapsed(false);
      }
    };

    syncCollapsed();

    collapseBtn.addEventListener("click", () => {
      if (!desktopQuery.matches) {
        document.dispatchEvent(new Event("sidebar:close"));
        return;
      }
      const nextState = !isCollapsed;
      applyCollapsed(nextState);
      storeCollapsed(nextState);
    });

    const handleDesktopChange = event => {
      if (event.matches) {
        const stored = readStoredCollapsed();
        applyCollapsed(stored);
      } else {
        applyCollapsed(false);
      }
    };

    if (typeof desktopQuery.addEventListener === "function") {
      desktopQuery.addEventListener("change", handleDesktopChange);
    } else if (typeof desktopQuery.addListener === "function") {
      desktopQuery.addListener(handleDesktopChange);
    }

    const setState = (message, state = "info", options = {}) => {
      const { hideList = true } = options;
      stateEl.textContent = message;
      stateEl.dataset.state = state;
      stateEl.hidden = false;
      listEl.hidden = hideList;
    };

    const showList = () => {
      stateEl.hidden = true;
      listEl.hidden = false;
    };

    const formatTimestamp = value => {
      if (!value) return "";
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) {
        return "";
      }

      const now = new Date();
      const diff = now - date;
      const minute = 60 * 1000;
      const hour = 60 * minute;
      const day = 24 * hour;

      if (diff < minute) return "방금";
      if (diff < hour) return `${Math.max(1, Math.round(diff / minute))}분 전`;
      if (diff < day) return `${Math.max(1, Math.round(diff / hour))}시간 전`;
      if (diff < day * 7) return `${Math.max(1, Math.round(diff / day))}일 전`;

      try {
        return new Intl.DateTimeFormat("ko-KR", {
          month: "numeric",
          day: "numeric",
        }).format(date);
      } catch (error) {
        console.warn("날짜 포맷팅에 실패했습니다.", error);
        return date.toLocaleDateString();
      }
    };

    const buildConversationItem = conversation => {
      const listItem = document.createElement("li");
      const button = document.createElement("button");
      button.type = "button";
      button.className = "conversation-item";
      button.setAttribute("data-sidebar-link", "true");
      button.setAttribute("data-conversation-id", String(conversation.id));
      button.setAttribute(
        "title",
        (conversation.title && conversation.title.trim()) || "제목 없는 대화"
      );

      if (String(conversation.id) === activeConversationId) {
        button.classList.add("is-active");
      }

      const titleWrapper = document.createElement("span");
      titleWrapper.className = "conversation-item__title";
      const titleText = document.createElement("span");
      titleText.textContent =
        (conversation.title && conversation.title.trim()) || "제목 없는 대화";
      titleWrapper.appendChild(titleText);
      button.appendChild(titleWrapper);

      const metaText = formatTimestamp(conversation.updated_at || conversation.created_at);
      if (metaText) {
        const meta = document.createElement("span");
        meta.className = "conversation-item__meta";
        meta.textContent = metaText;
        button.appendChild(meta);
      }

      button.addEventListener("click", () => {
        if (String(conversation.id) === activeConversationId) {
          document.dispatchEvent(new Event("sidebar:close"));
          return;
        }
        window.location.href = `/conversation/?conversation_id=${conversation.id}`;
      });

      listItem.appendChild(button);
      return listItem;
    };

    const fetchConversations = async () => {
      setState("대화를 불러오는 중입니다...", "info", { hideList: true });

      try {
        const response = await fetch("/api/v1/conversations/", {
          credentials: "same-origin",
        });

        if (response.status === 401 || response.status === 403) {
          setState("로그인 후 대화 목록을 확인할 수 있습니다. 새 대화를 시작해보세요!", "info", {
            hideList: listEl.childElementCount === 0,
          });
          return;
        }

        if (!response.ok) {
          throw new Error(`Failed to load conversations: ${response.status}`);
        }

        const payload = await response.json();
        const results = Array.isArray(payload)
          ? payload
          : Array.isArray(payload?.results)
            ? payload.results
            : [];

        if (!results.length) {
          setState("아직 대화가 없습니다. 새 대화를 시작해보세요!", "info", { hideList: true });
          return;
        }

        listEl.innerHTML = "";
        results.forEach(conversation => {
          const item = buildConversationItem(conversation);
          listEl.appendChild(item);
        });

        showList();
      } catch (error) {
        console.error("대화 목록을 불러오지 못했습니다.", error);
        setState(
          "대화 목록을 불러오지 못했습니다. 잠시 후 다시 시도해주세요.",
          "error",
          { hideList: listEl.childElementCount === 0 }
        );
      }
    };

    const getCSRFToken = () => {
      const cookie = document.cookie
        .split("; ")
        .find(row => row.startsWith("csrftoken="));
      return cookie ? cookie.split("=")[1] : "";
    };

    if (newBtn) {
      newBtn.addEventListener("click", async () => {
        newBtn.disabled = true;
        newBtn.setAttribute("aria-busy", "true");

        try {
          const response = await fetch("/api/v1/conversations/", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCSRFToken(),
            },
            credentials: "same-origin",
            body: JSON.stringify({ title: "새 대화" }),
          });

          if (!response.ok) {
            throw new Error(`Failed to create conversation: ${response.status}`);
          }

          const data = await response.json();

          if (data?.id) {
            window.location.href = `/conversation/?conversation_id=${data.id}`;
            return;
          }

          throw new Error("Invalid response payload");
        } catch (error) {
          console.error("새 대화를 생성하지 못했습니다.", error);
          setState("새 대화를 시작하지 못했습니다. 잠시 후 다시 시도해주세요.", "error", {
            hideList: listEl.childElementCount === 0,
          });
        } finally {
          newBtn.disabled = false;
          newBtn.removeAttribute("aria-busy");
        }
      });
    }

    fetchConversations();
  }

  if (searchInput && searchFillButtons.length) {
    searchFillButtons.forEach(button => {
      button.addEventListener("click", () => {
        const value = button.dataset.searchFill || button.textContent.trim();
        if (!value) return;
        searchInput.value = value;
        searchInput.focus();
      });
    });
  }

  if (searchBtn && searchInput) {
    const supportsInlineChat =
      Boolean(chatSection && chatBox) &&
      typeof window.appendMessage === "function" &&
      typeof window.showTypingIndicator === "function" &&
      typeof window.removeTypingIndicator === "function";

    if (supportsInlineChat) {
      const hideElement = element => {
        if (!element) return;
        element.setAttribute("hidden", "");
        element.setAttribute("aria-hidden", "true");
      };

      const showElement = element => {
        if (!element) return;
        element.removeAttribute("hidden");
        element.removeAttribute("aria-hidden");
      };

      const escapeHtml = value =>
        String(value).replace(/[&<>'"]/g, match => {
          const map = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;",
          };
          return map[match] || match;
        });

      let isSubmitting = false;

      const activateInlineChat = () => {
        hideElement(searchSection);
        if (chatSection) {
          showElement(chatSection);
        }
      };

      const startInlineConversation = async query => {
        if (!query || isSubmitting) return;

        isSubmitting = true;
        searchBtn.setAttribute("aria-busy", "true");
        searchBtn.disabled = true;
        searchInput.setAttribute("aria-busy", "true");

        activateInlineChat();

        window.removeTypingIndicator();
        window.appendMessage("user", query);
        searchInput.value = "";
        window.showTypingIndicator();

        try {
          const response = await fetch(
            `/api/v1/search/?query=${encodeURIComponent(query)}`
          );
          const data = await response.json();

          window.removeTypingIndicator();

          if (!response.ok) {
            const message = data?.detail || data?.message || "검색에 실패했습니다.";
            throw new Error(message);
          }

          if (typeof window.renderAssistantMessage === "function") {
            window.appendMessage("assistant", window.renderAssistantMessage(data));
          } else {
            window.appendMessage("assistant", data);
          }
        } catch (error) {
          window.removeTypingIndicator();
          console.error("Search API 오류:", error);
          const fallback =
            (error && (error.message || error.detail)) || "잠시 후 다시 시도해주세요.";
          window.appendMessage(
            "assistant",
            `<div class="text-red-600">⚠️ ${escapeHtml(fallback)}</div>`
          );
        } finally {
          isSubmitting = false;
          searchBtn.removeAttribute("aria-busy");
          searchBtn.disabled = false;
          searchInput.removeAttribute("aria-busy");
          if (chatInput) {
            chatInput.focus();
          } else {
            searchInput.focus();
          }
        }
      };

      const handleSearchSubmit = () => {
        const query = searchInput.value.trim();
        if (!query) return;
        startInlineConversation(query);
      };

      searchBtn.addEventListener("click", handleSearchSubmit);

      searchInput.addEventListener("keypress", event => {
        if (event.key === "Enter") {
          event.preventDefault();
          handleSearchSubmit();
        }
      });
    } else {
      const navigateToConversation = query => {
        if (!query) return;
        const params = new URLSearchParams({ query });
        window.location.href = `/conversation/?${params.toString()}`;
      };

      const handleSearchSubmit = () => {
        const query = searchInput.value.trim();
        if (!query) return;
        navigateToConversation(query);
      };

      searchBtn.addEventListener("click", handleSearchSubmit);

      searchInput.addEventListener("keypress", event => {
        if (event.key === "Enter") {
          event.preventDefault();
          handleSearchSubmit();
        }
      });
    }

  }
});

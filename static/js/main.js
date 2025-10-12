document.addEventListener("DOMContentLoaded", () => {
  const SIDEBAR_ENABLED = false;
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

  const tokenStorage = (() => {
    const keys = {
      access: "access_token",
      refresh: "refresh_token",
    };

    const safeSet = (key, value) => {
      try {
        if (value) {
          localStorage.setItem(key, value);
        }
      } catch (error) {
        console.warn(`토큰을 저장하지 못했습니다. (${key})`, error);
      }
    };

    const safeRemove = (key) => {
      try {
        localStorage.removeItem(key);
      } catch (error) {
        console.warn(`토큰을 삭제하지 못했습니다. (${key})`, error);
      }
    };

    const safeGet = (key) => {
      try {
        return localStorage.getItem(key);
      } catch (error) {
        console.warn(`토큰을 불러오지 못했습니다. (${key})`, error);
        return null;
      }
    };

    return {
      setTokens(access, refresh) {
        if (access) {
          safeSet(keys.access, access);
        }
        if (refresh) {
          safeSet(keys.refresh, refresh);
        }
      },
      clearTokens() {
        safeRemove(keys.access);
        safeRemove(keys.refresh);
      },
      getAccess() {
        return safeGet(keys.access);
      },
      getRefresh() {
        return safeGet(keys.refresh);
      },
    };
  })();

  /* === PATCH: safe JSON parse (추가) === */
  function tryParseJSON(text) {
    if (!text) return null;
    try { return JSON.parse(text); } catch { return null; }
  }

  const initLoginFormSync = () => {
    const loginForm = document.querySelector("[data-login-form]");
    if (!loginForm) return;

    loginForm.addEventListener("submit", async (event) => {
      if (loginForm.dataset.jwtSync === "done") {
        return;
      }

      event.preventDefault();

      const formData = new FormData(loginForm);
      const email = (formData.get("email") || "").toString().trim();
      const password = (formData.get("password") || "").toString();

      if (!email || !password) {
        loginForm.dataset.jwtSync = "done";
        loginForm.submit();
        return;
      }

      try {
        const response = await fetch("/api/v1/auth/login/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email, password }),
        });

        if (!response.ok) {
          console.warn("로그인 토큰 발급이 실패했습니다.", response.status);
        } else {
          const contentType = response.headers.get("content-type") || "";
          if (contentType.includes("application/json")) {
            const data = await response.json();
            if (data?.access && data?.refresh) {
              tokenStorage.setTokens(data.access, data.refresh);
              console.info("로그인 토큰을 저장했습니다.");
            }
          }
        }
      } catch (error) {
        console.error("로그인 토큰 동기화 중 오류가 발생했습니다.", error);
      } finally {
        loginForm.dataset.jwtSync = "done";
        loginForm.submit();
      }
    });
  };

  const initLogoutSync = () => {
    const logoutForm = document.querySelector("[data-logout-form]");
    if (!logoutForm) return;

    logoutForm.addEventListener("submit", async (event) => {
      if (logoutForm.dataset.jwtSync === "done") {
        return;
      }

      event.preventDefault();

      const access = tokenStorage.getAccess();
      const refresh = tokenStorage.getRefresh();

      if (!refresh) {
        console.warn("저장된 리프레시 토큰이 없어 바로 로그아웃합니다.");
        tokenStorage.clearTokens();
        logoutForm.dataset.jwtSync = "done";
        logoutForm.submit();
        return;
      }

      try {
        // === Authorization 보강 (원래 코드 유지; 이미 구현됨) ===
        const headers = { "Content-Type": "application/json" };
        if (access) headers.Authorization = `Bearer ${access}`;

        const response = await fetch("/api/v1/auth/logout/", {
          method: "POST",
          headers,
          body: JSON.stringify({ refresh }),
          keepalive: true,
        });

        if (!response.ok) {
          console.warn("로그아웃 API 호출이 실패했습니다.", response.status);
        } else {
          console.info("로그아웃 API 호출이 완료되었습니다.");
        }
      } catch (error) {
        console.error("로그아웃 요청 중 오류가 발생했습니다.", error);
      } finally {
        tokenStorage.clearTokens();
        logoutForm.dataset.jwtSync = "done";
        logoutForm.submit();
      }
    });
  };

  initLoginFormSync();
  initLogoutSync();

  // ---------- Theme ----------
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
    const optionLabels = Array.from(
      form.querySelectorAll("[data-theme-option]")
    );
    const inputs = Array.from(form.querySelectorAll("input[name='theme']"));

    const labelMap = {
      light: "라이트 모드",
      dark: "다크 모드",
      system: "시스템 기본",
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

    const readPreference = () => {
      try {
        return localStorage.getItem(storageKey);
      } catch (error) {
        console.warn("테마 설정을 불러오지 못했습니다.", error);
        return null;
      }
    };

    const persistPreference = (value) => {
      try {
        localStorage.setItem(storageKey, value);
      } catch (error) {
        console.warn("테마 설정을 저장하지 못했습니다.", error);
      }
    };

    const resolveTheme = (preference) => {
      if (preference === "system") {
        return systemMatcher.matches ? "dark" : "light";
      }
      return preference;
    };

    const getIndicatorColor = (value) => {
      let color = value;
      if (color.startsWith("var(")) {
        const varName = color.match(/var\((--[^)]+)\)/)?.[1];
        if (varName) {
          color = getComputedStyle(document.documentElement)
            .getPropertyValue(varName)
            .trim();
        }
      }
      return color;
    };

    const updateIndicator = (preference, resolvedTheme) => {
      if (!indicator) return;
      const styleKey = preference === "system" ? resolvedTheme : preference;
      const styles = indicatorStyles[styleKey] || indicatorStyles.system;

      indicator.style.backgroundColor = getIndicatorColor(styles.color);
      indicator.style.boxShadow = `0 0 0 4px ${styles.ring}`;
    };

    const updateOptionStyles = (preference, resolvedTheme) => {
      optionLabels.forEach((label) => {
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
    };

    const applyTheme = (preference, { updateForm = true } = {}) => {
      const resolvedTheme = resolveTheme(preference);

      document.body.setAttribute("data-theme", resolvedTheme);
      document.documentElement.style.colorScheme =
        resolvedTheme === "dark" ? "dark" : "light";

      updateIndicator(preference, resolvedTheme);
      updateOptionStyles(preference, resolvedTheme);

      if (currentText) {
        const displayText =
          preference === "system"
            ? `시스템 기본 · ${resolvedTheme === "dark" ? "다크" : "기본"}`
            : labelMap[preference] || labelMap.light;
        currentText.textContent = displayText;
      }

      if (updateForm) {
        inputs.forEach((input) => {
          input.checked = input.value === preference;
        });
      }
    };

    const initialPreference = readPreference() || "light";
    applyTheme(initialPreference);

    form.addEventListener("change", (event) => {
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
        ? (callback) => window.requestAnimationFrame(callback)
        : (callback) => setTimeout(callback, 0);

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

      trigger.addEventListener("keydown", (event) => {
        if (event.key === "Escape") {
          trigger.blur();
        }
      });
    }
  }

  // ---------- Header ----------
  function initHeaderScroll() {
    const header = document.querySelector("[data-header]");
    if (!header) return;

    const updateHeaderState = () => {
      const shouldActivate = window.scrollY > 16;
      header.classList.toggle("is-scrolled", shouldActivate);
    };

    updateHeaderState();
    window.addEventListener("scroll", updateHeaderState, { passive: true });
  }

  // ---------- Sidebar ----------
  function initSidebarToggle() {
    if (!SIDEBAR_ENABLED) return;
    const shell = document.querySelector(".app-shell");
    const sidebar = document.querySelector("[data-sidebar]");
    const toggleBtn = document.querySelector("[data-sidebar-toggle]");
    const backdrop = document.querySelector("[data-sidebar-backdrop]");

    if (!shell || !sidebar || !toggleBtn) return;

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
      if (mobileQuery.matches) return;
      shell.classList.contains("has-sidebar-open")
        ? closeSidebar()
        : openSidebar();
    };

    const handleMediaChange = () => {
      if (mobileQuery.matches) closeSidebar();
    };

    toggleBtn.addEventListener("click", toggleSidebar);
    if (backdrop) backdrop.addEventListener("click", closeSidebar);
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeSidebar();
    });

    sidebar.addEventListener("click", (event) => {
      const link = event.target.closest("[data-sidebar-link]");
      if (!link) return;
      if (!mobileQuery.matches) closeSidebar();
    });

    document.addEventListener("sidebar:close", closeSidebar);
    document.addEventListener("sidebar:open", openSidebar);

    if (typeof mobileQuery.addEventListener === "function") {
      mobileQuery.addEventListener("change", handleMediaChange);
    }

    handleMediaChange();
  }

  // ---------- Conversation Sidebar ----------
  function initConversationSidebar() {
    if (!SIDEBAR_ENABLED) return;
    const shell = document.querySelector(".app-shell");
    const sidebar = document.querySelector("[data-sidebar]");
    const collapseBtn = document.querySelector("[data-sidebar-collapse]");
    const stateEl = document.querySelector("[data-conversation-state]");
    const listEl = document.querySelector("[data-conversation-list]");
    const newBtn = document.querySelector("[data-new-conversation]");
    const isAuthenticated =
      document.body?.dataset.authenticated === "true";

    if (!shell || !sidebar || !collapseBtn || !stateEl || !listEl) return;

    const desktopQuery = window.matchMedia("(min-width: 1024px)");
    const collapseStorageKey = "nourisher.sidebar.collapsed";
    const chatBox = document.getElementById("chat-box");
    const activeConversationId = chatBox?.dataset.conversationId || null;

    const readStoredCollapsed = () => {
      try {
        return localStorage.getItem(collapseStorageKey) === "1";
      } catch {
        console.warn("사이드바 접힘 상태를 불러오지 못했습니다.");
        return false;
      }
    };

    const storeCollapsed = (value) => {
      try {
        localStorage.setItem(collapseStorageKey, value ? "1" : "0");
      } catch {
        console.warn("사이드바 접힘 상태를 저장하지 못했습니다.");
      }
    };

    let isCollapsed = false;

    const applyCollapsed = (collapsed) => {
      isCollapsed = collapsed;
      shell.classList.toggle(
        "is-sidebar-collapsed",
        collapsed && desktopQuery.matches
      );
      collapseBtn.setAttribute("aria-expanded", (!collapsed).toString());
      collapseBtn.setAttribute(
        "aria-label",
        collapsed ? "사이드바 펼치기" : "사이드바 접기"
      );
    };

    const syncCollapsed = () => {
      if (desktopQuery.matches) {
        const stored = readStoredCollapsed();
        applyCollapsed(stored);
        isCollapsed = stored;
      } else {
        applyCollapsed(false);
        isCollapsed = false;
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

    if (typeof desktopQuery.addEventListener === "function") {
      desktopQuery.addEventListener("change", (event) => {
        if (event.matches) {
          const stored = readStoredCollapsed();
          applyCollapsed(stored);
          isCollapsed = stored;
        } else {
          applyCollapsed(false);
          isCollapsed = false;
        }
      });
    }

    const setState = (message, state = "info", options = {}) => {
      const { hideList = listEl.childElementCount === 0 } = options;
      stateEl.textContent = message;
      stateEl.dataset.state = state;
      stateEl.hidden = false;
      listEl.hidden = hideList;
    };

    const showList = () => {
      stateEl.hidden = true;
      listEl.hidden = false;
    };

    const formatTimestamp = (value) => {
      if (!value) return "";
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return "";

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
      } catch {
        return date.toLocaleDateString();
      }
    };

    const buildConversationItem = (conversation) => {
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

      const metaText =
        formatTimestamp(conversation.updated_at || conversation.created_at);
      const metaActionsWrapper = document.createElement("span");
      metaActionsWrapper.className = "conversation-item__meta-actions";

      if (metaText) {
        const meta = document.createElement("span");
        meta.className = "conversation-item__meta";
        meta.textContent = metaText;
        metaActionsWrapper.appendChild(meta);
      }

      const actions = document.createElement("span");
      actions.className = "conversation-item__actions";

      const renameBtn = document.createElement("button");
      renameBtn.type = "button";
      renameBtn.className = "conversation-action conversation-action--rename";
      renameBtn.setAttribute("aria-label", "대화 제목 수정");
      renameBtn.innerHTML =
        '<span aria-hidden="true">✏️</span><span class="sr-only">제목 수정</span>';

      renameBtn.addEventListener("click", async (event) => {
        event.stopPropagation();
        const currentTitle = (conversation.title || "").trim();
        const newTitle = prompt("새 대화 제목을 입력하세요.", currentTitle);

        if (newTitle === null) {
          return;
        }

        const trimmed = newTitle.trim();
        if (!trimmed) {
          alert("대화 제목은 비워둘 수 없습니다.");
          return;
        }

        try {
          const response = await fetch(`/api/v1/conversations/${conversation.id}/`, {
            method: "PATCH",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCSRFToken(),
            },
            credentials: "same-origin",
            body: JSON.stringify({ title: trimmed }),
          });

          if (!response.ok) {
            throw new Error(`Failed to update conversation: ${response.status}`);
          }

          await fetchConversations();
        } catch (error) {
          console.error("대화 제목을 수정하지 못했습니다.", error);
          alert("대화 제목을 수정하지 못했습니다. 잠시 후 다시 시도해주세요.");
        }
      });

      const deleteBtn = document.createElement("button");
      deleteBtn.type = "button";
      deleteBtn.className = "conversation-action conversation-action--delete";
      deleteBtn.setAttribute("aria-label", "대화 삭제");
      deleteBtn.innerHTML =
        '<span aria-hidden="true">🗑️</span><span class="sr-only">대화 삭제</span>';

      deleteBtn.addEventListener("click", async (event) => {
        event.stopPropagation();

        if (!confirm("선택한 대화를 삭제할까요?")) {
          return;
        }

        try {
          const response = await fetch(`/api/v1/conversations/${conversation.id}/`, {
            method: "DELETE",
            headers: {
              "X-CSRFToken": getCSRFToken(),
            },
            credentials: "same-origin",
          });

        if (response.status !== 204) {
            throw new Error(`Failed to delete conversation: ${response.status}`);
          }

          if (String(conversation.id) === activeConversationId) {
            window.location.href = "/conversation/";
            return;
          }

          await fetchConversations();
        } catch (error) {
          console.error("대화를 삭제하지 못했습니다.", error);
          alert("대화를 삭제하지 못했습니다. 잠시 후 다시 시도해주세요.");
        }
      });

      actions.appendChild(renameBtn);
      actions.appendChild(deleteBtn);
      metaActionsWrapper.appendChild(actions);
      button.appendChild(metaActionsWrapper);

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
      setState("대화를 불러오는 중입니다...");

      try {
        const response = await fetch("/api/v1/conversations/", {
          credentials: "same-origin",
        });

        if (response.status === 401 || response.status === 403) {
          listEl.innerHTML = "";
          setState(
            "로그인을 하면 대화 목록을 확인할 수 있습니다.",
            "info",
            { hideList: true }
          );

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
          setState("아직 대화가 없습니다. 새 대화를 시작해보세요!");
          return;
        }

        listEl.innerHTML = "";
        results.forEach((conversation) => {
          const item = buildConversationItem(conversation);
          listEl.appendChild(item);
        });

        showList();
      } catch (error) {
        console.error("대화 목록을 불러오지 못했습니다.", error);
        setState("대화 목록을 불러올 수 없습니다. 잠시 후 다시 시도해주세요.", "error");
      }
    };

    const getCSRFToken = () => {
      const cookie = document.cookie
        .split("; ")
        .find((row) => row.trim().startsWith("csrftoken="));
      return cookie ? cookie.split("=")[1] : "";
    };

    /* === PATCH: 새 대화 생성 핸들러 교체 (비정상 응답 안전화) === */
    if (newBtn) {
      const authAlertMessage =
        newBtn.dataset.requiresAuthMessage || "로그인이 필요합니다.";

      newBtn.addEventListener("click", async () => {
        if (!isAuthenticated) {
          alert(authAlertMessage);
          return;
        }

        newBtn.disabled = true;
        newBtn.setAttribute("aria-busy", "true");

        try {
          const resp = await fetch("/api/v1/conversations/", {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCSRFToken(),
              // JWT 기반이면 필요 시 추가:
              // "Authorization": `Bearer ${localStorage.getItem("access_token") || ""}`,
            },
            credentials: "same-origin",
            body: JSON.stringify({ title: "새 대화" }),
          });

          if (resp.status === 401 || resp.status === 403) {
            alert(authAlertMessage);
            return;
          }

          // 본문을 텍스트로 받고 JSON 파싱 시도 (HTML 로그인 페이지 대응)
          const raw = await resp.text();
          const data = tryParseJSON(raw);

          if (!resp.ok) {
            const msg = (data && (data.detail || data.message)) || raw || `HTTP ${resp.status}`;
            throw new Error(msg);
          }

          if (!data || typeof data.id === "undefined") {
            throw new Error("Invalid response payload");
          }

          window.location.href = `/conversation/?conversation_id=${data.id}`;
        } catch (error) {
          console.error("새 대화를 생성하지 못했습니다.", error);
          setState("새 대화를 시작하지 못했습니다. 잠시 후 다시 시도해주세요.", "error");
          alert("새 대화를 생성하지 못했습니다.\n" + (error?.message || ""));
        } finally {
          newBtn.disabled = false;
          newBtn.removeAttribute("aria-busy");
        }
      });
    }

    if (isAuthenticated) {
      fetchConversations();
    } else {
      listEl.innerHTML = "";
      setState("로그인을 하면 대화 목록을 확인할 수 있습니다.", "info", { hideList: true });
    }
  }

  // ---------- Search ----------
  if (searchInput && searchFillButtons.length) {
    searchFillButtons.forEach((button) => {
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
      const hideElement = (element) => {
        if (!element) return;
        element.setAttribute("hidden", "");
        element.setAttribute("aria-hidden", "true");
      };

      const showElement = (element) => {
        if (!element) return;
        element.removeAttribute("hidden");
        element.removeAttribute("aria-hidden");
      };
      const escapeHtml = (value) =>
        String(value).replace(/[&<>'"]/g, (match) => {
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

      const startInlineConversation = async (query) => {
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

      searchInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
          event.preventDefault();
          handleSearchSubmit();
        }
      });
    } else {
      const navigateToConversation = (query) => {
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

      searchInput.addEventListener("keypress", (event) => {
        if (event.key === "Enter") {
          event.preventDefault();
          handleSearchSubmit();
        }
      });
    }
  }
});

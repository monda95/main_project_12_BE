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
  const searchFillButtons = Array.from(
    document.querySelectorAll("[data-search-fill]")
  );

  function ensureChatUiReady(context = "초기화") {
    const ready = Boolean(
      searchBtn && searchInput && searchSection && chatSection && chatBox
    );
    if (!ready) {
      console.warn(
        `검색/대화 UI 요소를 찾을 수 없어 ${context} 초기화를 건너뜁니다.`
      );
    }
    return ready;
  }

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

    // ... (테마 관련 로직 동일, 변경 없음)
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
    const shell = document.querySelector(".app-shell");
    const sidebar = document.querySelector("[data-sidebar]");
    const collapseBtn = document.querySelector("[data-sidebar-collapse]");
    const stateEl = document.querySelector("[data-conversation-state]");
    const listEl = document.querySelector("[data-conversation-list]");
    const newBtn = document.querySelector("[data-new-conversation]");

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
      setState("대화를 불러오는 중입니다...");

      try {
        const response = await fetch("/api/v1/conversations/", {
          credentials: "same-origin",
        });

        if (response.status === 401 || response.status === 403) {
          setState("로그인 후 대화 목록을 확인할 수 있습니다. 새 대화를 시작해보세요!");
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
          setState("새 대화를 시작하지 못했습니다. 잠시 후 다시 시도해주세요.", "error");
        } finally {
          newBtn.disabled = false;
          newBtn.removeAttribute("aria-busy");
        }
      });
    }

    fetchConversations();
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

  if (
    searchBtn &&
    searchInput &&
    searchSection &&
    chatSection &&
    chatBox &&
    typeof window.appendMessage === "function"
  ) {
    const startConversation = async (query) => {
      if (!query) return;

      searchSection.classList.add("hidden");
      chatSection.classList.remove("hidden");

      window.appendMessage("user", query);
      window.showTypingIndicator();

      try {
        const res = await fetch(
          `/api/v1/search/?query=${encodeURIComponent(query)}`
        );
        const data = await res.json();

        window.removeTypingIndicator();

        if (typeof window.renderAssistantMessage === "function") {
          window.appendMessage("assistant", window.renderAssistantMessage(data));
        } else {
          console.warn("renderAssistantMessage not ready, fallback to JSON");
          window.appendMessage(
            "assistant",
            `<pre>${JSON.stringify(data, null, 2)}</pre>`
          );
        }
      } catch (err) {
        console.error("Search API 오류:", err);
        window.removeTypingIndicator();
        window.appendMessage("assistant", "⚠️ 오류가 발생했습니다.");
      }
    };

    searchBtn.addEventListener("click", () => {
      const query = searchInput.value.trim();
      if (query) startConversation(query);
    });

    searchInput.addEventListener("keypress", (event) => {
      if (event.key === "Enter") {
        const query = searchInput.value.trim();
        if (query) startConversation(query);
      }
    });
  }
});

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
@@ -210,74 +216,440 @@ document.addEventListener("DOMContentLoaded", () => {

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
        isCollapsed = stored;
      } else {
        applyCollapsed(false);
        isCollapsed = false;
      }
    };

    syncCollapsed();

    collapseBtn.addEventListener("click", () => {
      if (!desktopQuery.matches) {
        // 모바일에서는 접기 대신 오버레이 토글을 사용
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
        isCollapsed = stored;
      } else {
        applyCollapsed(false);
        isCollapsed = false;
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
      titleText.textContent = (conversation.title && conversation.title.trim()) || "제목 없는 대화";
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

  // 검색 기능 (메인 페이지에만 존재)
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

  if (searchBtn && searchInput && searchSection && chatSection && chatBox && typeof window.appendMessage === "function") {
    const startConversation = async query => {
      if (!query) return;

      // 대화창으로 전환
      searchSection.classList.add("hidden");
      chatSection.classList.remove("hidden");

      // 사용자 메시지 append
      window.appendMessage("user", query);

      // ✅ 추가: 로딩 애니메이션
      window.showTypingIndicator();

      try {
        const res = await fetch(`/api/v1/search/?query=${encodeURIComponent(query)}`);
        const data = await res.json();

        // ✅ 추가: 로딩 애니메이션 제거
        window.removeTypingIndicator();

        // ✅ 수정: 렌더링 함수 사용
        if (typeof window.renderAssistantMessage === "function") {
          window.appendMessage("assistant", window.renderAssistantMessage(data));
        } else {
          console.warn("renderAssistantMessage not ready, fallback to JSON");
          window.appendMessage("assistant", `<pre>${JSON.stringify(data, null, 2)}</pre>`);
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

    searchInput.addEventListener("keypress", event => {
      if (event.key === "Enter") {
        const query = searchInput.value.trim();
        if (query) startConversation(query);
      }
    });
  }
});
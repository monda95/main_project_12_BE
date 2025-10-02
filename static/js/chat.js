document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chat-box");
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send");

  if (!chatBox) {
    console.warn("chat.js: 대화 UI 요소를 찾을 수 없습니다. appendMessage는 비활성화됩니다.");
    return;
  }


  function escapeHtml(value) {
    if (value === null || value === undefined) return "";
    return String(value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#39;");
  }

  function renderAssistantContent(content) {
    if (!content || typeof content !== "object") {
      return `<p>${escapeHtml(content)}</p>`;
    }

    if (content.raw_text) {
      return `<p>${escapeHtml(content.raw_text)}</p>`;
    }

    const sections = [];

    if (content.nutrition && typeof content.nutrition === "object") {
      const nutritionEntries = Object.entries(content.nutrition)
        .filter(([, value]) => value !== null && value !== undefined && value !== "")
        .map(
          ([key, value]) => `
            <div class="assistant-nutrition-item">
              <span class="assistant-nutrition-label">${escapeHtml(key)}</span>
              <span class="assistant-nutrition-value">${escapeHtml(value)}</span>
            </div>
          `,
        )
        .join("");

      if (nutritionEntries) {
        sections.push(`
          <section class="assistant-section">
            <h3 class="assistant-section-title">영양 정보</h3>
            <div class="assistant-nutrition-grid">
              ${nutritionEntries}
            </div>
          </section>
        `);
      }
    }

    const infoFields = [
      ["allergy", "알레르기"],
      ["storage", "보관"],
      ["processing", "가공법"],
      ["source", "출처"],
    ];

    const definitionItems = infoFields
      .map(([key, label]) => {
        const value = content[key];
        if (value === null || value === undefined || value === "") {
          return "";
        }
        return `
          <div class="assistant-definition-item">
            <dt class="assistant-definition-term">${escapeHtml(label)}</dt>
            <dd class="assistant-definition-description">${escapeHtml(value)}</dd>
          </div>
        `;
      })
      .filter(Boolean)
      .join("");

    if (definitionItems) {
      sections.push(`
        <section class="assistant-section">
          <h3 class="assistant-section-title">추가 정보</h3>
          <dl class="assistant-definition-list">
            ${definitionItems}
          </dl>
        </section>
      `);
    }

    if (!sections.length) {
      return `<pre class="whitespace-pre-wrap text-sm bg-gray-100 p-2 rounded">${escapeHtml(JSON.stringify(content, null, 2))}</pre>`;
    }

    return `<div class="assistant-card">${sections.join("")}</div>`;
  }

  // 말풍선 append
  function appendMessage(role, content, isTemp = false) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("chat-message", role);
    if (isTemp) wrapper.dataset.temp = "true"; // typing indicator용

    let displayContent;
    if (role === "assistant" && typeof content === "object") {
      displayContent = renderAssistantContent(content);
    } else if (typeof content === "string") {
      displayContent = escapeHtml(content);
    } else if (content && typeof content === "object" && "raw_text" in content) {
      displayContent = `<p>${escapeHtml(content.raw_text)}</p>`;
    } else {
      displayContent = escapeHtml(String(content ?? ""));
    }

    wrapper.innerHTML = `
      <div class="chat-bubble">
        <div class="chat-role">${role === "user" ? "사용자" : "Nourisher AI"}</div>
        <div class="chat-content">${displayContent}</div>
      </div>
    `;

    removeEmptyState();
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  window.appendMessage = appendMessage;

  // 로딩 말풍선 (… 점 3개 애니메이션)
  function showTypingIndicator() {
    appendMessage(
      "assistant",
      `<span class="typing-dots"><span></span><span></span><span></span></span>`,
      true
    );
  }

  function removeTypingIndicator() {
    const temp = chatBox.querySelector('[data-temp="true"]');
    if (temp) temp.remove();
  }

  // 전송 버튼 이벤트
  sendBtn.addEventListener("click", async () => {
    const query = input.value.trim();
    if (!query) return;

    // 사용자 메시지 append
    appendMessage("user", query);
    input.value = "";

    // 로딩 말풍선 append
    showTypingIndicator();

    try {
      const res = await fetch(`/api/v1/search/?query=${encodeURIComponent(query)}`);
      const data = await res.json();

      // 로딩 제거 후 응답 append
      removeTypingIndicator();
      appendMessage("assistant", data.content || "응답을 불러올 수 없습니다.");
    } catch (err) {
      removeTypingIndicator();
      appendMessage("assistant", "⚠️ 오류가 발생했습니다.");
    }
  });

  // Enter 키 이벤트
  input.addEventListener("keydown", e => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendBtn.click();
    }
  });
});

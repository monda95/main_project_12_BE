(function () {
  const chatBox = document.getElementById("chat-box");
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send");
  const guideMessage = document.getElementById("chat-guide");

  if (!chatBox) {
    console.warn("chat.js: #chat-box 요소를 찾을 수 없습니다.");
    return;
  }

  // 🔹 안내 문구 표시
  function showGuideMessage() {
    if (!guideMessage) return;
    guideMessage.hidden = false;
  }

  // 🔹 안내 문구 제거
  function hideGuideMessage() {
    if (!guideMessage) return;
    guideMessage.hidden = true;
  }

  function syncGuideMessage() {
    if (!guideMessage) return;
    const hasMessages = Boolean(chatBox.querySelector(".chat-message"));
    guideMessage.hidden = hasMessages;
  }

  // 🔹 AI 답변 렌더링
  function renderAssistantMessage(data) {
    if (!data) {
      return `<div class="text-gray-500">⚠️ 응답을 불러올 수 없습니다.</div>`;
    }

    const content = data.content || data;

    if (!content || typeof content !== "object") {
      return `<div class="text-gray-700">🤖 Nourisher는 식품 정보에 특화된 비서예요. 음식 관련 질문을 해주세요.</div>`;
    }

    const nutrition = content.nutrition || {};
    const macros = [
      { label: "열량", value: nutrition.calories },
      { label: "단백질", value: nutrition.protein },
      { label: "지방", value: nutrition.fat },
      { label: "탄수화물", value: nutrition.carbohydrates }
    ];
    const macroList = macros
      .filter((item) => item.value !== undefined && item.value !== null && item.value !== "")
      .map(
        (item) => `
          <li>
            <span>${item.label}</span>
            <span>${item.value}</span>
          </li>
        `
      )
      .join("");
    const macroHasValue = Boolean(macroList);

    const detailSources = [
      { label: "⚠️ 알레르기", value: content.allergy },
      { label: "📦 보관", value: content.storage },
      { label: "⚙️ 가공", value: content.processing },
      { label: "🌱 원료", value: content.source }
    ];
    const detailMarkup = detailSources
      .filter((item) => item.value !== undefined && item.value !== null && item.value !== "")
      .map(
        (item) => `
          <div class="assistant-card__item">
            <span class="assistant-card__item-label">${item.label}</span>
            <span>${item.value}</span>
          </div>
        `
      )
      .join("");
    const detailHasValue = Boolean(detailMarkup);

    if (macroHasValue || detailHasValue) {
      return `
        <article class="assistant-card" aria-label="영양 정보 카드">
          <header class="assistant-card__header">
            <h3>🍽️ 영양 정보</h3>
            <p>100g 기준 주요 정보를 정리했어요.</p>
          </header>
          ${
            macroHasValue
              ? `<ul class="assistant-card__list">${macroList}</ul>`
              : ""
          }
          ${macroHasValue && detailHasValue ? '<hr class="assistant-card__divider">' : ""}
          ${detailHasValue ? detailMarkup : ""}
        </article>
      `;
    }

    return `<div class="text-gray-700">🤖 Nourisher는 식품 정보에 특화된 비서예요. 음식 관련 질문을 해주세요.</div>`;
  }

  // 🔹 말풍선 append
  function appendMessage(role, content, isTemp = false) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("chat-message", role);
    if (isTemp) wrapper.dataset.temp = "true";

    let displayContent = content;

    if (!isTemp && role === "assistant" && typeof content === "object") {
      displayContent = renderAssistantMessage(content);
    }

    if (typeof displayContent === "string" && displayContent.indexOf("<") === -1) {
      displayContent = displayContent.replace(/\n/g, "<br>");
    }

    const meta = document.createElement("div");
    meta.className = `chat-meta ${role === "user" ? "items-end text-right" : "items-start text-left"}`;

    const roleLabel = document.createElement("span");
    roleLabel.className = "chat-role";
    roleLabel.textContent = role === "user" ? "사용자" : "Nourisher AI";

    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${role === "user" ? "chat-bubble-user" : "chat-bubble-assistant"}`;
    if (isTemp) {
      bubble.classList.add("chat-bubble-typing");
    }

    const contentWrapper = document.createElement("div");
    contentWrapper.className = "chat-content";
    contentWrapper.innerHTML = displayContent;

    bubble.appendChild(contentWrapper);
    meta.appendChild(roleLabel);
    meta.appendChild(bubble);
    wrapper.appendChild(meta);

    hideGuideMessage();
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // 🔹 로딩 중(생각중) 말풍선
  function showTypingIndicator() {
    appendMessage(
      "assistant",
      `<span class="typing-dots"><span></span><span></span><span></span></span>`,
      true
    );
  }

  // 🔹 로딩 중 제거
  function removeTypingIndicator() {
    const temp = chatBox.querySelector('[data-temp="true"]');
    if (temp) temp.remove();
  }

  // 전역 노출
  window.appendMessage = appendMessage;
  window.showTypingIndicator = showTypingIndicator;
  window.removeTypingIndicator = removeTypingIndicator;
  window.showGuideMessage = showGuideMessage;
  window.hideGuideMessage = hideGuideMessage;
  window.renderAssistantMessage = renderAssistantMessage;
  console.log("✅ chat.js 초기화 완료: renderAssistantMessage 준비됨");

  // 초기 안내 문구
  syncGuideMessage();

  // 🔹 전송 이벤트
  if (sendBtn && input) {
    const handleSend = () => {
      const query = input.value.trim();
      if (!query) return;

      appendMessage("user", query);
      input.value = "";

      // "생각중" 표시
      showTypingIndicator();

      // API 호출
      fetch(`/api/v1/search/?query=${encodeURIComponent(query)}`)
        .then((res) => res.json())
        .then((data) => {
          removeTypingIndicator();

          if (data.error || data.detail) {
            appendMessage(
              "assistant",
              `<div class="text-red-600">⚠️ 서버가 잠시 응답하지 않습니다. 잠시 후 다시 시도해주세요.</div>`
            );
            return;
          }

          // ✅ 객체 그대로 넘기면 renderAssistantMessage가 처리
          appendMessage("assistant", data);
        })
        .catch((err) => {
          console.error(err);
          removeTypingIndicator();
          appendMessage(
            "assistant",
            `<div class="text-red-600">⚠️ 일시적인 오류가 발생했습니다. 다시 시도해주세요.</div>`
          );
        });
    };

    sendBtn.addEventListener("click", handleSend);
    input.addEventListener("keypress", (event) => {
      if (event.key === "Enter") handleSend();
    });
  }
})();

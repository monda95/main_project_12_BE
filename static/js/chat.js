(function () {
  const chatBox = document.getElementById("chat-box");
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send");

  if (!chatBox) {
    console.warn("chat.js: #chat-box 요소를 찾을 수 없습니다.");
    return;
  }

  // 🔹 안내 문구 표시
  function showGuideMessage() {
    if (!chatBox.querySelector('[data-guide="true"]')) {
      const guide = document.createElement("p");
      guide.dataset.guide = "true";
      guide.className = "text-gray-500 text-center";
      guide.textContent = "Nourisher는 오늘도 열심히 학습 중입니다.";
      chatBox.appendChild(guide);
    }
  }

  // 🔹 안내 문구 제거
  function hideGuideMessage() {
    const guide = chatBox.querySelector('[data-guide="true"]');
    if (guide) guide.remove();
  }

  // 🔹 AI 답변 렌더링
  function renderAssistantMessage(data) {
    if (!data || !data.content) {
      return `<div class="text-gray-500">⚠️ 응답을 불러올 수 없습니다.</div>`;
    }

    const content = data.content;

    // 음식 데이터인 경우 → 카드 형태
    if (content.nutrition || content.allergy || content.storage) {
      const nutrition = content.nutrition || {};
      return `
        <div class="assistant-card p-3 bg-white rounded-lg shadow text-sm space-y-2">
          <h3 class="font-bold mb-2">🍽️ 영양 성분 (100g 기준)</h3>
          <ul class="mb-2 list-disc list-inside">
            <li>열량: ${nutrition.calories || " -"}</li>
            <li>단백질: ${nutrition.protein || " -"}</li>
            <li>지방: ${nutrition.fat || " -"}</li>
            <li>탄수화물: ${nutrition.carbohydrates || " -"}</li>
          </ul>
          <p>⚠️ 알레르기: ${content.allergy || "정보 없음"}</p>
          <p>📦 보관: ${content.storage || "정보 없음"}</p>
          <p>⚙️ 가공: ${content.processing || "정보 없음"}</p>
          <p>🌱 원료: ${content.source || "정보 없음"}</p>
        </div>
      `;
    }

    // 음식 관련 정보가 없는 경우
    return `<div class="text-gray-700">🤖 Nourisher는 식품 정보에 특화된 비서예요. 음식 관련 질문을 해주세요.</div>`;
  }

  // 🔹 말풍선 append
  function appendMessage(role, content, isTemp = false) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("chat-message", role);
    if (isTemp) wrapper.dataset.temp = "true";

    let displayContent = content;

    // 객체일 경우 강제로 보기 좋게 변환
    if (typeof content === "object") {
      displayContent = renderAssistantMessage(content);
    }

    wrapper.innerHTML = `
      <div class="chat-bubble">
        <div class="chat-role">${role === "user" ? "사용자" : "Nourisher AI"}</div>
        <div class="chat-content">${displayContent}</div>
      </div>
    `;

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
  showGuideMessage();

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

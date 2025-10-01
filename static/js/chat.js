document.addEventListener("DOMContentLoaded", () => {
  const chatBox = document.getElementById("chat-box");
  const input = document.getElementById("chat-input");
  const sendBtn = document.getElementById("chat-send");

  // 말풍선 append
  function appendMessage(role, content, isTemp = false) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("chat-message", role);
    if (isTemp) wrapper.dataset.temp = "true"; // typing indicator용

    // content가 객체일 경우 JSON 문자열화
    let displayContent;
    if (typeof content === "object") {
      displayContent = `<pre class="whitespace-pre-wrap text-sm bg-gray-100 p-2 rounded">${JSON.stringify(content, null, 2)}</pre>`;
    } else {
      displayContent = content;
    }

    wrapper.innerHTML = `
      <div class="chat-bubble">
        <div class="chat-role">${role === "user" ? "사용자" : "Nourisher AI"}</div>
        <div class="chat-content">${displayContent}</div>
      </div>
    `;

    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
  }

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

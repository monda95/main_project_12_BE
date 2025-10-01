document.addEventListener("DOMContentLoaded", () => {
  const searchBtn = document.getElementById("search-btn");
  const searchInput = document.getElementById("search-input");
  const searchSection = document.getElementById("search-section");
  const chatSection = document.getElementById("chat-section");
  const chatBox = document.getElementById("chat-box");

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

  searchInput.addEventListener("keydown", e => {
    if (e.key === "Enter") {
      e.preventDefault();
      startConversation(searchInput.value.trim());
    }
  });

  // 채팅 append 함수 (chat.js에서 쓰는 것과 동일하게 유지)
  function appendMessage(role, content) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("chat-message", role);
    wrapper.innerHTML = `
      <div class="chat-bubble">
        <div class="chat-role">${role === "user" ? "사용자" : "Nourisher AI"}</div>
        <div class="chat-content">${content}</div>
      </div>`;
    chatBox.appendChild(wrapper);
    chatBox.scrollTop = chatBox.scrollHeight;
  }
});

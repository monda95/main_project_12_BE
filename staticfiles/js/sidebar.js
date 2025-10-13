document.addEventListener("DOMContentLoaded", () => {
  const convList = document.getElementById("conversation-list");
  const newBtn = document.getElementById("new-conv");

  function getCSRFToken() {
    const cookie = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
    return cookie ? cookie.split("=")[1] : "";
  }

  // 새 대화
  newBtn?.addEventListener("click", async () => {
    const resp = await fetch("/api/v1/conversations/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify({ title: "새 대화" }),
    });
    const conv = await resp.json();
    location.href = `/conversations/${conv.id}/`;
  });

  // CRUD 이벤트 위임
  convList?.addEventListener("click", async (e) => {
    const li = e.target.closest("li[data-id]");
    if (!li) return;
    const convId = li.dataset.id;

    // 삭제
    if (e.target.classList.contains("delete-conv")) {
      e.stopPropagation();
      await fetch(`/api/v1/conversations/${convId}/`, {
        method: "DELETE",
        headers: { "X-CSRFToken": getCSRFToken() },
      });
      li.remove();
      return;
    }

    // 수정 (더블클릭)
    if (e.detail === 2) {
      const titleSpan = li.querySelector("span");
      const oldTitle = titleSpan.textContent;
      const input = document.createElement("input");
      input.type = "text";
      input.value = oldTitle;
      input.className = "w-full border px-2 py-1 rounded";

      titleSpan.replaceWith(input);
      input.focus();

      input.addEventListener("blur", async () => {
        const newTitle = input.value.trim() || oldTitle;
        const resp = await fetch(`/api/v1/conversations/${convId}/`, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
          },
          body: JSON.stringify({ title: newTitle }),
        });
        if (resp.ok) {
          const span = document.createElement("span");
          span.className = "truncate";
          span.textContent = newTitle;
          input.replaceWith(span);
        } else {
          input.replaceWith(titleSpan); // rollback
        }
      });
      return;
    }

    // 조회 (단순 클릭)
    if (!e.target.classList.contains("delete-conv")) {
      location.href = `/conversations/${convId}/`;
    }
  });
});

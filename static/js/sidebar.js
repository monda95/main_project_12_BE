document.addEventListener("DOMContentLoaded", () => {
  const convList = document.getElementById("conversation-list");
  const newBtn = document.getElementById("new-conv");
  const logoutBtn = document.getElementById("logout-btn"); // ✅ [추가] 로그아웃 버튼 요소

  function getCSRFToken() {
    const cookie = document.cookie.split("; ").find(row => row.startsWith("csrftoken="));
    return cookie ? cookie.split("=")[1] : "";
  }

  // ✅ [추가] 로그아웃 처리 함수
  async function handleLogout() {
    const access = localStorage.getItem("access_token");
    const refresh = localStorage.getItem("refresh_token");

    if (!refresh) {
      alert("로그인 정보가 없습니다.");
      return;
    }

    try {
      const res = await fetch("/api/v1/auth/logout/", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${access}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ refresh }),
      });

      if (res.status === 204 || res.status === 205) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        alert("로그아웃 되었습니다.");
        location.href = "/login/";
      } else if (res.status === 401) {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        alert("이미 로그아웃된 상태입니다.");
        location.href = "/login/";
      } else {
        console.warn("Logout failed:", await res.text());
        alert("로그아웃에 실패했습니다.");
      }
    } catch (err) {
      console.error("Logout error:", err);
      alert("네트워크 오류가 발생했습니다.");
    }
  }

  // ✅ [추가] 로그아웃 버튼 이벤트 등록
  if (logoutBtn) {
    logoutBtn.addEventListener("click", handleLogout);
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

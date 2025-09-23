document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("search-input");
  const recommendedButtons = document.querySelectorAll(".recommended-btn");
  const searchBtn = document.getElementById("search-btn");

  // 추천 검색어 클릭 시 → 검색창에 입력
  recommendedButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      searchInput.value = btn.innerText;
      searchInput.focus();
    });
  });

  // 검색 버튼 클릭 시 API 호출 (예시)
  searchBtn.addEventListener("click", () => {
    const query = searchInput.value.trim();
    if (query) {
      console.log("검색 API 호출:", query);
      // fetch("/api/v1/search/?q=" + encodeURIComponent(query))
      //   .then(res => res.json())
      //   .then(data => console.log("검색 결과:", data));
    }
  });
});

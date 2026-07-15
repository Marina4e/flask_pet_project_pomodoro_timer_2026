(function () {
  function resolveTheme(theme) {
    if (theme !== "system") {
      return theme;
    }
    return window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }

  function applyTheme(theme, persist = false) {
    const resolved = resolveTheme(theme);
    document.documentElement.dataset.theme = resolved;
    document.documentElement.setAttribute("data-bs-theme", resolved);
    if (persist) {
      localStorage.setItem("pomodoro.theme", theme);
    }
  }

  const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
  mediaQuery.addEventListener("change", () => {
    const storedTheme = localStorage.getItem("pomodoro.theme") || "system";
    if (storedTheme === "system") {
      applyTheme("system");
    }
  });

  document.addEventListener("pomodoro:theme-change", (event) => {
    applyTheme(event.detail.theme, event.detail.persist ?? false);
  });

  window.PomodoroTheme = {
    applyTheme,
  };
})();

(function () {
  const form = document.getElementById("settings-form");
  const messageElement = document.getElementById("settings-message");
  const timezoneInput = document.getElementById("timezone-input");
  const timezoneCurrent = document.getElementById("timezone-current-value");
  const timezoneError = document.getElementById("timezone-error");

  const SettingsStore = {
    current: null,
    async loadSettings() {
      const settings = await window.pomodoroApi.get("/api/settings");
      this.current = settings;
      this.applyToForm(settings);
      this.applyTheme(settings.theme, false);
      document.dispatchEvent(
        new CustomEvent("pomodoro:settings-ready", { detail: settings }),
      );
      return settings;
    },
    applyToForm(settings) {
      if (!form) {
        return;
      }

      document.getElementById("work-duration-input").value =
        settings.work_duration_minutes;
      document.getElementById("short-break-input").value =
        settings.short_break_minutes;
      document.getElementById("long-break-input").value =
        settings.long_break_minutes;
      document.getElementById("cycles-before-long-break-input").value =
        settings.cycles_before_long_break;
      document.getElementById("theme-select").value = settings.theme;
      document.getElementById("timezone-input").value = settings.timezone;
      if (timezoneCurrent) timezoneCurrent.textContent = settings.timezone;
      if (timezoneInput) timezoneInput.setAttribute("aria-invalid", "false");
      if (timezoneError) {
        timezoneError.textContent = "";
        timezoneError.classList.add("hidden");
      }
      document.getElementById("sound-enabled-input").checked =
        settings.sound_enabled;
      document.getElementById("auto-start-next-session-input").checked =
        settings.auto_start_next_session;
    },
    applyTheme(theme, persist) {
      document.dispatchEvent(
        new CustomEvent("pomodoro:theme-change", {
          detail: { theme, persist },
        }),
      );
      if (persist) {
        localStorage.setItem("pomodoro.theme", theme);
      }
    },
    getDurationForMode(mode) {
      if (!this.current) {
        return 0;
      }

      if (mode === "work") {
        return this.current.work_duration_minutes * 60;
      }
      if (mode === "short_break") {
        return this.current.short_break_minutes * 60;
      }
      return this.current.long_break_minutes * 60;
    },
    async saveSettings(payload) {
      const settings = await window.pomodoroApi.put("/api/settings", payload);
      this.current = settings;
      this.applyToForm(settings);
      this.applyTheme(settings.theme, true);
      document.dispatchEvent(
        new CustomEvent("pomodoro:settings-updated", { detail: settings }),
      );
      return settings;
    },
  };

  async function onSubmit(event) {
    event.preventDefault();
    if (!form) {
      return;
    }

    const previousSettings = SettingsStore.current;
    const payload = {
      work_duration_minutes: Number(
        document.getElementById("work-duration-input").value,
      ),
      short_break_minutes: Number(
        document.getElementById("short-break-input").value,
      ),
      long_break_minutes: Number(
        document.getElementById("long-break-input").value,
      ),
      cycles_before_long_break: Number(
        document.getElementById("cycles-before-long-break-input").value,
      ),
      theme: document.getElementById("theme-select").value,
      timezone: timezoneInput.value.trim(),
      sound_enabled: document.getElementById("sound-enabled-input").checked,
      auto_start_next_session: document.getElementById(
        "auto-start-next-session-input",
      ).checked,
    };

    try {
      await SettingsStore.saveSettings(payload);
      messageElement.textContent = "Settings saved.";
    } catch (error) {
      if (previousSettings) {
        SettingsStore.applyToForm(previousSettings);
      }
      if (error.details?.timezone && timezoneError) {
        timezoneError.textContent =
          "Please enter a valid timezone, for example Europe/Kyiv.";
        timezoneError.classList.remove("hidden");
        timezoneInput.setAttribute("aria-invalid", "true");
        messageElement.textContent = "Settings were not saved.";
      } else {
        messageElement.textContent = `Could not save settings: ${error.message}`;
      }
    }
  }

  if (form) {
    form.addEventListener("submit", onSubmit);
  }

  window.PomodoroSettings = SettingsStore;

  document.addEventListener("DOMContentLoaded", () => {
    window.PomodoroSettings.loadSettings().catch((error) => {
      if (messageElement) {
        messageElement.textContent = `Could not load settings: ${error.message}`;
      }
    });
  });
})();

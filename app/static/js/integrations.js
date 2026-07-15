(function () {
  function initializeGoogleCalendar() {
    const syncButton = document.getElementById("google-calendar-sync-button");
    if (!syncButton) {
      return;
    }

    const elements = {
      statusPill: document.getElementById("google-calendar-status-pill"),
      statusMessage: document.getElementById("google-calendar-status-message"),
      calendarIdLabel: document.getElementById("google-calendar-id-label"),
      sessionLabel: document.getElementById("google-calendar-session-label"),
    };

    function renderStatus(status, extraMessage = "") {
      elements.statusPill.textContent = status.configured ? "Ready" : "Setup";
      elements.calendarIdLabel.textContent = status.calendar_id || "Not configured";
      elements.sessionLabel.textContent = status.latest_work_session_id
        ? `#${status.latest_work_session_id}${status.latest_work_session_synced ? " (synced)" : ""}`
        : "No completed work sessions";
      syncButton.classList.toggle("hidden", !status.configured);
      syncButton.disabled = !status.configured;

      if (extraMessage) {
        elements.statusMessage.textContent = extraMessage;
        return;
      }

      elements.statusMessage.textContent = status.configured
        ? "Google Calendar integration is ready. The button syncs the latest completed work session."
        : "Add calendar ID and service-account credentials to `.env` to enable sync.";
    }

    async function loadStatus() {
      try {
        const status = await window.pomodoroApi.get(
          "/api/integrations/google-calendar/status",
        );
        renderStatus(status);
      } catch (error) {
        elements.statusPill.textContent = "Error";
        syncButton.classList.add("hidden");
        syncButton.disabled = true;
        elements.statusMessage.textContent = `Failed to check integration: ${error.message}`;
      }
    }

    async function syncCalendar() {
      syncButton.disabled = true;
      elements.statusMessage.textContent = "Syncing to Google Calendar...";

      try {
        const timezone = window.PomodoroSettings?.current?.timezone || "UTC";
        const payload = await window.pomodoroApi.post(
          "/api/integrations/google-calendar/sync",
          { timezone },
        );

        renderStatus(
          payload.status,
          `Session #${payload.session_id} was synced to Google Calendar.`,
        );
      } catch (error) {
        elements.statusPill.textContent = "Error";
        elements.statusMessage.textContent = `Sync failed: ${error.message}`;
      } finally {
        syncButton.disabled = false;
      }
    }

    syncButton.addEventListener("click", () => {
      syncCalendar().catch(() => {});
    });

    loadStatus().catch(() => {});
    document.addEventListener("pomodoro:sessions-changed", () => {
      loadStatus().catch(() => {});
    });
  }

  function initializeGoogleSheets() {
    const elements = {
      enabledInput: document.getElementById("google-sheets-enabled-input"),
      spreadsheetIdInput: document.getElementById(
        "google-sheets-spreadsheet-id-input",
      ),
      saveButton: document.getElementById("google-sheets-save-button"),
      syncButton: document.getElementById("google-sheets-sync-button"),
      statusMessage: document.getElementById("google-sheets-status-message"),
    };

    if (!elements.saveButton || !elements.syncButton) {
      return;
    }

    function renderSettings(settings, message = "") {
      elements.enabledInput.checked = settings.enabled;
      elements.spreadsheetIdInput.value = settings.spreadsheet_id || "";
      elements.syncButton.disabled = !settings.enabled || !settings.spreadsheet_id;

      if (message) {
        elements.statusMessage.textContent = message;
        return;
      }

      if (!settings.credentials_configured) {
        elements.statusMessage.textContent =
          "Add GOOGLE_SHEETS_CREDENTIALS_JSON to `.env` before syncing.";
      } else if (!settings.enabled) {
        elements.statusMessage.textContent = "Google Sheets export is disabled.";
      } else {
        elements.statusMessage.textContent =
          "Ready to export completed work sessions without duplicate Session IDs.";
      }
    }

    async function loadSheetsSettings() {
      try {
        const settings = await window.pomodoroApi.get(
          "/api/integrations/google-sheets/settings",
        );
        renderSettings(settings);
      } catch (error) {
        elements.statusMessage.textContent = `Failed to load settings: ${error.message}`;
        elements.syncButton.disabled = true;
      }
    }

    async function saveSheetsSettings() {
      elements.saveButton.disabled = true;

      try {
        const settings = await window.pomodoroApi.put(
          "/api/integrations/google-sheets/settings",
          {
            enabled: elements.enabledInput.checked,
            spreadsheet_id: elements.spreadsheetIdInput.value.trim(),
          },
        );
        renderSettings(settings, "Google Sheets settings were saved.");
      } catch (error) {
        elements.statusMessage.textContent = `Save failed: ${error.message}`;
      } finally {
        elements.saveButton.disabled = false;
      }
    }

    async function syncCompletedSessions() {
      elements.syncButton.disabled = true;
      elements.statusMessage.textContent = "Syncing completed work sessions...";

      try {
        const payload = await window.pomodoroApi.post(
          "/api/integrations/google-sheets/sync",
          {},
        );
        elements.statusMessage.textContent = payload.message;
      } catch (error) {
        elements.statusMessage.textContent = `Sync failed: ${error.message}`;
      } finally {
        elements.syncButton.disabled =
          !elements.enabledInput.checked || !elements.spreadsheetIdInput.value.trim();
      }
    }

    elements.saveButton.addEventListener("click", () => {
      saveSheetsSettings().catch(() => {});
    });
    elements.syncButton.addEventListener("click", () => {
      syncCompletedSessions().catch(() => {});
    });

    loadSheetsSettings().catch(() => {});
  }

  document.addEventListener("DOMContentLoaded", () => {
    initializeGoogleCalendar();
    initializeGoogleSheets();
  });
})();

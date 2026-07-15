(function () {
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
      const status = await window.pomodoroApi.get("/api/integrations/google-calendar/status");
      renderStatus(status);
    } catch (error) {
      elements.statusPill.textContent = "Error";
      syncButton.classList.add("hidden");
      syncButton.disabled = true;
      elements.statusMessage.textContent = `Failed to check integration: ${error.message}`;
    }
  }

  async function syncSheets() {
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
    syncSheets().catch(() => {});
  });

  document.addEventListener("DOMContentLoaded", () => {
    loadStatus().catch(() => {});
  });

  document.addEventListener("pomodoro:sessions-changed", () => {
    loadStatus().catch(() => {});
  });
})();

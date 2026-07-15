(function () {
  function setState(element, state, text) {
    element.dataset.state = state;
    if (text !== undefined) {
      element.textContent = text;
    }
  }

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
    let currentStatus = null;

    function canSync(status) {
      return Boolean(
        status?.configured &&
          status.latest_work_session_id &&
          !status.latest_work_session_synced,
      );
    }

    function describeCalendarStatus(status) {
      if (status.calendar_id && !status.calendar_id_valid) {
        return {
          state: "error",
          text: "Replace the embed or sharing URL with the Calendar ID from Google Calendar settings.",
        };
      }
      if (!status.configured) {
        const missingId = status.missing.includes("GOOGLE_CALENDAR_ID");
        const missingCredentials = status.missing.includes(
          "GOOGLE_CALENDAR_CREDENTIALS_JSON",
        );
        const missingParts = [
          ...(missingId ? ["Calendar ID"] : []),
          ...(missingCredentials ? ["server credentials"] : []),
        ];
        return {
          state: "warning",
          text: `Setup required: add ${missingParts.join(" and ")} to the server .env, then restart Flask.`,
        };
      }
      if (!status.latest_work_session_id) {
        return {
          state: "warning",
          text: "Calendar is configured. Complete one focus session to enable the sync button.",
        };
      }
      if (status.latest_work_session_synced) {
        return {
          state: "success",
          text: "The latest focus session is already in Google Calendar. Complete the next focus session to sync again.",
        };
      }
      return {
        state: "success",
        text: "Ready. The button will create one event for the latest completed focus session.",
      };
    }

    function renderCalendarStatus(status, feedback = null) {
      currentStatus = status;

      if (status.calendar_id && !status.calendar_id_valid) {
        setState(elements.statusPill, "error", "Fix Calendar ID");
        elements.calendarIdLabel.textContent = "A URL was entered — use Calendar ID only";
      } else if (status.configured) {
        setState(elements.statusPill, "success", "Ready");
        elements.calendarIdLabel.textContent = status.calendar_id;
      } else {
        setState(elements.statusPill, "warning", "Setup required");
        elements.calendarIdLabel.textContent = status.calendar_id || "Missing from .env";
      }

      elements.sessionLabel.textContent = status.latest_work_session_id
        ? `#${status.latest_work_session_id}${status.latest_work_session_synced ? " (synced)" : " (ready to sync)"}`
        : "No completed focus sessions";
      syncButton.disabled = !canSync(status);

      const message = feedback || describeCalendarStatus(status);
      setState(elements.statusMessage, message.state, message.text);
    }

    async function loadGoogleCalendarStatus() {
      try {
        const status = await window.pomodoroApi.get(
          "/api/integrations/google-calendar/status",
        );
        renderCalendarStatus(status);
      } catch (error) {
        currentStatus = null;
        setState(elements.statusPill, "error", "Status error");
        setState(
          elements.statusMessage,
          "error",
          `Failed to check Calendar configuration: ${error.message}`,
        );
        syncButton.disabled = true;
      }
    }

    async function syncGoogleCalendar() {
      if (!canSync(currentStatus)) {
        return;
      }

      syncButton.disabled = true;
      setState(
        elements.statusMessage,
        "warning",
        "Creating the Google Calendar event for the latest focus session...",
      );

      try {
        const timezone = window.PomodoroSettings?.current?.timezone || "UTC";
        const payload = await window.pomodoroApi.post(
          "/api/integrations/google-calendar/sync",
          { timezone },
        );

        renderCalendarStatus(payload.status, {
          state: "success",
          text: `Session #${payload.session_id} was saved to Google Calendar. Open the shared calendar to view the event.`,
        });
      } catch (error) {
        setState(elements.statusPill, "error", "Sync error");
        setState(
          elements.statusMessage,
          "error",
          `Calendar sync failed: ${error.message}`,
        );
        syncButton.disabled = !canSync(currentStatus);
      }
    }

    syncButton.addEventListener("click", () => {
      syncGoogleCalendar().catch(() => {});
    });

    loadGoogleCalendarStatus().catch(() => {});
    document.addEventListener("pomodoro:sessions-changed", () => {
      loadGoogleCalendarStatus().catch(() => {});
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
      statusPill: document.getElementById("google-sheets-status-pill"),
      statusMessage: document.getElementById("google-sheets-status-message"),
      credentialsLabel: document.getElementById(
        "google-sheets-credentials-label",
      ),
    };

    if (!elements.saveButton || !elements.syncButton) {
      return;
    }

    let currentSettings = null;
    let hasUnsavedChanges = false;

    function isReady(settings) {
      return Boolean(settings?.enabled && settings.configured);
    }

    function describeSheetsSettings(settings) {
      if (!settings.enabled) {
        return {
          pill: "Optional · Off",
          state: "optional",
          text: "Google Sheets export is off by choice. The timer, SQLite, statistics, CSV, and Calendar continue to work normally.",
        };
      }
      if (!settings.spreadsheet_id) {
        return {
          pill: "Setup required",
          state: "warning",
          text: "Enter the Spreadsheet ID, add server credentials, and save the enabled settings.",
        };
      }
      if (!settings.spreadsheet_id_valid) {
        return {
          pill: "Fix Sheet ID",
          state: "error",
          text: "The Spreadsheet ID is invalid. Copy only the value between /d/ and /edit, not the whole URL.",
        };
      }
      if (!settings.credentials_configured) {
        return {
          pill: "Server setup",
          state: "warning",
          text: "Add GOOGLE_SHEETS_CREDENTIALS_JSON to the server .env and restart Flask before syncing.",
        };
      }
      if (!settings.credentials_valid) {
        return {
          pill: "Fix credentials",
          state: "error",
          text: "The server credentials JSON is invalid or incomplete. Replace it with a complete one-line service-account JSON.",
        };
      }
      return {
        pill: "Ready",
        state: "success",
        text: "Ready to export completed focus sessions. Existing Session IDs will be skipped.",
      };
    }

    function renderCredentialsState(settings) {
      if (!settings.credentials_configured) {
        setState(elements.credentialsLabel, "error", "Missing from server .env");
      } else if (!settings.enabled) {
        setState(
          elements.credentialsLabel,
          "warning",
          "Present · validated when enabled",
        );
      } else if (!settings.credentials_valid) {
        setState(elements.credentialsLabel, "error", "Invalid or incomplete");
      } else {
        setState(elements.credentialsLabel, "success", "Configured and valid");
      }
    }

    function renderSheetsSettings(settings, feedback = null) {
      currentSettings = settings;
      hasUnsavedChanges = false;
      elements.enabledInput.checked = settings.enabled;
      elements.spreadsheetIdInput.value = settings.spreadsheet_id || "";
      elements.syncButton.disabled = !isReady(settings);
      renderCredentialsState(settings);

      const readiness = describeSheetsSettings(settings);
      setState(elements.statusPill, readiness.state, readiness.pill);
      if (feedback) {
        setState(
          elements.statusMessage,
          feedback.state,
          `${feedback.text} ${readiness.text}`,
        );
      } else {
        setState(elements.statusMessage, readiness.state, readiness.text);
      }
    }

    function markSheetsSettingsDirty() {
      if (!currentSettings) {
        return;
      }
      hasUnsavedChanges = true;
      elements.syncButton.disabled = true;
      setState(elements.statusPill, "warning", "Unsaved changes");
      setState(
        elements.statusMessage,
        "warning",
        "Click Save Settings first. Saving validates the enabled setup but does not export any rows.",
      );
    }

    async function loadGoogleSheetsSettings() {
      try {
        const settings = await window.pomodoroApi.get(
          "/api/integrations/google-sheets/settings",
        );
        renderSheetsSettings(settings);
      } catch (error) {
        setState(elements.statusPill, "error", "Status error");
        setState(
          elements.statusMessage,
          "error",
          `Failed to load Sheets settings: ${error.message}`,
        );
        elements.syncButton.disabled = true;
      }
    }

    async function saveGoogleSheetsSettings() {
      elements.saveButton.disabled = true;
      elements.syncButton.disabled = true;
      setState(elements.statusMessage, "warning", "Validating and saving settings...");

      try {
        const settings = await window.pomodoroApi.put(
          "/api/integrations/google-sheets/settings",
          {
            enabled: elements.enabledInput.checked,
            spreadsheet_id: elements.spreadsheetIdInput.value.trim(),
          },
        );
        renderSheetsSettings(settings, {
          state: "success",
          text: "Settings were saved in SQLite. No rows were sent to Google.",
        });
      } catch (error) {
        setState(elements.statusPill, "error", "Fix settings");
        setState(
          elements.statusMessage,
          "error",
          `Settings were not saved: ${error.message}`,
        );
        elements.syncButton.disabled = true;
      } finally {
        elements.saveButton.disabled = false;
      }
    }

    async function syncGoogleSheets() {
      if (!isReady(currentSettings) || hasUnsavedChanges) {
        return;
      }

      elements.syncButton.disabled = true;
      setState(elements.statusPill, "warning", "Syncing");
      setState(
        elements.statusMessage,
        "warning",
        "Reading completed focus sessions and existing spreadsheet Session IDs...",
      );

      try {
        const payload = await window.pomodoroApi.post(
          "/api/integrations/google-sheets/sync",
          {},
        );
        setState(elements.statusPill, "success", "Ready");
        setState(
          elements.statusMessage,
          "success",
          `${payload.message} Open the first worksheet to verify columns A:I.`,
        );
      } catch (error) {
        setState(elements.statusPill, "error", "Sync error");
        setState(
          elements.statusMessage,
          "error",
          `Sheets sync failed: ${error.message}`,
        );
      } finally {
        elements.syncButton.disabled = !isReady(currentSettings) || hasUnsavedChanges;
      }
    }

    elements.enabledInput.addEventListener("change", markSheetsSettingsDirty);
    elements.spreadsheetIdInput.addEventListener("input", markSheetsSettingsDirty);
    elements.saveButton.addEventListener("click", () => {
      saveGoogleSheetsSettings().catch(() => {});
    });
    elements.syncButton.addEventListener("click", () => {
      syncGoogleSheets().catch(() => {});
    });

    loadGoogleSheetsSettings().catch(() => {});
  }

  document.addEventListener("DOMContentLoaded", () => {
    initializeGoogleCalendar();
    initializeGoogleSheets();
  });
})();

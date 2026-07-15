(function () {
  const widget = document.getElementById("timer-widget");
  if (!widget) {
    return;
  }

  const STORAGE_KEY = "pomodoro.timerState";
  const AUTO_ADVANCE_DELAY_MS = 900;
  const PRESETS = {
    standard: {
      label: "Standard 25/5",
      durations: null,
    },
    demo: {
      label: "Test mode 10s / 5s",
      durations: {
        work: 10,
        short_break: 5,
        long_break: 5,
      },
    },
  };
  const MODE_LABELS = {
    work: "work",
    short_break: "short break",
    long_break: "long break",
  };
  const STATUS_LABELS = {
    idle: "Ready",
    running: "Running",
    paused: "Paused",
    completed: "Done",
  };

  const elements = {
    display: document.getElementById("timer-display"),
    progressBar: document.getElementById("timer-progress-bar"),
    message: document.getElementById("timer-message"),
    durationLabel: document.getElementById("timer-duration-label"),
    statusPill: document.getElementById("timer-status-pill"),
    start: document.getElementById("start-timer-button"),
    pause: document.getElementById("pause-timer-button"),
    resume: document.getElementById("resume-timer-button"),
    reset: document.getElementById("reset-timer-button"),
    modeButtons: document.querySelectorAll(".mode-button"),
    presetButtons: document.querySelectorAll(".preset-button"),
    cycleNote: document.getElementById("timer-cycle-note"),
    nextModeNote: document.getElementById("timer-next-mode-note"),
    demoPresetButton: document.getElementById("preset-demo-button"),
    testModeBadge: document.getElementById("test-mode-badge"),
    runners: document.querySelectorAll("[data-runner]"),
  };

  let state = loadState();
  let settings = null;
  let intervalId = null;
  let transitionTimeoutId = null;
  let audioUnlocked = false;

  function sanitizeState(rawState) {
    if (!rawState || typeof rawState !== "object") {
      return null;
    }

    return {
      mode: rawState.mode || "work",
      status: rawState.status || "idle",
      plannedDurationSeconds: Number(rawState.plannedDurationSeconds || 1500),
      remainingSeconds: Number(rawState.remainingSeconds || 1500),
      startedAtUtc: rawState.startedAtUtc || null,
      expectedEndAtUtc: rawState.expectedEndAtUtc || null,
      completedAtUtc: rawState.completedAtUtc || null,
      clientSessionId: rawState.clientSessionId || null,
      completionSaved: Boolean(rawState.completionSaved),
      cycleCount: Number(rawState.cycleCount || 0),
      activePreset: rawState.activePreset || "standard",
    };
  }

  function defaultState(mode = "work", overrides = {}) {
    const activePreset = overrides.activePreset || state?.activePreset || "standard";
    const cycleCount =
      typeof overrides.cycleCount === "number"
        ? overrides.cycleCount
        : state?.cycleCount || 0;
    const durationSeconds = settings ? getSelectedDurationForMode(mode, activePreset) : 25 * 60;

    return {
      mode,
      status: "idle",
      plannedDurationSeconds: durationSeconds,
      remainingSeconds: durationSeconds,
      startedAtUtc: null,
      expectedEndAtUtc: null,
      completedAtUtc: null,
      clientSessionId: null,
      completionSaved: false,
      cycleCount,
      activePreset,
    };
  }

  function loadState() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? sanitizeState(JSON.parse(raw)) : null;
    } catch (_error) {
      return null;
    }
  }

  function persistState() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }

  function canUseDemoPreset() {
    return Boolean(settings?.test_mode_enabled);
  }

  function getActivePreset() {
    if (state?.activePreset === "demo" && !canUseDemoPreset()) {
      return "standard";
    }
    return state?.activePreset || "standard";
  }

  function getSelectedDurationForMode(mode, preset = getActivePreset()) {
    if (preset === "demo" && canUseDemoPreset()) {
      return PRESETS.demo.durations[mode];
    }
    return window.PomodoroSettings.getDurationForMode(mode);
  }

  function getNextTransition(currentMode, currentCycleCount) {
    if (currentMode === "work") {
      const nextCycleCount = currentCycleCount + 1;
      const cycleInterval = settings?.cycles_before_long_break || 4;
      const nextMode =
        nextCycleCount % cycleInterval === 0 ? "long_break" : "short_break";
      return { nextMode, nextCycleCount };
    }

    if (currentMode === "short_break") {
      return { nextMode: "work", nextCycleCount: currentCycleCount };
    }

    return { nextMode: "work", nextCycleCount: 0 };
  }

  function formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${String(minutes).padStart(2, "0")}:${String(remainingSeconds).padStart(2, "0")}`;
  }

  function humanDuration(seconds) {
    if (seconds < 60) {
      return `${seconds} sec`;
    }
    return `${Math.round(seconds / 60)} min`;
  }

  function prettyMode(mode) {
    return MODE_LABELS[mode] || mode;
  }

  function updateRunnerState(status) {
    elements.runners.forEach((runner) => {
      const animatedAsset = runner.querySelector(".clock-asset-running");
      runner.dataset.runner = status;

      if (!animatedAsset) {
        return;
      }

      if (status === "running") {
        const animatedSrc = animatedAsset.dataset.animatedSrc;
        if (animatedSrc && !animatedAsset.getAttribute("src")) {
          animatedAsset.setAttribute("src", animatedSrc);
        }
        return;
      }

      animatedAsset.removeAttribute("src");
    });
  }

  function updateUi() {
    const total = Math.max(state.plannedDurationSeconds || 1, 1);
    const remaining = getRemainingSeconds();
    const nextTransition = getNextTransition(state.mode, state.cycleCount);

    state.remainingSeconds = remaining;
    elements.display.textContent = formatDuration(remaining);
    elements.progressBar.style.width = `${((total - remaining) / total) * 100}%`;
    elements.durationLabel.textContent = humanDuration(total);
    elements.statusPill.textContent = STATUS_LABELS[state.status] || state.status;

    elements.modeButtons.forEach((button) => {
      button.classList.toggle("is-active", button.dataset.mode === state.mode);
    });

    elements.presetButtons.forEach((button) => {
      button.classList.toggle("is-active", button.dataset.preset === getActivePreset());
    });

    if (elements.demoPresetButton) {
      elements.demoPresetButton.classList.toggle("hidden", !canUseDemoPreset());
    }

    elements.cycleNote.textContent = `Session #${state.cycleCount + 1}`;
    elements.nextModeNote.textContent = `Next: ${prettyMode(nextTransition.nextMode)}`;
    if (elements.testModeBadge) {
      elements.testModeBadge.classList.toggle("hidden", !canUseDemoPreset());
    }

    elements.start.disabled = state.status === "running";
    elements.pause.disabled = state.status !== "running";
    elements.resume.disabled = state.status !== "paused";
    elements.reset.disabled =
      state.status === "idle" &&
      state.remainingSeconds === state.plannedDurationSeconds;

    updateRunnerState(state.status);
  }

  function getRemainingSeconds() {
    if (state.status === "paused" || state.status === "idle" || state.status === "completed") {
      return state.remainingSeconds;
    }

    if (!state.expectedEndAtUtc) {
      return state.remainingSeconds;
    }

    const diff = Math.ceil(
      (new Date(state.expectedEndAtUtc).getTime() - Date.now()) / 1000,
    );
    return Math.max(diff, 0);
  }

  function stopPendingTransition() {
    if (transitionTimeoutId !== null) {
      window.clearTimeout(transitionTimeoutId);
      transitionTimeoutId = null;
    }
  }

  function startInterval() {
    stopInterval();
    intervalId = window.setInterval(() => {
      const remaining = getRemainingSeconds();
      state.remainingSeconds = remaining;
      if (remaining <= 0) {
        completeTimer();
        return;
      }
      persistState();
      updateUi();
    }, 1000);
  }

  function stopInterval() {
    if (intervalId !== null) {
      window.clearInterval(intervalId);
      intervalId = null;
    }
  }

  function generateSessionId() {
    if (window.crypto?.randomUUID) {
      return window.crypto.randomUUID();
    }
    return `session-${Date.now()}-${Math.floor(Math.random() * 1000)}`;
  }

  async function saveCompletedSession() {
    const completedAt = state.completedAtUtc || new Date().toISOString();
    const payload = {
      client_session_id: state.clientSessionId,
      mode: state.mode,
      planned_duration_seconds: state.plannedDurationSeconds,
      actual_duration_seconds: state.plannedDurationSeconds,
      started_at_utc: state.startedAtUtc,
      completed_at_utc: completedAt,
    };

    try {
      await window.pomodoroApi.post("/api/sessions", payload);
      state.completionSaved = true;
      persistState();
      elements.message.textContent = "Session saved to the database.";
      document.dispatchEvent(new Event("pomodoro:sessions-changed"));
    } catch (error) {
      if (error.status === 409) {
        state.completionSaved = true;
        persistState();
        elements.message.textContent = "This session was already saved.";
        return;
      }
      elements.message.textContent = `Could not save the session: ${error.message}`;
    }
  }

  function unlockAudio() {
    audioUnlocked = true;
  }

  function playSoundIfEnabled() {
    if (!settings?.sound_enabled || !audioUnlocked) {
      return;
    }

    try {
      const audioContext = new (window.AudioContext || window.webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      oscillator.type = "sine";
      oscillator.frequency.setValueAtTime(880, audioContext.currentTime);
      gainNode.gain.setValueAtTime(0.001, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.18, audioContext.currentTime + 0.02);
      gainNode.gain.exponentialRampToValueAtTime(0.0001, audioContext.currentTime + 0.4);
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      oscillator.start();
      oscillator.stop(audioContext.currentTime + 0.45);
    } catch (_error) {
      // Browser may block audio without prior interaction.
    }
  }

  function startTimer() {
    stopPendingTransition();
    audioUnlocked = true;
    const plannedDurationSeconds = getSelectedDurationForMode(state.mode);

    state = {
      ...defaultState(state.mode, {
        cycleCount: state.cycleCount,
        activePreset: getActivePreset(),
      }),
      status: "running",
      plannedDurationSeconds,
      remainingSeconds: plannedDurationSeconds,
      startedAtUtc: new Date().toISOString(),
      expectedEndAtUtc: new Date(
        Date.now() + plannedDurationSeconds * 1000,
      ).toISOString(),
      clientSessionId: generateSessionId(),
    };

    elements.message.textContent = `Timer started: ${PRESETS[getActivePreset()].label}.`;
    persistState();
    updateUi();
    startInterval();
  }

  function pauseTimer() {
    stopPendingTransition();
    state.remainingSeconds = getRemainingSeconds();
    state.status = "paused";
    state.expectedEndAtUtc = null;
    elements.message.textContent = "Timer paused.";
    stopInterval();
    persistState();
    updateUi();
  }

  function resumeTimer() {
    stopPendingTransition();
    state.status = "running";
    state.expectedEndAtUtc = new Date(
      Date.now() + state.remainingSeconds * 1000,
    ).toISOString();
    elements.message.textContent = "Timer resumed.";
    persistState();
    updateUi();
    startInterval();
  }

  function resetTimer() {
    stopInterval();
    stopPendingTransition();
    state = defaultState(state.mode, {
      cycleCount: state.cycleCount,
      activePreset: getActivePreset(),
    });
    elements.message.textContent = "Timer reset.";
    persistState();
    updateUi();
  }

  function prepareNextSession(nextMode, nextCycleCount, shouldAutoStart) {
    stopPendingTransition();
    state = defaultState(nextMode, {
      cycleCount: nextCycleCount,
      activePreset: getActivePreset(),
    });
    persistState();
    updateUi();

    if (!shouldAutoStart) {
      elements.message.textContent = `Next mode ready: ${prettyMode(nextMode)}.`;
      return;
    }

    transitionTimeoutId = window.setTimeout(() => {
      startTimer();
      elements.message.textContent = `Started automatically: ${prettyMode(nextMode)}.`;
    }, AUTO_ADVANCE_DELAY_MS);
  }

  async function completeTimer() {
    stopInterval();
    stopPendingTransition();
    state.status = "completed";
    state.remainingSeconds = 0;
    state.expectedEndAtUtc = null;
    state.completedAtUtc = new Date().toISOString();
    persistState();
    updateUi();
    playSoundIfEnabled();
    elements.message.textContent = `${prettyMode(state.mode)} session completed. Saving...`;
    await saveCompletedSession();

    const transition = getNextTransition(state.mode, state.cycleCount);
    prepareNextSession(
      transition.nextMode,
      transition.nextCycleCount,
      Boolean(settings?.auto_start_next_session),
    );
  }

  function changeMode(mode) {
    stopInterval();
    stopPendingTransition();
    state = defaultState(mode, {
      cycleCount: state.cycleCount,
      activePreset: getActivePreset(),
    });
    elements.message.textContent = `Selected mode: ${prettyMode(mode)}.`;
    persistState();
    updateUi();
  }

  function applyPreset(preset) {
    if (preset === "demo" && !canUseDemoPreset()) {
      return;
    }

    stopInterval();
    stopPendingTransition();
    state = defaultState(state.mode, {
      cycleCount: state.cycleCount,
      activePreset: preset,
    });
    elements.message.textContent = `Active preset: ${PRESETS[preset].label}.`;
    persistState();
    updateUi();
  }

  function restoreState() {
    if (!settings) {
      return;
    }

    if (!state) {
      state = defaultState();
    }

    state.activePreset = getActivePreset();

    if (state.status === "idle") {
      state.plannedDurationSeconds = getSelectedDurationForMode(state.mode);
      state.remainingSeconds = state.plannedDurationSeconds;
    }

    if (state.status === "running" && state.expectedEndAtUtc) {
      const remaining = getRemainingSeconds();
      if (remaining <= 0) {
        completeTimer();
        return;
      }
      state.remainingSeconds = remaining;
      startInterval();
    }

    if (state.status === "completed" && !state.completionSaved && state.clientSessionId) {
      saveCompletedSession();
    }

    persistState();
    updateUi();
  }

  elements.start.addEventListener("click", startTimer);
  elements.pause.addEventListener("click", pauseTimer);
  elements.resume.addEventListener("click", resumeTimer);
  elements.reset.addEventListener("click", resetTimer);

  elements.modeButtons.forEach((button) => {
    button.addEventListener("click", () => changeMode(button.dataset.mode));
  });

  elements.presetButtons.forEach((button) => {
    button.addEventListener("click", () => applyPreset(button.dataset.preset));
  });

  ["click", "keydown", "touchstart"].forEach((eventName) => {
    document.addEventListener(eventName, unlockAudio, { once: true });
  });

  document.addEventListener("pomodoro:settings-ready", (event) => {
    settings = event.detail;
    restoreState();
  });

  document.addEventListener("pomodoro:settings-updated", (event) => {
    settings = event.detail;
    state = defaultState(state?.mode || "work", {
      cycleCount: state?.cycleCount || 0,
      activePreset: getActivePreset(),
    });
    elements.message.textContent = "Timer settings updated.";
    persistState();
    updateUi();
  });
})();

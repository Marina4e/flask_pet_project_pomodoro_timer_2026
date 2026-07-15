(function () {
  const app = document.getElementById("calendar-app");
  if (!app) {
    return;
  }

  const elements = {
    monthLabel: document.getElementById("calendar-month-label"),
    timezoneNote: document.getElementById("calendar-timezone-note"),
    grid: document.getElementById("calendar-grid"),
    prevButton: document.getElementById("calendar-prev-button"),
    nextButton: document.getElementById("calendar-next-button"),
    selectedDateLabel: document.getElementById("selected-date-label"),
    selectedFocus: document.getElementById("selected-day-focus"),
    selectedWork: document.getElementById("selected-day-work"),
    selectedTotal: document.getElementById("selected-day-total"),
    sessionList: document.getElementById("day-session-list"),
  };

  const now = new Date();
  let currentYear = now.getFullYear();
  let currentMonth = now.getMonth() + 1;
  let timezone = "UTC";
  let selectedDate = null;

  function toIsoDate(year, month, day) {
    return `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
  }

  function isVisibleMonthDate(isoDate) {
    return isoDate.startsWith(`${currentYear}-${String(currentMonth).padStart(2, "0")}-`);
  }

  function defaultSelectedDateForVisibleMonth() {
    const today = new Date();
    const todayYear = today.getFullYear();
    const todayMonth = today.getMonth() + 1;

    if (currentYear === todayYear && currentMonth === todayMonth) {
      return toIsoDate(todayYear, todayMonth, today.getDate());
    }

    return toIsoDate(currentYear, currentMonth, 1);
  }

  function monthName(year, month) {
    return new Intl.DateTimeFormat("en-US", {
      month: "long",
      year: "numeric",
      timeZone: timezone,
    }).format(new Date(Date.UTC(year, month - 1, 1)));
  }

  function firstWeekdayOffset(year, month) {
    const day = new Date(Date.UTC(year, month - 1, 1)).getUTCDay();
    return day === 0 ? 6 : day - 1;
  }

  function renderMonth(summary) {
    const daysInMonth = new Date(summary.year, summary.month, 0).getDate();
    const offset = firstWeekdayOffset(summary.year, summary.month);
    const byDate = new Map(summary.days.map((item) => [item.date, item]));
    elements.grid.innerHTML = "";
    elements.monthLabel.textContent = monthName(summary.year, summary.month);
    elements.timezoneNote.textContent = `Timezone: ${timezone}`;
    const todayIso = new Intl.DateTimeFormat("en-CA", {
      timeZone: timezone,
    }).format(new Date());

    for (let index = 0; index < offset; index += 1) {
      const spacer = document.createElement("div");
      spacer.className = "calendar-day is-empty";
      elements.grid.appendChild(spacer);
    }

    for (let day = 1; day <= daysInMonth; day += 1) {
      const isoDate = toIsoDate(summary.year, summary.month, day);
      const info = byDate.get(isoDate) || {
        date: isoDate,
        session_count: 0,
        completed_work_sessions: 0,
        focus_minutes: 0,
        has_activity: false,
      };
      const button = document.createElement("button");
      button.type = "button";
      button.className = "calendar-day";
      if (info.has_activity) {
        button.classList.add("has-activity");
      }
      if (isoDate === todayIso) {
        button.classList.add("is-today");
      }
      if (selectedDate === isoDate) {
        button.classList.add("is-selected");
      }
      button.innerHTML = `
        <span class="calendar-day-number">${day}</span>
        <span class="calendar-day-meta">
          <span>${info.completed_work_sessions} work</span>
          <span>${info.focus_minutes} min</span>
        </span>
      `;
      button.addEventListener("click", () => selectDate(isoDate));
      elements.grid.appendChild(button);
    }
  }

  function renderDay(details) {
    selectedDate = details.date;
    elements.selectedDateLabel.textContent = details.date;
    elements.selectedFocus.textContent = details.focus_minutes;
    elements.selectedWork.textContent = details.completed_work_sessions;
    elements.selectedTotal.textContent = details.total_sessions;

    if (!details.sessions.length) {
      elements.sessionList.innerHTML =
        '<li class="muted-text">No sessions for this date.</li>';
      return;
    }

    const modeLabels = {
      work: "Work",
      short_break: "Short break",
      long_break: "Long break",
    };

    elements.sessionList.innerHTML = details.sessions
      .map(
        (session) => `
          <li>
            <strong>${modeLabels[session.mode] || session.mode}</strong><br>
            ${session.actual_duration_seconds} sec<br>
            ${session.started_at_local} → ${session.completed_at_local}
          </li>
        `,
      )
      .join("");
  }

  async function loadMonth() {
    const summary = await window.pomodoroApi.get(
      `/api/calendar/month?year=${currentYear}&month=${currentMonth}&timezone=${encodeURIComponent(timezone)}`,
    );
    renderMonth(summary);
    if (!selectedDate || !isVisibleMonthDate(selectedDate)) {
      selectedDate = defaultSelectedDateForVisibleMonth();
    }
    await selectDate(selectedDate);
  }

  async function selectDate(isoDate) {
    selectedDate = isoDate;
    const details = await window.pomodoroApi.get(
      `/api/calendar/day?date=${isoDate}&timezone=${encodeURIComponent(timezone)}`,
    );
    renderDay(details);
    await loadMonthWithoutSelectionReset();
  }

  async function loadMonthWithoutSelectionReset() {
    const summary = await window.pomodoroApi.get(
      `/api/calendar/month?year=${currentYear}&month=${currentMonth}&timezone=${encodeURIComponent(timezone)}`,
    );
    renderMonth(summary);
  }

  elements.prevButton.addEventListener("click", () => {
    currentMonth -= 1;
    if (currentMonth === 0) {
      currentMonth = 12;
      currentYear -= 1;
    }
    selectedDate = null;
    loadMonth().catch(() => {});
  });

  elements.nextButton.addEventListener("click", () => {
    currentMonth += 1;
    if (currentMonth === 13) {
      currentMonth = 1;
      currentYear += 1;
    }
    selectedDate = null;
    loadMonth().catch(() => {});
  });

  document.addEventListener("pomodoro:settings-ready", (event) => {
    timezone = event.detail.timezone;
    loadMonth().catch(() => {});
  });

  document.addEventListener("pomodoro:settings-updated", (event) => {
    timezone = event.detail.timezone;
    loadMonth().catch(() => {});
  });

  document.addEventListener("pomodoro:sessions-changed", () => {
    loadMonth().catch(() => {});
  });
})();

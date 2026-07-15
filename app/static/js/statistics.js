(function () {
  let chart = null;

  const elements = {
    todayFocus: document.getElementById("today-focus-minutes"),
    todayFocusHours: document.getElementById("today-focus-hours"),
    todayWork: document.getElementById("today-work-sessions"),
    todayTotal: document.getElementById("today-total-sessions"),
    weekFocus: document.getElementById("week-focus-minutes"),
    weekFocusHours: document.getElementById("week-focus-hours"),
    weekWork: document.getElementById("week-work-sessions"),
    weekTotal: document.getElementById("week-total-sessions"),
    monthFocus: document.getElementById("month-focus-minutes"),
    monthFocusHours: document.getElementById("month-focus-hours"),
    monthWork: document.getElementById("month-work-sessions"),
    monthTotal: document.getElementById("month-total-sessions"),
    todayLabel: document.getElementById("today-date-label"),
    weekLabel: document.getElementById("week-date-label"),
    monthLabel: document.getElementById("month-date-label"),
    chartCanvas: document.getElementById("productivity-chart"),
    timezoneNote: document.getElementById("chart-timezone-note"),
    chartCollapse: document.getElementById("productivity-chart-collapse"),
    chartToggle: document.getElementById("productivity-chart-toggle"),
  };

  function setupChartCollapse() {
    if (!elements.chartCollapse || !elements.chartToggle) {
      return;
    }

    elements.chartCollapse.addEventListener("shown.bs.collapse", () => {
      elements.chartToggle.textContent = "Hide chart";
      if (chart) {
        chart.resize();
      }
    });

    elements.chartCollapse.addEventListener("hidden.bs.collapse", () => {
      elements.chartToggle.textContent = "Show chart";
    });
  }

  function formatHours(minutes) {
    return `${(minutes / 60).toFixed(2)} h`;
  }

  function hasStatisticsUi() {
    return (
      elements.todayFocus ||
      elements.weekFocus ||
      elements.monthFocus ||
      elements.chartCanvas
    );
  }

  function updateSummary(prefix, summary) {
    const focusElement = elements[`${prefix}Focus`];
    const focusHoursElement = elements[`${prefix}FocusHours`];
    const workElement = elements[`${prefix}Work`];
    const totalElement = elements[`${prefix}Total`];
    const labelElement = elements[`${prefix}Label`];

    if (focusElement) focusElement.textContent = `${summary.focus_minutes} min`;
    if (focusHoursElement) {
      focusHoursElement.textContent = formatHours(summary.focus_minutes);
    }
    if (workElement) workElement.textContent = summary.completed_work_sessions;
    if (totalElement) {
      totalElement.textContent = `${summary.total_tracked_minutes} min`;
    }
    if (labelElement) {
      labelElement.textContent = `${summary.start_date} — ${summary.end_date}`;
    }
  }

  function renderChart(points) {
    if (!elements.chartCanvas || typeof Chart === "undefined") {
      return;
    }

    if (chart) {
      chart.destroy();
    }

    chart = new Chart(elements.chartCanvas, {
      type: "bar",
      data: {
        labels: points.map((item) => item.date),
        datasets: [
          {
            label: "Focus hours",
            data: points.map((item) => Number((item.focus_minutes / 60).toFixed(2))),
            backgroundColor: "rgba(255, 93, 54, 0.75)",
            borderRadius: 14,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: "Hours",
            },
          },
        },
      },
    });
  }

  async function loadStatistics(timezone) {
    if (!hasStatisticsUi()) {
      return;
    }

    const query = `?timezone=${encodeURIComponent(timezone)}`;
    const [today, week, month, chartData] = await Promise.all([
      window.pomodoroApi.get(`/api/statistics/today${query}`),
      window.pomodoroApi.get(`/api/statistics/week${query}`),
      window.pomodoroApi.get(`/api/statistics/month${query}`),
      window.pomodoroApi.get(`/api/statistics/chart${query}`),
    ]);

    updateSummary("today", today);
    updateSummary("week", week);
    updateSummary("month", month);
    renderChart(chartData.days);
    if (elements.timezoneNote) {
      elements.timezoneNote.textContent = timezone;
    }
  }

  document.addEventListener("pomodoro:settings-ready", (event) => {
    loadStatistics(event.detail.timezone).catch(() => {});
  });

  document.addEventListener("pomodoro:settings-updated", (event) => {
    loadStatistics(event.detail.timezone).catch(() => {});
  });

  document.addEventListener("pomodoro:sessions-changed", () => {
    const timezone = window.PomodoroSettings?.current?.timezone || "UTC";
    loadStatistics(timezone).catch(() => {});
  });

  setupChartCollapse();
})();

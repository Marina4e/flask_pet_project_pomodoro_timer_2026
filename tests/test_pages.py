from __future__ import annotations


def test_home_page_contains_expected_ui(client):
    response = client.get("/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Pomodoro Work Tracker" in html
    assert 'id="pomodoroPagesCarousel"' in html
    assert (
        'class="carousel-item active carousel-page-item carousel-page-item-timer"'
        in html
    )
    assert html.count('data-bs-slide-to="') == 5
    assert 'data-bs-slide="prev"' in html
    assert 'data-bs-slide="next"' in html
    assert html.count("bootstrap.min.css") == 1
    assert html.count("bootstrap.bundle.min.js") == 1
    assert 'href="/#timer-widget"' in html
    assert 'href="/statistics"' in html
    assert 'id="timer-widget"' in html
    assert 'id="skip-timer-button"' in html
    assert 'aria-label="Skip current focus or break"' in html
    assert 'href="/#settings-panel"' in html
    assert 'id="settings-panel"' in html
    assert "styles.css" in html
    assert "api.js" in html
    assert 'href="/calendar"' in html
    assert 'id="export-control"' in html
    assert 'id="google-calendar-card"' in html
    assert 'href="/#google-calendar-card"' in html
    assert 'id="google-sheets-card"' in html
    assert "Google Sheets Settings" in html
    assert 'id="google-sheets-enabled-input"' in html
    assert 'id="google-sheets-spreadsheet-id-input"' in html
    assert 'id="google-sheets-credentials-input"' not in html
    assert 'name="GOOGLE_SHEETS_CREDENTIALS_JSON"' not in html
    assert "Optional feature" in html
    assert "Required only when enabled" in html
    assert 'id="google-calendar-sync-button"' in html
    assert 'id="google-sheets-save-button"' in html
    assert 'id="google-sheets-sync-button"' in html
    assert 'lang="en"' in html
    assert "images/tomato-idle-transparent.png" in html
    timer_runner = html.split('id="timer-tomato-runner"', 1)[1].split("</div>", 1)[0]
    assert "images/tomato-idle.png" not in timer_runner
    assert "images/clock-face-static.png" in timer_runner
    assert "images/clock-face.gif" in timer_runner
    assert "Used for daily, weekly, and monthly statistics." in html


def test_calendar_page_renders(client):
    response = client.get("/calendar")

    assert response.status_code == 200
    assert "Activity Calendar" in response.get_data(as_text=True)


def test_swagger_page_renders(client):
    response = client.get("/api/docs")

    assert response.status_code == 200
    assert "SwaggerUIBundle" in response.get_data(as_text=True)


def test_not_found_page_returns_html(client):
    response = client.get("/missing-page")

    assert response.status_code == 404
    assert "Page not found" in response.get_data(as_text=True)

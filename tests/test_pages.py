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
    assert 'href="/#settings-panel"' in html
    assert 'id="settings-panel"' in html
    assert "styles.css" in html
    assert "api.js" in html
    assert 'href="/calendar"' in html
    assert 'id="export-control"' in html
    assert 'id="google-calendar-card"' in html
    assert 'href="/#google-calendar-card"' in html
    assert 'lang="en"' in html
    assert "images/tomato-idle.png" in html
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

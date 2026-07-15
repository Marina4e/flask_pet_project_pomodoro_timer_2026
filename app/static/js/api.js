(function () {
  async function request(url, options = {}) {
    const response = await fetch(url, {
      headers: {
        Accept: "application/json",
        ...(options.body ? { "Content-Type": "application/json" } : {}),
        ...(options.headers || {}),
      },
      ...options,
    });

    const contentType = response.headers.get("content-type") || "";
    const payload = contentType.includes("application/json")
      ? await response.json()
      : await response.text();

    if (!response.ok) {
      const error = payload?.error || {
        code: "request_failed",
        message: response.statusText,
        details: {},
      };
      throw Object.assign(new Error(error.message), {
        status: response.status,
        code: error.code,
        details: error.details,
      });
    }

    return payload;
  }

  window.pomodoroApi = {
    get(url) {
      return request(url, { method: "GET" });
    },
    post(url, data) {
      return request(url, { method: "POST", body: JSON.stringify(data) });
    },
    put(url, data) {
      return request(url, { method: "PUT", body: JSON.stringify(data) });
    },
    delete(url) {
      return request(url, { method: "DELETE" });
    },
  };
})();

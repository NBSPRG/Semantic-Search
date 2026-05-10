const healthStatus = document.querySelector("#healthStatus");
const ingestForm = document.querySelector("#ingestForm");
const searchForm = document.querySelector("#searchForm");
const ingestMessage = document.querySelector("#ingestMessage");
const searchMessage = document.querySelector("#searchMessage");
const results = document.querySelector("#results");
const clearResults = document.querySelector("#clearResults");
const ingestText = document.querySelector("#ingestText");
const metadata = document.querySelector("#metadata");
const query = document.querySelector("#query");
const topK = document.querySelector("#topK");

function setMessage(element, text, type = "") {
  element.textContent = text;
  element.className = `message ${type}`.trim();
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(data.detail)
      ? data.detail.map((item) => item.msg).join(", ")
      : data.detail || "Request failed";
    throw new Error(detail);
  }
  return data;
}

async function refreshHealth() {
  try {
    const data = await requestJson("/health");
    healthStatus.className = `status ${data.status === "ok" ? "ok" : "bad"}`;
    healthStatus.querySelector("span:last-child").textContent =
      data.status === "ok" ? "Ready" : "Degraded";
  } catch {
    healthStatus.className = "status bad";
    healthStatus.querySelector("span:last-child").textContent = "Offline";
  }
}

function parseMetadata(raw) {
  if (!raw.trim()) {
    return {};
  }
  const parsed = JSON.parse(raw);
  if (!parsed || Array.isArray(parsed) || typeof parsed !== "object") {
    throw new Error("Metadata must be a JSON object.");
  }
  return parsed;
}

function renderResults(items) {
  if (!items.length) {
    results.innerHTML = '<p class="empty">No similar records found.</p>';
    return;
  }

  results.innerHTML = items
    .map(
      (item) => `
        <article class="result">
          <div class="resultTop">
            <strong>#${item.id}</strong>
            <span class="score">${(item.similarity * 100).toFixed(1)}%</span>
          </div>
          <p class="recordText">${escapeHtml(item.text)}</p>
          <pre>${escapeHtml(JSON.stringify(item.metadata, null, 2))}</pre>
        </article>
      `,
    )
    .join("");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

ingestForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = ingestForm.querySelector("button");
  button.disabled = true;
  setMessage(ingestMessage, "Storing...");

  try {
    const payload = {
      text: ingestText.value.trim(),
      metadata: parseMetadata(metadata.value),
    };
    const data = await requestJson("/ingest", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setMessage(ingestMessage, `Stored record #${data.id}.`, "success");
    ingestText.value = "";
  } catch (error) {
    setMessage(ingestMessage, error.message, "error");
  } finally {
    button.disabled = false;
    refreshHealth();
  }
});

searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = searchForm.querySelector("button");
  button.disabled = true;
  setMessage(searchMessage, "Searching...");

  try {
    const payload = {
      query: query.value.trim(),
      top_k: Number(topK.value),
    };
    const data = await requestJson("/search", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    renderResults(data.results);
    setMessage(searchMessage, `Found ${data.results.length} result(s).`, "success");
  } catch (error) {
    setMessage(searchMessage, error.message, "error");
  } finally {
    button.disabled = false;
    refreshHealth();
  }
});

clearResults.addEventListener("click", () => {
  results.innerHTML = '<p class="empty">Search results will appear here.</p>';
  setMessage(searchMessage, "");
});

refreshHealth();

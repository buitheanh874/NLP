const DEFAULT_INPUT = [
  "great product and fast shipping",
  "terrible experience, support never replied",
  "not bad overall",
  "good but late delivery",
].join("\n");

const dom = {
  statusGrid: document.getElementById("status-grid"),
  inputText: document.getElementById("input-text"),
  includeTransformer: document.getElementById("include-transformer"),
  showNonPositiveOnly: document.getElementById("show-non-positive-only"),
  analyzeBtn: document.getElementById("analyze-btn"),
  sampleBtn: document.getElementById("sample-btn"),
  clearBtn: document.getElementById("clear-btn"),
  exportBtn: document.getElementById("export-btn"),
  runMessage: document.getElementById("run-message"),
  summaryPanel: document.getElementById("summary-panel"),
  distributionPanel: document.getElementById("distribution-panel"),
  resultsPanel: document.getElementById("results-panel"),
  issuesPanel: document.getElementById("issues-panel"),
  kpiGrid: document.getElementById("kpi-grid"),
  distributionBars: document.getElementById("distribution-bars"),
  attentionTableBody: document.querySelector("#attention-table tbody"),
  resultsHead: document.querySelector("#results-table thead"),
  resultsBody: document.querySelector("#results-table tbody"),
  issuesTableBody: document.querySelector("#issues-table tbody"),
  mismatchNote: document.getElementById("mismatch-note"),
};

let currentPredictions = [];
let currentTransformerLoaded = false;

function setMessage(text, isError = false) {
  dom.runMessage.textContent = text;
  dom.runMessage.style.color = isError ? "#a4361f" : "";
}

function setLoading(isLoading) {
  dom.analyzeBtn.disabled = isLoading;
  dom.analyzeBtn.textContent = isLoading ? "Analyzing..." : "Analyze";
}

function parseInputLines() {
  return dom.inputText.value
    .split("\n")
    .map((x) => x.trim())
    .filter(Boolean);
}

function formatProb(value) {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "N/A";
  }
  return Number(value).toFixed(3);
}

function labelPill(label) {
  const normalized = String(label || "").toLowerCase();
  return `<span class="pill ${normalized}">${label || "N/A"}</span>`;
}

function renderStatus(status) {
  const modelInfo = status?.classic?.model_info || {};
  const cards = [
    ["Classic K*", modelInfo.k_features ?? "N/A"],
    ["Thresholds", modelInfo.thresholds ?? "N/A"],
    ["Variant", modelInfo.variant ?? "N/A"],
    ["Issue Mode", status?.classic?.issue_mode ?? "N/A"],
    ["Transformer", status?.transformer?.message ?? "disabled"],
    ["Model Timestamp", modelInfo.trained_at ?? "N/A"],
  ];

  dom.statusGrid.innerHTML = cards
    .map(
      ([label, value]) => `
      <article class="status-card">
        <p class="status-label">${label}</p>
        <p class="status-value">${value}</p>
      </article>
    `
    )
    .join("");
}

function renderKpis(summary) {
  const items = [
    ["Inputs", summary.total, "neutral"],
    ["Flagged", summary.flagged, "alert"],
    ["Negative", summary.negative, "alert"],
    ["Uncertain", summary.uncertain, "neutral"],
    ["Positive", summary.positive, "good"],
  ];
  dom.kpiGrid.innerHTML = items
    .map(
      ([label, value, tone]) => `
        <article class="kpi-card ${tone}">
          <h3>${label}</h3>
          <p>${value}</p>
        </article>
      `
    )
    .join("");
}

function renderDistribution(distribution) {
  dom.distributionBars.innerHTML = distribution
    .map((row) => {
      const width = Math.max(2, Number(row.share_percent || 0));
      return `
        <div class="bar-row">
          <div class="bar-label">${row.label}</div>
          <div class="bar-track"><div class="bar-fill" style="width:${width}%"></div></div>
          <div class="bar-value">${row.count} (${row.share_percent}%)</div>
        </div>
      `;
    })
    .join("");
}

function renderAttentionQueue(rows) {
  if (!rows.length) {
    dom.attentionTableBody.innerHTML = `
      <tr><td colspan="5">No non-positive predictions in this batch.</td></tr>
    `;
    return;
  }

  dom.attentionTableBody.innerHTML = rows
    .map(
      (row) => `
      <tr>
        <td>${labelPill(row.classic_label)}</td>
        <td>${Number(row.risk_score).toFixed(1)}</td>
        <td>${formatProb(row.classic_probability)}</td>
        <td>${row.issue_summary || "-"}</td>
        <td>${row.text || ""}</td>
      </tr>
    `
    )
    .join("");
}

function resultColumns(includeTransformer) {
  const cols = [
    { key: "text", label: "Review Text" },
    { key: "classic_label", label: "Classic Label", type: "label" },
    { key: "classic_probability", label: "Classic P(+)", type: "prob" },
    { key: "classic_confidence", label: "Classic Confidence" },
    { key: "fallback_reason", label: "Fallback Reason" },
    { key: "issue_summary", label: "Issue Tags/Labels" },
    { key: "issue_count", label: "Issue Count" },
    { key: "risk_score", label: "Risk Score", type: "score" },
  ];

  if (includeTransformer) {
    cols.push(
      { key: "transformer_label", label: "Transformer Label", type: "label" },
      { key: "transformer_probability", label: "Transformer P(+)", type: "prob" },
      { key: "agreement", label: "Agreement" }
    );
  }

  return cols;
}

function renderResultsTable(rows, includeTransformer, nonPositiveOnly) {
  const cols = resultColumns(includeTransformer);
  const filtered = nonPositiveOnly
    ? rows.filter((r) => r.classic_label !== "POSITIVE")
    : rows;

  dom.resultsHead.innerHTML = `<tr>${cols.map((c) => `<th>${c.label}</th>`).join("")}</tr>`;

  if (!filtered.length) {
    dom.resultsBody.innerHTML = `<tr><td colspan="${cols.length}">No rows for current filter.</td></tr>`;
    return;
  }

  dom.resultsBody.innerHTML = filtered
    .map((row) => {
      const tds = cols.map((col) => {
        if (col.type === "label") {
          return `<td>${labelPill(row[col.key])}</td>`;
        }
        if (col.type === "prob") {
          return `<td>${formatProb(row[col.key])}</td>`;
        }
        if (col.type === "score") {
          const score = row[col.key];
          return `<td>${score === null || score === undefined ? "N/A" : Number(score).toFixed(1)}</td>`;
        }
        return `<td>${row[col.key] ?? "-"}</td>`;
      });
      return `<tr>${tds.join("")}</tr>`;
    })
    .join("");
}

function renderIssues(issueRows) {
  if (!issueRows.length) {
    dom.issuesTableBody.innerHTML = `<tr><td colspan="3">No issue labels predicted for this batch.</td></tr>`;
    return;
  }

  dom.issuesTableBody.innerHTML = issueRows
    .map(
      (row) => `
      <tr>
        <td>${row.label}</td>
        <td>${row.count}</td>
        <td>${Number(row.avg_confidence).toFixed(3)}</td>
      </tr>
    `
    )
    .join("");
}

function showResultPanels(show) {
  const method = show ? "remove" : "add";
  dom.summaryPanel.classList[method]("hidden");
  dom.distributionPanel.classList[method]("hidden");
  dom.resultsPanel.classList[method]("hidden");
  dom.issuesPanel.classList[method]("hidden");
}

function csvEscape(value) {
  if (value === null || value === undefined) {
    return "";
  }
  const str = String(value);
  if (str.includes(",") || str.includes('"') || str.includes("\n")) {
    return `"${str.replace(/"/g, '""')}"`;
  }
  return str;
}

function downloadCsv() {
  if (!currentPredictions.length) {
    setMessage("No predictions to export.", true);
    return;
  }

  const includeTransformer = currentTransformerLoaded;
  const cols = resultColumns(includeTransformer);
  const rows = dom.showNonPositiveOnly.checked
    ? currentPredictions.filter((r) => r.classic_label !== "POSITIVE")
    : currentPredictions;

  const header = cols.map((c) => c.key).join(",");
  const body = rows.map((r) => cols.map((c) => csvEscape(r[c.key])).join(",")).join("\n");
  const csv = `${header}\n${body}`;
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "review_predictions.csv";
  link.click();
  URL.revokeObjectURL(url);
}

async function fetchStatus() {
  try {
    const includeTransformer = dom.includeTransformer.checked;
    const response = await fetch(`/api/status?include_transformer=${includeTransformer}`);
    if (!response.ok) {
      throw new Error(`Status endpoint failed (${response.status})`);
    }
    const status = await response.json();
    renderStatus(status);
  } catch (error) {
    setMessage(`Cannot load model status: ${error.message}`, true);
  }
}

async function analyze() {
  const texts = parseInputLines();
  if (!texts.length) {
    setMessage("No valid input lines found.", true);
    showResultPanels(false);
    return;
  }

  setLoading(true);
  setMessage("Running inference...");

  try {
    const payload = {
      texts,
      include_transformer: dom.includeTransformer.checked,
    };
    const response = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.detail || "Prediction request failed.");
    }

    currentPredictions = data.predictions || [];
    currentTransformerLoaded = Boolean(data.status?.transformer?.loaded);
    renderStatus(data.status || {});
    renderKpis(data.summary || {});
    renderDistribution(data.label_distribution || []);
    renderAttentionQueue(data.attention_queue || []);
    renderResultsTable(
      currentPredictions,
      currentTransformerLoaded,
      dom.showNonPositiveOnly.checked
    );
    renderIssues(data.issue_summary || []);

    const mismatch = data.mismatch_count;
    if (mismatch === null || mismatch === undefined) {
      dom.mismatchNote.textContent = data.status?.transformer?.requested
        ? `Transformer unavailable: ${data.status?.transformer?.message || "unknown reason"}`
        : "Transformer disabled.";
    } else {
      dom.mismatchNote.textContent = `Transformer mismatches: ${mismatch}`;
    }

    showResultPanels(true);
    setMessage(`Done. Processed ${data.summary?.total ?? texts.length} reviews.`);
  } catch (error) {
    showResultPanels(false);
    setMessage(error.message, true);
  } finally {
    setLoading(false);
  }
}

function setInitialValues() {
  dom.inputText.value = DEFAULT_INPUT;
}

function attachEvents() {
  dom.analyzeBtn.addEventListener("click", analyze);
  dom.sampleBtn.addEventListener("click", () => {
    dom.inputText.value = DEFAULT_INPUT;
    setMessage("Sample loaded.");
  });
  dom.clearBtn.addEventListener("click", () => {
    dom.inputText.value = "";
    setMessage("Input cleared.");
  });
  dom.exportBtn.addEventListener("click", downloadCsv);
  dom.showNonPositiveOnly.addEventListener("change", () => {
    renderResultsTable(
      currentPredictions,
      currentTransformerLoaded,
      dom.showNonPositiveOnly.checked
    );
  });
  dom.includeTransformer.addEventListener("change", fetchStatus);
}

function init() {
  setInitialValues();
  attachEvents();
  fetchStatus();
}

init();

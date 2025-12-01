import { CONFIG } from "./config.js";

let chartInstance = null;
let heatmapChart = null;
let toastTimer = null;

const els = {
  modeLabel: () => document.getElementById("mode-label"),
  flowNote: () => document.getElementById("flow-note"),
  sendBtn: () => document.getElementById("send-btn"),
  sendText: () => document.getElementById("send-text"),
  sendSpinner: () => document.getElementById("send-spinner"),
  textarea: () => document.getElementById("user-input"),
  messages: () => document.getElementById("messages"),
  emptyState: () => document.getElementById("empty-state"),
  toast: () => document.getElementById("toast"),
  history: () => document.getElementById("history-list"),
  chartCanvas: () => document.getElementById("emotions-chart"),
  heatmapCanvas: () => document.getElementById("emotions-heatmap"),
  tips: () => document.getElementById("tips-list"),
};

const flowCopy = {
  chat: {
    title: "Mindful Chat",
    note: "Share how you feel. You'll get a grounded, empathic reply.",
  },
};

export function setMode(mode) {
  const label = flowCopy[mode]?.title || "Mindful Chat";
  els.modeLabel().textContent = label;
  els.flowNote().textContent = flowCopy[mode]?.note || flowCopy.chat.note;
}

export function setLoading(isLoading) {
  const btn = els.sendBtn();
  btn.disabled = isLoading;
  els.sendSpinner().classList.toggle("hidden", !isLoading);
  els.sendText().textContent = isLoading ? "Sending..." : "Send";
}

export function resetInput() {
  const textarea = els.textarea();
  textarea.value = "";
  textarea.focus();
}

export function showToast(message, type = "error") {
  const toast = els.toast();
  toast.textContent = message;
  toast.classList.remove("hidden");
  toast.classList.toggle("toast-error", type === "error");
  toast.classList.toggle("toast-success", type === "success");

  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.add("hidden");
  }, CONFIG.toastDurationMs);
}

export function hideToast() {
  const toast = els.toast();
  toast.classList.add("hidden");
}

const formatTimestamp = (ts) => {
  if (!ts) return "";
  try {
    const date = new Date(ts);
    return date.toLocaleString(undefined, {
      weekday: "short",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch (e) {
    return "";
  }
};

const renderSuggestions = (suggestions = []) => {
  if (!Array.isArray(suggestions) || suggestions.length === 0) return "";
  const items = suggestions
    .slice(0, 4)
    .map((s) => `<li class="suggestion-pill">${s}</li>`)
    .join("");
  return `<div class="suggestions"><div class="suggestions-label">Action suggestions</div><ul>${items}</ul></div>`;
};

export function renderMessages(messages) {
  const container = els.messages();
  if (!messages || messages.length === 0) {
    els.emptyState().classList.remove("hidden");
    container.innerHTML = "";
    return;
  }
  els.emptyState().classList.add("hidden");
  const ordered = [...messages].slice().reverse(); // newest first
  const items = ordered
    .map((msg) => {
      const roleClass = msg.role === "user" ? "msg-user" : "msg-assistant";
      const badge =
        msg.role === "user"
          ? `<span class="pill subtle">You</span>`
          : `<span class="pill accent">${(msg.mode || "chat").replace("-", " ")}</span>`;
      const suggestions = renderSuggestions(msg.suggestions);
      const emotionTags =
        Array.isArray(msg.emotions) && msg.emotions.length > 0
          ? `<div class="emotion-tags">${msg.emotions
              .slice(0, 4)
              .map((e) => `<span class="pill ghost">${e.label}: ${Math.round((e.score || 0) * 100)}%</span>`)
              .join("")}</div>`
          : "";
      return `
        <article class="message ${roleClass}">
          <header class="message-meta">
            ${badge}
            <span class="time">${formatTimestamp(msg.timestamp)}</span>
          </header>
          <div class="message-body">${(msg.text || "").replace(/\n/g, "<br>")}</div>
          ${suggestions}
          ${emotionTags}
        </article>
      `;
    })
    .join("");
  container.innerHTML = items;
}

export function renderStats(data) {
  // Deprecated in favor of renderCharts
}

function normalizeEmotionScores(messages) {
  const assistants = messages.filter((m) => m.role === "assistant" && Array.isArray(m.emotions) && m.emotions.length > 0);
  const recent = assistants.slice(-12).reverse(); // newest first for labels (#1 ...)
  if (recent.length === 0) {
    return { labels: [], series: [], heatmap: { labels: [], emotions: [], recent: [] } };
  }
  const labels = recent.map((_, idx) => `#${idx + 1}`);

  // collect all emotion labels
  const emotionSet = new Set();
  recent.forEach((msg) => msg.emotions.forEach((e) => emotionSet.add(e.label || "Unknown")));
  const emotions = Array.from(emotionSet);

  const series = emotions.map((emotion) => {
    const data = recent.map((msg) => {
      const found = msg.emotions.find((e) => e.label === emotion);
      return found ? found.score || 0 : 0;
    });
    return { label: emotion, data };
  });

  // pick top 4 emotions by max score to keep chart legible
  const topSeries = series
    .map((s) => ({ ...s, max: Math.max(...s.data) }))
    .sort((a, b) => b.max - a.max)
    .slice(0, 4)
    .map((s) => ({ label: s.label, data: s.data }));

  return { labels, series: topSeries, heatmap: { labels, emotions, recent } };
}

function renderLineChart(labels, series) {
  const canvas = els.chartCanvas();
  if (!canvas) return;
  if (chartInstance) {
    chartInstance.destroy();
    chartInstance = null;
  }
  if (!labels.length || !series.length) {
    canvas.getContext("2d").clearRect(0, 0, canvas.width, canvas.height);
    return;
  }
  const ctx = canvas.getContext("2d");

  chartInstance = new Chart(ctx, {
    type: "line",
    data: {
      labels,
      datasets: series.map((s, idx) => ({
        label: s.label,
        data: s.data,
        borderColor: ["#1fa99f", "#4fb3bf", "#7a8fbf", "#95b28f"][idx % 4],
        backgroundColor: "rgba(79, 179, 191, 0.08)",
        borderWidth: 2.2,
        tension: 0.32,
        fill: idx === 0,
      })),
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: true, labels: { boxWidth: 12 } },
        tooltip: { mode: "index", intersect: false },
      },
      scales: {
        y: { suggestedMin: 0, suggestedMax: 1, grid: { color: "rgba(0,0,0,0.05)" } },
        x: { grid: { display: false } },
      },
    },
  });
}

function renderHeatmapGrid(heatmap) {
  const canvas = els.heatmapCanvas();
  if (!canvas) return;
  const { labels, emotions, recent } = heatmap;
  if (!labels.length || !emotions.length) {
    canvas.innerHTML = '<div class="stats-source">No emotion data yet.</div>';
    return;
  }
  const colors = emotions.reduce((acc, emotion) => {
    acc[emotion] = "#1fa99f";
    return acc;
  }, {});

  const columns = labels.length + 1;
  let html = `<div class="heatmap-grid" style="grid-template-columns: repeat(${columns}, minmax(50px, 1fr));">`;
  html += '<div class="heatmap-cell heatmap-header"></div>';
  labels.forEach((label) => {
    html += `<div class="heatmap-cell heatmap-header">${label}</div>`;
  });
  emotions.forEach((emotion, eIdx) => {
    html += `<div class="heatmap-cell heatmap-row">${emotion}</div>`;
    labels.forEach((_, idx) => {
      const msg = recent[idx] || { emotions: [] };
      const found = msg.emotions.find((e) => e.label === emotion);
      const score = found ? Number(found.score || 0) : 0;
      const intensity = Math.min(1, Math.max(0, score));
      const bg = score ? `rgba(31,169,159,${0.15 + intensity * 0.7})` : "rgba(0,0,0,0.02)";
      html += `<div class="heatmap-cell" style="background:${bg}" title="${emotion}: ${(score * 100).toFixed(0)}%"></div>`;
    });
  });
  html += "</div>";
  canvas.innerHTML = html;
}

export function renderCharts(messages) {
  const normalized = normalizeEmotionScores(messages || []);
  renderLineChart(normalized.labels, normalized.series);
  renderHeatmapGrid(normalized.heatmap);
}

export function renderHistory(historyData) {
  const list = els.history();
  const items = historyData?.items || [];
  if (!list) return;
  if (items.length === 0) {
    list.innerHTML = `<li class="history-empty">No history yet.</li>`;
    return;
  }
  list.innerHTML = items
    .slice(0, 6)
    .map(
      (h) => `
      <li>
        <div>
          <div class="history-emotion">${h.emotion || "—"}</div>
          <div class="history-time">${formatTimestamp(h.timestamp)}</div>
        </div>
        <span class="pill ghost">${(h.mode || "").replace("-", " ")}</span>
      </li>
    `,
    )
    .join("");
}

export function renderTips() {
  const tips = [
    "Try a 3–minute grounding: name 3 things you see, hear, and feel.",
    "Short notes beat long rants—share specifics to get actionable steps.",
    "Slow your inhale, and make the exhale a touch longer.",
  ];
  els.tips().innerHTML = tips.map((t) => `<li>${t}</li>`).join("");
}

import { CONFIG } from "./config.js";
import { fetchHistory, requestChat } from "./api.js";
import { hideToast, renderCharts, renderHistory, renderMessages, renderTips, resetInput, setLoading, setMode, showToast } from "./ui.js";

const state = {
  mode: CONFIG.defaultMode || "chat",
  messages: [],
};

const textarea = document.getElementById("user-input");
const form = document.getElementById("chat-form");

const MIN_EMOTION_SCORE = 0.01;

const normalizeEmotions = (emotions) => {
  const cleanLabel = (label) => {
    if (!label) return "";
    const trimmed = String(label).trim();
    if (!trimmed) return "";
    return trimmed.charAt(0).toUpperCase() + trimmed.slice(1).toLowerCase();
  };

  const normalizeList = (list) =>
    list
      .filter((e) => e && e.label)
      .map((e) => {
        const scoreNum = typeof e.score === "number" ? e.score : Number(e.score) || 0;
        return { label: cleanLabel(e.label), score: scoreNum };
      })
      .filter((e) => e.label && e.score > MIN_EMOTION_SCORE);

  if (Array.isArray(emotions)) {
    return normalizeList(emotions);
  }
  if (emotions && typeof emotions === "object") {
    // handle {label,intensity,score,scores:{...}} or dict of label->score
    if (emotions.label && emotions.scores && typeof emotions.scores === "object") {
      return normalizeList(Object.entries(emotions.scores).map(([label, score]) => ({ label, score })));
    }
    return normalizeList(Object.entries(emotions).map(([label, score]) => ({ label, score })));
  }
  return [];
};

const normalizeSuggestions = (raw) => {
  if (!raw) return [];
  if (Array.isArray(raw)) return raw;
  if (typeof raw === "string") return raw.split(",").map((s) => s.trim()).filter(Boolean);
  return [];
};

function buildAssistantMessage(payload, mode) {
  const suggestions =
    normalizeSuggestions(payload.suggestions) ||
    normalizeSuggestions(payload.meta?.suggestedExercise) ||
    normalizeSuggestions(payload.meta?.suggestedExercises);

  const emotions = normalizeEmotions(payload.emotions || payload.emotion);

  return {
    role: "assistant",
    text: payload.reply || payload.message || payload.text || "I am here with you.",
    suggestions,
    emotions,
    timestamp: payload.timestamp || new Date().toISOString(),
    mode: payload.meta?.mode || mode,
  };
}

async function handleSubmit(event) {
  event.preventDefault();
  hideToast();
  const text = textarea.value.trim();
  if (!text || state.loading) return;
  state.loading = true;
  setLoading(true);

  state.messages.push({
    role: "user",
    text,
    timestamp: new Date().toISOString(),
    mode: state.mode,
  });
  renderMessages(state.messages);
  renderCharts(state.messages);

  const result = await requestChat(text, state.mode);
  if (!result.ok) {
    showToast(result.error || "服务暂时不可用，请稍后重试。");
    state.loading = false;
    setLoading(false);
    return;
  }

  const assistantMessage = buildAssistantMessage(result.data || {}, state.mode);
  state.messages.push(assistantMessage);
  renderMessages(state.messages);
  renderCharts(state.messages);

  refreshSidebars();
  resetInput();

  state.loading = false;
  setLoading(false);
}

function bindModeToggle() {
  // single-mode (chat) – nothing to toggle
}

function bindCollapsibles() {
  const toggles = document.querySelectorAll(".collapse-toggle");
  toggles.forEach((toggle) => {
    toggle.addEventListener("click", () => {
      const targetId = toggle.dataset.target;
      const panel = document.getElementById(targetId);
      const section = toggle.closest(".collapsible");
      if (!panel) return;
      const isExpanded = toggle.getAttribute("aria-expanded") === "true";
      toggle.setAttribute("aria-expanded", (!isExpanded).toString());
      toggle.textContent = isExpanded ? "Show" : "Hide";
      panel.classList.toggle("collapsed", isExpanded);
      section?.classList.toggle("collapsed", isExpanded);
    });
  });
}

const smoothScrollTo = (el, align = "start", yOffset = -12) => {
  if (!el) return;
  const rect = el.getBoundingClientRect();
  const targetY = rect.top + window.scrollY + yOffset;
  window.scrollTo({ top: targetY, behavior: "smooth" });
};

function bindNav() {
  const buttons = document.querySelectorAll(".nav button");
  const setActive = (btn) => {
    buttons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
  };

  buttons.forEach((btn) => {
    btn.addEventListener("click", () => {
      setActive(btn);
      const target = btn.dataset.target;
      if (target === "overview") {
        smoothScrollTo(document.getElementById("overview-section"), "start", -20);
        return;
      }
      if (target === "chat") {
        smoothScrollTo(document.getElementById("chat-card"), "start", -12);
        return;
      }
      if (target === "history") {
        const feed = document.getElementById("session-feed");
        smoothScrollTo(feed, "start", -12);
        const oldest = document.querySelector("#messages .message:last-child");
        if (oldest) {
          setTimeout(() => smoothScrollTo(oldest, "end", -40), 160);
        }
      }
    });
  });
}

async function refreshSidebars() {
  const historyRes = await fetchHistory();
  if (historyRes.ok) {
    renderHistory(historyRes.data);
  }
}

function bindForm() {
  form.addEventListener("submit", handleSubmit);
  textarea.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
      handleSubmit(e);
    }
  });
}

async function init() {
  setMode(state.mode);
  renderMessages(state.messages);
  renderCharts(state.messages);
  renderTips();
  bindModeToggle();
  bindForm();
  bindNav();
  bindCollapsibles();
  await refreshSidebars();
}

init();

import { CONFIG } from "./config.js";
import { fetchHistory, requestChat } from "./api.js";
import { hideToast, renderCharts, renderHistory, renderMessages, renderTips, resetInput, setLoading, setMode, showToast } from "./ui.js";

const state = {
  mode: CONFIG.defaultMode || "chat",
  messages: [],
};

const textarea = document.getElementById("user-input");
const form = document.getElementById("chat-form");

const normalizeEmotions = (emotions) => {
  if (Array.isArray(emotions)) {
    return emotions
      .filter((e) => e && e.label)
      .map((e) => ({ label: e.label, score: typeof e.score === "number" ? e.score : Number(e.score) || 0 }));
  }
  if (emotions && typeof emotions === "object") {
    // handle {label,intensity,score,scores:{...}} or dict of label->score
    if (emotions.label && emotions.scores && typeof emotions.scores === "object") {
      return Object.entries(emotions.scores).map(([label, score]) => ({ label, score: Number(score) || 0 }));
    }
    return Object.entries(emotions).map(([label, score]) => ({ label, score: Number(score) || 0 }));
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
  await refreshSidebars();
}

init();

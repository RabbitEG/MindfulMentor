import { CONFIG } from "./config.js";

const defaultHeaders = {
  "Content-Type": "application/json",
};

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const wrapError = (message, cause) => ({
  ok: false,
  error: message,
  cause,
});

const withTimeout = (promise, timeoutMs) => {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  return Promise.race([
    promise(controller.signal),
    new Promise((_, reject) => {
      setTimeout(() => reject(new Error("timeout")), timeoutMs);
    }),
  ]).finally(() => clearTimeout(timer));
};

const doFetch = async (path, options = {}) => {
  const url = `${CONFIG.apiBaseUrl}${path}`;
  const request = (signal) =>
    fetch(url, {
      ...options,
      headers: {
        ...defaultHeaders,
        ...(options.headers || {}),
      },
      signal,
    });
  const response = await withTimeout(request, CONFIG.requestTimeoutMs);
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`HTTP ${response.status}: ${text || "request failed"}`);
  }
  return response.json();
};

export async function requestChat(text, mode) {
  if (CONFIG.mockResponses) {
    return mockChat(text, mode);
  }
  try {
    const payload = await doFetch(CONFIG.endpoints.chat, {
      method: "POST",
      body: JSON.stringify({ text, mode }),
    });
    return { ok: true, data: payload };
  } catch (err) {
    if (CONFIG.fallbackToMockOnError) {
      return mockChat(text, mode, err);
    }
    return wrapError("服务暂时不可用，请稍后重试。", err);
  }
}

export async function fetchHistory() {
  try {
    const payload = await doFetch(CONFIG.endpoints.history, { method: "GET" });
    return { ok: true, data: payload };
  } catch (err) {
    return wrapError("无法获取历史记录。", err);
  }
}

export async function fetchStats() {
  if (CONFIG.mockResponses) {
    return mockStats();
  }
  try {
    const payload = await doFetch(CONFIG.endpoints.stats, { method: "GET" });
    return { ok: true, data: payload };
  } catch (err) {
    if (CONFIG.fallbackToMockOnError) {
      return mockStats(err);
    }
    return wrapError("无法获取情绪统计。", err);
  }
}

// ---------------------------------------------------------------------------
// Mock helpers (fallback-friendly)
// ---------------------------------------------------------------------------

const pick = (arr) => arr[Math.floor(Math.random() * arr.length)];

const mockEmotions = () => [
  { label: "Calm", score: 0.62 },
  { label: "Anxious", score: 0.24 },
  { label: "Tired", score: 0.18 },
  { label: "Hopeful", score: 0.15 },
];

async function mockChat(text, mode, cause) {
  await sleep(CONFIG.mockDelayMs);
  const suggestions = [
    "Take three slow inhales, exhale a touch longer than you inhale.",
    "List the top 3 things you can control this hour.",
    "Try a short body scan to release tension in shoulders.",
  ];
  return {
    ok: true,
    data: {
      reply: `I hear the pressure you're under. Let's break it down into small, doable steps so you can feel less stuck.\n\nI can stay with you while you move through this.`,
      emotions: mockEmotions(),
      suggestions,
      meta: {
        mode,
        source: "mock",
        cause: cause ? String(cause) : undefined,
      },
      trace_id: `mock-${Date.now()}`,
    },
  };
}

async function mockStats(cause) {
  await sleep(CONFIG.mockDelayMs);
  const labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  const values = labels.map(() => Number((0.2 + Math.random() * 0.65).toFixed(2)));
  return {
    ok: true,
    data: {
      labels,
      series: [
        { label: "Calm", data: values },
        { label: "Anxious", data: labels.map(() => Number((0.1 + Math.random() * 0.4).toFixed(2))) },
      ],
      meta: { source: "mock", cause: cause ? String(cause) : undefined },
    },
  };
}

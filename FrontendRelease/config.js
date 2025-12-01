export const CONFIG = {
  apiBaseUrl: "http://127.0.0.1:8003",
  endpoints: {
    chat: "/chat",
    history: "/history",
    stats: "/stats",
  },
  defaultMode: "chat",
  requestTimeoutMs: 60000,
  mockResponses: false,
  fallbackToMockOnError: true,
  mockDelayMs: 320,
  toastDurationMs: 4200,
};

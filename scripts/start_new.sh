#!/usr/bin/env bash

################################################################
# MindfulMentor — Stable Multi-Service Launcher
# - 不使用 set -e（避免因 pip/环境警告导致整脚本崩）
# - 自动暂时关闭所有代理（只在脚本内部生效）
# - 每次启动都会 pip install 确保依赖齐全
# - 每个服务独立启动 + 日志记录
################################################################

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${ROOT}/.venv"
LOG_DIR="${ROOT}/.logs"

# Temporarily disable proxies for this script to avoid blocking pip installs or localhost calls.
OLD_HTTP_PROXY="${http_proxy:-}"; OLD_HTTPS_PROXY="${https_proxy:-}"; OLD_ALL_PROXY="${ALL_PROXY:-}"
restore_proxy() {
  export http_proxy="${OLD_HTTP_PROXY}"
  export https_proxy="${OLD_HTTPS_PROXY}"
  export ALL_PROXY="${OLD_ALL_PROXY}"
}
trap restore_proxy EXIT
unset http_proxy https_proxy ALL_PROXY

mkdir -p "${LOG_DIR}"

################################################################
# LAUNCH FUNCTION
################################################################
launch() {
  local name="$1"
  local dir="$2"
  shift 2

  echo ">>> Starting ${name}..."
  (
    cd "${dir}" || exit 1
    "$@" > "${LOG_DIR}/${name}.log" 2>&1 &
    echo $! >> "${LOG_DIR}/pids"
  )
}

################################################################
# CLEAN OLD PID FILE
################################################################
rm -f "${LOG_DIR}/pids"

################################################################
# PORT GUARD
################################################################
free_port() {
  local port="$1"
  local pids
  if command -v lsof >/dev/null 2>&1; then
    pids=$(lsof -ti tcp:"${port}" || true)
    if [[ -n "${pids}" ]]; then
      echo ">>> Port ${port} in use by PID(s): ${pids}. Stopping to avoid collision..."
      kill ${pids} || true
      sleep 1
    fi
  else
    echo "!!! WARNING: 'lsof' not found. Skipping port pre-check for ${port}."
  fi
}

wait_port() {
  local port="$1"
  local name="$2"
  for _ in {1..40}; do
    if (echo >/dev/tcp/127.0.0.1/"${port}") >/dev/null 2>&1; then
      return 0
    fi
    sleep 0.5
  done
  echo "!!! ${name} did not open port ${port} in time."
  return 1
}

################################################################
# START SERVICES
################################################################

free_port 8001
launch "emotion"      "${ROOT}"    python -m EmotionService.App
wait_port 8001 "EmotionService" || exit 1

free_port 8002
launch "prompt"       "${ROOT}"    python -m PromptEngine.App
wait_port 8002 "PromptEngine" || exit 1

free_port 8004
launch "llm-gateway"  "${ROOT}"    python -m LlmGateway.App
wait_port 8004 "LlmGateway" || exit 1

free_port 8003
launch "orchestrator" "${ROOT}"    python -m Orchestrator.App
wait_port 8003 "Orchestrator" || exit 1

free_port 8501
# headless=true to stop streamlit from auto-opening random browser handlers; we open 8501 ourselves below.
launch "frontend"     "${ROOT}"    streamlit run "${ROOT}/FrontEnd/App.py" --server.port 8501 --server.address 127.0.0.1 --server.headless true
wait_port 8501 "FrontEnd" || exit 1


url="http://127.0.0.1:8501"

# 如果是 WSL 环境
if grep -qi "microsoft" /proc/version 2>/dev/null; then
    if command -v wslview >/dev/null 2>&1; then
        echo ">>> Detected WSL, opening in Windows browser via wslview..."
        wslview "$url" >/dev/null 2>&1 || {
            echo "!!! Failed to auto-open, please open manually: $url"
        }
    else
        echo ">>> Detected WSL but 'wslview' not installed."
        echo ">>> Please install it with: sudo apt install -y wslu"
        echo ">>> Or just open manually: $url"
    fi
else
    # 非 WSL：继续用 Python webbrowser（原来的逻辑）
    python - <<'PY'
import webbrowser

url = "http://127.0.0.1:8501"
try:
    opened = webbrowser.open(url, new=1)
    if opened:
        print(f">>> Opened browser: {url}")
    else:
        print(f"!!! Browser did not auto-open; please open manually: {url}")
except Exception as exc:  # pragma: no cover
    print(f"!!! Could not open browser automatically: {exc}")
    print(f"    Please open manually: {url}")
PY
fi


################################################################
# RESTORE PROXY (only for this shell)
################################################################
echo ">>> Restoring proxy for this shell..."
restore_proxy

echo ">>> All services started."
echo ">>> Logs: ${LOG_DIR}/*.log"

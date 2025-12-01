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

mkdir -p "${LOG_DIR}"

export PYTHONPATH="${ROOT}:${PYTHONPATH:-}"

echo ">>> Activating venv..."
source "${VENV}/bin/activate" || {
    echo "!!! ERROR: virtualenv not found at ${VENV}"
    exit 1
}

################################################################
# SMART DEPENDENCY CHECK
################################################################
# Only install if requirements have changed or packages are missing
REQUIREMENTS_FILE="${ROOT}/requirements.txt"
INSTALL_MARKER="${VENV}/.installed_requirements_hash"

should_install() {
  # If marker doesn't exist, need to install
  if [[ ! -f "${INSTALL_MARKER}" ]]; then
    return 0
  fi
  
  # Check if requirements.txt has changed
  local current_hash
  current_hash=$(md5sum "${REQUIREMENTS_FILE}" | cut -d' ' -f1)
  local saved_hash
  saved_hash=$(cat "${INSTALL_MARKER}" 2>/dev/null || echo "")
  
  if [[ "${current_hash}" != "${saved_hash}" ]]; then
    return 0
  fi
  
  # Quick sanity check: verify key packages are installed
  python -c "import fastapi, streamlit, transformers" 2>/dev/null || return 0
  
  return 1
}

if should_install; then
  echo ">>> Installing/updating dependencies..."
  pip install -q -r "${REQUIREMENTS_FILE}"
  md5sum "${REQUIREMENTS_FILE}" | cut -d' ' -f1 > "${INSTALL_MARKER}"
  echo ">>> Dependencies installed."
else
  echo ">>> Dependencies already satisfied (skipping pip install)."
fi

################################################################
# EMOTION MODEL CHECK
################################################################
MODEL_DIR="${ROOT}/EmotionService/.models/facebook--bart-large-mnli"
if [[ ! -d "${MODEL_DIR}" ]] || [[ -z "$(ls -A "${MODEL_DIR}" 2>/dev/null)" ]]; then
  echo ">>> Emotion model not found. Downloading..."
  python "${ROOT}/EmotionService/download_models.py" || {
    echo "!!! WARNING: Model download failed. Service may not work properly."
  }
else
  echo ">>> Emotion model already cached."
fi

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
  pids=$(lsof -ti tcp:"${port}" 2>/dev/null || true)
  if [[ -n "${pids}" ]]; then
    echo ">>> Port ${port} in use by PID(s): ${pids}. Stopping to avoid collision..."
    # Use kill -9 to force kill, then wait for port to be freed
    kill -9 ${pids} 2>/dev/null || true
    
    # Wait up to 3 seconds for port to be released
    for i in {1..6}; do
      sleep 0.5
      if ! lsof -ti tcp:"${port}" >/dev/null 2>&1; then
        echo ">>> Port ${port} freed."
        return 0
      fi
    done
    
    echo "!!! WARNING: Port ${port} may still be in use."
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
}

################################################################
# START SERVICES
################################################################

free_port 8001
launch "emotion"      "${ROOT}"    python -m EmotionService.App
wait_port 8001 "EmotionService"

free_port 8002
launch "prompt"       "${ROOT}"    python -m PromptEngine.App
wait_port 8002 "PromptEngine"

free_port 8004
launch "llm-gateway"  "${ROOT}"    python -m LlmGateway.App
wait_port 8004 "LlmGateway"

free_port 8003
launch "orchestrator" "${ROOT}"    python -m Orchestrator.App
wait_port 8003 "Orchestrator"

free_port 8501
# headless=true to stop streamlit from auto-opening random browser handlers; we open 8501 ourselves below.
launch "frontend"     "${ROOT}"    streamlit run "${ROOT}/FrontEnd/App.py" --server.port 8501 --server.address 127.0.0.1 --server.headless true
wait_port 8501 "FrontEnd"


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
export http_proxy="${OLD_HTTP_PROXY}"
export https_proxy="${OLD_HTTPS_PROXY}"
export ALL_PROXY="${OLD_ALL_PROXY}"

echo ">>> All services started."
echo ">>> Logs: ${LOG_DIR}/*.log"

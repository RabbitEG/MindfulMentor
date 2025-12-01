#!/usr/bin/env bash

################################################################
# MindfulMentor — Stable Multi-Service Launcher
# - 不使用 set -e（避免因 pip/环境警告导致整脚本崩）
# - 启动时暂时关闭代理（只在脚本内部生效）
# - 支持 venv / python / python3 三种方式找解释器
# - 每个服务独立启动 + 日志记录 + 端口检测
################################################################

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${ROOT}/.venv"
LOG_DIR="${ROOT}/.logs"
ENV_FILE="${ROOT}/.env"

mkdir -p "${LOG_DIR}"

################################################################
# 清理环境（原 ClearEnv.sh 内容）
################################################################
echo ">>> Cleaning MindfulMentor processes and ports..."
PORTS=(8001 8002 8003 8004 8501)

kill_by_port() {
  local port="$1"
  if command -v lsof >/dev/null 2>&1; then
    local pids
    pids=$(lsof -t -i:"$port" || true)
    if [[ -n "$pids" ]]; then
      echo "  - Killing port $port (PIDs: $pids)"
      kill -9 $pids 2>/dev/null || true
    fi
  elif command -v fuser >/dev/null 2>&1; then
    echo "  - Killing port $port via fuser"
    fuser -k "${port}/tcp" 2>/dev/null || true
  else
    echo "  ! Neither lsof nor fuser found, cannot kill by port $port"
  fi
}

for p in "${PORTS[@]}"; do
  kill_by_port "$p"
done

pkill -f "streamlit run App.py" 2>/dev/null || true
pkill -f "uvicorn App:app" 2>/dev/null || true
pkill -f "MindfulMentor/LlmGateway" 2>/dev/null || true
pkill -f "MindfulMentor/Orchestrator" 2>/dev/null || true
pkill -f "MindfulMentor/EmotionService" 2>/dev/null || true

rm -f "${LOG_DIR}/pids" 2>/dev/null || true
: > "${LOG_DIR}/orchestrator.log" 2>/dev/null || true
: > "${LOG_DIR}/prompt.log" 2>/dev/null || true
: > "${LOG_DIR}/emotion.log" 2>/dev/null || true
: > "${LOG_DIR}/frontend.log" 2>/dev/null || true
: > "${LOG_DIR}/llm-gateway.log" 2>/dev/null || true

echo ">>> Done. Environment cleaned."

################################################################
# 代理处理：脚本期间关闭代理，退出时恢复
################################################################
OLD_HTTP_PROXY="${http_proxy:-}"
OLD_HTTPS_PROXY="${https_proxy:-}"
OLD_ALL_PROXY="${ALL_PROXY:-}"

restore_proxy() {
  export http_proxy="${OLD_HTTP_PROXY}"
  export https_proxy="${OLD_HTTPS_PROXY}"
  export ALL_PROXY="${OLD_ALL_PROXY}"
}

trap restore_proxy EXIT
unset http_proxy https_proxy ALL_PROXY

################################################################
# Python 解释器选择 + PYTHONPATH
################################################################

export PYTHONPATH="${ROOT}:${PYTHONPATH:-}"

# 优先使用 venv，其次系统 python，再次 python3
if [[ -x "${VENV}/bin/python" ]]; then
  PYTHON_BIN="${VENV}/bin/python"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="python"
elif command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="python3"
else
  echo "!!! No python / python3 found in PATH. Abort."
  exit 1
fi

# 如果你想强制启用 venv + 自动 pip install，可以取消下面这一块的注释：
echo ">>> Activating venv at ${VENV} (if present)..."
if [[ -f "${VENV}/bin/activate" ]]; then
  # shellcheck source=/dev/null
  source "${VENV}/bin/activate"
else
  echo "!!! WARNING: venv not found at ${VENV}, using ${PYTHON_BIN} without venv."
fi

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
# Keep in sync with EmotionService/download_models.py default path
MODEL_DIR="${ROOT}/EmotionService/.models/bart-large-mnli"
if [[ ! -d "${MODEL_DIR}" ]] || [[ -z "$(ls -A "${MODEL_DIR}" 2>/dev/null)" ]]; then
  echo ">>> Emotion model not found. Downloading..."
  python "${ROOT}/EmotionService/download_models.py" || {
    echo "!!! WARNING: Model download failed. Service may not work properly."
  }
else
  echo ">>> Emotion model already cached."
fi

################################################################
# ENV FILE (.env)
################################################################
ensure_env_files() {
  if [[ ! -f "${ENV_FILE}" ]]; then
    cat > "${ENV_FILE}" <<'EOF'
# MindfulMentor environment (LLM + misc). Fill in real values as needed.
LLM_PROVIDER=
LLM_API_KEY=
LLM_BASE_URL=
LLM_API_MODEL=gpt-3.5-turbo
LLM_TIMEOUT=60
# LLM_LOCAL_MODEL=sshleifer/tiny-gpt2
EOF
    echo ">>> Created ${ENV_FILE} (includes LLM settings)."
  fi
}

load_env_files() {
  set -a
  [[ -f "${ENV_FILE}" ]] && source "${ENV_FILE}"
  set +a
  if [[ -f "${ROOT}/.env.llm" ]]; then
    echo ">>> Note: .env.llm detected but ignored; merge its values into ${ENV_FILE}."
  fi
}

apply_llm_defaults() {
  local provider_lower="${LLM_PROVIDER,,}"
  local api_key="${LLM_API_KEY:-}"
  local missing_llm=0

  if [[ -z "${LLM_PROVIDER:-}" ]]; then
    missing_llm=1
  elif [[ "${provider_lower}" =~ ^(api|openai|deepseek|openai-compatible)$ ]] && [[ -z "${api_key}" ]]; then
    missing_llm=1
  fi

  export LLM_TIMEOUT="${LLM_TIMEOUT:-60}"

  if [[ ${missing_llm} -eq 1 ]]; then
    export LLM_PROVIDER="tiny-local"
    export LLM_API_KEY=""
    export LLM_BASE_URL=""
    export LLM_API_MODEL="${LLM_API_MODEL:-gpt-3.5-turbo}"
    export LLM_LOCAL_MODEL="${LLM_LOCAL_MODEL:-sshleifer/tiny-gpt2}"
    echo ">>> LLM config missing; using toy model (tiny-local). Edit ${ENV_FILE} to use your real API."
  else
    echo ">>> Using LLM provider '${LLM_PROVIDER}' from ${ENV_FILE}."
  fi
}

ensure_env_files
load_env_files
apply_llm_defaults

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
  return 1
}

################################################################
# START SERVICES
################################################################

free_port 8001
launch "emotion"      "${ROOT}"    "${PYTHON_BIN}" -m EmotionService.App
wait_port 8001 "EmotionService" || exit 1

free_port 8002
launch "prompt"       "${ROOT}"    "${PYTHON_BIN}" -m PromptEngine.App
wait_port 8002 "PromptEngine" || exit 1

free_port 8004
launch "llm-gateway"  "${ROOT}"    python -m LlmGateway.App
wait_port 8004 "LlmGateway" || exit 1

free_port 8003
launch "orchestrator" "${ROOT}"    python -m Orchestrator.App
wait_port 8003 "Orchestrator" || exit 1

free_port 8501
# headless=true to stop streamlit from auto-opening random browser handlers; we open 8501 ourselves below.
launch "frontend"     "${ROOT}"    streamlit run "${ROOT}/FrontendDeveloper/App.py" --server.port 8501 --server.address 127.0.0.1 --server.headless true
wait_port 8501 "FrontendDeveloper" || exit 1


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

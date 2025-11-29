#!/usr/bin/env bash
set -e

# 找到项目根目录（scripts 的上一级）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo ">>> Cleaning MindfulMentor processes and ports..."

# 这几个是你项目用的端口：llm-gateway / orchestrator / emotion / frontend
PORTS=(8002 8003 8004 8501)

kill_by_port() {
  local port="$1"
  # 优先用 lsof，Ubuntu 默认有；没有再尝试 fuser
  if command -v lsof >/dev/null 2>&1; then
    PIDS=$(lsof -t -i:"$port" || true)
    if [ -n "$PIDS" ]; then
      echo "  - Killing port $port (PIDs: $PIDS)"
      kill -9 $PIDS 2>/dev/null || true
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

# 再兜底杀一些典型进程名（防止换端口或命令行写法变化）
pkill -f "streamlit run App.py" 2>/dev/null || true
pkill -f "uvicorn App:app" 2>/dev/null || true
pkill -f "MindfulMentor/LlmGateway" 2>/dev/null || true
pkill -f "MindfulMentor/Orchestrator" 2>/dev/null || true
pkill -f "MindfulMentor/EmotionService" 2>/dev/null || true

# 清理 PID 文件和旧日志（可选）
rm -f "$PROJECT_ROOT/.logs/pids" 2>/dev/null || true
# 如果你想每次都把日志清空，放开下面三行；不想清就注释掉
: > "$PROJECT_ROOT/.logs/orchestrator.log" 2>/dev/null || true
: > "$PROJECT_ROOT/.logs/prompt.log"       2>/dev/null || true
: > "$PROJECT_ROOT/.logs/emotion.log"      2>/dev/null || true
: > "$PROJECT_ROOT/.logs/frontend.log"     2>/dev/null || true

echo ">>> Done. Environment cleaned."

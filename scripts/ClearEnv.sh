#!/usr/bin/env bash
set -e

# 找到项目根目录（scripts 的上一级）
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo ">>> Cleaning MindfulMentor processes and ports..."

# 项目使用的端口：emotion(8001), prompt(8002), orchestrator(8003), llm-gateway(8004), frontend(8501)
PORTS=(8001 8002 8003 8004 8501)

kill_by_port() {
  local port="$1"
  # 优先用 lsof，Ubuntu 默认有；没有再尝试 fuser
  if command -v lsof >/dev/null 2>&1; then
    PIDS=$(lsof -t -i:"$port" 2>/dev/null || true)
    if [ -n "$PIDS" ]; then
      echo "  - Killing port $port (PIDs: $PIDS)"
      kill -9 $PIDS 2>/dev/null || true
      # Wait for process to actually die
      sleep 0.3
    fi
  elif command -v fuser >/dev/null 2>&1; then
    echo "  - Killing port $port via fuser"
    fuser -k -9 "${port}/tcp" 2>/dev/null || true
    sleep 0.3
  else
    echo "  ! Neither lsof nor fuser found, cannot kill by port $port"
  fi
}

for p in "${PORTS[@]}"; do
  kill_by_port "$p"
done

# 再兜底杀一些典型进程名（防止换端口或命令行写法变化）
pkill -9 -f "streamlit run.*App.py" 2>/dev/null || true
pkill -9 -f "uvicorn.*App:app" 2>/dev/null || true
pkill -9 -f "EmotionService.App" 2>/dev/null || true
pkill -9 -f "PromptEngine.App" 2>/dev/null || true
pkill -9 -f "LlmGateway.App" 2>/dev/null || true
pkill -9 -f "Orchestrator.App" 2>/dev/null || true

# Give processes time to fully terminate
sleep 0.5

# 清理 PID 文件和旧日志（可选）
rm -f "$PROJECT_ROOT/.logs/pids" 2>/dev/null || true
# 如果你想每次都把日志清空，放开下面几行；不想清就注释掉
: > "$PROJECT_ROOT/.logs/orchestrator.log" 2>/dev/null || true
: > "$PROJECT_ROOT/.logs/prompt.log"       2>/dev/null || true
: > "$PROJECT_ROOT/.logs/emotion.log"      2>/dev/null || true
: > "$PROJECT_ROOT/.logs/llm-gateway.log"  2>/dev/null || true
: > "$PROJECT_ROOT/.logs/frontend.log"     2>/dev/null || true

echo ">>> Done. Environment cleaned."

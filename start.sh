#!/bin/bash
# 即梦AI - 快捷启动脚本
# 同时启动后端（FastAPI）和前端（Vite）

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BACKEND_DIR="$SCRIPT_DIR/jimeng-ai-webapp/backend"
FRONTEND_DIR="$SCRIPT_DIR/jimeng-ai-webapp/frontend"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cleanup() {
    echo -e "\n${YELLOW}正在关闭服务...${NC}"
    [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null
    [ -n "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null
    wait 2>/dev/null
    echo -e "${GREEN}服务已关闭${NC}"
    exit 0
}
trap cleanup SIGINT SIGTERM

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  即梦AI - 启动中...${NC}"
echo -e "${GREEN}========================================${NC}"

# 1. 启动后端
echo -e "\n${YELLOW}[1/2] 启动后端 (FastAPI :8000)...${NC}"
cd "$BACKEND_DIR"
python main.py &
BACKEND_PID=$!
sleep 2

if kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${GREEN}  ✓ 后端已启动: http://localhost:8000${NC}"
    echo -e "${GREEN}  ✓ API 文档: http://localhost:8000/docs${NC}"
else
    echo -e "${RED}  ✗ 后端启动失败！${NC}"
    exit 1
fi

# 2. 启动前端
echo -e "\n${YELLOW}[2/2] 启动前端 (Vite :5173)...${NC}"
cd "$FRONTEND_DIR"
npm run dev &
FRONTEND_PID=$!
sleep 3

if kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${GREEN}  ✓ 前端已启动: http://localhost:5173${NC}"
else
    echo -e "${RED}  ✗ 前端启动失败！${NC}"
    cleanup
    exit 1
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}  全部启动完成！${NC}"
echo -e "${GREEN}  前端: http://localhost:5173${NC}"
echo -e "${GREEN}  后端: http://localhost:8000${NC}"
echo -e "${GREEN}  API文档: http://localhost:8000/docs${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "${YELLOW}按 Ctrl+C 关闭所有服务${NC}"

wait

@echo off
REM Family Accounting 后端启动脚本
REM 用于 Windows Server 服务启动

REM 切换到项目目录
cd /d C:\Apps\FamilyAccounting

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 启动 FastAPI 服务
uvicorn app.main:app --host 0.0.0.0 --port 8000

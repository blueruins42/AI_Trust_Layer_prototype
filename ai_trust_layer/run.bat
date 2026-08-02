@echo off
cd /d %~dp0
call .venv\Scripts\activate.bat
taskkill /F /IM streamlit.exe >nul 2>&1
streamlit run app.py --server.port 8600

@echo off
echo Starting DevSecOps Tools Backend...
cd backend
python -m uvicorn app.main:app --reload --port 8000

@echo off
cd /d C:\Users\m.laghari\Documents\Projects\meeting_note_taker\python-service
C:\Users\m.laghari\AppData\Local\miniconda3\python.exe -m uvicorn src.server:app --host 127.0.0.1 --port 9877

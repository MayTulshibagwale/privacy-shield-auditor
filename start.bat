@echo off
title Privacy Shield Auditor - Backend Server

echo.
echo  =====================================================
echo    Privacy Shield Auditor — Starting Backend Server
echo  =====================================================
echo.
echo  Keep this window open while using the extension.
echo  Close it when you are done for the day.
echo.

python server.py

echo.
echo  Server stopped. Press any key to close this window.
pause > nul
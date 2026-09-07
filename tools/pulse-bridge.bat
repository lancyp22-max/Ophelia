@echo off
set MODE=%1
if "%MODE%"=="" set MODE=status

if /I "%MODE%"=="status" (
  echo [Ophelia] Pulse bridge online
  echo Mission: Render the Ophelia SVG module.
  goto :eof
)

if /I "%MODE%"=="sync" (
  echo [Ophelia] Syncing seeds -^> substrate index
  echo Source: seeds/sample-seed.json
  echo Target: ophelia_lumaria_substrate.yaml
  goto :eof
)

echo Usage: tools\pulse-bridge.bat [status^|sync]
exit /b 1

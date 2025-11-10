@echo off
echo ============================================================
echo    OLLAMA WARM-UP - Pre-carregando modelo na memoria
echo ============================================================
echo.
echo Isso vai fazer o modelo responder MUITO mais rapido depois!
echo.
echo Modelo: llama3.2:1b
echo Primeira chamada: ~5s (carregando)
echo Proximas chamadas: ~1-2s (ja carregado!)
echo.
echo ============================================================
echo.

curl http://localhost:11434/api/generate -d "{\"model\": \"llama3.2:1b\", \"prompt\": \"Test\", \"stream\": false}"

echo.
echo.
echo ============================================================
echo    MODELO CARREGADO! Agora vai responder RAPIDO!
echo ============================================================
echo.
pause

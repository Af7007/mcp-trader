@echo off
echo ============================================================
echo GOLD LOSS ZERO GAME - Sistema de Predicao M1 OTIMIZADO
echo ============================================================
echo.
echo CONFIGURACAO OTIMIZADA:
echo - Timeframe: M1 (1 minuto)
echo - Volume: 0.02 lotes
echo - SL Inicial: $5.00 (aumentado para M1)
echo - Trailing Step: $0.20 (mais robusto)
echo - Worker: 0.5 segundo (2x mais rapido)
echo - Max Posicoes: 1 (evita acumular perdas)
echo.
echo FILTROS DE SEGURANCA:
echo 1. Confirmacao de tendencia M5 (OBRIGATORIO)
echo 2. Momentum minimo 0.01%% em M1
echo 3. Preco deve estar acima/abaixo da media
echo 4. Evita volatilidade extrema (2x media)
echo 5. Requer 3 de 5 candles na mesma direcao
echo.
echo TRAILING AGRESSIVO:
echo - Ativa quando positiva (lucro ^> $0)
echo - Sobe a cada $0.20
echo - Worker verifica a cada 0.5s
echo.
echo ============================================================
echo.

cd /d "%~dp0"
python src\agents\gold_loss_zero_game.py

pause

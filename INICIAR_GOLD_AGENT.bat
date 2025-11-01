@echo off
cd /d "C:\mcp-trader"
title GOLD_AGENT - XAUUSDm
uv run python src\agents\btc_hedge_agent.py XAUUSDm --volume 0.01

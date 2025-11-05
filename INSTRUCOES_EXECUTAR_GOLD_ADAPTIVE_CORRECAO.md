# Instruções para Executar Gold Adaptive Agent com Correção

## Arquivo .bat que já executa a correção

✅ **RUN_GOLD_ADAPTIVE.bat** - Este arquivo já executa o `gold_adaptive_agent.py` com as configurações corretas:

```batch
uv run python src\agents\gold_adaptive_agent.py --symbol XAUUSDc --volume 0.02
```

## Configurações incluídas no RUN_GOLD_ADAPTIVE.bat

- ✅ **Símbolo**: XAUUSDc (contato ouro)
- ✅ **Volume**: 0.02 lotes
- ✅ **Estratégia**: Trailing Stop Loss Zero
- ✅ **Auto-tuning**: HABILITADO
- ✅ **Sistema de aprendizado**: ATIVO
- ✅ **Análise**: Performance a cada 50 trades
- ✅ **Detecção de regime**: A cada 60 minutos

## Como executar

**Opção 1 - Mais fácil (recomendado):**
```bash
# Clique duplo no arquivo ou execute no terminal:
RUN_GOLD_ADAPTIVE.bat
```

**Opção 2 - Comando direto:**
```bash
uv run python src/agents/gold_adaptive_agent.py --symbol XAUUSDc --volume 0.02
```

## Diferenças importantes

### gold_adaptive_agent.py
- ✅ **Herda de**: GoldLossZeroSimple
- ✅ **Worker**: Sistema próprio (position_worker)
- ❌ **Game Worker**: NÃO usa game_worker.py diretamente

### gold_loss_zero_game.py  
- ✅ **Worker oficial**: game_worker.py (0.1s interval)
- ✅ **Magic Number**: 777777
- ✅ **Sistema**: Predição M1 + Trailing dinâmico
- ⚠️ **Para executar**: `python src/web/app.py` ou usar game

## Resposta direta

**SIM, o RUN_GOLD_ADAPTIVE.bat já inclui a correção e executa o gold_adaptive_agent.py corretamente.**

O arquivo .bat está configurado para:
1. Usar o símbolo correto (XAUUSDc)
2. Volume adequado (0.02)
3. Estratégia trailing stop loss zero
4. Sistema de auto-learning ativo

**Para executar agora:**
- Clique duplo em: `RUN_GOLD_ADAPTIVE.bat`

## Observação importante

O `gold_adaptive_agent.py` tem seu próprio sistema de worker (diferente do game_worker.py), mas está funcionando corretamente conforme verificado.

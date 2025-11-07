# 📊 Guia do Visualizador BTC Loss Zero

**Data**: 2025-11-01
**Status**: ✅ IMPLEMENTADO E PRONTO PARA USO
**Versão**: 1.0

---

## 🎯 Objetivo

O **EA_BTC_Loss_Zero_Visualizer.mq5** é um Expert Advisor visual que mostra **em tempo real** as linhas de trading do agente BTC Loss Zero diretamente no gráfico do MetaTrader 5.

**Visualização Inclui:**
- 🔵 **Linha de Entrada** (Entry Price) - Onde a posição foi aberta
- 🔴 **Linha de SL** (Stop Loss) - Proteção de $4 máximo
- 🟢 **Linha de TP** (Take Profit) - Alvo de ~$20
- 🟡 **Linha de Trailing Stop** (dinâmica) - Defende o lucro acumulado

---

## 🚀 Como Usar

### Passo 1: Iniciar o Agente Python

```batch
# Iniciar o agente BTC Loss Zero
python EXECUTAR_LOSS_ZERO.py
```

ou

```batch
# Testar primeiro
python TESTAR_LOSS_ZERO.py
```

O agente começará a exportar dados para `btc_loss_zero_data.json` a cada 15 segundos.

### Passo 2: Abrir o MT5 e Adicionar o EA ao Gráfico

1. **Abrir MT5**
2. **Abrir gráfico do BTCUSDc** (qualquer timeframe)
3. **Abrir MetaEditor** (F4)
4. **Abrir o arquivo**: `EA_BTC_Loss_Zero_Visualizer.mq5`
5. **Compilar** (F7)
   - Se houver erros, verifique a sintaxe
   - Deve aparecer: "0 error(s), 0 warning(s)"
6. **Voltar ao MT5**
7. **Navegador** (Ctrl+N) → **Expert Advisors** → Arrastar `EA_BTC_Loss_Zero_Visualizer` para o gráfico BTCUSDc
8. **Permitir AutoTrading** (botão verde no topo) - apenas para permitir que o EA rode, ele não abre posições
9. **Verificar** que apareceu um sorriso 😊 no canto superior direito do gráfico

### Passo 3: Monitorar em Tempo Real

O visualizador atualizará **automaticamente a cada 5 segundos** mostrando:

**Painel de Informações (canto superior esquerdo):**
```
=== BTC LOSS ZERO AGENT ===
Status: TRADING / ANALYZING
Position: BUY #110583019
Entry: 110220.00
Current: 110235.50
Profit: $15.50
Trailing: ACTIVE ($14.50)
Trail Level: 110230.50
SL: 110216.00 ($4 max)
TP: 110240.00 (~$20)
Last update: 12:34:56
```

**Linhas no Gráfico:**
- 🔵 **Linha Azul** (Entry): Preço onde a posição foi aberta
- 🔴 **Linha Vermelha** (SL): Stop Loss atual ($4 proteção)
- 🟢 **Linha Verde** (TP): Take Profit (~$20 alvo)
- 🟡 **Linha Amarela Tracejada** (Trailing): Nível do trailing stop dinâmico

---

## ⚙️ Configurações do EA

Ao adicionar o EA ao gráfico, você pode ajustar:

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `DataFilePath` | `C:\mcp-trader\btc_loss_zero_data.json` | Caminho do arquivo JSON |
| `UpdateIntervalSeconds` | 5 | Intervalo de atualização (segundos) |
| `ShowEntryLine` | true | Mostrar linha de entrada |
| `ShowSLLine` | true | Mostrar linha de SL |
| `ShowTPLine` | true | Mostrar linha de TP |
| `ShowTrailingLine` | true | Mostrar linha de trailing |
| `ShowInfoPanel` | true | Mostrar painel de informações |
| `EntryLineColor` | Azul | Cor da linha de entrada |
| `SLLineColor` | Vermelho | Cor da linha de SL |
| `TPLineColor` | Verde | Cor da linha de TP |
| `TrailingLineColor` | Amarelo | Cor da linha de trailing |

---

## 📋 Arquivo JSON Exportado

O agente Python exporta os dados para `C:\mcp-trader\btc_loss_zero_data.json`:

```json
{
  "timestamp": "2025-11-01T12:34:56.789012",
  "symbol": "BTCUSDc",
  "current_price": 110235.5,
  "has_position": true,
  "trailing_active": true,
  "trailing_amount_dollars": 14.5,
  "entry_price": 110220.0,
  "entry_ticket": 110583019,
  "position_type": "BUY",
  "sl": 110216.0,
  "tp": 110240.0,
  "profit": 15.5,
  "trailing_stop_level": 110230.5
}
```

---

## 🔄 Como Funciona

### Fluxo de Dados

```
┌─────────────────────────────────────────────────────────┐
│ 1. AGENTE PYTHON (btc_loss_zero_otimizado.py)         │
│    ├─ Analisa mercado (RSI + MFI)                     │
│    ├─ Abre/gerencia posições                          │
│    ├─ Calcula trailing stop dinâmico                  │
│    └─ Exporta dados → btc_loss_zero_data.json        │
└─────────────────────────────────────────────────────────┘
                         ⬇️
┌─────────────────────────────────────────────────────────┐
│ 2. ARQUIVO JSON (btc_loss_zero_data.json)             │
│    └─ Atualizado a cada 15 segundos                   │
└─────────────────────────────────────────────────────────┘
                         ⬇️
┌─────────────────────────────────────────────────────────┐
│ 3. EA VISUALIZADOR (EA_BTC_Loss_Zero_Visualizer.mq5)  │
│    ├─ Lê JSON a cada 5 segundos                       │
│    ├─ Desenha linhas no gráfico                       │
│    └─ Atualiza painel de informações                  │
└─────────────────────────────────────────────────────────┘
```

### Ciclo de Atualização

1. **Python Agent** (a cada 15s):
   - Executa ciclo de análise
   - Gerencia posições
   - Exporta dados para JSON

2. **EA Visualizador** (a cada 5s):
   - Lê arquivo JSON
   - Atualiza linhas no gráfico
   - Atualiza painel de info

**Resultado**: Visualização quase em tempo real com latência máxima de 5-15 segundos.

---

## 🎨 Exemplo de Visualização

```
Gráfico BTCUSDc M5:

     TP 🟢━━━━━━━━━━━━━━━━━━━━━━━ 110240.00 (~$20 alvo)
      |
      |    Trailing 🟡╍╍╍╍╍╍╍╍╍╍╍╍ 110230.50 (defendendo $14.50)
      |
 Current Price: 110235.50 💰 +$15.50
      |
  Entry 🔵━━━━━━━━━━━━━━━━━━━━━━ 110220.00 (BUY #110583019)
      |
      |
     SL 🔴━━━━━━━━━━━━━━━━━━━━━━━ 110216.00 ($4 max loss)


Painel Info:
┌─────────────────────────────┐
│ === BTC LOSS ZERO AGENT === │
│ Status: TRADING             │
│ Position: BUY #110583019    │
│ Entry: 110220.00            │
│ Current: 110235.50          │
│ Profit: $15.50 ✅           │
│ Trailing: ACTIVE ($14.50)   │
│ Trail Level: 110230.50      │
│ SL: 110216.00 ($4 max)      │
│ TP: 110240.00 (~$20)        │
│ Last update: 12:34:56       │
└─────────────────────────────┘
```

---

## ❌ Solução de Problemas

### Problema: EA não mostra informações

**Causa**: Arquivo JSON não encontrado

**Solução**:
1. Verificar que o agente Python está rodando
2. Verificar que o arquivo existe: `C:\mcp-trader\btc_loss_zero_data.json`
3. Verificar o caminho no parâmetro `DataFilePath` do EA

### Problema: Linhas não aparecem no gráfico

**Causa 1**: Sem posição aberta
- **Normal**: As linhas só aparecem quando há uma posição ativa

**Causa 2**: Arquivo JSON desatualizado
- **Solução**: Reiniciar o agente Python

### Problema: "Erro ao abrir arquivo"

**Causa**: Caminho incorreto

**Solução**:
1. Verificar que o caminho está correto: `C:\mcp-trader\btc_loss_zero_data.json`
2. No EA, clicar com botão direito → Propriedades
3. Verificar parâmetro `DataFilePath`
4. Ajustar se necessário

### Problema: Painel não atualiza

**Causa**: UpdateIntervalSeconds muito alto

**Solução**:
1. Remover EA do gráfico
2. Adicionar novamente
3. Ajustar `UpdateIntervalSeconds` para 5 (ou menos)

---

## 🧪 Testar Sem Agente Real

Você pode testar o visualizador sem rodar o agente real criando um arquivo JSON manualmente:

```batch
# Criar arquivo de teste
echo { > C:\mcp-trader\btc_loss_zero_data.json
echo   "timestamp": "2025-11-01T12:00:00", >> C:\mcp-trader\btc_loss_zero_data.json
echo   "symbol": "BTCUSDc", >> C:\mcp-trader\btc_loss_zero_data.json
echo   "current_price": 110235.5, >> C:\mcp-trader\btc_loss_zero_data.json
echo   "has_position": true, >> C:\mcp-trader\btc_loss_zero_data.json
echo   "trailing_active": true, >> C:\mcp-trader\btc_loss_zero_data.json
echo   "trailing_amount_dollars": 14.5, >> C:\mcp-trader\btc_loss_zero_data.json
echo   "entry_price": 110220.0, >> C:\mcp-trader\btc_loss_zero_data.json
echo   "entry_ticket": 999999, >> C:\mcp-trader\btc_loss_zero_data.json
echo   "position_type": "BUY", >> C:\mcp-trader\btc_loss_zero_data.json
echo   "sl": 110216.0, >> C:\mcp-trader\btc_loss_zero_data.json
echo   "tp": 110240.0, >> C:\mcp-trader\btc_loss_zero_data.json
echo   "profit": 15.5, >> C:\mcp-trader\btc_loss_zero_data.json
echo   "trailing_stop_level": 110230.5 >> C:\mcp-trader\btc_loss_zero_data.json
echo } >> C:\mcp-trader\btc_loss_zero_data.json
```

---

## 📝 Checklist de Uso

- [ ] Agente Python rodando (`python EXECUTAR_LOSS_ZERO.py`)
- [ ] Arquivo JSON sendo criado (`btc_loss_zero_data.json` existe)
- [ ] MT5 aberto com gráfico BTCUSDc
- [ ] EA compilado sem erros (F7 no MetaEditor)
- [ ] EA adicionado ao gráfico
- [ ] AutoTrading ativado (botão verde)
- [ ] Painel de informações visível
- [ ] Linhas aparecendo quando há posição

---

## 🎯 Benefícios

✅ **Visualização em Tempo Real**: Veja exatamente onde estão SL, TP e trailing stop
✅ **Sem Intervenção**: Totalmente automático
✅ **Informações Claras**: Painel mostra todos os dados importantes
✅ **Trailing Dinâmico**: Linha amarela sobe conforme o trailing avança
✅ **Múltiplos Símbolos**: Pode ter várias instâncias do EA em diferentes gráficos
✅ **Customizável**: Cores, posições e intervalos configuráveis

---

## 📚 Arquivos Relacionados

| Arquivo | Descrição |
|---------|-----------|
| `src/agents/btc_loss_zero_otimizado.py` | Agente Python (exporta dados) |
| `EA_BTC_Loss_Zero_Visualizer.mq5` | EA visualizador (MT5) |
| `btc_loss_zero_data.json` | Dados exportados (gerado automaticamente) |
| `EXECUTAR_LOSS_ZERO.py` | Script para iniciar o agente |
| `TESTAR_LOSS_ZERO.py` | Script de teste do agente |
| `RESUMO_FINAL_COMPLETO.txt` | Documentação completa do agente |

---

## 🚀 Próximos Passos

1. **Iniciar o agente Python**
   ```batch
   python EXECUTAR_LOSS_ZERO.py
   ```

2. **Adicionar EA ao gráfico BTCUSDc no MT5**

3. **Monitorar as operações em tempo real** 📊

4. **Observar o trailing stop subindo dinamicamente** 🟡

5. **Acompanhar o lucro acumulado** 💰

---

**Status**: ✅ PRONTO PARA USO

**Última Atualização**: 2025-11-01
**Versão**: 1.0 (Inicial)

---

**IMPORTANTE**: O visualizador NÃO abre posições. Ele apenas mostra as linhas das posições abertas pelo agente Python. O agente Python é quem controla toda a lógica de trading.

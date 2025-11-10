# Quick Start - BTC AI Agent v3.0.0

## Configuracao Rapida (5 minutos)

### 1. Obter API Key do Claude Haiku

1. Acesse: https://console.anthropic.com/
2. Crie uma conta (se nao tiver)
3. Va em API Keys
4. Clique em "Create Key"
5. Copie a chave (comeca com `sk-ant-...`)

### 2. Configurar .env

Abra `.env` e substitua:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

Por:

```env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxx
```

(Cole sua chave real acima)

### 3. Testar Configuracao

```batch
python test_btc_ai_config.py
```

Se mostrar `[OK] API configurada corretamente`, pode prosseguir!

### 4. Executar Agente AI

```batch
RUN_BTC_AI.bat
```

---

## Comparacao: v2.0.0 (Tecnico) vs v3.0.0 (IA)

### v2.0.0 - Analise Tecnica
```
[M5 BUY] Score: 4.5
  RSI: 45.2 (neutro)
  MACD: 0.15 (positivo)
  SMA20 > SMA50: True
  Momentum: +0.12%
  Volume spike: False

Decisao: BUY (score >= 4.0)
```

### v3.0.0 - Analise IA
```
[IA M5] Analisando ultimas 10 velas...

Claude responde:
  Direcao: BUY
  Score: 4.8
  Razao: "Padrao martelo invertido na vela 2,
         seguido de rompimento com volume.
         Rejeicao clara de baixa em $95000."

Decisao: BUY (score >= 4.0)
```

**Diferenca**: IA reconhece PADROES (martelo, engolfo, pin bar), nao apenas numeros.

---

## Custos

### Tier Free (Comeco)
- Limite: 50 requisicoes/minuto
- Custo: ~$0.001/analise
- 100 trades/dia = $3/mes
- **Suficiente para comecar**

### Tier 1 (Se escalar)
- Limite: 1000 req/min
- Custo: Mesmo ($0.001/analise)
- Ilimitado para uso normal

---

## Quando Usar IA vs Tecnico

### Use v3.0.0 (IA) se:
- Mercado lateral/complexo
- Quer reconhecer padroes graficos
- Pode pagar $3/mes
- Internet estavel

### Use v2.0.0 (Tecnico) se:
- Mercado em tendencia clara
- Quer custo zero
- Internet instavel
- Prefere velocidade maxima

---

## Fallback Automatico

Se API Key nao configurada, o agente v3.0.0 automaticamente volta para analise tecnica v2.0.0:

```
[AVISO] ANTHROPIC_API_KEY nao configurada no .env
        Usando analise tecnica como fallback

[M5 BUY] Score: 4.2 (analise tecnica)
```

**Seguranca**: Nunca para de funcionar!

---

## Monitorar Custos

1. Acesse: https://console.anthropic.com/
2. Va em "Usage"
3. Veja total gasto no mes

**Estimativa**:
- 10 trades/dia = $0.30/mes
- 50 trades/dia = $1.50/mes
- 100 trades/dia = $3.00/mes

---

## Executar Ambos (Comparacao)

**Terminal 1** (Tecnico):
```batch
RUN_BTC_V2.bat
```

**Terminal 2** (IA):
```batch
RUN_BTC_AI.bat
```

Apos 20-30 trades cada, compare:
- Win rate
- Avg win/loss
- Net result
- Tipos de trades acertados

Use `python analyze_btc_results.py` para comparacao automatica.

---

## Proximo Passo

1. Configure API Key no .env
2. Teste: `python test_btc_ai_config.py`
3. Execute: `RUN_BTC_AI.bat`
4. Aguarde 20-30 trades
5. Compare resultados com v2.0.0

**Documentacao Completa**: Ver `BTC_AI_README.md` e `COMPARACAO_TECNICO_VS_IA.md`

# Dashboard de Trades

## 📊 Visualize Todos os Seus Trades

Um dashboard web completo para visualizar, analisar e monitorar o histórico de todas as suas operações de trading.

---

## 🚀 Como Iniciar

### Opção 1: Script Windows (Recomendado)
```batch
RUN_DASHBOARD.bat
```

### Opção 2: Python Direto
```bash
uv run python src/web/dashboard.py
```

### Opção 3: Com uv
```bash
uv run python -m src.web.dashboard
```

---

## 🌐 Acessar o Dashboard

Abra seu navegador e vá para:
```
http://localhost:3001
```

**Nota**: O dashboard roda na porta 3001 (não confundir com a web app na porta 3000)

---

## 📈 Funcionalidades

### 1. **Estatísticas Gerais** (Topo)

Cartões com informações resumidas:
- **Total de Trades**: Número total de operações
- **Operações Vencedoras**: Quantas tiveram lucro
- **Operações Perdedoras**: Quantas tiveram prejuízo
- **Taxa de Acerto**: Porcentagem de wins (w/total)
- **Lucro Total**: Soma de todos os lucros/prejuízos
- **Lucro Médio**: Média por operação
- **Maior Lucro**: Trade mais lucrativo
- **Maior Prejuízo**: Trade mais prejudicial

### 2. **Gráficos Interativos**

#### 📈 Lucro Acumulado
Mostra a evolução do patrimônio ao longo do tempo. Curva suave que permite visualizar se o agente está tendendo para cima ou para baixo.

#### 💹 Performance por Símbolo
Gráfico de barras comparando lucro/prejuízo de cada símbolo:
- Verde: Lucro
- Vermelho: Prejuízo
- Altura: Quantidade de lucro/prejuízo

#### 📊 Últimos 7 Dias
Número de trades realizados em cada dia da última semana. Útil para ver padrões de atividade.

#### ✅ Win vs Loss
Gráfico de rosca (pie chart) mostrando proporção de trades vencedores vs perdedores.

### 3. **Histórico Detalhado de Trades**

Tabela completa com informações de cada trade:
- **ID**: Identificador único no banco
- **Ticket**: Número do ticket no MT5
- **Símbolo**: Qual ativo foi negociado (BTCUSDm, EURUSDc, etc)
- **Tipo**: BUY (verde) ou SELL (vermelho)
- **Volume**: Quantidade de lotes
- **Entrada**: Preço de abertura
- **Saída**: Preço de fechamento
- **Abertura**: Data/hora exata da abertura
- **Fechamento**: Data/hora exata do fechamento
- **SL**: Stop Loss utilizado
- **TP**: Take Profit utilizado
- **Lucro**: Resultado ($) - verde se positivo, vermelho se negativo

### 4. **Filtros e Busca**

**Filtro por Símbolo**:
- Dropdown no topo da tabela
- Mostra apenas trades do símbolo selecionado
- Opção "Todos" para ver tudo

### 5. **Paginação**

- 50 trades por página
- Botões "Anterior" e "Próxima"
- Indicador de página atual
- Suporta voltar e avançar entre páginas

---

## 📊 Exemplos de Análise

### Exemplo 1: Identificar Símbolo Mais Lucrativo
1. Veja o gráfico "Performance por Símbolo"
2. Procure a barra mais alta em verde
3. Use o filtro para ver APENAS esse símbolo
4. Analise os trades individuais

### Exemplo 2: Verificar Winning Streak
1. Veja a tabela de trades
2. Procure sequências de "Lucro" positivo
3. Note o padrão de entrada/saída
4. Identifique qual timeframe estava funcionando

### Exemplo 3: Avaliar Gerenciamento de Risco
1. Veja coluna "SL" vs "Entrada" (distância)
2. Veja coluna "TP" vs "Entrada" (distância)
3. Verifique se risk/reward era consistente
4. Compare com a coluna "Lucro"

### Exemplo 4: Performance Diária
1. Veja o gráfico "Últimos 7 Dias"
2. Identifique qual dia teve mais trades
3. Use a tabela para filtrar por data (futura melhoria)
4. Compare lucro daquele dia com média

---

## 🔧 APIs Disponíveis

Se quiser integrar com outro sistema, há APIs disponíveis:

### GET /api/stats
Retorna estatísticas gerais.

**Resposta**:
```json
{
  "total_trades": 150,
  "wins": 102,
  "losses": 48,
  "total_profit": 250.50,
  "avg_profit": 1.67,
  "max_profit": 5.20,
  "min_profit": -2.10,
  "win_rate": 68.0,
  "by_symbol": [
    {"symbol": "BTCUSDm", "count": 75, "profit": 180.30},
    {"symbol": "EURUSDc", "count": 50, "profit": 45.20}
  ],
  "last_7_days": [
    {"date": "2025-10-20", "count": 20, "profit": 35.50},
    {"date": "2025-10-21", "count": 22, "profit": 40.20}
  ]
}
```

### GET /api/trades?limit=50&offset=0&symbol=BTCUSDm
Retorna lista paginada de trades.

### GET /api/performance
Retorna performance por símbolo e tipo.

### GET /api/equity-curve
Retorna curva de patrimônio ao longo do tempo.

### GET /api/symbols
Retorna lista de símbolos com trades.

---

## 🎨 Design e Layout

### Cores
- **Verde**: Sucesso, lucro, positivo
- **Vermelho**: Perda, negativo
- **Azul**: Informações
- **Laranja**: Avisos

### Responsivo
- Desktop: Layout em grid completo
- Tablet: Ajusta para 2 colunas
- Mobile: Coluna única (com scroll horizontal na tabela)

### Dark Mode
- Tema escuro por padrão
- Contraste adequado para leitura
- Fundo gradiente

---

## 🔄 Atualização em Tempo Real

- **Estatísticas**: Atualizadas a cada 30 segundos automaticamente
- **Gráficos**: Recarregam ao mudar filtro
- **Tabela**: Recarrega ao mudar página ou filtro
- **Banco de dados**: Reflete dados em tempo real

---

## 📋 Dados Exibidos

Todos os dados vêm do banco SQLite (`trades.db`):

```sql
SELECT
  id, ticket, symbol, type, volume,
  open_price, close_price, open_time, close_time,
  sl, tp, profit, comment
FROM trades
```

---

## ⚙️ Requisitos Técnicos

- **Banco de dados**: SQLite (trades.db)
- **Framework**: Flask
- **Charts**: Chart.js (CDN)
- **Port**: 3001
- **Browser**: Chrome, Firefox, Safari, Edge (moderno)

---

## 🚀 Extensões Possíveis

### Filtro por Data
Seria possível adicionar:
```html
<input type="date" id="dateFilter">
```

### Exportar CSV
Botão para baixar dados em CSV:
```
📥 Exportar CSV
```

### Mais Gráficos
- Distribuição de lucro (histograma)
- Drawdown máximo
- Razão Sharpe
- Análise de horários (qual hora funciona melhor)

### Dashboard em Tempo Real
Integração com agente para atualizar enquanto está rodando.

---

## 🐛 Solução de Problemas

### "Conexão recusada na porta 3001"
**Solução**:
- Certifique-se que o script está rodando
- Tente `http://localhost:3001` exatamente
- Verifique se a porta 3001 não está em uso

### "Tabela vazia"
**Solução**:
- Certifique-se que tem trades no banco
- Execute um agente primeiro: `RUN_BTC_AGENT.bat`
- Aguarde algumas operações serem concluídas

### "Gráficos em branco"
**Solução**:
- Atualize o navegador (F5)
- Limpe cache (Ctrl+Shift+Del)
- Tente outro navegador

### "Erro 500"
**Solução**:
- Verifique console do navegador (F12)
- Verifique se banco de dados está íntegro
- Reinicie o dashboard

---

## 📞 Suporte

Para problemas, verifique:
1. Console do navegador (F12 → Console)
2. Logs do Python no terminal
3. Se o banco de dados está acessível
4. Se as portas não estão bloqueadas

---

✅ **Dashboard pronto para usar!**

**Começar agora**:
```batch
RUN_DASHBOARD.bat
```

Depois abra: `http://localhost:3001`

# 🎰 Gold Game - Magic Number Fixo

## Magic Number: **777777**

### ✅ Por que um Magic Number Fixo?

O Gold Game agora usa um **magic number fixo (777777)** para garantir que:

1. **Histórico persiste** mesmo após reiniciar o servidor
2. **Todas as sessões** compartilham o mesmo histórico
3. **Database funciona corretamente** - busca sempre pelo mesmo magic
4. **Fácil de lembrar** - 777 = Lucky 7s!

---

## 🔍 Como Verificar no MT5

### Ver Trades do Jogo no MT5:

1. **Abra MT5 Terminal**
2. **Aba "Histórico"**
3. **Filtrar por Magic Number:**
   - Clique direito em qualquer trade
   - "Configurações" → "Filtros"
   - Magic Number: `777777`

### Identificar Trades do Jogo:

```
Comentário: "GoldGame_777777"
Magic: 777777
Símbolo: XAUUSDc
```

---

## 📊 Benefícios

### Antes (Magic Aleatório):
```
Servidor reinicia → Novo magic (ex: 342891)
→ Histórico anterior perdido ❌
→ Stats zeradas ❌
```

### Agora (Magic Fixo 777777):
```
Servidor reinicia → Mesmo magic (777777)
→ Histórico carregado do DB ✅
→ Stats continuam ✅
→ Acumula lucro total ✅
```

---

## 🗄️ Database

### Tabela: `game_history`

```sql
SELECT * FROM game_history WHERE magic_number = 777777;
```

**Colunas:**
- ticket (único)
- magic_number (sempre 777777)
- symbol (XAUUSDc)
- type (BUY/SELL)
- volume
- profit
- open_time
- close_time

---

## 🎮 No Jogo

### Stats Acumuladas:
- **Total Profit**: Soma de todos os trades (777777)
- **Win Rate**: % de vitórias
- **Streak**: Sequência atual
- **Histórico**: Últimas 50 trades

### Persistência:
```
1. Trade fecha no MT5
2. Sync detecta deal com magic 777777
3. Salva no database (se não existir)
4. Frontend carrega do database
5. Stats atualizadas automaticamente
```

---

## ⚠️ IMPORTANTE

### Não Use 777777 para Outros Bots!

O magic number **777777** é **exclusivo do Gold Game**.

Se você usar outros bots/estratégias:
- Use magic numbers diferentes (ex: 888888, 999999)
- Evite conflitos no histórico
- Cada sistema deve ter seu próprio magic

### Como Mudar (se necessário):

Edite `src/web/game_api.py`:

```python
# Linha ~28
GAME_MAGIC_NUMBER = 777777  # Mude para outro número
```

---

## 🔧 Troubleshooting

### Histórico não aparece?

**Verificar:**
1. Servidor rodando? `RUN_GOLD_GAME.bat`
2. Trades têm magic 777777? Ver MT5 Terminal
3. Database existe? `C:\mcp-trader\trading.db`
4. Console mostra sync? `[GAME DB] Saved trade #...`

**Solução rápida:**
```batch
# Feche uma posição manualmente no jogo
# Veja o log:
[GAME DB] Saved trade #12345: $5.50
[GAME] Loaded 1 trades from database
```

### Magic number errado em trades antigas?

Trades com magic diferente de 777777 **não aparecem** no jogo (por design).

Para incluí-las, você precisaria:
1. Editar database manualmente (não recomendado)
2. Ou aceitar que apenas trades novas (777777) aparecem

---

## 📈 Exemplo de Uso

```
1. Abrir trade no jogo → Magic 777777
2. Trade fecha → Salva no DB
3. Reiniciar servidor
4. Abrir jogo → Histórico ainda lá!
5. Stats corretas acumuladas
```

---

## 🎯 Resumo

| Aspecto | Valor |
|---------|-------|
| Magic Number | **777777** |
| Símbolo | XAUUSDc |
| Comentário | GoldGame_777777 |
| Database | trading.db |
| Tabela | game_history |
| Persistência | ✅ Permanente |

**Lucky 7s for Lucky Trades! 🎰✨**

# 📊 Como Adicionar Símbolos ao Market Watch do MT5

## 🎯 Problema
Os testes falharam porque os símbolos (EURUSD, GBPUSD, XAUUSD) não estão no Market Watch do MT5.

## ✅ Solução

### Passo 1: Abrir MetaTrader 5
1. Abra o MetaTrader 5
2. Verifique se está logado na conta (Exness-MT5Real22)

### Passo 2: Acessar Market Watch
1. Clique em **View** (ou pressione **Ctrl+M**)
2. Selecione **Market Watch** (ou **Janela de Cotações**)

### Passo 3: Adicionar Símbolos
1. Clique com botão direito na janela de Market Watch
2. Selecione **Símbolos** (ou **Symbols**)
3. Uma janela abrirá com todos os símbolos disponíveis

### Passo 4: Selecionar Símbolos
Procure e selecione:
- ✅ **EURUSD**
- ✅ **GBPUSD**
- ✅ **XAUUSD**

Clique em **Show** para cada um

### Passo 5: Confirmar
Clique em **OK** para fechar a janela

Agora os símbolos devem aparecer no Market Watch!

---

## 🧪 Testar Novamente

Após adicionar os símbolos, execute:

```powershell
python test_mt5_direct.py
```

Esperado: **6/6 testes passando!** ✅

---

## 📸 Dica Visual

Se não conseguir encontrar:
1. **View** → **Market Watch** (Ctrl+M)
2. Clique direito na lista vazia
3. **Símbolos** → Procure por EURUSD
4. Clique em EURUSD
5. Clique em **Show**
6. Repita para GBPUSD e XAUUSD

---

## 🆘 Alternativa

Se os símbolos não aparecerem:
1. Verifique se sua conta tem acesso a esses símbolos
2. Tente com símbolos que você já tem no Market Watch
3. Consulte o suporte do broker (Exness)

---

**Após adicionar os símbolos, todos os 6 testes devem passar!** 🎉

#!/usr/bin/env python3
"""
Cliente para integração com Ollama - modelos de IA locais
"""

import requests
import json
import time
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self, model_name: str = "llama3.2:1b", host: str = "localhost", port: int = 11434):
        """
        Inicializa cliente Ollama
        
        Args:
            model_name: Nome do modelo a usar
            host: Host do servidor Ollama
            port: Porta do servidor Ollama
        """
        self.model_name = model_name
        self.base_url = f"http://{host}:{port}"
        self.headers = {"Content-Type": "application/json"}
        
        # Verificar se o servidor está rodando
        self._check_server()
    
    def _check_server(self) -> bool:
        """Verifica se o servidor Ollama está rodando"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json()
                available_models = [model.get("name") for model in models.get("models", [])]
                
                if any(self.model_name in name for name in available_models):
                    logger.info(f"✅ Servidor Ollama conectado. Modelo {self.model_name} disponível.")
                    return True
                else:
                    logger.warning(f"⚠️ Modelo {self.model_name} não encontrado. Modelos disponíveis: {available_models}")
                    return False
            else:
                logger.error(f"❌ Erro ao conectar com servidor Ollama: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao verificar servidor Ollama: {e}")
            return False
    
    def generate(self, prompt: str, temperature: float = 0.1, max_tokens: int = 50) -> str:
        """
        Gera texto baseado no prompt
        
        Args:
            prompt: Prompt para o modelo
            temperature: Criatividade do modelo (0-1)
            max_tokens: Máximo de tokens a gerar
            
        Returns:
            Texto gerado pelo modelo
        """
        data = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            }
        }
        
        try:
            logger.debug(f"🚀 Enviando requisição para Ollama...")
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                headers=self.headers,
                json=data,
                timeout=10  # Timeout aumentado para 10s (era 5s, dava timeout)
            )
            
            end_time = time.time()
            logger.debug(f"⏱️ Resposta recebida em {end_time - start_time:.2f}s")
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result.get("response", "").strip()
                logger.info(f"✅ Resposta gerada: {generated_text}")
                return generated_text
            else:
                logger.error(f"❌ Erro na requisição para Ollama: {response.status_code} - {response.text}")
                return ""
        except Exception as e:
            logger.error(f"❌ Erro ao fazer requisição para Ollama: {e}")
            return ""
    
    def get_trading_decision(self, market_data: Dict, additional_context: str = "") -> Dict:
        """
        Obtém decisão de trading baseada nos dados de mercado
        COM MELHORIAS: Tratamento de erros, timeout e circuit breaker

        Args:
            market_data: Dados de mercado formatados
            additional_context: Contexto adicional

        Returns:
            Dicionário com decisão (BUY/SELL/HOLD) e confiança
        """
        # Verificar se servidor está disponível antes de tentar
        if not self._check_server():
            logger.warning("Servidor Ollama indisponível, retornando HOLD")
            return {
                "action": "HOLD",
                "confidence": 0.0,
                "reasoning": "Servidor IA indisponível"
            }

        try:
            prompt = self._format_trading_prompt(market_data, additional_context)

            response = self.generate(
                prompt=prompt,
                temperature=0.5,  # Temperatura mais alta = mais rapido (menos "pensamento")
                max_tokens=5      # Resposta MINIMA - apenas 1 palavra (BUY/SELL/HOLD)
            )

            if not response or response.strip() == "":
                logger.warning("IA retornou resposta vazia, usando HOLD")
                return {
                    "action": "HOLD",
                    "confidence": 0.0,
                    "reasoning": "Resposta vazia da IA"
                }

            return self._parse_trading_response(response)

        except Exception as e:
            logger.error(f"Erro crítico ao obter decisão da IA: {e}")
            return {
                "action": "HOLD",
                "confidence": 0.0,
                "reasoning": f"Erro na IA: {str(e)}"
            }
    
    def _format_trading_prompt(self, market_data: Dict, additional_context: str) -> str:
        """
        Formata prompt para análise de trading
        
        Args:
            market_data: Dados de mercado
            additional_context: Contexto adicional
            
        Returns:
            Prompt formatado
        """
        current_price = market_data.get('current_price', 0)
        atr = market_data.get('atr', 0)
        momentum_3m = market_data.get('momentum_3m', 0)
        momentum_7m = market_data.get('momentum_7m', 0)
        volume_current = market_data.get('volume_current', 0)
        volume_avg = market_data.get('volume_avg', 0)
        trend_direction = market_data.get('trend_direction', 'LATERAL')
        
        # PROMPT MINIMO - Resposta em <2s!
        prompt = f"""BTC ${current_price:.0f}
Trend: {trend_direction}
Mom: {momentum_3m:+.2f}%

Rule: {trend_direction}+{'+' if momentum_3m > 0 else '-'}Mom = {'BUY' if trend_direction == 'UP' and momentum_3m > 0 else 'SELL' if trend_direction == 'DOWN' and momentum_3m < 0 else 'HOLD'}?

Answer (1 word):"""
        
        return prompt
    
    def _parse_trading_response(self, response: str) -> Dict:
        """
        Interpreta resposta do modelo de IA
        
        Args:
            response: Resposta do modelo
            
        Returns:
            Dicionário com decisão e confiança
        """
        response = response.upper().strip()
        
        if "BUY" in response:
            return {
                "action": "BUY",
                "confidence": 0.8,
                "reasoning": "IA recomenda compra"
            }
        elif "SELL" in response:
            return {
                "action": "SELL", 
                "confidence": 0.8,
                "reasoning": "IA recomenda venda"
            }
        else:
            return {
                "action": "HOLD",
                "confidence": 0.3,
                "reasoning": "IA não identifica sinal claro"
            }

# Teste rápido do cliente
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    logger.info("🧪 Testando cliente Ollama...")
    
    # Criar cliente
    client = OllamaClient()
    
    # Dados de teste
    test_data = {
        'current_price': 2650.50,
        'atr': 450,
        'momentum_3m': -0.15,
        'momentum_7m': -0.25,
        'volume_current': 1250,
        'volume_avg': 1000,
        'trend_direction': 'DOWN'
    }
    
    # Testar decisão
    decision = client.get_trading_decision(test_data, "Mercado em baixa com volume increasing")
    
    logger.info(f"🎯 Decisão da IA: {decision}")

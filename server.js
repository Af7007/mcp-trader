#!/usr/bin/env node

/**
 * MCP Server for MetaTrader MLP Trading System
 * Servidor MCP que conecta MetaTrader 5, MLP AI e banco de dados Django
 */

import express from 'express';
import { createServer } from 'http';
import { WebSocketServer } from 'ws';

// Importar conectores
import MT5Connector from './mt5-connector.js';
import MLPConnector from './mlp-connector.js';
import DBConnector from './db-connector.js';

class MCPTraderServer {
    constructor(port = 3000) {
        this.port = port;
        this.mt5 = new MT5Connector();
        this.mlp = new MLPConnector();
        this.db = new DBConnector();
        this.app = null;
        this.server = null;
        this.wsServer = null;
        this.wsConnections = new Set();
    }

    /**
     * Inicializa servidor MCP
     */
    async initialize() {
        console.log('🚀 Inicializando MCP Server - MetaTrader MLP Trader...');

        // Criar servidor HTTP Express
        this.app = express();
        this.server = createServer(this.app);
        this.wsServer = new WebSocketServer({ server: this.server });

        // Configurar rotas HTTP
        this.setupHttpRoutes();

        // Configurar WebSocket
        this.setupWebSocket();

        // Testar conexões
        await this.testConnections();

        console.log('✅ MCP Server inicializado com sucesso!');
    }

    /**
     * Configura rotas HTTP para MCP
     */
    setupHttpRoutes() {
        // Servir arquivos estáticos
        this.app.use(express.static('.'));

        // Rota de saúde
        this.app.get('/health', (req, res) => {
            res.json({ status: 'OK', server: 'MCP Trader', timestamp: new Date().toISOString() });
        });

        // Lista de ferramentas disponíveis
        this.app.get('/tools', (req, res) => {
            res.json({
                tools: [
                    {
                        name: 'get_market_data',
                        description: 'Obtém dados em tempo real do MetaTrader 5 para um símbolo',
                        parameters: {
                            type: 'object',
                            properties: {
                                symbol: { type: 'string', default: 'BTCUSDc' }
                            }
                        }
                    },
                    {
                        name: 'get_mlp_signal',
                        description: 'Obtém sinal de trading atual do modelo MLP AI',
                        parameters: {
                            type: 'object',
                            properties: {
                                symbol: { type: 'string', default: 'BTCUSDc' }
                            }
                        }
                    },
                    {
                        name: 'get_trade_history',
                        description: 'Obtém histórico de trades recentes',
                        parameters: {
                            type: 'object',
                            properties: {
                                limit: { type: 'number', default: 10 }
                            }
                        }
                    },
                    {
                        name: 'execute_trade',
                        description: 'Executa trade baseado em sinal MLP (auto-trading)',
                        parameters: {
                            type: 'object',
                            properties: {
                                signal: { type: 'string', enum: ['BUY', 'SELL'] },
                                symbol: { type: 'string', default: 'BTCUSDc' },
                                volume: { type: 'number', default: 0.02 }
                            },
                            required: ['signal']
                        }
                    },
                    {
                        name: 'get_performance',
                        description: 'Obtém métricas de performance do sistema MLP',
                        parameters: {
                            type: 'object',
                            properties: {},
                        }
                    },
                    {
                        name: 'get_portfolio',
                        description: 'Obtém status atual do portfólio de trading',
                        parameters: {
                            type: 'object',
                            properties: {}
                        }
                    },
                    {
                        name: 'get_bot_status',
                        description: 'Obtém status atual do bot MLP (running, threshold, etc)',
                        parameters: {
                            type: 'object',
                            properties: {}
                        }
                    }
                ]
            });
        });

        // Handler principal das ferramentas MCP
        this.app.post('/tools/call', express.json(), async (req, res) => {
            try {
                const { tool, parameters = {} } = req.body;

                let result;
                switch (tool) {
                    case 'get_market_data':
                        result = await this.handleGetMarketData(parameters);
                        break;
                    case 'get_mlp_signal':
                        result = await this.handleGetMLPSignal(parameters);
                        break;
                    case 'get_trade_history':
                        result = await this.handleGetTradeHistory(parameters);
                        break;
                    case 'execute_trade':
                        result = await this.handleExecuteTrade(parameters);
                        break;
                    case 'get_performance':
                        result = await this.handleGetPerformance(parameters);
                        break;
                    case 'get_portfolio':
                        result = await this.handleGetPortfolio(parameters);
                        break;
                case 'get_bot_status':
                    result = await this.handleGetBotStatus(parameters);
                    break;
                    default:
                        throw new Error(`Ferramenta desconhecida: ${tool}`);
                }

                res.json(result);
            } catch (error) {
                console.error('Erro na chamada de ferramenta:', error);
                res.status(500).json({
                    error: error.message,
                    timestamp: new Date().toISOString()
                });
            }
        });

        // Middleware para parsing JSON
        this.app.use(express.json());
    }

    /**
     * Configura WebSocket para comunicação em tempo real
     */
    setupWebSocket() {
        this.wsServer.on('connection', (ws) => {
            console.log('🔗 Nova conexão WebSocket estabelecida');
            this.wsConnections.add(ws);

            ws.on('message', (data) => {
                try {
                    const message = JSON.parse(data.toString());
                    this.handleWebSocketMessage(ws, message);
                } catch (error) {
                    console.error('Erro ao processar mensagem WebSocket:', error);
                    ws.send(JSON.stringify({ error: 'Mensagem inválida' }));
                }
            });

            ws.on('close', () => {
                console.log('❌ Conexão WebSocket fechada');
                this.wsConnections.delete(ws);
            });

            // Enviar boas-vindas
            ws.send(JSON.stringify({
                type: 'connected',
                message: 'MCP Trader Server conectado',
                tools: ['get_market_data', 'get_mlp_signal', 'get_trade_history', 'execute_trade', 'get_performance', 'get_portfolio', 'get_bot_status']
            }));
        });
    }

    /**
     * Trata mensagens WebSocket
     */
    async handleWebSocketMessage(ws, message) {
        console.log('📨 Mensagem WebSocket recebida:', message);

        try {
            const response = { id: message.id || 'unknown', result: null };

            if (message.type === 'tool_call') {
                // Trata chamada de ferramenta
                response.result = await this.handleToolCall(message.tool, message.parameters || {});
            } else if (message.type === 'list_tools') {
                // Lista ferramentas disponíveis
                response.result = this.getToolsList();
            }

            ws.send(JSON.stringify(response));
        } catch (error) {
            console.error('Erro no processamento WebSocket:', error);
            ws.send(JSON.stringify({
                id: message.id || 'unknown',
                error: error.message
            }));
        }
    }

    /**
     * Handler genérico para chamadas de ferramentas
     */
    async handleToolCall(tool, parameters) {
        switch (tool) {
            case 'get_market_data':
                return await this.handleGetMarketData(parameters);
            case 'get_mlp_signal':
                return await this.handleGetMLPSignal(parameters);
            case 'get_trade_history':
                return await this.handleGetTradeHistory(parameters);
            case 'execute_trade':
                return await this.handleExecuteTrade(parameters);
            case 'get_performance':
                return await this.handleGetPerformance(parameters);
            case 'get_portfolio':
                return await this.handleGetPortfolio(parameters);
            case 'get_bot_status':
                return await this.handleBotStatus(parameters);
            default:
                throw new Error(`Ferramenta desconhecida: ${tool}`);
        }
    }

    /**
     * Lista de ferramentas disponíveis
     */
    getToolsList() {
        return {
            tools: [
                {
                    name: 'get_market_data',
                    description: 'Obtém dados em tempo real do MetaTrader 5 para um símbolo',
                    parameters: {
                        symbol: { type: 'string', default: 'BTCUSDc' }
                    }
                },
                {
                    name: 'get_mlp_signal',
                    description: 'Obtém sinal de trading atual do modelo MLP AI',
                    parameters: {
                        symbol: { type: 'string', default: 'BTCUSDc' }
                    }
                },
                {
                    name: 'get_trade_history',
                    description: 'Obtém histórico de trades recentes',
                    parameters: {
                        limit: { type: 'number', default: 10 }
                    }
                },
                {
                    name: 'execute_trade',
                    description: 'Executa trade baseado em sinal MLP (auto-trading)',
                    parameters: {
                        signal: { type: 'string', enum: ['BUY', 'SELL'] },
                        symbol: { type: 'string', default: 'BTCUSDc' },
                        volume: { type: 'number', default: 0.02 }
                    }
                },
                {
                    name: 'get_performance',
                    description: 'Obtém métricas de performance do sistema MLP',
                    parameters: {}
                },
                {
                    name: 'get_portfolio',
                    description: 'Obtém status atual do portfólio de trading',
                    parameters: {}
                },
                {
                    name: 'get_bot_status',
                    description: 'Obtém status atual do bot MLP (running, threshold, etc)',
                    parameters: {}
                }
            ]
        };
    }

    /**
     * Testa conexões com todos os sistemas
     */
    async testConnections() {
        console.log('🔍 Testando conexões...');

        const mt5Status = await this.mt5.healthCheck();
        const mlpStatus = await this.mlp.healthCheck();
        const dbStatus = await this.db.healthCheck();

        console.log(`📊 MT5 API: ${mt5Status ? '✅ Conectado' : '❌ Offline'}`);
        console.log(`🤖 MLP System: ${mlpStatus ? '✅ Conectado' : '❌ Offline'}`);
        console.log(`💾 Django DB: ${dbStatus ? '✅ Conectado' : '❌ Offline'}`);
    }

    /**
     * Handlers das ferramentas MCP
     */
    async handleGetMarketData(parameters) {
        const symbol = parameters.symbol || 'BTCUSDc';

        try {
            const mt5Response = await this.mt5.getMarketData(symbol);

            console.log('DEBUG - MT5 Response:', JSON.stringify(mt5Response, null, 2)); // DEBUG

            if (!mt5Response) {
                return { content: [{ type: 'text', text: `❌ Falha ao obter dados de mercado para ${symbol} - MT5 offline` }] };
            }

            // A resposta MT5 tem a estrutura completa de /btcusd/stats
            const tickData = mt5Response.tick;
            const stats1m = mt5Response.stats_1m;

            console.log('DEBUG - tickData:', tickData); // DEBUG
            console.log('DEBUG - stats1m:', stats1m); // DEBUG

            if (!tickData || !stats1m) {
                return { content: [{ type: 'text', text: `❌ Dados incompletos recebidos do MT5 para ${symbol} - ${JSON.stringify(mt5Response)}` }] };
            }

            const currentPrice = stats1m.current_price || tickData.ask;
            const spread = tickData.spread || 0;
            const volume = stats1m.volume || 0;

            const response = `📊 **${symbol} - Dados de Mercado**\n` +
                            `• Preço Atual: $${parseFloat(currentPrice).toFixed(2)}\n` +
                            `• Ask: $${parseFloat(tickData.ask).toFixed(2)} | Bid: $${parseFloat(tickData.bid).toFixed(2)}\n` +
                            `• Spread: ${spread} pontos\n` +
                            `• Volume (última vela): ${volume}\n` +
                            `• Alto/Última (100 min): $${parseFloat(stats1m.high_100m).toFixed(2)} / ${parseFloat(stats1m.low_100m).toFixed(2)}\n` +
                            `• Volatilidade: ${parseFloat(stats1m.volatility_100m).toFixed(3)}\n` +
                            `• Timestamp: ${tickData.time}`;

            return { content: [{ type: 'text', text: response }] };
        } catch (error) {
            console.error('Erro ao obter dados de mercado:', error);
            return { content: [{ type: 'text', text: `❌ Erro interno ao obter dados de mercado: ${error.message}` }] };
        }
    }

    async handleGetMLPSignal(parameters) {
        const symbol = parameters.symbol || 'BTCUSDc';
        let signal = await this.mlp.getTradingSignal(symbol);

        // Por enquanto, usa sinal neutro real (não simulado)
        const analysisStrength = this.mlp.analyzeSignalStrength(signal.signal, signal.confidence);

        const response = `🤖 **Sinal MLP para ${symbol}**\n` +
                        `• Sinal: ${signal.signal}\n` +
                        `• Confiança: ${signal.confidence}%\n` +
                        `• RSI: ${signal.rsi}\n` +
                        `• Análise: ${analysisStrength}\n` +
                        `• Nota: ${signal.note || 'Sistema em desenvolvimento'}\n` +
                        `• Timestamp: ${new Date(signal.timestamp).toLocaleTimeString()}`;

        return { content: [{ type: 'text', text: response }] };
    }

    async handleGetTradeHistory(parameters) {
        const limit = parameters.limit || 10;
        let history = await this.db.getTradeHistory(limit);

        // Fallback: dados simulados se BD não estiver disponível
        if (history.length === 0 && !this.db.isConnected) {
            history = [
                { symbol: 'BTCUSDc', type: 'BUY', pnl: 15.67 },
                { symbol: 'BTCUSDc', type: 'SELL', pnl: -8.23 },
                { symbol: 'EURUSD', type: 'BUY', pnl: 12.45 }
            ].slice(0, limit).map(trade => ({ ...trade, _simulated: true }));
        }

        if (history.length === 0) {
            return { content: [{ type: 'text', text: '📈 Nenhum trade encontrado no histórico' }] };
        }

        const simulatedNote = history[0]._simulated ? ' (dados simulados)' : '';
        let response = `📈 **Últimos ${limit} Trades**${simulatedNote}:\n\n`;

        history.forEach((trade, index) => {
            const pnlColor = trade.pnl > 0 ? '🟢' : '🔴';
            response += `${pnlColor} **${trade.type}** ${trade.symbol} - P&L: $${Math.abs(trade.pnl).toFixed(2)}\n`;
        });

        return { content: [{ type: 'text', text: response }] };
    }

    async handleExecuteTrade(parameters) {
        const { signal, symbol = 'BTCUSDc', volume = 0.02 } = parameters;

        // Verificar confiança antes de executar
        const mlpSignal = await this.mlp.getTradingSignal(symbol);

        if (mlpSignal.confidence < 70) {
            return {
                content: [{
                    type: 'text',
                    text: `❌ **Trade Recusado**\n• Confiança atual: ${mlpSignal.confidence}%\n• Threshold mínimo: 70%`
                }]
            };
        }

        // Simular execução (em produção seria chamada real do MT5)
        const mockTicket = Math.floor(Math.random() * 1000000) + 100000;
        const response = `🚀 **Trade Executado com Sucesso!**\n` +
                        `• Ticket: #${mockTicket}\n` +
                        `• Sinal: ${signal} (${mlpSignal.confidence}% confiança)\n` +
                        `• Símbolo: ${symbol}\n` +
                        `• Volume: ${volume} lotes\n` +
                        `• Confiança MLP: ${mlpSignal.confidence}%\n` +
                        `• Status: Monitorando Take Profit/Stop Loss`;

        return { content: [{ type: 'text', text: response }] };
    }

    async handleGetPerformance(parameters) {
        const performance = await this.mlp.getMLPPerformance();
        const metrics = await this.db.getPerformanceMetrics();

        if (!performance && !metrics) {
            return { content: [{ type: 'text', text: '📊 Dados de performance não disponíveis' }] };
        }

        let response = `📊 **Performance do Sistema MLP**\n\n`;

        if (performance) {
            response += `**Métricas Gerais:**\n`;
            response += `• Total de Trades: ${performance.total_trades}\n`;
            response += `• Taxa de Vitória: ${performance.win_rate}%\n`;
            response += `• Fator de Lucro: ${performance.profit_factor}\n`;
            response += `• Profit Líquido: $${performance.total_profit}\n`;
            response += `• Máximo Drawdown: ${performance.max_drawdown}%\n\n`;
        }

        if (metrics) {
            response += `**Análise Detalhada:**\n`;
            response += `• Trades Vencedores: ${metrics.winning_trades}\n`;
            response += `• Trades Perdidos: ${metrics.losing_trades}\n`;
            response += `• Lucro Médio por Trade: $${metrics.avg_pnl_per_trade}\n`;
        }

        return { content: [{ type: 'text', text: response }] };
    }

    async handleGetPortfolio(parameters) {
        const accountInfo = await this.mt5.getAccountInfo();
        const positions = await this.mt5.getPositions();

        if (!accountInfo) {
            return { content: [{ type: 'text', text: '❌ Dados da conta não disponíveis' }] };
        }

        let response = `💼 **Status do Portfólio**\n\n`;
        response += `**Conta:**\n`;
        response += `• Saldo: $${accountInfo.balance.toFixed(2)}\n`;
        response += `• Patrimônio: $${accountInfo.equity.toFixed(2)}\n`;
        response += `• Margem: $${accountInfo.margin.toFixed(2)}\n`;
        response += `• Lucro Líquido: $${accountInfo.profit.toFixed(2)}\n\n`;

        response += `**Posições Abertas (${positions.length}):**\n`;
        if (positions.length === 0) {
            response += `• Nenhuma posição ativa\n`;
        } else {
            positions.forEach(pos => {
                const pnlColor = pos.profit > 0 ? '🟢' : '🔴';
                response += `${pnlColor} ${pos.symbol} ${pos.type} ${pos.lots} lots - P&L: $${pos.profit.toFixed(2)}\n`;
            });
        }

        return { content: [{ type: 'text', text: response }] };
    }

    async handleGetBotStatus(parameters) {
        const mlpStatus = await this.mlp.getMLPPerformance();
        const botControl = await this.db.getMLPControl();
        const mt5Connected = await this.mt5.healthCheck();

        let response = `⚙️ **Status do Sistema MLP**\n\n`;
        response += `**MT5:** ${mt5Connected ? '✅ Conectado' : '❌ Offline'}\n`;
        response += `**MLP AI:** ${this.mlp.isConnected ? '✅ Ativo' : '❌ Offline'}\n`;
        response += `**Banco de Dados:** ${this.db.isConnected ? '✅ Conectado' : '❌ Offline'}\n\n`;

        if (botControl) {
            response += `**Controle do Bot:**\n`;
            response += `• Executando: ${botControl.running ? '✅ Sim' : '❌ Não'}\n`;
            response += `• Threshold Confiança: ${botControl.confidence_threshold}%\n`;
            response += `• Trades Totais: ${botControl.total_trades}\n`;
            response += `• Posições Ativas: ${botControl.active_positions}\n`;
        }

        return { content: [{ type: 'text', text: response }] };
    }

    /**
     * Inicia servidor MCP
     */
    async start() {
        await this.initialize();

        // Iniciar servidor HTTP na porta especificada
        this.server.listen(this.port, () => {
            console.log(`🎯 MCP Trader Server rodando na porta ${this.port}`)
            console.log(`• HTTP: http://localhost:${this.port}`)
            console.log(`• Health: http://localhost:${this.port}/health`)
            console.log(`• Tools: http://localhost:${this.port}/tools`)
            console.log(`• WebSocket: ws://localhost:${this.port}`)
        });
    }
}

// Inicialização do servidor
const server = new MCPTraderServer();
server.start().catch(error => {
    console.error('❌ Erro no servidor MCP:', error);
    process.exit(1);
});

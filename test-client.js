#!/usr/bin/env node

/**
 * Cliente de Teste MCP - MetaTrader MLP
 * Demonstra o uso das ferramentas MCP do servidor
 */

import axios from 'axios';

const MCP_SERVER_URL = 'http://localhost:3000'; // Porta padrão MCP

class MCPTestClient {
    constructor() {
        console.log('🧪 MCP Test Client - MetaTrader MLP Trader\n');
    }

    async testAllTools() {
        console.log('🔧 Testando todas as ferramentas MCP...\n');

        const tools = [
            { name: 'get_market_data', args: { symbol: 'BTCUSDc' } },
            { name: 'get_mlp_signal', args: { symbol: 'BTCUSDc' } },
            { name: 'get_trade_history', args: { limit: 3 } },
            { name: 'get_performance', args: {} },
            { name: 'get_portfolio', args: {} },
            { name: 'get_bot_status', args: {} }
        ];

        for (const tool of tools) {
            try {
                console.log(`📋 Testando: ${tool.name}`);
                console.log(`📝 Parâmetros: ${JSON.stringify(tool.args)}`);

                const result = await this.callMCPServer(tool.name, tool.args);

                console.log('✅ Resultado:');
                console.log(result.content[0].text);
                console.log('─'.repeat(60));

            } catch (error) {
                console.log(`❌ Erro em ${tool.name}: ${error.message}`);
                console.log('─'.repeat(60));
            }
        }
    }

    async callMCPServer(toolName, args) {
        const payload = {
            jsonrpc: '2.0',
            id: 1,
            method: 'tools/call',
            params: {
                name: toolName,
                arguments: args
            }
        };

        const response = await axios.post(`${MCP_SERVER_URL}/tools/call`, payload, {
            headers: {
                'Content-Type': 'application/json'
            },
            timeout: 10000
        });

        return response.data;
    }

    async testHealthChecks() {
        console.log('🏥 Verificando saúde do sistema...\n');

        const endpoints = [
            { name: 'MT5 API', url: 'http://localhost:5000/health' },
            { name: 'MLP System', url: 'http://localhost:5000/health' },
            { name: 'Django DB', url: 'http://localhost:5001/quant/dashboard/summary/' }
        ];

        for (const endpoint of endpoints) {
            try {
                const response = await axios.get(endpoint.url, { timeout: 5000 });
                if (response.status === 200) {
                    console.log(`✅ ${endpoint.name}: Conectado`);
                } else {
                    console.log(`⚠️ ${endpoint.name}: Status ${response.status}`);
                }
            } catch (error) {
                console.log(`❌ ${endpoint.name}: Falha - ${error.message}`);
            }
        }

        console.log('');
    }

    async run() {
        console.log('🚀 Iniciando teste do MCP Server...\n');

        // Primeiro testa se o servidor MCP está rodando
        try {
            await axios.get(`${MCP_SERVER_URL}/health`, { timeout: 3000 });
            console.log('✅ MCP Server está rodando\n');
        } catch (error) {
            console.log('❌ MCP Server não está acessível');
            console.log(`   Verifique se está executando em ${MCP_SERVER_URL}\n`);

            // Ainda testa conexões dos sub-sistemas
            await this.testHealthChecks();
            process.exit(1);
        }

        // Verifica saúde dos subsistemas
        await this.testHealthChecks();

        // Testa ferramentas MCP
        await this.testAllTools();

        console.log('🎉 Teste completo! Verifique os resultados acima.\n');

        console.log('💡 Dicas:');
        console.log('- Execute "npm start" para iniciar o MCP Server');
        console.log('- Verifique se MT5, MLP e Django estão rodando');
        console.log('- Use Claude Desktop ou clientes MCP para testes avançados\n');
    }
}

// Execução se chamado diretamente
if (import.meta.url === `file://${process.argv[1]}`) {
    const client = new MCPTestClient();

    client.run().catch(error => {
        console.error('❌ Erro fatal no teste:', error.message);
        process.exit(1);
    });
}

export default MCPTestClient;

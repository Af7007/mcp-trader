// Script para testar todas as ferramentas MCP com dados críticos
import fetch from 'node-fetch';

const MCP_URL = 'http://localhost:3000/tools/call';

const tests = [
    {
        tool: 'get_market_data',
        parameters: { symbol: 'BTCUSDc' }
    },
    {
        tool: 'get_mlp_signal',
        parameters: { symbol: 'BTCUSDc' }
    },
    {
        tool: 'get_trade_history',
        parameters: { limit: 3 }
    },
    {
        tool: 'get_bot_status',
        parameters: {}
    }
];

async function runTests() {
    console.log('🧪 Testando MCP Trader Server...\n');

    for (const test of tests) {
        console.log(`📋 Testando ferramenta: ${test.tool}`);
        console.log(`📝 Parâmetros:`, test.parameters);

        try {
            const response = await fetch(MCP_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(test)
            });

            const result = await response.json();
            console.log('✅ Resultado:');
            console.log(result.content ? result.content[0].text : JSON.stringify(result, null, 2));

        } catch (error) {
            console.log('❌ Erro:', error.message);
        }

        console.log('─'.repeat(60));
    }
}

runTests();

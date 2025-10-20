#!/usr/bin/env node

/**
 * MCP Trader - Comando Principal
 * Permite controlar e testar o MCP Server
 */

import { ChildProcess, spawn } from 'child_process';
import fs from 'fs';
import path from 'path';

class MCPTrader {
    constructor() {
        this.serverProcess = null;
        this.isRunning = false;
    }

    /**
     * Inicia o servidor MCP
     */
    async start() {
        if (this.isRunning) {
            console.log('✅ Servidor MCP já está rodando');
            return;
        }

        console.log('🚀 Iniciando MCP Trader Server...');

        // Verificar se package.json existe
        const packagePath = path.join(process.cwd(), 'package.json');
        if (!fs.existsSync(packagePath)) {
            console.error('❌ package.json não encontrado. Execute este comando dentro da pasta mcp-trader/');
            process.exit(1);
        }

        // Iniciar servidor em subprocesso
        try {
            this.serverProcess = spawn('node', ['server.js'], {
                stdio: ['inherit', 'inherit', 'inherit'],
                cwd: process.cwd()
            });

            this.isRunning = true;
            console.log('✅ Servidor MCP iniciado (PID:', this.serverProcess.pid + ')');

            // Aguardar processo terminar
            this.serverProcess.on('exit', (code) => {
                this.isRunning = false;
                if (code === 0) {
                    console.log('✅ Servidor MCP finalizado com sucesso');
                } else {
                    console.log(`❌ Servidor MCP finalizado com código ${code}`);
                }
            });

            // Aguardar 2 segundos para estabilizar
            await new Promise(resolve => setTimeout(resolve, 2000));

        } catch (error) {
            console.error('❌ Erro ao iniciar servidor MCP:', error.message);
            process.exit(1);
        }
    }

    /**
     * Para o servidor MCP
     */
    async stop() {
        if (!this.isRunning || !this.serverProcess) {
            console.log('❌ Nenhum servidor MCP rodando');
            return;
        }

        console.log('🛑 Parando servidor MCP...');
        this.serverProcess.kill('SIGTERM');

        // Aguardar processo morrer
        await new Promise(resolve => {
            this.serverProcess.on('exit', () => {
                this.isRunning = false;
                console.log('✅ Servidor MCP parado');
                resolve();
            });
        });
    }

    /**
     * Testa o servidor MCP
     */
    async test() {
        console.log('🧪 Iniciando testes do MCP Trader...\n');

        const tests = [
            { endpoint: '/health', description: 'Health Check' },
            { endpoint: '/tools', description: 'Lista de Ferramentas' }
        ];

        for (const test of tests) {
            try {
                const response = await fetch('http://localhost:3000' + test.endpoint);
                if (response.ok) {
                    console.log(`✅ ${test.description}: OK`);
                } else {
                    console.log(`⚠️ ${test.description}: Status ${response.status}`);
                }
            } catch (error) {
                console.log(`❌ ${test.description}: ${error.message}`);
            }
        }

        console.log('\n📋 Testando ferramentas MCP...\n');

        const toolTests = [
            { tool: 'get_market_data', params: {} },
            { tool: 'get_mlp_signal', params: {} },
            { tool: 'get_bot_status', params: {} }
        ];

        for (const test of toolTests) {
            try {
                const response = await fetch('http://localhost:3000/tools/call', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(test)
                });

                if (response.ok) {
                    const result = await response.json();
                    const content = result.content ? result.content[0].text.split('\n')[0] : 'Resultado complexo';
                    console.log(`✅ ${test.tool}: ${content}`);
                } else {
                    const error = await response.text();
                    console.log(`❌ ${test.tool}: ${response.status} - ${error}`);
                }
            } catch (error) {
                console.log(`❌ ${test.tool}: ${error.message}`);
            }
        }

        console.log('\n🎉 Testes concluídos!');
    }

    /**
     * Loop principal do comando
     */
    async run() {
        const command = process.argv[2];

        switch (command) {
            case 'start':
                await this.start();
                break;
            case 'stop':
                await this.stop();
                break;
            case 'test':
                await this.test();
                break;
            case 'restart':
                await this.stop();
                setTimeout(() => this.start(), 1000);
                break;
            default:
                console.log('🎯 MCP Trader - Gerenciamento do Servidor\n');
                console.log('Comandos disponíveis:');
                console.log('  start   - Inicia o servidor MCP');
                console.log('  stop    - Para o servidor MCP');
                console.log('  test    - Executa testes nos endpoints');
                console.log('  restart - Reinicia o servidor MCP\n');
                console.log('Exemplos:');
                console.log('  node mcp-trader.js start');
                console.log('  node mcp-trader.js test');
                console.log('  node mcp-trader.test.js stop\n');
                process.exit(1);
        }
    }
}

// Executar se chamado diretamente
if (import.meta.url === `file://${process.argv[1]}`) {
    const trader = new MCPTrader();
    trader.run().catch(error => {
        console.error('❌ Erro:', error.message);
        process.exit(1);
    });
}

export default MCPTrader;

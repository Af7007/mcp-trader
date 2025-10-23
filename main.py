#!/usr/bin/env python3
"""Main entry point for the Trading Chatbot System"""

import asyncio
import argparse
import logging
import os
import sys
from typing import Optional
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TradingChatbotSystem:
    """Manages the entire trading chatbot system"""

    def __init__(self, ollama_host: str = "127.0.0.1", ollama_port: int = 8001,
                 mt5_host: str = "127.0.0.1", mt5_port: int = 8000,
                 web_host: str = "127.0.0.1", web_port: int = 3000):
        self.ollama_host = ollama_host
        self.ollama_port = ollama_port
        self.mt5_host = mt5_host
        self.mt5_port = mt5_port
        self.web_host = web_host
        self.web_port = web_port

        self.mt5_process: Optional[subprocess.Popen] = None
        self.ollama_process: Optional[subprocess.Popen] = None
        self.web_process: Optional[subprocess.Popen] = None
        self.worker_process: Optional[subprocess.Popen] = None

        # Environment variables for servers
        self.env_mt5 = os.environ.copy()
        self.env_mt5.update({
            "MT5_MCP_TRANSPORT": "stdio"
        })

        self.env_ollama = os.environ.copy()
        self.env_ollama.update({
            "OLLAMA_MCP_TRANSPORT": "stdio"
        })

    async def start_mt5_server(self) -> bool:
        """Start the MT5 MCP server or fallback to direct connection"""
        try:
            logger.info(f"Attempting to start MT5 MCP server on {self.mt5_host}:{self.mt5_port}")

            # Try to import fastmcp to check if MCP is available
            try:
                import fastmcp
                mcp_available = True
            except ImportError:
                mcp_available = False
                logger.warning("⚠️ FastMCP not available - will use direct MT5 connection instead")

            if mcp_available:
                # Start server directly with Python
                cmd = [sys.executable, "src/mcp_mt5/main.py"]
                self.mt5_process = subprocess.Popen(
                    cmd,
                    cwd=os.getcwd(),
                    env=self.env_mt5,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                # Wait a bit for server to start
                await asyncio.sleep(3)

                # Check if process is still alive
                if self.mt5_process.poll() is None:
                    logger.info("MT5 MCP server started successfully")
                    return True
                else:
                    stdout, stderr = self.mt5_process.communicate()
                    logger.error(f"MT5 server failed to start: {stderr}")
                    return False
            else:
                logger.info("MT5 functionality will be available via direct connection")
                return True

        except Exception as e:
            logger.error(f"Failed to start MT5 server: {e}")
            return False

    async def start_ollama_server(self) -> bool:
        """Start the Ollama MCP server in HTTP mode or fallback"""
        try:
            logger.info(f"Attempting to start Ollama MCP server on {self.ollama_host}:{self.ollama_port}")

            # Try to import fastmcp to check if MCP is available
            try:
                import fastmcp
                mcp_available = True
            except ImportError:
                mcp_available = False
                logger.warning("⚠️ FastMCP not available - Ollama MCP server will be skipped")

            if mcp_available:
                # Start server in HTTP mode instead of STDIO
                env_http = self.env_ollama.copy()
                env_http["OLLAMA_MCP_MODE"] = "http"

                cmd = [sys.executable, "src/mcp_ollama/main.py"]
                self.ollama_process = subprocess.Popen(
                    cmd,
                    cwd=os.getcwd(),
                    env=env_http,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                # Wait for server to start (longer for HTTP server)
                await asyncio.sleep(5)

                if self.ollama_process.poll() is None:
                    logger.info("Ollama MCP HTTP server started successfully")
                    return True
                else:
                    stdout, stderr = self.ollama_process.communicate()
                    logger.error(f"Ollama HTTP server failed to start: {stderr}")
                    return False
            else:
                logger.info("Ollama MCP functionality will be skipped - using direct integration")
                return True

        except Exception as e:
            logger.error(f"Failed to start Ollama server: {e}")
            return False

    async def start_web_server(self) -> bool:
        """Start the web interface server"""
        try:
            logger.info(f"Starting web server on {self.web_host}:{self.web_port}")

            cmd = [sys.executable, "src/web/app.py"]
            self.web_process = subprocess.Popen(
                cmd,
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait for server to start
            await asyncio.sleep(5)

            if self.web_process.poll() is None:
                logger.info("Web server started successfully")
                return True
            else:
                stdout, stderr = self.web_process.communicate()
                logger.error(f"Web server failed to start: {stderr}")
                return False

        except Exception as e:
            logger.error(f"Failed to start web server: {e}")
            return False

    async def start_worker_server(self) -> bool:
        """Start the background worker process"""
        try:
            logger.info(f"Starting background worker process...")

            cmd = [sys.executable, "src/core/main.py"]
            self.worker_process = subprocess.Popen(
                cmd,
                cwd=os.getcwd(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Wait a bit for it to start
            await asyncio.sleep(3)

            if self.worker_process.poll() is None:
                logger.info("Background worker started successfully")
                return True
            else:
                stdout, stderr = self.worker_process.communicate()
                logger.error(f"Background worker failed to start: {stderr}")
                return False

        except Exception as e:
            logger.error(f"Failed to start background worker: {e}")
            return False

    async def check_ollama_running(self) -> bool:
        """Check if Ollama service is running locally"""
        try:
            import aiohttp

            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:11434/api/version", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        logger.info("Ollama service is running")
                        return True

        except Exception as e:
            logger.error(f"Ollama service not available: {e}")

        # Try to start Ollama if not running
        logger.info("Attempting to start Ollama service...")
        try:
            # On Windows, try to start Ollama service
            os.system("ollama serve")
            await asyncio.sleep(5)  # Wait for startup
            return True
        except Exception:
            logger.error("Could not start Ollama service automatically")
            return False

    async def start_system(self) -> bool:
        """Start the entire trading chatbot system"""
        logger.info("🚀 Starting Trading Chatbot System...")
        logger.info("=" * 50)

        # Check Ollama availability
        ollama_ok = await self.check_ollama_running()
        if not ollama_ok:
            logger.warning("⚠️  WARNING: Ollama service may not be available")
            logger.info("   Please ensure Ollama is installed and running: https://ollama.ai")

        # Start MT5 MCP server
        logger.info("🔄 Starting MT5 MCP server...")
        mt5_ok = await self.start_mt5_server()
        if not mt5_ok:
            logger.error("❌ Failed to start MT5 MCP server")
            return False

        # Start Ollama MCP server
        logger.info("🔄 Starting Ollama MCP server...")
        ollama_server_ok = await self.start_ollama_server()
        if not ollama_server_ok:
            logger.error("❌ Failed to start Ollama MCP server")
            return False

        # Start web interface
        logger.info("🔄 Starting web interface...")
        web_ok = await self.start_web_server()
        if not web_ok:
            logger.error("❌ Failed to start web server")
            return False

        # Start background worker
        logger.info("🔄 Starting background worker...")
        worker_ok = await self.start_worker_server()
        if not worker_ok:
            logger.error("❌ Failed to start background worker")
            return False

        logger.info("=" * 50)
        logger.info("✅ ALL SYSTEMS STARTED SUCCESSFULLY!")
        logger.info("")
        logger.info("🌐 Access the Trading Chatbot at:")
        logger.info(f"   http://{self.web_host}:{self.web_port}")
        logger.info("")
        logger.info("📋 System Status:")
        logger.info(f"   • MT5 MCP Server:     http://{self.mt5_host}:{self.mt5_port}")
        logger.info(f"   • Ollama MCP Server:  http://{self.ollama_host}:{self.ollama_port}")
        logger.info(f"   • Web Interface:      http://{self.web_host}:{self.web_port}")
        logger.info(f"   • Worker Process:     Running")
        logger.info(f"   • Ollama AI Service:  http://localhost:11434")
        logger.info("")
        logger.info("🔧 Troubleshooting:")
        logger.info("   • Check MT5 terminal is running and logged in")
        logger.info("   • Ensure Python dependencies are installed")
        logger.info("   • Pull models: ollama pull qwen2.5-coder llama3.1")
        logger.info("")
        logger.info("🎯 Ready for natural language trading commands!")
        logger.info("=" * 50)

        return True

    async def stop_system(self):
        """Stop all running servers"""
        logger.info("🛑 Stopping Trading Chatbot System...")

        processes = [
            ("MT5 MCP", self.mt5_process),
            ("Ollama MCP", self.ollama_process),
            ("Web server", self.web_process),
            ("Worker", self.worker_process)
        ]

        for name, process in processes:
            if process and process.poll() is None:
                logger.info(f"Stopping {name}...")
                try:
                    process.terminate()
                    # Wait up to 5 seconds for graceful shutdown
                    for _ in range(10):
                        if process.poll() is not None:
                            break
                        await asyncio.sleep(0.5)
                    else:
                        # Force kill if still running
                        process.kill()
                except Exception as e:
                    logger.error(f"Error stopping {name}: {e}")

        logger.info("✅ All servers stopped")

    async def monitor_system(self):
        """Monitor running servers and restart if necessary"""
        while True:
            processes = [
                ("MT5 MCP", self.mt5_process, self.start_mt5_server),
                ("Ollama MCP", self.ollama_process, self.start_ollama_server),
                ("Web server", self.web_process, self.start_web_server),
                ("Worker", self.worker_process, self.start_worker_server)
            ]

            restart_count = 0
            for name, process, start_func in processes:
                if process and process.poll() is not None:
                    logger.warning(f"{name} server crashed, restarting...")
                    try:
                        success = await start_func()
                        if success:
                            logger.info(f"✅ {name} server restarted")
                            restart_count += 1
                        else:
                            logger.error(f"❌ Failed to restart {name} server")
                    except Exception as e:
                        logger.error(f"Error restarting {name}: {e}")

            if restart_count > 0:
                logger.info(f"Restarted {restart_count} servers")

            await asyncio.sleep(30)  # Check every 30 seconds


async def main(args):
    """Main async function to run the system."""
    system = TradingChatbotSystem(
        mt5_host=args.mt5_host,
        mt5_port=args.mt5_port,
        ollama_host=args.ollama_host,
        ollama_port=args.ollama_port,
        web_host=args.web_host,
        web_port=args.web_port,
    )

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def shutdown_handler():
        logger.info("Shutdown signal received. Stopping system...")
        stop_event.set()

    # Add signal handlers for graceful shutdown
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, shutdown_handler)
        except NotImplementedError:
            # Windows doesn't support add_signal_handler for SIGTERM
            # SIGINT (Ctrl+C) should still work
            logger.warning(f"Signal {sig} not supported on this platform.")

    monitor_task = None
    try:
        success = await system.start_system()
        if not success:
            logger.error("Failed to start system, shutting down.")
            return 1

        logger.info("System is running. Press Ctrl+C to stop.")
        monitor_task = asyncio.create_task(system.monitor_system())

        # Wait for the stop event to be set
        await stop_event.wait()

    except Exception as e:
        logger.error(f"An unexpected error occurred in main loop: {e}", exc_info=True)
    finally:
        if monitor_task and not monitor_task.done():
            monitor_task.cancel()
        await system.stop_system()
        logger.info("System shutdown complete.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trading Chatbot System")
    parser.add_argument("--mt5-host", default="127.0.0.1", help="MT5 MCP server host")
    parser.add_argument("--mt5-port", type=int, default=8000, help="MT5 MCP server port")
    parser.add_argument("--ollama-host", default="127.0.0.1", help="Ollama MCP server host")
    parser.add_argument("--ollama-port", type=int, default=8001, help="Ollama MCP server port")
    parser.add_argument("--web-host", default="127.0.0.1", help="Web interface host")
    parser.add_argument("--web-port", type=int, default=3000, help="Web interface port")
    parser.add_argument("--command", choices=["start"], default="start", help="Command to execute")
    args = parser.parse_args()

    if args.command == "start":
        import signal
        try:
            sys.exit(asyncio.run(main(args)))
        except KeyboardInterrupt:
            logger.info("System interrupted by user. Exiting.")
            sys.exit(0)

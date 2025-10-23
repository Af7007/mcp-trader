#!/usr/bin/env python3
"""
Test script for Agent Manager Web Integration
Tests all the new endpoints and functionalities
"""

import asyncio
import json
import time
import requests
from typing import Dict, Any

class AgentManagerWebTester:
    """Test class for Agent Manager web integration"""

    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url
        self.session = requests.Session()

    def test_health(self) -> bool:
        """Test basic health endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Health check: {data.get('status')}")
                return True
            else:
                print(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Health check error: {e}")
            return False

    def test_chatbot_initialization(self) -> bool:
        """Test chatbot initialization"""
        try:
            response = self.session.post(f"{self.base_url}/api/chatbot/initialize")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Chatbot initialized: {data.get('message')}")
                    return True
                else:
                    print(f"❌ Chatbot initialization failed: {data.get('error')}")
                    return False
            else:
                print(f"❌ Chatbot initialization HTTP error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Chatbot initialization error: {e}")
            return False

    def test_agents_list(self) -> bool:
        """Test agents list endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/agents")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    agents = data.get('agents', [])
                    print(f"✅ Agents list: {len(agents)} agents found")
                    for agent in agents:
                        print(f"   - {agent.get('name')} ({agent.get('status')})")
                    return True
                else:
                    print(f"❌ Agents list failed: {data.get('error')}")
                    return False
            else:
                print(f"❌ Agents list HTTP error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Agents list error: {e}")
            return False

    def test_create_agent(self, command: str = "criar agente EURUSD com RSI") -> bool:
        """Test create agent endpoint"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/agents/create",
                json={"message": command}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    agent = data.get('agent', {})
                    print(f"✅ Agent created: {agent.get('name')} (ID: {agent.get('id')})")
                    return True
                else:
                    print(f"❌ Agent creation failed: {data.get('error')}")
                    return False
            else:
                print(f"❌ Agent creation HTTP error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Agent creation error: {e}")
            return False

    def test_agent_operations(self, agent_id: str) -> bool:
        """Test agent pause/resume/stop operations"""
        if not agent_id or agent_id == "nonexistent-id":
            print("❌ Agent operations: No valid agent ID provided")
            return False

        operations = [
            ("pause", "POST", f"/api/agents/{agent_id}/pause"),
            ("resume", "POST", f"/api/agents/{agent_id}/resume"),
            ("stop", "POST", f"/api/agents/{agent_id}/stop")
        ]

        all_success = True

        for operation_name, method, endpoint in operations:
            try:
                response = self.session.post(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ Agent {operation_name}: Success")
                    else:
                        print(f"❌ Agent {operation_name}: {data.get('message', data.get('error', 'Unknown error'))}")
                        # Don't fail the test if agent not found (expected for invalid ID)
                        if "not found" not in data.get('message', '').lower():
                            all_success = False
                else:
                    print(f"❌ Agent {operation_name} HTTP error: {response.status_code}")
                    all_success = False
            except Exception as e:
                print(f"❌ Agent {operation_name} error: {e}")
                all_success = False

            time.sleep(1)  # Small delay between operations

        return all_success

    def test_worker_operations(self) -> bool:
        """Test worker start/stop operations"""
        operations = [
            ("start", "POST", "/api/agents/worker/start"),
            ("stop", "POST", "/api/agents/worker/stop")
        ]

        all_success = True

        for operation_name, method, endpoint in operations:
            try:
                response = self.session.post(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ Worker {operation_name}: Success")
                    else:
                        print(f"❌ Worker {operation_name}: {data.get('error')}")
                        all_success = False
                else:
                    print(f"❌ Worker {operation_name} HTTP error: {response.status_code}")
                    all_success = False
            except Exception as e:
                print(f"❌ Worker {operation_name} error: {e}")
                all_success = False

            time.sleep(2)  # Delay between worker operations

        return all_success

    def test_worker_toggle(self) -> bool:
        """Test worker toggle operation"""
        try:
            response = self.session.post(f"{self.base_url}/api/agents/worker/toggle")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    worker_status = "started" if data.get('worker_running') else "stopped"
                    print(f"✅ Worker toggle: {worker_status}")
                    return True
                else:
                    print(f"❌ Worker toggle failed: {data.get('error')}")
                    return False
            else:
                print(f"❌ Worker toggle HTTP error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Worker toggle error: {e}")
            return False

    def test_bulk_operations(self) -> bool:
        """Test bulk operations (pause all, resume all, stop all)"""
        operations = [
            ("pause_all", "POST", "/api/agents/bulk/pause"),
            ("resume_all", "POST", "/api/agents/bulk/resume"),
            ("stop_all", "POST", "/api/agents/bulk/stop")
        ]

        all_success = True

        for operation_name, method, endpoint in operations:
            try:
                response = self.session.post(f"{self.base_url}{endpoint}")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        count = data.get('paused_count', data.get('resumed_count', data.get('stopped_count', 0)))
                        print(f"✅ Bulk {operation_name}: {count} agents affected")
                    else:
                        print(f"❌ Bulk {operation_name}: {data.get('error')}")
                        all_success = False
                else:
                    print(f"❌ Bulk {operation_name} HTTP error: {response.status_code}")
                    all_success = False
            except Exception as e:
                print(f"❌ Bulk {operation_name} error: {e}")
                all_success = False

            time.sleep(1)

        return all_success

    def test_agent_stats(self) -> bool:
        """Test agent statistics endpoints"""
        try:
            # Test all agents stats
            response = self.session.get(f"{self.base_url}/api/agents/stats/all")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    stats = data.get('stats', [])
                    print(f"✅ All agents stats: {len(stats)} agents")
                    for stat in stats:
                        print(f"   - {stat.get('name')}: {stat.get('trades_opened')} trades, ${stat.get('total_profit', 0):.2f} profit")
                    return True
                else:
                    print(f"❌ All agents stats failed: {data.get('error')}")
                    return False
            else:
                print(f"❌ All agents stats HTTP error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ All agents stats error: {e}")
            return False

    def test_agent_history(self, agent_id: str) -> bool:
        """Test agent history endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/agents/{agent_id}/history")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    history = data.get('history', [])
                    print(f"✅ Agent history: {len(history)} events")
                    for event in history[:3]:  # Show first 3 events
                        print(f"   - {event.get('type')} at {event.get('timestamp')}")
                    return True
                else:
                    print(f"❌ Agent history failed: {data.get('error')}")
                    return False
            else:
                print(f"❌ Agent history HTTP error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Agent history error: {e}")
            return False

    def test_summary(self) -> bool:
        """Test agents summary endpoint"""
        try:
            response = self.session.get(f"{self.base_url}/api/agents/summary")
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    summary = data.get('summary', {})
                    print("✅ Agents summary:")
                    print(f"   - Total agents: {summary.get('total_agents', 0)}")
                    print(f"   - Active: {summary.get('active', 0)}")
                    print(f"   - Paused: {summary.get('paused', 0)}")
                    print(f"   - Stopped: {summary.get('stopped', 0)}")
                    print(f"   - Total trades: {summary.get('total_trades', 0)}")
                    print(f"   - Total profit: ${summary.get('total_profit', 0):.2f}")
                    print(f"   - Worker running: {summary.get('worker_running', False)}")
                    return True
                else:
                    print(f"❌ Summary failed: {data.get('error')}")
                    return False
            else:
                print(f"❌ Summary HTTP error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Summary error: {e}")
            return False

    def test_chat_message(self, message: str = "Quanto tenho de saldo?") -> bool:
        """Test chat message endpoint"""
        try:
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json={"message": message, "use_ollama": False}
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Chat message: {message}")
                    print(f"   Response: {data.get('response', '')[:100]}...")
                    return True
                else:
                    print(f"❌ Chat message failed: {data.get('error')}")
                    return False
            else:
                print(f"❌ Chat message HTTP error: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Chat message error: {e}")
            return False

    def run_all_tests(self) -> bool:
        """Run all tests"""
        print("🧪 Starting Agent Manager Web Integration Tests")
        print("=" * 60)

        # First create an agent to get a valid ID for testing
        print("\n🔍 Creating test agent...")
        agent_create_result = self.test_create_agent("criar agente EURUSD com RSI")
        agent_id = None

        if agent_create_result:
            # Get the created agent ID from the last creation
            try:
                response = self.session.get(f"{self.base_url}/api/agents")
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success') and data.get('agents'):
                        agent_id = data['agents'][0]['id']
                        print(f"   Using agent ID: {agent_id}")
            except Exception as e:
                print(f"   Could not get agent ID: {e}")

        tests = [
            ("Health Check", self.test_health),
            ("Chatbot Initialization", self.test_chatbot_initialization),
            ("Chat Message", lambda: self.test_chat_message("Quanto tenho de saldo?")),
            ("Agents List", self.test_agents_list),
            ("Create Agent", lambda: agent_create_result),
            ("Agent Operations", lambda: self.test_agent_operations(agent_id) if agent_id else False),
            ("Worker Operations", self.test_worker_operations),
            ("Worker Toggle", self.test_worker_toggle),
            ("Bulk Operations", self.test_bulk_operations),
            ("Agent Stats", self.test_agent_stats),
            ("Summary", self.test_summary),
        ]

        passed = 0
        total = len(tests)

        for test_name, test_func in tests:
            print(f"\n🔍 Testing: {test_name}")
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
            except Exception as e:
                print(f"❌ {test_name} ERROR: {e}")

            time.sleep(1)  # Small delay between tests

        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All tests passed! Agent Manager web integration is working correctly.")
            return True
        else:
            print(f"⚠️  {total - passed} tests failed. Check the output above for details.")
            return False

def main():
    """Main test function"""
    import argparse

    parser = argparse.ArgumentParser(description="Test Agent Manager Web Integration")
    parser.add_argument("--url", default="http://localhost:3000", help="Web server URL")
    parser.add_argument("--test", help="Run specific test only")

    args = parser.parse_args()

    tester = AgentManagerWebTester(args.url)

    if args.test:
        # Run specific test
        test_methods = {
            "health": tester.test_health,
            "init": tester.test_chatbot_initialization,
            "agents": tester.test_agents_list,
            "create": lambda: tester.test_create_agent(),
            "worker": tester.test_worker_operations,
            "bulk": tester.test_bulk_operations,
            "stats": tester.test_agent_stats,
            "summary": tester.test_summary,
            "chat": lambda: tester.test_chat_message(),
        }

        if args.test in test_methods:
            print(f"🧪 Running specific test: {args.test}")
            success = test_methods[args.test]()
            print("✅ PASSED" if success else "❌ FAILED")
        else:
            print(f"❌ Unknown test: {args.test}")
            print(f"Available tests: {list(test_methods.keys())}")
    else:
        # Run all tests
        success = tester.run_all_tests()
        exit(0 if success else 1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Comprehensive Feature Test Script for TradeIQ
Tests all core features including:
1. Market volatility detection → Analysis → Personalized insight → Bluesky content generation
2. LLM/AI Agent functionality
3. API endpoints
"""

import sys
import time
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

BASE_URL = "http://127.0.0.1:8000"
API_BASE = f"{BASE_URL}/api"

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text:^70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")


def print_success(text: str):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")


def print_error(text: str):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")


def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")


def print_info(text: str):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")


def check_server() -> bool:
    """Check if backend server is running"""
    try:
        response = requests.get(f"{BASE_URL}/api/", timeout=5)
        return response.status_code in [200, 404]  # 404 is OK, means server is running
    except requests.exceptions.RequestException:
        return False


def test_agent_query(agent_type: str, query: str) -> Optional[Dict[str, Any]]:
    """Test agent query endpoint"""
    print_info(f"Testing {agent_type} agent with query: '{query}'")
    
    try:
        response = requests.post(
            f"{API_BASE}/agents/query/",
            json={
                "query": query,
                "agent_type": agent_type,
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success(f"{agent_type} agent responded")
            print(f"   Response: {result.get('response', '')[:200]}...")
            print(f"   Tools used: {result.get('tools_used', [])}")
            return result
        else:
            print_error(f"Status {response.status_code}: {response.text[:200]}")
            return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None


def test_agent_chat(message: str) -> Optional[Dict[str, Any]]:
    """Test agent chat endpoint"""
    print_info(f"Testing chat with message: '{message}'")
    
    try:
        response = requests.post(
            f"{API_BASE}/agents/chat/",
            json={"message": message},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Chat responded")
            print(f"   Message: {result.get('message', '')[:200]}...")
            print(f"   Agent type: {result.get('agent_type', 'unknown')}")
            return result
        else:
            print_error(f"Status {response.status_code}: {response.text[:200]}")
            return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None


def test_pipeline_full(custom_event: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Test the full 4-agent pipeline"""
    print_info("Testing full Agent Team Pipeline")
    
    # Demo portfolio
    demo_portfolio = [
        {"instrument": "EUR/USD", "direction": "long", "size": 1.0, "entry_price": 1.083, "pnl": 12.5},
        {"instrument": "BTC/USD", "direction": "long", "size": 0.1, "entry_price": 95000, "pnl": 250.0},
        {"instrument": "GOLD", "direction": "short", "size": 0.5, "entry_price": 2860, "pnl": -15.0},
    ]
    
    payload = {
        "user_portfolio": demo_portfolio,
        "skip_content": False,  # Generate Bluesky content
    }
    
    if custom_event:
        payload["custom_event"] = custom_event
        print_info(f"Using custom event: {custom_event.get('instrument')} {custom_event.get('change_pct', 0):+.2f}%")
    
    try:
        print_info("Sending pipeline request (this may take 30-60 seconds)...")
        response = requests.post(
            f"{API_BASE}/agents/pipeline/",
            json=payload,
            timeout=120  # Longer timeout for LLM calls
        )
        
        if response.status_code == 200:
            result = response.json()
            print_success("Pipeline completed")
            
            # Check each stage
            if result.get("volatility_event"):
                event = result["volatility_event"]
                print_success(f"Stage 1 - Market Monitor: Detected {event.get('instrument')} {event.get('price_change_pct', 0):+.2f}%")
            else:
                print_warning("Stage 1 - Market Monitor: No event detected")
            
            if result.get("analysis_report"):
                report = result["analysis_report"]
                print_success(f"Stage 2 - Analyst: {report.get('event_summary', '')[:100]}...")
                print(f"   Root causes: {len(report.get('root_causes', []))} found")
            else:
                print_warning("Stage 2 - Analyst: No report generated")
            
            if result.get("personalized_insight"):
                insight = result["personalized_insight"]
                print_success(f"Stage 3 - Portfolio Advisor: {insight.get('impact_summary', '')[:100]}...")
                print(f"   Risk: {insight.get('risk_assessment', 'unknown')}")
            else:
                print_warning("Stage 3 - Portfolio Advisor: No insight generated")
            
            if result.get("market_commentary"):
                commentary = result["market_commentary"]
                print_success(f"Stage 4 - Content Creator: Generated Bluesky post")
                print(f"   Post preview: {commentary.get('post', '')[:150]}...")
                print(f"   Published: {commentary.get('published', False)}")
            else:
                print_warning("Stage 4 - Content Creator: No commentary generated")
            
            print(f"\n   Status: {result.get('status', 'unknown')}")
            if result.get("errors"):
                print_warning(f"   Warnings: {len(result['errors'])}")
                for err in result["errors"]:
                    print(f"      - {err}")
            
            return result
        else:
            print_error(f"Status {response.status_code}: {response.text[:500]}")
            return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None


def test_individual_agents():
    """Test individual agent endpoints"""
    print_header("Testing Individual Agent Endpoints")
    
    # Test Monitor
    print_info("Testing Market Monitor agent")
    try:
        response = requests.post(
            f"{API_BASE}/agents/monitor/",
            json={"custom_event": {"instrument": "BTC/USD", "price": 97500, "change_pct": 5.2}},
            timeout=30
        )
        if response.status_code == 200:
            print_success("Market Monitor agent working")
        else:
            print_error(f"Monitor failed: {response.status_code}")
    except Exception as e:
        print_error(f"Monitor error: {str(e)}")
    
    # Test Analyst
    print_info("Testing Analyst agent")
    try:
        response = requests.post(
            f"{API_BASE}/agents/analyst/",
            json={
                "instrument": "BTC/USD",
                "current_price": 97500,
                "price_change_pct": 5.2,
                "direction": "spike",
                "magnitude": "high"
            },
            timeout=60
        )
        if response.status_code == 200:
            result = response.json()
            print_success(f"Analyst agent working: {result.get('event_summary', '')[:100]}...")
        else:
            print_error(f"Analyst failed: {response.status_code}")
    except Exception as e:
        print_error(f"Analyst error: {str(e)}")


def main():
    print_header("TradeIQ Comprehensive Feature Test")
    
    # Check server
    print_info("Checking if backend server is running...")
    if not check_server():
        print_error("Backend server is not running!")
        print_info("Please start the backend server first:")
        print_info("  ./scripts/start_backend.sh")
        print_info("  or")
        print_info("  cd backend && python manage.py runserver")
        return 1
    
    print_success("Backend server is running")
    
    # Test 1: LLM/AI Agent Queries
    print_header("Test 1: LLM/AI Agent Functionality")
    
    # Market agent
    test_agent_query("market", "Why did EUR/USD move today?")
    time.sleep(2)
    
    # Behavior agent (requires user_id, but we'll test without)
    test_agent_query("behavior", "What patterns do you see in my trading?")
    time.sleep(2)
    
    # Content agent
    test_agent_query("content", "Generate a Bluesky post about BTC volatility")
    time.sleep(2)
    
    # Chat endpoint
    test_agent_chat("Explain what happened to gold prices today")
    time.sleep(2)
    
    # Test 2: Full Pipeline - Market Volatility → Analysis → Personalized → Bluesky
    print_header("Test 2: Full Agent Team Pipeline")
    print_info("Testing: Market Volatility → Analysis → Personalized Insight → Bluesky Content")
    
    # Test with custom BTC event
    btc_event = {
        "instrument": "BTC/USD",
        "price": 97500,
        "change_pct": 5.2
    }
    
    pipeline_result = test_pipeline_full(custom_event=btc_event)
    
    if pipeline_result:
        print_success("\n✅ Full pipeline test completed!")
        
        # Verify all stages completed
        stages_complete = {
            "Market Monitor": bool(pipeline_result.get("volatility_event")),
            "Analyst": bool(pipeline_result.get("analysis_report")),
            "Portfolio Advisor": bool(pipeline_result.get("personalized_insight")),
            "Content Creator": bool(pipeline_result.get("market_commentary")),
        }
        
        print("\n" + "="*70)
        print("Pipeline Stage Summary:")
        print("="*70)
        for stage, complete in stages_complete.items():
            status = "✅" if complete else "❌"
            print(f"  {status} {stage}")
        
        # Show Bluesky content if generated
        if pipeline_result.get("market_commentary"):
            commentary = pipeline_result["market_commentary"]
            print("\n" + "="*70)
            print("Generated Bluesky Post:")
            print("="*70)
            print(commentary.get("post", ""))
            print(f"\nHashtags: {', '.join(commentary.get('hashtags', []))}")
            if commentary.get("published"):
                print(f"✅ Published to Bluesky: {commentary.get('bluesky_url', 'N/A')}")
            else:
                print("⚠️  Draft mode (not published)")
    else:
        print_error("Pipeline test failed!")
    
    # Test 3: Individual Agents
    print_header("Test 3: Individual Agent Endpoints")
    test_individual_agents()
    
    # Summary
    print_header("Test Summary")
    print_success("All tests completed!")
    print_info("Check the results above for any warnings or errors.")
    print_info("\nTo view the frontend:")
    print_info("  ./scripts/start_frontend.sh")
    print_info("  Then visit: http://localhost:3000/pipeline")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())

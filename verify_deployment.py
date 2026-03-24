"""
Deployment Verification Script

This script verifies that your Graph Query System is properly deployed
and all features are working correctly.

Usage:
    python verify_deployment.py <backend_url>
    
Example:
    python verify_deployment.py https://your-app.onrender.com
"""

import sys
import requests
import json
from typing import Dict, Any, List


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(80)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 80}{Colors.RESET}\n")


def print_test(name: str, passed: bool, details: str = ""):
    """Print test result."""
    status = f"{Colors.GREEN}✓ PASS{Colors.RESET}" if passed else f"{Colors.RED}✗ FAIL{Colors.RESET}"
    print(f"{status} | {name}")
    if details:
        print(f"       {Colors.YELLOW}{details}{Colors.RESET}")


def test_health_check(base_url: str) -> bool:
    """Test health check endpoint."""
    try:
        response = requests.get(f"{base_url}/api/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            neo4j_connected = data.get("neo4j_connected", False)
            llm_provider = data.get("llm_provider", "unknown")
            
            if neo4j_connected:
                print_test("Health Check", True, f"Neo4j connected, LLM: {llm_provider}")
                return True
            else:
                print_test("Health Check", False, "Neo4j not connected")
                return False
        else:
            print_test("Health Check", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_test("Health Check", False, f"Error: {str(e)}")
        return False


def test_schema_endpoint(base_url: str) -> bool:
    """Test schema endpoint."""
    try:
        response = requests.get(f"{base_url}/api/schema", timeout=10)
        if response.status_code == 200:
            data = response.json()
            node_types = data.get("node_types", {})
            relationship_types = data.get("relationship_types", [])
            
            # Check for SAP entities
            sap_entities = ["SalesOrder", "BillingDocument", "BusinessPartner", "Product"]
            has_sap = any(entity in node_types for entity in sap_entities)
            
            if has_sap:
                print_test(
                    "Schema Endpoint", 
                    True, 
                    f"{len(node_types)} node types, {len(relationship_types)} relationship types"
                )
                return True
            else:
                print_test("Schema Endpoint", False, "SAP entities not found in schema")
                return False
        else:
            print_test("Schema Endpoint", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_test("Schema Endpoint", False, f"Error: {str(e)}")
        return False


def test_query_endpoint(base_url: str) -> bool:
    """Test query endpoint with a simple query."""
    try:
        query_data = {
            "query": "Show me the top 5 products by sales orders",
            "include_cypher": True
        }
        
        response = requests.post(
            f"{base_url}/api/query",
            json=query_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            results = data.get("data", [])
            cypher = data.get("cypher", "")
            
            if success and len(results) > 0:
                print_test(
                    "Query Endpoint", 
                    True, 
                    f"Returned {len(results)} results"
                )
                return True
            elif success and len(results) == 0:
                print_test("Query Endpoint", False, "Query succeeded but returned no results (data may not be imported)")
                return False
            else:
                error = data.get("error", "Unknown error")
                print_test("Query Endpoint", False, f"Query failed: {error}")
                return False
        else:
            print_test("Query Endpoint", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_test("Query Endpoint", False, f"Error: {str(e)}")
        return False


def test_guardrails(base_url: str) -> bool:
    """Test guardrails with an off-topic query."""
    try:
        query_data = {
            "query": "What is the weather today?"
        }
        
        response = requests.post(
            f"{base_url}/api/query",
            json=query_data,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            success = data.get("success", False)
            error = data.get("error", "")
            
            # Guardrails should reject this query
            if not success and "domain" in error.lower():
                print_test("Guardrails", True, "Off-topic query correctly rejected")
                return True
            else:
                print_test("Guardrails", False, "Off-topic query was not rejected")
                return False
        else:
            print_test("Guardrails", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_test("Guardrails", False, f"Error: {str(e)}")
        return False


def test_graph_endpoint(base_url: str) -> bool:
    """Test graph data endpoint."""
    try:
        response = requests.get(f"{base_url}/api/graph?limit=10", timeout=10)
        if response.status_code == 200:
            data = response.json()
            nodes = data.get("nodes", [])
            edges = data.get("edges", [])
            
            if len(nodes) > 0:
                print_test(
                    "Graph Endpoint", 
                    True, 
                    f"{len(nodes)} nodes, {len(edges)} edges"
                )
                return True
            else:
                print_test("Graph Endpoint", False, "No nodes returned (data may not be imported)")
                return False
        else:
            print_test("Graph Endpoint", False, f"Status code: {response.status_code}")
            return False
    except Exception as e:
        print_test("Graph Endpoint", False, f"Error: {str(e)}")
        return False


def test_cors(base_url: str) -> bool:
    """Test CORS headers."""
    try:
        response = requests.options(
            f"{base_url}/api/health",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET"
            },
            timeout=10
        )
        
        cors_header = response.headers.get("Access-Control-Allow-Origin", "")
        
        if cors_header:
            print_test("CORS Configuration", True, f"CORS enabled: {cors_header}")
            return True
        else:
            print_test("CORS Configuration", False, "CORS headers not found")
            return False
    except Exception as e:
        print_test("CORS Configuration", False, f"Error: {str(e)}")
        return False


def main():
    """Main verification function."""
    if len(sys.argv) < 2:
        print(f"{Colors.RED}Error: Backend URL required{Colors.RESET}")
        print(f"\nUsage: python verify_deployment.py <backend_url>")
        print(f"Example: python verify_deployment.py https://your-app.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')
    
    print_header("Graph Query System - Deployment Verification")
    print(f"Testing backend: {Colors.BOLD}{base_url}{Colors.RESET}\n")
    
    # Run all tests
    tests = [
        ("Health Check", lambda: test_health_check(base_url)),
        ("Schema Endpoint", lambda: test_schema_endpoint(base_url)),
        ("Graph Endpoint", lambda: test_graph_endpoint(base_url)),
        ("Query Endpoint", lambda: test_query_endpoint(base_url)),
        ("Guardrails", lambda: test_guardrails(base_url)),
        ("CORS Configuration", lambda: test_cors(base_url)),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print_test(name, False, f"Unexpected error: {str(e)}")
            results.append((name, False))
    
    # Print summary
    print_header("Verification Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Tests Passed: {Colors.GREEN}{passed}{Colors.RESET}/{total}")
    print(f"Tests Failed: {Colors.RED}{total - passed}{Colors.RESET}/{total}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ All tests passed! Your deployment is ready.{Colors.RESET}")
        print(f"\n{Colors.BLUE}Next steps:{Colors.RESET}")
        print(f"1. Test the frontend at your Vercel URL")
        print(f"2. Try the example queries in the chat interface")
        print(f"3. Submit the assignment form")
        sys.exit(0)
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ Some tests failed. Please review the errors above.{Colors.RESET}")
        print(f"\n{Colors.BLUE}Common issues:{Colors.RESET}")
        print(f"- Health Check fails: Check Neo4j credentials")
        print(f"- Query/Graph endpoints return no data: Import SAP data first")
        print(f"- CORS fails: Add frontend URL to CORS_ORIGINS")
        sys.exit(1)


if __name__ == "__main__":
    main()

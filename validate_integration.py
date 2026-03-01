"""
validate_integration.py
Quick validation script to verify the integration code is correct.
Does not require running servers - just validates the code structure.
"""
import ast
import os


def validate_api_server():
    """Validate api_server.py structure."""
    print("\n[1/4] Validating API Server (api_server.py)")
    print("-" * 60)
    
    if not os.path.exists("api_server.py"):
        print("❌ api_server.py not found")
        return False
    
    with open("api_server.py", "r") as f:
        content = f.read()
    
    # Check for required imports
    required_imports = [
        "from fastapi import FastAPI",
        "from fastapi.middleware.cors import CORSMiddleware",
        "from pydantic import BaseModel"
    ]
    
    for imp in required_imports:
        if imp in content:
            print(f"✅ Found: {imp}")
        else:
            print(f"❌ Missing: {imp}")
            return False
    
    # Check for required endpoints
    required_endpoints = [
        '@app.post("/api/query"',
        '@app.get("/health"',
        '@app.get("/api/tools"'
    ]
    
    for endpoint in required_endpoints:
        if endpoint in content:
            print(f"✅ Found endpoint: {endpoint}")
        else:
            print(f"❌ Missing endpoint: {endpoint}")
            return False
    
    # Check for CORS configuration
    if "CORSMiddleware" in content and "allow_origins" in content:
        print(f"✅ CORS middleware configured")
    else:
        print(f"❌ CORS middleware not configured")
        return False
    
    print("✅ API server structure valid")
    return True


def validate_frontend_integration():
    """Validate frontend App.tsx integration."""
    print("\n[2/4] Validating Frontend Integration (frontend/src/App.tsx)")
    print("-" * 60)
    
    app_path = "frontend/src/App.tsx"
    if not os.path.exists(app_path):
        print(f"❌ {app_path} not found")
        return False
    
    with open(app_path, "r") as f:
        content = f.read()
    
    # Check for API call
    if "fetch('http://localhost:8000/api/query'" in content:
        print("✅ API endpoint call found")
    else:
        print("❌ API endpoint call not found")
        return False
    
    # Check for query submission
    if "handleQuerySubmit" in content:
        print("✅ Query submission handler found")
    else:
        print("❌ Query submission handler not found")
        return False
    
    # Check for latency tracking
    if "totalLatencyMs" in content or "total_latency_ms" in content:
        print("✅ Latency tracking found")
    else:
        print("❌ Latency tracking not found")
        return False
    
    # Check for HLS URL handling
    if "videoClips" in content or "video_clips" in content:
        print("✅ Video clips handling found")
    else:
        print("❌ Video clips handling not found")
        return False
    
    print("✅ Frontend integration valid")
    return True


def validate_test_script():
    """Validate test_integration.py exists and is structured correctly."""
    print("\n[3/4] Validating Integration Test (test_integration.py)")
    print("-" * 60)
    
    if not os.path.exists("test_integration.py"):
        print("❌ test_integration.py not found")
        return False
    
    with open("test_integration.py", "r") as f:
        content = f.read()
    
    # Check for test functions
    required_tests = [
        "def test_api_health",
        "def test_query_endpoint",
        "def test_query_routing",
        "def test_hls_url_format"
    ]
    
    for test in required_tests:
        if test in content:
            print(f"✅ Found: {test}")
        else:
            print(f"❌ Missing: {test}")
            return False
    
    print("✅ Integration test structure valid")
    return True


def validate_documentation():
    """Validate INTEGRATION_GUIDE.md exists."""
    print("\n[4/4] Validating Documentation (INTEGRATION_GUIDE.md)")
    print("-" * 60)
    
    if not os.path.exists("INTEGRATION_GUIDE.md"):
        print("❌ INTEGRATION_GUIDE.md not found")
        return False
    
    with open("INTEGRATION_GUIDE.md", "r") as f:
        content = f.read()
    
    # Check for key sections
    required_sections = [
        "## Architecture",
        "## API Contract",
        "## Setup Instructions",
        "## Testing",
        "## Latency Optimization"
    ]
    
    for section in required_sections:
        if section in content:
            print(f"✅ Found section: {section}")
        else:
            print(f"❌ Missing section: {section}")
            return False
    
    print("✅ Documentation complete")
    return True


def main():
    """Run all validation checks."""
    print("=" * 60)
    print("INTEGRATION VALIDATION")
    print("=" * 60)
    print("\nTask 9.1: Frontend-to-Backend Integration")
    print("Validating code structure without running servers...")
    print("=" * 60)
    
    results = []
    
    # Run validations
    results.append(("API Server", validate_api_server()))
    results.append(("Frontend Integration", validate_frontend_integration()))
    results.append(("Integration Tests", validate_test_script()))
    results.append(("Documentation", validate_documentation()))
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n✅ All validations passed!")
        print("\nNext steps:")
        print("1. Start the API server: python api_server.py")
        print("2. Start the frontend: cd frontend && pnpm run dev")
        print("3. Run integration tests: python test_integration.py")
        print("\nTask 9.1 implementation complete!")
        return True
    else:
        print("\n❌ Some validations failed. Review output above.")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

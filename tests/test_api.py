import requests
import json
import time

# API base URL
BASE_URL = "http://localhost:8000"

def test_health_endpoint():
    """Test the health check endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing health endpoint: {e}")
        return False

def test_chat_endpoint():
    """Test the chat endpoint."""
    print("\nTesting chat endpoint...")
    try:
        payload = {
            "question": "What is the annual leave policy?",
            "collection_name": "documents"
        }
        
        response = requests.post(
            f"{BASE_URL}/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing chat endpoint: {e}")
        return False

def test_collections_endpoint():
    """Test the collections endpoint."""
    print("\nTesting collections endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/collections")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing collections endpoint: {e}")
        return False

def test_error_handling():
    """Test error handling with invalid requests."""
    print("\nTesting error handling...")
    
    # Test empty question
    try:
        payload = {"question": ""}
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Empty question - Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error testing empty question: {e}")
    
    # Test very long question
    try:
        payload = {"question": "a" * 1001}  # Exceeds max length
        response = requests.post(f"{BASE_URL}/chat", json=payload)
        print(f"Long question - Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error testing long question: {e}")

def main():
    """Run all API tests."""
    print("=== FastAPI Backend Tests ===")
    
    # Wait a moment for server to start
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    # Test endpoints
    health_ok = test_health_endpoint()
    chat_ok = test_chat_endpoint()
    collections_ok = test_collections_endpoint()
    
    # Test error handling
    test_error_handling()
    
    # Summary
    print("\n=== Test Summary ===")
    print(f"Health endpoint: {'✓' if health_ok else '✗'}")
    print(f"Chat endpoint: {'✓' if chat_ok else '✗'}")
    print(f"Collections endpoint: {'✓' if collections_ok else '✗'}")
    
    if all([health_ok, chat_ok, collections_ok]):
        print("\nAll tests passed! FastAPI backend is working correctly.")
    else:
        print("\nSome tests failed. Check the server logs for details.")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""Example usage of the generic API client."""

import json
from cli_app.api_client import APIClient
from cli_app.config import Config


def main():
    """Demonstrate API client usage."""
    print("🚀 Python CLI App - API Client Example")
    print("=" * 50)
    
    # Load configuration
    try:
        config = Config()
        if not config.is_configured():
            print("❌ API not configured. Please run 'cli-app configure' first.")
            print("   Or set environment variables:")
            print("   export CLI_APP_API_ENDPOINT='https://api.example.com'")
            print("   export CLI_APP_API_TOKEN='your-token'")
            return
        
        print(f"✅ Configuration loaded:")
        print(f"   Endpoint: {config.api_endpoint}")
        print(f"   Token: {'*' * 8}")
        print(f"   Timeout: {config.timeout}s")
        print()
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return
    
    # Initialize API client
    try:
        client = APIClient(config.api_endpoint, config.api_token)
        print("🔌 API client initialized successfully")
        print()
        
    except Exception as e:
        print(f"❌ Error initializing API client: {e}")
        return
    
    # Example API operations
    print("📡 Example API Operations:")
    print("-" * 30)
    
    # Health check
    print("1. Health Check:")
    try:
        is_healthy = client.health_check()
        status = "✅ Healthy" if is_healthy else "❌ Unhealthy"
        print(f"   Status: {status}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # List resources
    print("2. List Resources:")
    try:
        resources = client.list_resources("users")
        print(f"   Response: {json.dumps(resources, indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Get specific resource
    print("3. Get Resource:")
    try:
        resource = client.get_resource("users/1")
        print(f"   Response: {json.dumps(resource, indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Create resource
    print("4. Create Resource:")
    try:
        new_data = {
            "name": "Example User",
            "email": "example@example.com",
            "status": "active"
        }
        created = client.create_resource("users", new_data)
        print(f"   Created: {json.dumps(created, indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Update resource
    print("5. Update Resource:")
    try:
        update_data = {"status": "inactive"}
        updated = client.update_resource("users/1", update_data)
        print(f"   Updated: {json.dumps(updated, indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Delete resource
    print("6. Delete Resource:")
    try:
        success = client.delete_resource("users/999")
        status = "✅ Success" if success else "❌ Failed"
        print(f"   Status: {status}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    # Context manager usage
    print("7. Context Manager Usage:")
    try:
        with APIClient(config.api_endpoint, config.api_token) as ctx_client:
            health = ctx_client.health_check()
            print(f"   Health check via context manager: {'✅' if health else '❌'}")
    except Exception as e:
        print(f"   Error: {e}")
    print()
    
    print("🎉 Example completed!")
    print("\n💡 Tips:")
    print("   - Use the CLI app: cli-app --help")
    print("   - Check status: cli-app status")
    print("   - Fetch data: cli-app fetch --resource users")
    print("   - Create data: cli-app create --resource users --data '{\"name\": \"John\"}'")


if __name__ == "__main__":
    main() 
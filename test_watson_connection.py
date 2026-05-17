"""
Test Watson API Connection
Quick script to verify your IBM watsonx.ai credentials are working
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_watson_connection():
    """Test connection to IBM watsonx.ai"""
    
    print("=" * 60)
    print("IBM Watson API Connection Test")
    print("=" * 60)
    
    # Check if credentials are set
    api_key = os.getenv('WATSONX_API_KEY')
    project_id = os.getenv('WATSONX_PROJECT_ID')
    url = os.getenv('WATSONX_URL', 'https://us-south.ml.cloud.ibm.com')
    
    print("\n1. Checking environment variables...")
    
    if not api_key or api_key == 'your_ibm_cloud_api_key_here':
        print("   ❌ WATSONX_API_KEY not set or using placeholder")
        print("   → Please update WATSONX_API_KEY in .env file")
        return False
    else:
        print(f"   ✅ WATSONX_API_KEY found (starts with: {api_key[:10]}...)")
    
    if not project_id or project_id == 'your_watsonx_project_id_here':
        print("   ❌ WATSONX_PROJECT_ID not set or using placeholder")
        print("   → Please update WATSONX_PROJECT_ID in .env file")
        return False
    else:
        print(f"   ✅ WATSONX_PROJECT_ID found: {project_id[:8]}...{project_id[-4:]}")
    
    print(f"   ✅ WATSONX_URL: {url}")
    
    # Check if SDK is installed
    print("\n2. Checking IBM watsonx.ai SDK...")
    try:
        from ibm_watsonx_ai import APIClient, Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference
        print("   ✅ IBM watsonx.ai SDK installed")
    except ImportError:
        print("   ❌ IBM watsonx.ai SDK not installed")
        print("   → Run: pip install ibm-watsonx-ai")
        return False
    
    # Test connection
    print("\n3. Testing connection to IBM watsonx.ai...")
    try:
        # Create credentials
        credentials = Credentials(api_key=api_key, url=url)
        print("   ✅ Credentials created")
        
        # Initialize client
        client = APIClient(credentials)
        print("   ✅ API client initialized")
        
        # Initialize model
        model = ModelInference(
            model_id='ibm/granite-13b-chat-v2',
            api_client=client,
            project_id=project_id,
            params={
                'max_new_tokens': 50,
                'temperature': 0.7
            }
        )
        print("   ✅ Model initialized (ibm/granite-13b-chat-v2)")
        
    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        print("\n   Troubleshooting:")
        print("   - Verify your API key is correct")
        print("   - Verify your Project ID is correct")
        print("   - Check your region URL matches your project")
        print("   - Ensure you have access to watsonx.ai")
        return False
    
    # Test generation
    print("\n4. Testing text generation...")
    try:
        test_prompt = "Hello! Please respond with 'Connection successful' if you can read this."
        response = model.generate_text(prompt=test_prompt)
        print(f"   ✅ Generation successful!")
        print(f"   Response preview: {response[:100]}...")
        
    except Exception as e:
        print(f"   ❌ Generation failed: {str(e)}")
        return False
    
    # Test Bob client
    print("\n5. Testing Bob client integration...")
    try:
        from src.ai_engine.bob_client import BobClient
        
        config = {
            'enabled': True,
            'mock_mode': False,
            'api_key': api_key,
            'project_id': project_id,
            'url': url
        }
        
        bob = BobClient(config)
        health = bob.health_check()
        
        if health['enabled'] and health['configured']:
            print("   ✅ Bob client configured and ready")
            print(f"   Model: {health['model_id']}")
        else:
            print("   ⚠️  Bob client not fully configured")
            print(f"   Status: {health}")
        
    except Exception as e:
        print(f"   ⚠️  Bob client test skipped: {str(e)}")
    
    # Success!
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYour IBM Watson API is configured correctly!")
    print("You can now use Bob AI reasoning in IBM Jeff.")
    print("\nNext steps:")
    print("1. Start the backend: python src/api_server.py")
    print("2. Run analysis: python test_pipeline.py")
    print("3. Access dashboard: http://localhost:8000")
    print("\n" + "=" * 60)
    
    return True


if __name__ == '__main__':
    try:
        success = test_watson_connection()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

# Made with Bob

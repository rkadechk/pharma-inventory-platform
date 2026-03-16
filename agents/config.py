"""
Anthropic Claude API Configuration
Initializes and manages Claude client for CrewAI agents
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get API key from environment
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

if not ANTHROPIC_API_KEY:
    print("\n❌ ERROR: ANTHROPIC_API_KEY not found!")
    print("\nTo get your API key:")
    print("1. Visit: https://console.anthropic.com/")
    print("2. Sign up or log in")
    print("3. Create an API key")
    print("4. Add to .env file: ANTHROPIC_API_KEY=your_key_here")
    print("\nOr set environment variable:")
    print("   export ANTHROPIC_API_KEY='your_key_here'")
    sys.exit(1)

# Claude Configuration
CLAUDE_MODEL = "claude-3-5-sonnet-20241022"
MAX_TOKENS = 4096
TEMPERATURE = 0.7

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
SYNTHETIC_DATA_DIR = Path(os.getenv("SYNTHETIC_DATA_DIR", PROJECT_ROOT / "data-generation" / "synthetic_data"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", PROJECT_ROOT / "output"))
MODELS_DIR = Path(os.getenv("MODELS_DIR", PROJECT_ROOT / "models"))

# Create output directories if they don't exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

def test_claude_connection():
    """Test if Claude API is accessible"""
    try:
        from anthropic import Anthropic
        
        client = Anthropic()
        
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Say 'Connected to Claude' if you receive this."}
            ]
        )
        
        print("✅ Claude API Connection Successful")
        print(f"   Model: {CLAUDE_MODEL}")
        print(f"   Response: {message.content[0].text if message.content else 'Empty'}")
        return True
        
    except Exception as e:
        print(f"❌ Claude API Connection Failed")
        print(f"   Error: {str(e)}")
        return False

def get_claude_client():
    """Get initialized Anthropic client"""
    from anthropic import Anthropic
    return Anthropic()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("TESTING CLAUDE API CONNECTION")
    print("="*60)
    
    success = test_claude_connection()
    
    if success:
        print("\n✅ Configuration OK - Ready to use CrewAI!")
    else:
        print("\n❌ Configuration Error - See above for details")
        sys.exit(1)

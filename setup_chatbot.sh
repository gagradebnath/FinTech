#!/bin/bash
# Script to set up Ollama and download Llama3.2:3b model
# Run this script to prepare the chat bot backend

echo "=== FinGuard ChatBot Setup ==="
echo "Setting up Ollama with Llama3.2:3b model"
echo

# Check if Ollama is installed
if ! command -v ollama &> /dev/null
then
    echo "❌ Ollama is not installed. Please install it first:"
    echo "   - Windows: Download from https://ollama.ai/download/windows"
    echo "   - macOS: Download from https://ollama.ai/download/mac" 
    echo "   - Linux: curl -fsSL https://ollama.ai/install.sh | sh"
    echo
    exit 1
fi

echo "✅ Ollama is installed"

# Check if Ollama service is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1
then
    echo "❌ Ollama service is not running. Please start it:"
    echo "   - Windows: Run 'ollama serve' in Command Prompt"
    echo "   - macOS/Linux: Run 'ollama serve' in terminal"
    echo
    exit 1
fi

echo "✅ Ollama service is running"

# Check if llama3.2:3b model is already available
if ollama list | grep -q "llama3.2:3b"
then
    echo "✅ Llama3.2:3b model is already installed"
else
    echo "📥 Downloading Llama3.2:3b model (this may take a while)..."
    ollama pull llama3.2:3b
    
    if [ $? -eq 0 ]; then
        echo "✅ Llama3.2:3b model downloaded successfully"
    else
        echo "❌ Failed to download Llama3.2:3b model"
        exit 1
    fi
fi

# Test the model
echo "🧪 Testing the chat model..."
response=$(curl -s -X POST http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2:3b",
    "messages": [
      {"role": "user", "content": "Hello, are you working?"}
    ],
    "stream": false
  }' | python -c "import sys, json; print(json.load(sys.stdin).get('message', {}).get('content', 'No response'))" 2>/dev/null)

if [ $? -eq 0 ] && [ ! -z "$response" ]; then
    echo "✅ Chat model is working correctly"
    echo "   Response: $response"
else
    echo "❌ Failed to test chat model"
    exit 1
fi

echo
echo "🎉 ChatBot setup completed successfully!"
echo
echo "Next steps:"
echo "1. Make sure Ollama service keeps running (ollama serve)"
echo "2. Start your FinGuard application"
echo "3. Look for the floating chat button in the bottom-right corner"
echo
echo "Troubleshooting:"
echo "- If chat doesn't work, check that Ollama is running on localhost:11434"
echo "- Check browser console for any JavaScript errors"
echo "- Verify the model is loaded: ollama list"

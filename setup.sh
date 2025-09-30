#!/bin/bash

# FloatChat Setup Script
# This script helps set up the FloatChat environment including LLM services

echo "🌊 FloatChat Setup Script"
echo "========================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install Ollama
install_ollama() {
    echo "Installing Ollama..."
    if command_exists curl; then
        curl -fsSL https://ollama.ai/install.sh | sh
        echo "Ollama installed successfully"
    else
        echo "curl not found. Please install curl first or install Ollama manually from https://ollama.ai"
        return 1
    fi
}

# Function to setup Ollama with Mistral
setup_ollama() {
    echo "Setting up Ollama with Mistral model..."
    
    if ! command_exists ollama; then
        read -p "Ollama not found. Install it? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            install_ollama
        else
            echo "Skipping Ollama setup"
            return 1
        fi
    fi
    
    echo "Starting Ollama service..."
    ollama serve &
    OLLAMA_PID=$!
    
    # Wait for service to start
    echo "Waiting for Ollama service to start..."
    sleep 5
    
    echo "Pulling Mistral model (this may take a few minutes)..."
    ollama pull mistral
    
    echo "Ollama setup complete"
    echo "Ollama is running on http://localhost:11434"
    
    # Test the model
    echo "Testing Mistral model..."
    echo "Hello, how are you?" | ollama run mistral
}

# Main setup process
main() {
    echo "Checking prerequisites..."
    
    # Check Python
    if command_exists python3; then
        echo "Python3 found: $(python3 --version)"
    else
        echo "Python3 not found. Please install Python 3.8 or higher"
        exit 1
    fi
    
    # Check pip
    if command_exists pip || command_exists pip3; then
        echo "pip found"
    else
        echo "pip not found. Please install pip"
        exit 1
    fi
    
    echo ""
    echo "Setting up FloatChat..."
    
    # Install Python dependencies
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    
    echo ""
    echo "LLM Setup Options:"
    echo "1. Ollama (Local, Recommended)"
    echo "2. Mistral API (Requires API key)"
    echo "3. Skip LLM setup (Use keyword fallback)"
    
    read -p "Choose an option (1-3): " -n 1 -r
    echo
    
    case $REPLY in
        1)
            setup_ollama
            ;;
        2)
            echo "Mistral API Setup"
            echo "Please get your API key from https://console.mistral.ai"
            read -p "Enter your Mistral API key: " mistral_key
            
            # Update .env file
            sed -i "s/LLM_PROVIDER=ollama/LLM_PROVIDER=mistral/" .env
            sed -i "s/MISTRAL_API_KEY=/MISTRAL_API_KEY=$mistral_key/" .env
            echo "Mistral API configured"
            ;;
        3)
            echo "Skipping LLM setup. The app will use keyword-based fallback."
            ;;
        *)
            echo "Invalid option selected"
            exit 1
            ;;
    esac
    
    echo ""
    echo "Running data consolidation..."
    python3 src/data_consolidation.py
    
    echo ""
    echo "Setup Complete!"
    echo ""
    echo "To start FloatChat:"
    echo "  streamlit run src/app.py"
    echo ""
    echo "The application will be available at http://localhost:8501"
    
    if [[ $REPLY == "1" ]]; then
        echo ""
        echo "Note: Ollama is running in the background (PID: $OLLAMA_PID)"
        echo "To stop Ollama later: kill $OLLAMA_PID"
    fi
}

# Run main function
main "$@"

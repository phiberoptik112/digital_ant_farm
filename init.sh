#!/bin/bash

# Digital Ant Farm - Initialization Script
# This script sets up the virtual environment and runs the simulation

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🐜 Digital Ant Farm - Initialization Script${NC}"
echo "================================================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed or not in PATH${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python 3 found: $(python3 --version)${NC}"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ] || [ ! -f "src/main.py" ]; then
    echo -e "${RED}❌ Please run this script from the project root directory${NC}"
    echo "Expected files: requirements.txt, src/main.py"
    exit 1
fi

# Virtual environment setup
VENV_DIR=".venv"

if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo -e "${YELLOW}⬆️  Upgrading pip...${NC}"
pip install --upgrade pip

# Install dependencies
echo -e "${YELLOW}📚 Installing dependencies...${NC}"
pip install -r requirements.txt

echo -e "${GREEN}✅ All dependencies installed${NC}"

# Check if pygame can be imported (basic test)
echo -e "${YELLOW}🧪 Testing pygame installation...${NC}"
python3 -c "import pygame; print(f'Pygame version: {pygame.version.ver}')" 2>/dev/null || {
    echo -e "${RED}❌ Pygame test failed${NC}"
    exit 1
}

echo -e "${GREEN}✅ Pygame test passed${NC}"

# Run the simulation
echo -e "${BLUE}🚀 Starting Digital Ant Farm simulation...${NC}"
echo "================================================"
echo -e "${YELLOW}Controls:${NC}"
echo "  - ESC: Exit simulation"
echo "  - SPACE: Pause/Resume"
echo "  - R: Reset simulation"
echo "  - Q: Queen controls (if available)"
echo "  - F: Food system controls (if available)"
echo "================================================"

# Change to src directory and run main.py
cd src
python3 main.py

echo -e "${GREEN}🎉 Simulation ended. Thank you for playing!${NC}"

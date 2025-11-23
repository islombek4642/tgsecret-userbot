#!/bin/bash
# Start Python Userbot

echo "🤖 Starting TgSecret Userbot..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "userbot" ]; then
    echo -e "${RED}Error: userbot directory not found!${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

cd userbot

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | grep -Po '(?<=Python )\d+\.\d+')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo -e "${RED}Error: Python 3.11+ is required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo -e "${GREEN}Installing Python dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: userbot/.env file not found!${NC}"
    echo "Please create userbot/.env file with required configuration"
    echo "See README.md for details"
    exit 1
fi

# Check if backend is running
if ! curl -s http://localhost:3001/health > /dev/null 2>&1; then
    echo -e "${YELLOW}Warning: Backend API is not responding on port 3001${NC}"
    echo "Make sure the backend is running: ./scripts/start-backend.sh"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${GREEN}✅ All checks passed!${NC}"
echo -e "${GREEN}Starting userbot...${NC}"
echo ""

# Start the userbot
python -m src.main

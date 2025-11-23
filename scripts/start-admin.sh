#!/bin/bash
# Start Admin Panel

echo "🎨 Starting TgSecret Admin Panel..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "admin" ]; then
    echo -e "${RED}Error: admin directory not found!${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

cd admin

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing admin panel dependencies...${NC}"
    npm install
fi

# Check if .env.local file exists
if [ ! -f ".env.local" ]; then
    echo -e "${RED}Error: admin/.env.local file not found!${NC}"
    echo "Please create admin/.env.local file with required configuration"
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
echo -e "${GREEN}Starting admin panel on port 3000...${NC}"
echo ""
echo "Admin panel will be available at:"
echo "👉 http://localhost:3000"
echo ""

# Start the admin panel
npm run dev

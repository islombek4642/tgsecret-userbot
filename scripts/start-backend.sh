#!/bin/bash
# Start Backend API Server

echo "🚀 Starting TgSecret Backend API..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo -e "${RED}Error: backend directory not found!${NC}"
    echo "Please run this script from the project root directory"
    exit 1
fi

cd backend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing backend dependencies...${NC}"
    npm install
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}Error: backend/.env file not found!${NC}"
    echo "Please create backend/.env file with required configuration"
    echo "See README.md for details"
    exit 1
fi

# Generate Prisma client
echo -e "${GREEN}Generating Prisma client...${NC}"
npx prisma generate

# Run database migrations
echo -e "${GREEN}Running database migrations...${NC}"
npx prisma migrate deploy

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo -e "${RED}Error: PostgreSQL is not running!${NC}"
    echo "Please start PostgreSQL first: sudo systemctl start postgresql"
    exit 1
fi

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo -e "${RED}Error: Redis is not running!${NC}"
    echo "Please start Redis first: sudo systemctl start redis-server"
    exit 1
fi

echo -e "${GREEN}✅ All checks passed!${NC}"
echo -e "${GREEN}Starting backend server on port 3001...${NC}"
echo ""

# Start the backend
npm run dev

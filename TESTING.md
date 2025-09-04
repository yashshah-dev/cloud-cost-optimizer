# Phase 1 Testing - Cloud Cost Optimizer

This document outlines the basic test suite for Phase 1 components.

## Backend Tests

### Database Tests
```python
# Test database connection and models
pytest backend/tests/test_database.py -v

# Test model relationships
pytest backend/tests/test_models.py -v
```

### API Tests
```python
# Test health endpoint
curl http://localhost:8000/health

# Test cost summary endpoint (with mock data)
curl -X POST http://localhost:8000/api/v1/costs/summary \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer mock-token" \
  -d '{
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  }'

# Test optimizations endpoint
curl -X POST http://localhost:8000/api/v1/optimizations \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer mock-token" \
  -d '{
    "min_savings": 100
  }'
```

### Cloud Provider Tests
```python
# Test AWS client (requires valid credentials)
pytest backend/tests/test_aws_client.py -v

# Test provider abstraction
pytest backend/tests/test_providers.py -v
```

### AI Agent Tests
```python
# Test agent initialization
pytest backend/tests/test_agents.py -v

# Test agent tools
pytest backend/tests/test_agent_tools.py -v
```

## Frontend Tests

### Component Tests
```bash
# Install dependencies
cd frontend && npm install

# Run component tests
npm test

# Test build process
npm run build
```

### Integration Tests
```bash
# Test API integration
npm run test:integration
```

## Docker Tests

### Container Build Tests
```bash
# Test backend container build
docker build -t cost-optimizer-backend ./backend

# Test frontend container build  
docker build -t cost-optimizer-frontend ./frontend

# Test full stack with Docker Compose
docker-compose up --build
```

### Health Check Tests
```bash
# Wait for containers to start, then test endpoints
sleep 30

# Test backend health
curl http://localhost:8000/health

# Test frontend accessibility
curl http://localhost:3000

# Test database connection
docker exec cost-optimizer-backend python -c "
from app.database import engine
import asyncio
async def test(): 
    async with engine.begin() as conn:
        result = await conn.execute('SELECT 1')
        print('Database OK')
asyncio.run(test())
"
```

## Manual Testing Checklist

### Phase 1 Core Features
- [ ] Application starts successfully with Docker Compose
- [ ] Database initializes with proper schema
- [ ] Health endpoint returns 200 status
- [ ] Frontend loads without errors
- [ ] Navigation between dashboard sections works
- [ ] Mock data displays correctly in charts
- [ ] API endpoints return proper error handling
- [ ] Agent scaffold responds to basic queries

### Error Scenarios
- [ ] Database connection failure handling
- [ ] Invalid API requests return proper errors
- [ ] Missing environment variables handled gracefully
- [ ] Frontend handles API unavailability

### Performance
- [ ] Dashboard loads within 3 seconds
- [ ] API responses return within 1 second
- [ ] No memory leaks in long-running containers
- [ ] Database queries use proper indexes

## Expected Test Results

### Success Criteria
- All containers start without errors
- Health endpoint returns healthy status
- Frontend displays dashboard with mock data
- API endpoints return expected response formats
- Database schema matches model definitions

### Known Limitations (Phase 1)
- No real cloud provider data integration
- Authentication uses mock tokens
- AI agent provides placeholder responses
- Limited error handling and validation
- No real-time data updates

## Next Phase Preparation

### Phase 2 Test Requirements
- Real cloud provider API integration tests
- Authentication and authorization tests
- LLM integration tests for AI agent
- Performance tests with real data volumes
- Security vulnerability tests

### Test Data Setup
- Create test AWS/GCP/Azure accounts
- Generate test cost data
- Set up test user accounts
- Configure test cloud resources

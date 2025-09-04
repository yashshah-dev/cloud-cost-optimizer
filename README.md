# Cloud Cost Optimizer - Phase 1 Foundation

## Overview

Phase 1 of the Cloud Cost Optimizer provides the foundational infrastructure for a comprehensive multi-cloud cost optimization platform. This implementation includes:

- **Data Ingestion & Persistence**: Complete database schema with TimescaleDB for time-series cost data
- **Multi-Cloud Provider Abstraction**: Unified interface supporting AWS, GCP, and Azure
- **RESTful API**: FastAPI-based backend with comprehensive endpoints
- **AI Agent Scaffold**: Extensible framework for intelligent cost optimization recommendations
- **Frontend Dashboard**: React-based UI with interactive charts and visualizations
- **Docker Environment**: Complete containerization for development and deployment

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- Cloud provider credentials (optional for Phase 1)

### 1. Clone and Setup
```bash
git clone <repository>
cd cloud-cost-optimizer

# Copy environment template
cp .env.example .env
# Edit .env with your configuration
```

### 2. Start with Docker
```bash
# Start all services
docker-compose up --build

# Or start in background
docker-compose up -d --build
```

### 3. Access the Application
- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/api/docs
- **Database**: localhost:5432 (postgres/postgres)

### 4. Verify Installation
```bash
# Check health endpoint
curl http://localhost:8000/health

# View dashboard
open http://localhost:3000
```

## 📁 Project Structure

```
cloud-cost-optimizer/
├── backend/                    # FastAPI backend application
│   ├── app/
│   │   ├── models.py          # SQLAlchemy database models
│   │   ├── schemas.py         # Pydantic API schemas
│   │   ├── database.py        # Database configuration
│   │   ├── main.py           # FastAPI application
│   │   ├── providers/        # Cloud provider clients
│   │   │   ├── base.py       # Provider abstraction
│   │   │   └── aws_client.py # AWS implementation
│   │   └── agents/           # AI agent framework
│   │       ├── base.py       # Agent base classes
│   │       └── cost_optimizer.py # Cost optimization agent
│   ├── requirements.txt      # Python dependencies
│   └── Dockerfile           # Backend container
├── frontend/                  # React frontend application
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── Layout.tsx    # Main layout
│   │   │   └── Dashboard.tsx # Dashboard component
│   │   ├── App.tsx          # Main app component
│   │   └── main.tsx         # Entry point
│   ├── package.json         # Node.js dependencies
│   └── Dockerfile          # Frontend container
├── infrastructure/           # Infrastructure setup
│   └── init.sql             # Database initialization
├── docker-compose.yml       # Docker Compose configuration
├── .env.example            # Environment variables template
├── TESTING.md              # Testing documentation
└── README.md               # This file
```

## 🔧 Architecture

### Database Layer
- **PostgreSQL** with **TimescaleDB** extension for time-series data
- Comprehensive schema for cloud resources, costs, and optimizations
- Materialized views for dashboard performance
- Proper indexing for query optimization

### Backend API
- **FastAPI** with async/await for high performance
- RESTful endpoints for cost analysis and resource management
- Pydantic schemas for request/response validation
- Multi-cloud provider abstraction layer
- AI agent framework for intelligent recommendations

### Frontend Dashboard
- **React 18** with TypeScript for type safety
- **Recharts** for interactive data visualizations
- **Tailwind CSS** for responsive design
- **React Query** for efficient data fetching
- Real-time cost monitoring and optimization insights

### Cloud Providers
- **AWS**: Cost Explorer, EC2, CloudWatch integration
- **GCP**: Billing API, Compute Engine (planned for Phase 2)
- **Azure**: Cost Management, Resource Manager (planned for Phase 2)

## 📊 Features Implemented

### ✅ Phase 1 Complete
- [x] Database schema with TimescaleDB
- [x] AWS cloud provider client
- [x] Cost summary and resource usage APIs
- [x] AI agent framework with tools
- [x] React dashboard with charts
- [x] Docker containerization
- [x] Health monitoring endpoints

### 🔄 Current Limitations
- Mock data for frontend visualization
- Placeholder authentication
- Basic AI agent responses
- AWS-only provider implementation

## 🔗 API Endpoints

### Health & Status
- `GET /health` - Application health check

### Cost Analysis
- `POST /api/v1/costs/summary` - Get cost summary for date range
- `POST /api/v1/resources/usage` - Get resource usage metrics

### Optimizations
- `POST /api/v1/optimizations` - Get optimization recommendations
- `GET /api/v1/resources` - List cloud resources

### AI Agent
- `POST /api/v1/agent/query` - Query AI agent for insights

## 🧪 Testing

### Run Backend Tests
```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v
```

### Run Frontend Tests
```bash
cd frontend
npm install
npm test
```

### Integration Testing
```bash
# Start services
docker-compose up -d

# Run integration tests
./scripts/test-integration.sh
```

See [TESTING.md](TESTING.md) for comprehensive testing guidelines.

## ⚙️ Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/cost_optimizer

# Cloud Providers
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret

# AI Features
OPENAI_API_KEY=your_openai_key

# Security
SECRET_KEY=your_secret_key
```

### Development Setup

For local development without Docker:

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

## 📈 Phase 2 Roadmap

### Planned Features
- [ ] Real cloud provider data integration
- [ ] Advanced LLM-powered AI agent
- [ ] User authentication and authorization  
- [ ] Real-time cost alerts and notifications
- [ ] Advanced optimization algorithms
- [ ] Multi-tenant support
- [ ] Enhanced security and compliance

### Technical Improvements
- [ ] Comprehensive test coverage
- [ ] Performance optimization
- [ ] Production deployment configuration
- [ ] Monitoring and observability
- [ ] API rate limiting and caching

## 🛠️ Development

### Adding New Cloud Providers
1. Create provider client in `backend/app/providers/`
2. Implement `CloudProviderClient` abstract base class
3. Add provider configuration to `database.py`
4. Update API endpoints to support new provider

### Extending AI Agent
1. Create new tools in `agents/cost_optimizer.py`
2. Implement tool execution logic
3. Add to agent tool registry
4. Update API response schemas

### Adding Dashboard Components
1. Create React component in `frontend/src/components/`
2. Add routing in `App.tsx`
3. Integrate with API using React Query
4. Style with Tailwind CSS

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For questions and support:
- Open an issue on GitHub
- Check the documentation in `/docs/`
- Review the testing guide in `TESTING.md`

---

**Note**: This is Phase 1 of the implementation. Phase 2 will include full cloud provider integration, advanced AI capabilities, and production-ready features.

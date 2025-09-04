# Cloud Cost Optimizer

AI-powered multi-cloud cost optimization and safe automation platform.

## 1. Repository Overview
Primary documentation:
- High‑level & detailed architecture: [architecture-diagram.md](architecture-diagram.md), enhanced Mermaid views: [architecture-diagram-enhanced.md](architecture-diagram-enhanced.md)
- Functional & non-functional requirements, user stories, deliverables: [cloud-ops-requirements.md](cloud-ops-requirements.md)
- End‑to‑end phased implementation blueprint: [implementation-plan.md](implementation-plan.md)
- Agentic AI tutorial & conceptual onboarding: [tutorial.md](tutorial.md)

## 2. Vision & Outcomes
Deliver measurable 20–35% cloud spend reduction through:
- Unified multi-cloud visibility
- AI pattern + anomaly detection
- Risk-aware optimization recommendations
- Safe, approval‑gated automated execution
- Enterprise-grade security, auditability, and observability

## 3. Tech Pillars
- Backend: FastAPI, async I/O, Celery workers, Redis queue/cache
- Data: PostgreSQL (transactional + JSONB), TimescaleDB (time series), Vector DB (embeddings), structured cost & optimization schema (see [implementation-plan.md](implementation-plan.md))
- AI/ML: Usage pattern ML models, risk assessment, LangChain agent tools
- Frontend: React + TypeScript dashboard (cost, optimization queue, approvals)
- Security: JWT auth, rate limiting, RBAC (future), encryption in transit, audit trail
- Observability: Prometheus, Grafana, structured JSON logs, tracing
- Deployment: Docker, Nginx reverse proxy, staged environments

## 4. High-Level Architecture
Refer to:
- Core layered & data flow diagrams: [architecture-diagram.md](architecture-diagram.md)
- Enhanced sequence, data, security & deployment flows: [architecture-diagram-enhanced.md](architecture-diagram-enhanced.md)

## 5. Development Phases (Execution Roadmap)
(Full technical depth in [implementation-plan.md](implementation-plan.md). This README gives an actionable tracker.)

### Phase 0: Preparation (Day 0)
Objectives:
- Confirm scope vs. [cloud-ops-requirements.md](cloud-ops-requirements.md)
- Finalize backlog & label (foundation / intelligence / automation / production / enhancement)
Tasks:
- Create issue templates (feature, task, bug)
- Establish branch strategy (see Section 8)
- Define CI quality gates (lint, type, tests)
Exit Criteria:
- Backlog groomed & prioritized
- CI pipeline skeleton green
KPIs:
- 0 critical unknowns; baseline velocity established

### Phase 1: Foundation (Weeks 1–2)
Objectives:
- Data ingestion + persistence + basic API + minimal dashboard + AI agent scaffold
Key Deliverables:
- Cloud provider abstraction layer (single provider fully functional; stubs for others)
- Core DB schema (cost_entries, cloud_resources, optimization_recommendations) — see schema in [implementation-plan.md](implementation-plan.md)
- FastAPI endpoints: cost summary, resource usage, recommendation request
- LangChain agent scaffold + tool interfaces placeholders
- Basic React dashboard: cost overview + top resources
- Docker Compose (dev) + .env.example
Tasks (Sequenced):
1. Data models & migrations
2. Provider client + retry/backoff + unified DTOs
3. API routes + Pydantic models + OpenAPI auto-doc
4. Seed sample data + test harness
5. Minimal dashboard charts
6. Agent skeleton (memory + tool registry)
Exit Criteria:
- End-to-end: ingest → DB → API → dashboard visualization
KPIs:
- <250ms median cost summary API (seed dataset)
- 80%+ model / schema unit test coverage

### Phase 2: Intelligence (Weeks 3–4)
Objectives:
- ML usage pattern analysis, risk assessment, recommendation engine, performance impact estimation
Deliverables:
- UsagePatternAnalyzer + feature engineering + time series CV
- RiskAssessor (resource, business impact, rollback complexity signals)
- OptimizationRecommender (rightsizing, reserved, spot; prioritization)
- Performance impact prediction stub (confidence scoring)
- Enhanced agent tool calls mapped to new services
Tasks:
1. Define ML feature set & validation strategy
2. Implement usage pattern pipeline + tests
3. Implement risk scoring + calibration dataset
4. Build recommendation orchestration
5. Expose recommendations API & enrich response metadata
6. Frontend: optimization queue table + filters
Exit Criteria:
- Recommendations generated from synthetic multi-week dataset
- Risk levels + potential savings surfaced in UI
KPIs:
- Top-5 recommendations accuracy (manual validation) ≥ 70% perceived relevance
- Latency: recommendation generation < 3s (sample dataset)

### Phase 3: Automation (Weeks 5–6)
Objectives:
- Safe execution path with rollback, approvals, performance monitoring, notifications
Deliverables:
- Safe optimization executor (pre/post validation hooks, rollback)
- ApprovalWorkflow (multi-level rules, escalation logic)
- PerformanceMonitor (baseline compare + deviation detection)
- NotificationService (email, Slack, SMS stubs, webhook)
- Audit logging for all execution events
Tasks:
1. Execution plan domain model + validation gates
2. Implement pre/post checks + rollback strategy
3. Approval workflow + persistence + escalation timers
4. Monitoring loop + thresholds + alert triggers
5. Multi-channel notification dispatch + templates
6. Frontend: approvals & execution status panels
Exit Criteria:
- Simulated optimization flows: recommend → approve → execute → validate → log
KPIs:
- Rollback success rate in failure simulations: 100%
- Notification dispatch latency < 5s
- Zero orphaned approval states in tests

### Phase 4: Production Readiness (Weeks 7–8)
Objectives:
- Deployment architecture, security hardening, comprehensive testing, observability, documentation
Deliverables:
- Hardened Docker images + Nginx reverse proxy config
- JWT auth + rate limiting + security headers
- Test suite: unit, integration, e2e (synthetic multi-cloud)
- Prometheus metrics + structured JSON logging + tracing instrumentation
- Documentation set (user, admin, API) referencing [implementation-plan.md](implementation-plan.md) & [tutorial.md](tutorial.md)
Tasks:
1. SecurityManager & middleware integration
2. Rate limiting + input validation enforcement
3. MonitoringSystem + metrics export endpoint
4. CI: coverage badge, performance test stage
5. Staging deployment smoke tests
6. Documentation & onboarding checklist
Exit Criteria:
- Staging environment stable under load profile
- All critical paths ≥ 90% test coverage
KPIs:
- p95 API latency < 500ms (staging dataset)
- Error rate < 1% during load test
- Mean time to detect (MTTD) simulated issue < 2m (alert pipeline)

### Phase 5: Advanced Enhancements (Post-MVP)
Options (prioritize via impact vs. effort):
- RBAC + organization/workspace model
- Policy-driven optimization guardrails
- FinOps reporting packs (budget variance, amortization, tagging compliance)
- Predictive capacity planning (extended time series modeling)
- Plugin framework for new cloud providers/tools
- Chargeback/showback dashboards
- Drift detection & automated remediation
- Cost anomaly real-time streaming detection

## 6. Issue & Tracking Framework
Label taxonomy (examples):
- scope:foundation / intelligence / automation / production / enhancement
- type:feature / bug / refactor / docs / ops
- risk:low|medium|high
- priority:P0–P3

Definition of Done (baseline):
- Code + tests pass locally & CI
- API/DTO changes documented
- Observability: logs & metrics added if long-lived process or async task
- Security review for new external calls

## 7. Quality Gates
Pipeline (sequential):
1. Static: lint (ruff/flake8), mypy, eslint, style
2. Unit tests (fast)
3. Integration tests (DB + mock cloud APIs)
4. Security scan (deps + container)
5. Migration dry run
6. Coverage threshold enforcement (≥85%)

## 8. Branching & Release
- main: stable, production-ready
- develop (optional if team grows)
- feature/* short-lived branches
- release/* tagged pre-production
- hotfix/* directly from main
Commit style: Conventional Commits (feat:, fix:, perf:, docs:, chore:, refactor:, test:, build:)

## 9. Environments
- Local: docker compose minimal (API + DB + Redis)
- Staging: full stack + synthetic data seeding + load tests
- Production: HA topology (read replicas, Redis cluster, horizontal API scaling)

## 10. Observability Baseline
Metrics (initial set):
- API: request_count, latency histogram, error_rate
- Worker: task_duration, task_failures, queue_depth
- Optimization: recommendations_generated, executions_success, rollback_count, savings_captured
Logging:
- Structured JSON, correlation IDs
Tracing:
- Request → DB → task execution spans (later phases)

## 11. Security & Compliance Foundations
Phase gating:
- Phase 1: Basic JWT + secrets management
- Phase 2: Input validation coverage + audit logs for rec generation
- Phase 3: Execution + approval audit immutability
- Phase 4: Hardened headers, TLS, rate limiting, dependency scanning
- Phase 5+: RBAC, least privilege cloud roles, anomaly-based auth monitoring

## 12. KPIs & Value Tracking
Business Metrics:
- Projected vs. realized savings
- Optimization adoption rate (% executed vs. recommended)
- Approval turnaround time
Technical Metrics:
- Recommendation accuracy (manual validation scorecard)
- Mean execution rollback latency
- System availability (SLO baseline 99.5%)

## 13. Onboarding Path
1. Read [cloud-ops-requirements.md](cloud-ops-requirements.md) (context & user value)
2. Study architecture: [architecture-diagram.md](architecture-diagram.md) then enhanced flows: [architecture-diagram-enhanced.md](architecture-diagram-enhanced.md)
3. Review phased depth: [implementation-plan.md](implementation-plan.md)
4. Learn agent concepts: [tutorial.md](tutorial.md)
5. Pull issues scoped to current phase

## 14. Risk Register (Initial)
| Risk | Mitigation |
|------|------------|
| Cloud API rate limits | Cached layers + exponential backoff |
| Model drift (usage patterns) | Scheduled retraining + validation metrics |
| Over-aggressive optimizations | RiskAssessor + approval workflow |
| Data volume growth | Partitioned tables + Timescale hypertables |
| Security regression | CI dependency scanning + OWASP headers tests |

## 15. Next Immediate Actions (Sprint 1 Seed)
- Initialize repo scaffolding
- Implement DB migrations & seed script
- Implement single provider client (e.g., AWS) + basic cost ingestion job
- Expose /api/v1/costs/summary
- Basic dashboard cost chart
- Add initial test suite + CI workflow

## 16. Contribution Workflow (Summary)
1. Open issue (linked to phase)
2. Branch: feature/<issue-id>-short-desc
3. Implement + tests + docs snippet
4. Open PR (template includes: scope, test evidence, risk)
5. Peer review (lint + coverage checks enforced)
6. Merge squash → main
7. Automated changelog update (planned Phase 4)

---

For detailed class, function, and code-level implementation refer to: [implementation-plan.md](implementation-plan.md).
// Configuration file for API endpoints
const getApiBaseUrl = (): string => {
  // Check if we're running in a browser (localhost) or in Docker
  const isLocalhost = typeof window !== 'undefined' && 
                     (window.location.hostname === 'localhost' || 
                      window.location.hostname === '127.0.0.1')
  
  // Use localhost when running in browser, backend service when in Docker
  return isLocalhost ? 'http://localhost:8000' : 'http://backend:8000'
}

export const API_BASE_URL = getApiBaseUrl()
export const API_ENDPOINTS = {
  COSTS_SUMMARY: `${API_BASE_URL}/api/v1/costs/summary`,
  OPTIMIZATIONS: `${API_BASE_URL}/api/v1/optimizations`,
  AI_AGENT_STATUS: `${API_BASE_URL}/api/v1/agent/status`,
  AI_EXPLAIN_OPTIMIZATION: `${API_BASE_URL}/api/v1/agent/explain-optimization`,
  AI_ANALYZE_TRENDS: `${API_BASE_URL}/api/v1/agent/analyze-cost-trends`,
  // New endpoints for additional components
  RESOURCES: `${API_BASE_URL}/api/v1/resources`,
  COST_REPORT: `${API_BASE_URL}/api/v1/costs/report`,
  OPTIMIZATION_REPORT: `${API_BASE_URL}/api/v1/optimizations/report`,
  RESOURCE_STATS: `${API_BASE_URL}/api/v1/resources/stats`,
  OPTIMIZATION_STATS: `${API_BASE_URL}/api/v1/optimizations/stats`,
  ML_RUN_PIPELINE: `${API_BASE_URL}/api/v1/ml/run-pipeline`,
} as const

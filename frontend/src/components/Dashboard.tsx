import React, { useState, useEffect } from 'react'
import { useQuery } from 'react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'
import { DollarSign, TrendingUp, TrendingDown, Server, AlertTriangle, Zap, Filter, CheckCircle, XCircle, Clock, Search, Bot, Brain, MessageSquare, Calendar, RefreshCw } from 'lucide-react'
import { format, subDays, startOfMonth, endOfMonth, subMonths, startOfWeek, endOfWeek } from 'date-fns'
import { API_ENDPOINTS } from '../config'

// Types
interface CostSummary {
  total_cost: number
  cost_by_provider: Record<string, number>
  cost_by_service: Record<string, number>
  daily_costs: Array<{ date: string; cost: number }>
}

interface OptimizationRecommendation {
  id: string
  resource_id?: string // Add resource_id for AI explanations
  type: string
  title: string
  description: string
  potential_savings: number
  risk_level: string
  confidence_score: number
  priority_rank?: number
  priority_level?: string
  implementation_complexity?: string
  estimated_effort_hours?: number
  requires_downtime?: boolean
  created_at?: string
}

interface AIAgentStatus {
  llm_available: boolean
  llm_model: {
    model_name: string
    provider: string
    available: boolean
    cost_efficient: boolean
  }
  available_tools: string[]
  cost_metrics: {
    total_requests: number
    total_tokens: number
    avg_response_time: number
    cost_savings: number
  }
  last_checked: string
}

interface AIExplanation {
  explanation: string
  generated_at: string
  model_used: string
  confidence: string
}

interface DateRange {
  startDate: Date
  endDate: Date
  label: string
}

// Predefined date range options
const DATE_RANGE_OPTIONS: DateRange[] = [
  {
    startDate: subDays(new Date(), 7),
    endDate: new Date(),
    label: 'Last 7 days'
  },
  {
    startDate: subDays(new Date(), 14),
    endDate: new Date(),
    label: 'Last 2 weeks'
  },
  {
    startDate: subDays(new Date(), 30),
    endDate: new Date(),
    label: 'Last 30 days'
  },
  {
    startDate: subDays(new Date(), 90),
    endDate: new Date(),
    label: 'Last 3 months'
  },
  {
    startDate: startOfMonth(new Date()),
    endDate: new Date(),
    label: 'Month to date'
  },
  {
    startDate: startOfMonth(subMonths(new Date(), 1)),
    endDate: endOfMonth(subMonths(new Date(), 1)),
    label: 'Last month'
  },
  {
    startDate: startOfMonth(subMonths(new Date(), 2)),
    endDate: endOfMonth(subMonths(new Date(), 2)),
    label: '2 months ago'
  }
]

// Modified API functions to accept date range parameters
const fetchCostSummary = async (dateRange?: DateRange): Promise<CostSummary> => {
  try {
    // Use provided date range or default to last 30 days
    const endDate = dateRange?.endDate || new Date()
    const startDate = dateRange?.startDate || subDays(endDate, 30)
    
    const response = await fetch(API_ENDPOINTS.COSTS_SUMMARY, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        start_date: format(startDate, 'yyyy-MM-dd'),
        end_date: format(endDate, 'yyyy-MM-dd')
      })
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch cost summary')
    }
    
    const data = await response.json()
    
    // Transform backend response to match frontend interface
    return {
      total_cost: data.total_cost,
      cost_by_provider: data.cost_by_provider,
      cost_by_service: data.cost_by_service,
      daily_costs: data.daily_costs.map((item: any) => ({
        date: item.date,
        cost: item.cost
      }))
    }
  } catch (error) {
    console.error('Error fetching cost summary:', error)
    throw error // Don't fallback to mock data
  }
}

const fetchOptimizations = async (): Promise<OptimizationRecommendation[]> => {
  try {
    const response = await fetch(API_ENDPOINTS.OPTIMIZATIONS, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        min_savings: 100.0
      })
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch optimizations')
    }
    
    const data = await response.json()
    
    // Transform backend response to match frontend interface
    const transformed = data.recommendations.map((rec: any) => ({
      id: rec.id,
      resource_id: rec.resource_id, // Add resource_id for AI explanations
      type: rec.type,
      title: rec.title,
      description: rec.description,
      potential_savings: rec.potential_savings,
      risk_level: rec.risk_level,
      confidence_score: rec.confidence_score
    }))
    
    console.log('=== Backend Response Transformation ===')
    console.log('Raw backend data:', data.recommendations[0])
    console.log('Transformed data:', transformed[0])
    
    return transformed
  } catch (error) {
    console.error('Error fetching optimizations:', error)
    throw error // Don't fallback to mock data
  }
}

// AI Agent API functions
const fetchAIAgentStatus = async (): Promise<AIAgentStatus> => {
  try {
    const response = await fetch(API_ENDPOINTS.AI_AGENT_STATUS)
    
    if (!response.ok) {
      throw new Error('Failed to fetch AI agent status')
    }
    
    return await response.json()
  } catch (error) {
    console.error('Error fetching AI agent status:', error)
    throw error // Don't fallback to mock data
  }
}

const fetchAIExplanation = async (optimizationId: string, resourceId: string): Promise<AIExplanation> => {
  console.log('=== fetchAIExplanation Called ===')
  console.log('optimizationId:', optimizationId)
  console.log('resourceId:', resourceId)
  
  try {
    // Use dynamic API endpoint based on environment
    const apiUrl = API_ENDPOINTS.AI_EXPLAIN_OPTIMIZATION
    
    console.log('API URL:', apiUrl)
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        optimization_id: optimizationId,
        resource_id: resourceId
      })
    })
    
    console.log('API Response status:', response.status)
    
    if (!response.ok) {
      throw new Error('Failed to get AI explanation')
    }
    
    return await response.json()
  } catch (error) {
    console.error('Error fetching AI explanation:', error)
    throw error // Don't fallback to mock data
  }
}

const fetchAITrendAnalysis = async (): Promise<any[]> => {
  try {
    // Use dynamic API endpoint based on environment
    const apiUrl = API_ENDPOINTS.AI_ANALYZE_TRENDS
    
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        days: 30
      })
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch AI trend analysis')
    }
    
    const data = await response.json()
    return data.predictions || []
  } catch (error) {
    console.error('Error fetching AI trend analysis:', error)
    throw error // Don't fallback to mock data
  }
}

// ML Pipeline API function
const runMLPipeline = async (): Promise<any> => {
  try {
    const response = await fetch(API_ENDPOINTS.ML_RUN_PIPELINE, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    
    if (!response.ok) {
      throw new Error('Failed to run ML pipeline')
    }
    
    return await response.json()
  } catch (error) {
    console.error('Error running ML pipeline:', error)
    throw error
  }
}

// Components
const DateRangeSelector: React.FC<{
  selectedRange: DateRange
  onRangeChange: (range: DateRange) => void
  customStartDate?: Date
  customEndDate?: Date
  onCustomDateChange?: (startDate: Date, endDate: Date) => void
}> = ({ selectedRange, onRangeChange, customStartDate, customEndDate, onCustomDateChange }) => {
  const [showCustom, setShowCustom] = useState(false)
  const [tempStartDate, setTempStartDate] = useState(customStartDate || new Date())
  const [tempEndDate, setTempEndDate] = useState(customEndDate || new Date())

  const handleCustomApply = () => {
    if (onCustomDateChange) {
      onCustomDateChange(tempStartDate, tempEndDate)
      onRangeChange({
        startDate: tempStartDate,
        endDate: tempEndDate,
        label: 'Custom range'
      })
    }
    setShowCustom(false)
  }

  return (
    <div className="flex items-center space-x-4">
      <div className="flex items-center space-x-2">
        <Calendar className="h-4 w-4 text-gray-500" />
        <span className="text-sm font-medium text-gray-700">Date Range:</span>
      </div>
      
      <select
        value={selectedRange.label}
        onChange={(e) => {
          const selected = DATE_RANGE_OPTIONS.find(option => option.label === e.target.value)
          if (selected) {
            onRangeChange(selected)
            setShowCustom(false)
          } else if (e.target.value === 'Custom range') {
            setShowCustom(true)
          }
        }}
        className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm"
      >
        {DATE_RANGE_OPTIONS.map(option => (
          <option key={option.label} value={option.label}>{option.label}</option>
        ))}
        <option value="Custom range">Custom range</option>
      </select>

      {showCustom && (
        <div className="flex items-center space-x-2 p-3 bg-gray-50 border border-gray-200 rounded-md">
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">From:</label>
            <input
              type="date"
              value={format(tempStartDate, 'yyyy-MM-dd')}
              onChange={(e) => setTempStartDate(new Date(e.target.value))}
              className="rounded border-gray-300 text-sm"
            />
          </div>
          <div className="flex items-center space-x-2">
            <label className="text-sm font-medium text-gray-700">To:</label>
            <input
              type="date"
              value={format(tempEndDate, 'yyyy-MM-dd')}
              onChange={(e) => setTempEndDate(new Date(e.target.value))}
              className="rounded border-gray-300 text-sm"
            />
          </div>
          <button
            onClick={handleCustomApply}
            className="px-3 py-1 bg-indigo-600 text-white text-sm rounded hover:bg-indigo-700"
          >
            Apply
          </button>
          <button
            onClick={() => setShowCustom(false)}
            className="px-3 py-1 bg-gray-300 text-gray-700 text-sm rounded hover:bg-gray-400"
          >
            Cancel
          </button>
        </div>
      )}
      
      <div className="text-sm text-gray-500">
        {format(selectedRange.startDate, 'MMM dd')} - {format(selectedRange.endDate, 'MMM dd, yyyy')}
      </div>
    </div>
  )
}

const AIExplanationModal: React.FC<{
  isOpen: boolean
  onClose: () => void
  explanation: AIExplanation | null
  isLoading: boolean
  title: string
}> = ({ isOpen, onClose, explanation, isLoading, title }) => {
  if (!isOpen) return null

  // Parse and render the structured explanation
  const renderExplanation = (text: string) => {
    const elements: JSX.Element[] = []
    
    // Check if text contains section headers
    if (!text.includes('**')) {
      // Fallback: treat as plain text with line breaks
      const paragraphs = text.split('\n').filter(p => p.trim())
      return (
        <div className="text-sm text-gray-700 leading-relaxed">
          {paragraphs.map((paragraph, idx) => (
            <p key={idx} className="mb-3 last:mb-0">
              {paragraph.trim()}
            </p>
          ))}
        </div>
      )
    }
    
    // Split by section headers (text between ** **)
    const sections = text.split(/\*\*([^*]+)\*\*/)
    let currentSection = ''
    
    for (let i = 0; i < sections.length; i++) {
      const section = sections[i].trim()
      
      if (i % 2 === 1) {
        // This is a section header
        currentSection = section
      } else if (section && currentSection) {
        // This is section content
        const contentLines = section.split('\n').filter(line => line.trim())
        const contentElements: JSX.Element[] = []
        
        contentLines.forEach((line, idx) => {
          const trimmedLine = line.trim()
          
          if (!trimmedLine) return
          
          // Handle bullet points
          if (trimmedLine.startsWith('•') || trimmedLine.startsWith('*') || trimmedLine.startsWith('-')) {
            const bulletContent = trimmedLine.substring(1).trim()
            contentElements.push(
              <div key={idx} className="flex items-start space-x-2 mb-2 ml-2">
                <span className="text-purple-500 mt-1 flex-shrink-0 text-sm">•</span>
                <span className="flex-1 leading-relaxed text-sm">{bulletContent}</span>
              </div>
            )
          } else if (trimmedLine.includes(':')) {
            // Handle sub-headers like "Positive impacts:" or "Negative impacts:"
            const colonIndex = trimmedLine.indexOf(':')
            const subHeader = trimmedLine.substring(0, colonIndex).trim()
            const subContent = trimmedLine.substring(colonIndex + 1).trim()
            
            contentElements.push(
              <div key={idx} className="mb-3">
                <span className="font-medium text-gray-800 text-sm">{subHeader}:</span>
                {subContent && (
                  <span className="ml-1 leading-relaxed text-sm">{subContent}</span>
                )}
              </div>
            )
          } else {
            // Regular paragraph
            contentElements.push(
              <p key={idx} className="leading-relaxed mb-3 last:mb-0 text-sm">
                {trimmedLine}
              </p>
            )
          }
        })
        
        elements.push(
          <div key={currentSection} className="mb-6 last:mb-0">
            <h4 className="text-base font-semibold text-gray-900 mb-3 border-b border-purple-200 pb-2 flex items-center">
              <span className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs font-medium mr-2">
                {currentSection}
              </span>
            </h4>
            <div className="text-sm text-gray-700 pl-1">
              {contentElements}
            </div>
          </div>
        )
      }
    }
    
    return elements
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <Brain className="h-6 w-6 text-purple-600" />
            <h3 className="text-lg font-medium text-gray-900">AI Explanation</h3>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <XCircle className="h-6 w-6" />
          </button>
        </div>

        <div className="mb-4">
          <h4 className="text-md font-medium text-gray-800">{title}</h4>
        </div>

        {isLoading ? (
          <div className="flex items-center justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600"></div>
            <span className="ml-2 text-gray-600">Generating AI explanation...</span>
          </div>
        ) : explanation ? (
          <div className="space-y-4">
            <div className="bg-purple-50 p-4 rounded-lg">
              <div className="flex items-center space-x-2 mb-2">
                <Bot className="h-4 w-4 text-purple-600" />
                <span className="text-sm font-medium text-purple-800">AI Analysis</span>
                <span className="text-xs text-purple-600 bg-purple-100 px-2 py-1 rounded">
                  {explanation.confidence} confidence
                </span>
              </div>
              <div className="prose prose-sm max-w-none text-gray-800">
                {renderExplanation(explanation.explanation)}
              </div>
            </div>

            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>Generated by {explanation.model_used}</span>
              <span>{format(new Date(explanation.generated_at), 'MMM dd, yyyy HH:mm')}</span>
            </div>
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            Unable to generate AI explanation at this time.
          </div>
        )}

        <div className="flex justify-end mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  )
}
// Components
const OptimizationCard: React.FC<{ 
  recommendation: OptimizationRecommendation
  onExplainWithAI?: (rec: OptimizationRecommendation) => void
}> = ({ recommendation, onExplainWithAI }) => {
  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'bg-green-100 text-green-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'critical': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'rightsizing': return <Server className="h-5 w-5" />
      case 'reserved_instance': return <DollarSign className="h-5 w-5" />
      case 'spot_instance': return <Zap className="h-5 w-5" />
      case 'storage_optimization': return <TrendingDown className="h-5 w-5" />
      default: return <AlertTriangle className="h-5 w-5" />
    }
  }

  return (
    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            {getTypeIcon(recommendation.type)}
          </div>
          <div className="flex-1">
            <h4 className="text-sm font-medium text-gray-900">{recommendation.title}</h4>
            <p className="text-sm text-gray-600 mt-1">{recommendation.description}</p>
            <div className="flex items-center space-x-4 mt-2">
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskColor(recommendation.risk_level)}`}>
                {recommendation.risk_level} risk
              </span>
              <span className="text-sm text-gray-500">
                {Math.round(recommendation.confidence_score * 100)}% confidence
              </span>
            </div>
            {onExplainWithAI && (
              <button
                onClick={() => onExplainWithAI(recommendation)}
                className="mt-3 inline-flex items-center px-3 py-1 border border-purple-300 rounded-md text-sm font-medium text-purple-700 bg-purple-50 hover:bg-purple-100 focus:outline-none focus:ring-2 focus:ring-purple-500"
              >
                <Brain className="h-4 w-4 mr-1" />
                Explain with AI
              </button>
            )}
          </div>
        </div>
        <div className="text-right">
          <div className="text-lg font-semibold text-green-600">
            ${recommendation.potential_savings.toFixed(0)}
          </div>
          <div className="text-sm text-gray-500">monthly savings</div>
        </div>
      </div>
    </div>
  )
}
const StatCard: React.FC<{
  title: string
  value: string
  change?: string
  changeType?: 'positive' | 'negative'
  icon: React.ComponentType<any>
}> = ({ title, value, change, changeType, icon: Icon }) => (
  <div className="bg-white overflow-hidden shadow rounded-lg">
    <div className="p-5">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <Icon className="h-6 w-6 text-gray-400" />
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
            <dd className="flex items-baseline">
              <div className="text-2xl font-semibold text-gray-900">{value}</div>
              {change && (
                <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                  changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                }`}>
                  {changeType === 'positive' ? (
                    <TrendingUp className="flex-shrink-0 self-center h-4 w-4" />
                  ) : (
                    <TrendingDown className="flex-shrink-0 self-center h-4 w-4" />
                  )}
                  <span className="ml-1">{change}</span>
                </div>
              )}
            </dd>
          </dl>
        </div>
      </div>
    </div>
  </div>
)

const OptimizationQueue: React.FC<{ 
  recommendations: OptimizationRecommendation[]
  onExplainWithAI?: (rec: OptimizationRecommendation) => void
}> = ({ recommendations, onExplainWithAI }) => {
  const [filters, setFilters] = useState({
    risk_level: '',
    type: '',
    priority_level: '',
    min_savings: '',
    search: ''
  })

  const [sortBy, setSortBy] = useState<'savings' | 'priority' | 'created'>('savings')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  // Filter and sort recommendations
  const filteredAndSortedRecommendations = React.useMemo(() => {
    let filtered = recommendations.filter(rec => {
      if (filters.risk_level && rec.risk_level !== filters.risk_level) return false
      if (filters.type && rec.type !== filters.type) return false
      if (filters.priority_level && rec.priority_level !== filters.priority_level) return false
      if (filters.min_savings && rec.potential_savings < parseFloat(filters.min_savings)) return false
      if (filters.search) {
        const searchTerm = filters.search.toLowerCase()
        const searchableText = `${rec.title} ${rec.description} ${rec.type}`.toLowerCase()
        if (!searchableText.includes(searchTerm)) return false
      }
      return true
    })

    // Sort
    filtered.sort((a, b) => {
      let aValue: any, bValue: any

      switch (sortBy) {
        case 'savings':
          aValue = a.potential_savings
          bValue = b.potential_savings
          break
        case 'priority':
          aValue = a.priority_rank || 999
          bValue = b.priority_rank || 999
          break
        case 'created':
          aValue = new Date(a.created_at || '2024-01-01').getTime()
          bValue = new Date(b.created_at || '2024-01-01').getTime()
          break
        default:
          return 0
      }

      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1
      } else {
        return aValue < bValue ? 1 : -1
      }
    })

    return filtered
  }, [recommendations, filters, sortBy, sortOrder])

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'bg-green-100 text-green-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'critical': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical': return 'bg-red-100 text-red-800'
      case 'high': return 'bg-orange-100 text-orange-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg leading-6 font-medium text-gray-900">
            Optimization Queue
          </h3>
          <span className="text-sm text-gray-500">
            {filteredAndSortedRecommendations.length} of {recommendations.length} recommendations
          </span>
        </div>

        {/* Filters */}
        <div className="mb-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
            <div className="relative">
              <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
              <input
                type="text"
                className="pl-10 w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                placeholder="Search recommendations..."
                value={filters.search}
                onChange={(e) => setFilters({...filters, search: e.target.value})}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Risk Level</label>
            <select
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              value={filters.risk_level}
              onChange={(e) => setFilters({...filters, risk_level: e.target.value})}
            >
              <option value="">All Risks</option>
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              value={filters.type}
              onChange={(e) => setFilters({...filters, type: e.target.value})}
            >
              <option value="">All Types</option>
              <option value="rightsizing">Rightsizing</option>
              <option value="reserved_instance">Reserved Instance</option>
              <option value="spot_instance">Spot Instance</option>
              <option value="storage_optimization">Storage Optimization</option>
              <option value="unused_resource">Unused Resource</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Min Savings ($)</label>
            <input
              type="number"
              className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              placeholder="100"
              value={filters.min_savings}
              onChange={(e) => setFilters({...filters, min_savings: e.target.value})}
            />
          </div>
        </div>

        {/* Sort Controls */}
        <div className="mb-4 flex items-center space-x-4">
          <span className="text-sm font-medium text-gray-700">Sort by:</span>
          <select
            className="rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as any)}
          >
            <option value="savings">Potential Savings</option>
            <option value="priority">Priority</option>
            <option value="created">Date Created</option>
          </select>
          <button
            onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
            className="text-sm text-indigo-600 hover:text-indigo-800"
          >
            {sortOrder === 'asc' ? '↑' : '↓'}
          </button>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Recommendation
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risk
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Savings
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Confidence
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredAndSortedRecommendations.map((rec) => (
                <tr key={rec.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{rec.title}</div>
                      <div className="text-sm text-gray-500">{rec.description}</div>
                      {rec.priority_level && (
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium mt-1 ${getPriorityColor(rec.priority_level)}`}>
                          {rec.priority_level}
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-sm text-gray-900 capitalize">{rec.type.replace('_', ' ')}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskColor(rec.risk_level)}`}>
                      {rec.risk_level}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    ${rec.potential_savings.toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                        <div
                          className="bg-indigo-600 h-2 rounded-full"
                          style={{ width: `${rec.confidence_score * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm text-gray-900">{Math.round(rec.confidence_score * 100)}%</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button className="text-indigo-600 hover:text-indigo-900">Details</button>
                      {onExplainWithAI && (
                        <button 
                          onClick={() => onExplainWithAI(rec)}
                          className="text-purple-600 hover:text-purple-900 flex items-center space-x-1"
                        >
                          <Brain className="h-4 w-4" />
                          <span>AI</span>
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {filteredAndSortedRecommendations.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500">No recommendations match the current filters.</p>
          </div>
        )}
      </div>
    </div>
  )
}

// Add interface for resources
interface CloudResource {
  id: string
  provider: string
  resource_id: string
  resource_type: string
  name: string
  region: string
  tags: Record<string, string>
  specifications: Record<string, any>
  monthly_cost?: number
  created_at: string
  updated_at: string
}

// Add function to fetch resources
const fetchResources = async (): Promise<CloudResource[]> => {
  try {
    const response = await fetch(API_ENDPOINTS.RESOURCES, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      }
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch resources')
    }
    
    return await response.json()
  } catch (error) {
    console.error('Error fetching resources:', error)
    throw error
  }
}

const Dashboard: React.FC = () => {
  // Date range state
  const [selectedDateRange, setSelectedDateRange] = useState<DateRange>(DATE_RANGE_OPTIONS[1]) // Default to "Last 30 days"
  const [customStartDate, setCustomStartDate] = useState<Date>(new Date())
  const [customEndDate, setCustomEndDate] = useState<Date>(new Date())

  // Create a wrapper function for fetchCostSummary that works with React Query
  const fetchCostSummaryWithRange = React.useCallback(async () => {
    return fetchCostSummary(selectedDateRange)
  }, [selectedDateRange])

  const { data: costSummary, isLoading: costLoading, refetch: refetchCostSummary } = useQuery(
    ['costSummary', selectedDateRange.startDate, selectedDateRange.endDate],
    fetchCostSummaryWithRange,
    { refetchInterval: 30000 }
  )

  const { data: optimizations, isLoading: optimizationsLoading } = useQuery(
    'optimizations',
    fetchOptimizations
  )

  const { data: resources, isLoading: resourcesLoading } = useQuery(
    'resources',
    fetchResources,
    { refetchInterval: 60000 } // Refresh every minute
  )

  const { data: aiStatus, isLoading: aiStatusLoading } = useQuery(
    'aiStatus',
    fetchAIAgentStatus,
    { refetchInterval: 60000 } // Refresh every minute
  )

  const { data: aiTrends } = useQuery(
    'aiTrends',
    fetchAITrendAnalysis,
    { refetchInterval: 300000 } // Refresh every 5 minutes
  )

  // Handle date range changes
  const handleDateRangeChange = (newRange: DateRange) => {
    setSelectedDateRange(newRange)
    // React Query will automatically refetch when the key changes
  }

  const handleCustomDateChange = (startDate: Date, endDate: Date) => {
    setCustomStartDate(startDate)
    setCustomEndDate(endDate)
  }

  // AI Explanation Modal State
  const [aiModalOpen, setAiModalOpen] = useState(false)
  const [selectedRecommendation, setSelectedRecommendation] = useState<OptimizationRecommendation | null>(null)
  const [aiExplanation, setAiExplanation] = useState<AIExplanation | null>(null)
  const [aiExplanationLoading, setAiExplanationLoading] = useState(false)

  // ML Pipeline state
  const [mlPipelineRunning, setMlPipelineRunning] = useState(false)
  const [mlPipelineResults, setMlPipelineResults] = useState<any>(null)
  const [mlPipelineError, setMlPipelineError] = useState<string | null>(null)

  // Handle AI explanation request
  const handleExplainWithAI = async (recommendation: OptimizationRecommendation) => {
    console.log('=== AI Explanation Request ===')
    console.log('Recommendation:', recommendation)
    console.log('Resource ID:', recommendation.resource_id)
    console.log('Optimization ID:', recommendation.id)
    
    setSelectedRecommendation(recommendation)
    setAiExplanationLoading(true)
    setAiModalOpen(true)

    try {
      const explanation = await fetchAIExplanation(
        recommendation.id, 
        recommendation.resource_id || recommendation.id // Use resource_id if available, fallback to optimization id
      )
      setAiExplanation(explanation)
    } catch (error) {
      console.error('Error getting AI explanation:', error)
      setAiExplanation({
        explanation: "Unable to generate AI explanation at this time. Please try again later.",
        generated_at: new Date().toISOString(),
        model_used: 'N/A',
        confidence: 'low'
      })
    } finally {
      setAiExplanationLoading(false)
    }
  }

  // Close AI explanation modal
  const closeAIModal = () => {
    setAiModalOpen(false)
    setSelectedRecommendation(null)
    setAiExplanation(null)
    setAiExplanationLoading(false)
  }

  // Handle ML pipeline execution
  const handleRunMLPipeline = async () => {
    setMlPipelineRunning(true)
    setMlPipelineError(null)
    setMlPipelineResults(null)

    try {
      const results = await runMLPipeline()
      setMlPipelineResults(results)
      console.log('ML Pipeline results:', results)
    } catch (error) {
      console.error('Error running ML pipeline:', error)
      setMlPipelineError(error instanceof Error ? error.message : 'Failed to run ML pipeline')
    } finally {
      setMlPipelineRunning(false)
    }
  }

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6']

  const providerData = costSummary ? Object.entries(costSummary.cost_by_provider).map(
    ([name, value]) => ({ name, value })
  ) : []

  const serviceData = costSummary ? Object.entries(costSummary.cost_by_service).map(
    ([name, value]) => ({ name, value })
  ) : []

  // Calculate real statistics from actual data
  const totalResources = resources ? resources.length : 0
  const totalPotentialSavings = optimizations ? optimizations.reduce((sum, opt) => sum + opt.potential_savings, 0) : 0
  const totalMonthlyCost = costSummary ? costSummary.total_cost : 0
  
  // Calculate optimization score based on potential savings ratio
  const calculateOptimizationScore = () => {
    if (!totalMonthlyCost || totalMonthlyCost === 0) return 'N/A'
    
    const savingsRatio = totalPotentialSavings / totalMonthlyCost
    if (savingsRatio >= 0.4) return 'A+'
    if (savingsRatio >= 0.3) return 'A'
    if (savingsRatio >= 0.25) return 'B+'
    if (savingsRatio >= 0.2) return 'B'
    if (savingsRatio >= 0.15) return 'C+'
    if (savingsRatio >= 0.1) return 'C'
    return 'D'
  }
  
  const optimizationScore = calculateOptimizationScore()
  
  // Calculate cost change percentage (mock for now, could be calculated from historical data)
  const costChangePercentage = costSummary?.daily_costs && costSummary.daily_costs.length >= 2 ? 
    ((costSummary.daily_costs[costSummary.daily_costs.length - 1].cost - 
      costSummary.daily_costs[costSummary.daily_costs.length - 7].cost) / 
     costSummary.daily_costs[costSummary.daily_costs.length - 7].cost * 100).toFixed(1) : '0.0'

  // Merge daily costs with AI predictions for chart display
  const chartData = React.useMemo(() => {
    if (!costSummary?.daily_costs) return []
    
    // Create a map of AI predictions by date for faster lookup
    const aiPredictionMap = new Map()
    if (aiTrends && aiTrends.length > 0) {
      aiTrends.forEach(trend => {
        aiPredictionMap.set(trend.date, trend)
      })
    }
    
    // Merge the data
    return costSummary.daily_costs.map(dailyCost => {
      const aiPrediction = aiPredictionMap.get(dailyCost.date)
      return {
        date: dailyCost.date,
        cost: dailyCost.cost,
        predicted_cost: aiPrediction?.predicted_cost || null,
        ai_insight: aiPrediction?.ai_insight || null
      }
    })
  }, [costSummary?.daily_costs, aiTrends])

  if (costLoading && optimizationsLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Date Range Selector */}
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg leading-6 font-medium text-gray-900 mb-2">
                Dashboard Overview
              </h3>
              <DateRangeSelector
                selectedRange={selectedDateRange}
                onRangeChange={handleDateRangeChange}
                customStartDate={customStartDate}
                customEndDate={customEndDate}
                onCustomDateChange={handleCustomDateChange}
              />
            </div>
            <button
              onClick={() => refetchCostSummary()}
              disabled={costLoading}
              className={`inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${costLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${costLoading ? 'animate-spin' : ''}`} />
              {costLoading ? 'Loading...' : 'Refresh Data'}
            </button>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
        <StatCard
          title="Total Monthly Cost"
          value={totalMonthlyCost > 0 ? `$${totalMonthlyCost.toLocaleString()}` : '$0'}
          change={`${costChangePercentage}%`}
          changeType={parseFloat(costChangePercentage) < 0 ? "positive" : "negative"}
          icon={DollarSign}
        />
        <StatCard
          title="Potential Savings"
          value={totalPotentialSavings > 0 ? `$${totalPotentialSavings.toLocaleString()}` : '$0'}
          change={optimizations ? `${optimizations.length} opportunities` : '0 opportunities'}
          changeType="positive"
          icon={TrendingDown}
        />
        <StatCard
          title="Active Resources"
          value={totalResources.toString()}
          change={resourcesLoading ? 'Loading...' : `${totalResources} total`}
          changeType="positive"
          icon={Server}
        />
        <StatCard
          title="Optimization Score"
          value={optimizationScore}
          change={totalPotentialSavings > 0 ? 
            `${((totalPotentialSavings / totalMonthlyCost) * 100).toFixed(1)}% savings potential` : 
            'No optimizations available'
          }
          changeType={optimizationScore !== 'D' && optimizationScore !== 'N/A' ? "positive" : "negative"}
          icon={Zap}
        />
        <StatCard
          title="AI Agent Status"
          value={aiStatus?.llm_available ? "Online" : "Offline"}
          change={aiStatus?.llm_available ? aiStatus.llm_model.model_name : "Check connection"}
          changeType={aiStatus?.llm_available ? "positive" : "negative"}
          icon={Bot}
        />
      </div>

      {/* ML Pipeline Control Section */}
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                ML Pipeline Control
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                Run the complete ML pipeline to generate new optimization recommendations
              </p>
            </div>
            <button
              onClick={handleRunMLPipeline}
              disabled={mlPipelineRunning}
              className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white ${
                mlPipelineRunning
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500'
              }`}
            >
              {mlPipelineRunning ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Running Pipeline...
                </>
              ) : (
                <>
                  <Zap className="h-4 w-4 mr-2" />
                  Run ML Pipeline
                </>
              )}
            </button>
          </div>

          {/* ML Pipeline Results */}
          {mlPipelineResults && (
            <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-md">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-400 mr-2" />
                <h4 className="text-sm font-medium text-green-800">Pipeline Execution Successful</h4>
              </div>
              <div className="mt-2 text-sm text-green-700">
                <p>Generated {mlPipelineResults.results?.total_recommendations || 0} optimization recommendations</p>
                <p>Total potential savings: ${mlPipelineResults.results?.total_potential_savings?.toFixed(2) || '0.00'}</p>
                <p>Execution time: {mlPipelineResults.execution_time}</p>
              </div>
            </div>
          )}

          {/* ML Pipeline Error */}
          {mlPipelineError && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-md">
              <div className="flex items-center">
                <XCircle className="h-5 w-5 text-red-400 mr-2" />
                <h4 className="text-sm font-medium text-red-800">Pipeline Execution Failed</h4>
              </div>
              <div className="mt-2 text-sm text-red-700">
                <p>{mlPipelineError}</p>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Daily Costs Chart with AI Insights */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-lg leading-6 font-medium text-gray-900">
                  Daily Cost Trend with AI Insights
                </h3>
                <p className="text-sm text-gray-500">
                  {format(selectedDateRange.startDate, 'MMM dd')} - {format(selectedDateRange.endDate, 'MMM dd, yyyy')}
                </p>
              </div>
              {aiStatus?.llm_available && (
                <div className="flex items-center space-x-1 text-xs text-purple-600">
                  <Brain className="h-4 w-4" />
                  <span>AI Enhanced</span>
                </div>
              )}
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => format(new Date(value), 'MM/dd')}
                  />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip 
                    formatter={(value: number, name: string) => {
                      if (name === 'ai_prediction') {
                        return [`$${value.toFixed(2)}`, 'AI Prediction']
                      }
                      return [`$${value.toFixed(2)}`, 'Actual Cost']
                    }}
                    labelFormatter={(label) => format(new Date(label), 'MMM dd, yyyy')}
                  />
                  <Line 
                    type="monotone" 
                    dataKey="cost" 
                    stroke="#3B82F6" 
                    strokeWidth={2}
                    dot={{ fill: '#3B82F6', strokeWidth: 2, r: 4 }}
                    name="actual"
                  />
                  <Line 
                    type="monotone" 
                    dataKey="predicted_cost" 
                    stroke="#8B5CF6" 
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={{ fill: '#8B5CF6', strokeWidth: 2, r: 3 }}
                    name="ai_prediction"
                    connectNulls={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>
            {aiTrends && aiTrends.length > 0 && (
              <div className="mt-4 p-3 bg-purple-50 rounded-lg">
                <div className="flex items-center space-x-2 mb-2">
                  <Brain className="h-4 w-4 text-purple-600" />
                  <span className="text-sm font-medium text-purple-800">AI Trend Analysis</span>
                </div>
                <div className="space-y-2">
                  <p className="text-sm text-purple-700">
                    {aiTrends[aiTrends.length - 1]?.ai_insight || 'AI analysis in progress...'}
                  </p>
                  {chartData.filter(d => d.predicted_cost !== null).length > 0 && (
                    <div className="text-xs text-purple-600">
                      • Predictions available for {chartData.filter(d => d.predicted_cost !== null).length} days
                      • Model: llama3.2 • Confidence: 85%
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Cost by Provider */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <div className="mb-4">
              <h3 className="text-lg leading-6 font-medium text-gray-900">
                Cost by Provider
              </h3>
              <p className="text-sm text-gray-500">
                {format(selectedDateRange.startDate, 'MMM dd')} - {format(selectedDateRange.endDate, 'MMM dd, yyyy')}
              </p>
            </div>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={providerData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {providerData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => [`$${value.toFixed(2)}`, 'Cost']} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Cost by Service Chart */}
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="mb-4">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Cost by Service
            </h3>
            <p className="text-sm text-gray-500">
              {format(selectedDateRange.startDate, 'MMM dd')} - {format(selectedDateRange.endDate, 'MMM dd, yyyy')}
            </p>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={serviceData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                <YAxis tick={{ fontSize: 12 }} />
                <Tooltip formatter={(value: number) => [`$${value.toFixed(2)}`, 'Cost']} />
                <Bar dataKey="value" fill="#3B82F6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Optimization Recommendations */}
      <div className="bg-white overflow-hidden shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Top Optimization Opportunities
            </h3>
            <span className="text-sm text-gray-500">
              {optimizations?.length || 0} recommendations
            </span>
          </div>
          <div className="space-y-4">
            {optimizations?.slice(0, 3).map((recommendation) => (
              <OptimizationCard 
                key={recommendation.id} 
                recommendation={recommendation}
                onExplainWithAI={handleExplainWithAI}
              />
            ))}
          </div>
        </div>
      </div>

      {/* Optimization Queue with Filters */}
      {optimizations && (
        <OptimizationQueue 
          recommendations={optimizations}
          onExplainWithAI={handleExplainWithAI}
        />
      )}

      {/* AI Explanation Modal */}
      <AIExplanationModal
        isOpen={aiModalOpen}
        onClose={closeAIModal}
        explanation={aiExplanation}
        isLoading={aiExplanationLoading}
        title={selectedRecommendation?.title || 'Optimization Analysis'}
      />
    </div>
  )
}

export default Dashboard

import React, { useState } from 'react'
import { useQuery } from 'react-query'
import { CheckCircle, XCircle, Clock, AlertTriangle, Filter, Search, TrendingUp, DollarSign, Bot, Eye, EyeOff } from 'lucide-react'
import { API_ENDPOINTS } from '../config'

// Types
interface OptimizationRecommendation {
  id: string
  resource_id?: string
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
  status?: 'pending' | 'approved' | 'rejected' | 'implemented'
  created_at?: string
  implemented_at?: string
  rejection_reason?: string
}

interface OptimizationStats {
  total_recommendations: number
  approved_recommendations: number
  implemented_recommendations: number
  total_potential_savings: number
  total_realized_savings: number
  average_implementation_time: number
}

// API functions
const fetchOptimizations = async (): Promise<OptimizationRecommendation[]> => {
  try {
    const response = await fetch(API_ENDPOINTS.OPTIMIZATIONS, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        min_savings: 0.0 // Get all recommendations
      })
    })

    if (!response.ok) {
      throw new Error('Failed to fetch optimizations')
    }

    const data = await response.json()
    console.log('=== Optimizations Backend Response ===')
    console.log('Raw data:', data)
    
    return data.recommendations.map((rec: any) => ({
      id: rec.id,
      resource_id: rec.resource_id,
      type: rec.type,
      title: rec.title,
      description: rec.description,
      potential_savings: rec.potential_savings,
      risk_level: rec.risk_level,
      confidence_score: rec.confidence_score,
      priority_rank: rec.priority_rank,
      priority_level: rec.priority_level || 'medium',
      implementation_complexity: rec.implementation_complexity || 'medium',
      estimated_effort_hours: rec.estimated_effort_hours || 2,
      requires_downtime: rec.requires_downtime || false,
      status: rec.status || 'pending',
      created_at: rec.created_at,
      implemented_at: rec.implemented_at,
      rejection_reason: rec.rejection_reason
    }))
  } catch (error) {
    console.error('Error fetching optimizations:', error)
    throw error // Don't fallback to mock data
  }
}

const fetchOptimizationStats = async (): Promise<OptimizationStats> => {
  try {
    const response = await fetch(API_ENDPOINTS.OPTIMIZATION_STATS)

    if (!response.ok) {
      throw new Error('Failed to fetch optimization stats')
    }

    return await response.json()
  } catch (error) {
    console.error('Error fetching optimization stats:', error)
    // Calculate stats from optimizations as fallback
    try {
      const optimizations = await fetchOptimizations()
      const approved = optimizations.filter(o => o.status === 'approved').length
      const implemented = optimizations.filter(o => o.status === 'implemented').length
      const totalPotential = optimizations.reduce((sum, o) => sum + o.potential_savings, 0)
      const totalRealized = optimizations.filter(o => o.status === 'implemented').reduce((sum, o) => sum + o.potential_savings, 0)

      return {
        total_recommendations: optimizations.length,
        approved_recommendations: approved,
        implemented_recommendations: implemented,
        total_potential_savings: totalPotential,
        total_realized_savings: totalRealized,
        average_implementation_time: 3.5 // Default value
      }
    } catch {
      return {
        total_recommendations: 0,
        approved_recommendations: 0,
        implemented_recommendations: 0,
        total_potential_savings: 0,
        total_realized_savings: 0,
        average_implementation_time: 0
      }
    }
  }
}

const fetchAIExplanation = async (optimizationId: string, resourceId: string): Promise<any> => {
  try {
    const response = await fetch(API_ENDPOINTS.AI_EXPLAIN_OPTIMIZATION, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        optimization_id: optimizationId,
        resource_id: resourceId
      })
    })

    if (!response.ok) {
      throw new Error('Failed to fetch AI explanation')
    }

    return await response.json()
  } catch (error) {
    console.error('Error fetching AI explanation:', error)
    throw error
  }
}

// Components
const StatCard: React.FC<{
  title: string
  value: string
  subtitle?: string
  icon: React.ComponentType<any>
  color: string
}> = ({ title, value, subtitle, icon: Icon, color }) => (
  <div className="bg-white overflow-hidden shadow rounded-lg">
    <div className="p-5">
      <div className="flex items-center">
        <div className="flex-shrink-0">
          <Icon className={`h-6 w-6 ${color}`} />
        </div>
        <div className="ml-5 w-0 flex-1">
          <dl>
            <dt className="text-sm font-medium text-gray-500 truncate">
              {title}
            </dt>
            <dd className="text-lg font-medium text-gray-900">
              {value}
            </dd>
            {subtitle && (
              <dd className="text-sm text-gray-500">
                {subtitle}
              </dd>
            )}
          </dl>
        </div>
      </div>
    </div>
  </div>
)

const AIExplanation: React.FC<{
  explanation: string
  isLoading: boolean
  error?: string
}> = ({ explanation, isLoading, error }) => {
  if (isLoading) {
    return (
      <div className="mt-4 p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-200 shadow-sm">
        <div className="flex items-center space-x-3">
          <Bot className="h-5 w-5 text-blue-500 animate-pulse" />
          <div className="flex-1">
            <span className="text-sm font-medium text-gray-900">Generating AI explanation...</span>
            <div className="flex items-center space-x-2 mt-2">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
              <span className="text-xs text-blue-600">This may take a few seconds</span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="mt-4 p-6 bg-gradient-to-br from-red-50 to-pink-50 rounded-lg border border-red-200 shadow-sm">
        <div className="flex items-center space-x-3">
          <AlertTriangle className="h-5 w-5 text-red-500" />
          <div className="flex-1">
            <span className="text-sm font-medium text-red-900">Failed to generate AI explanation</span>
            <p className="text-xs text-red-700 mt-1">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  if (!explanation) {
    return null
  }

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
                <span className="text-blue-500 mt-1 flex-shrink-0 text-sm">•</span>
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
            <h4 className="text-base font-semibold text-gray-900 mb-3 border-b border-blue-200 pb-2 flex items-center">
              <span className="bg-blue-100 text-blue-800 px-2 py-1 rounded text-xs font-medium mr-2">
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
    <div className="mt-4 p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border border-blue-200 shadow-sm">
      <div className="flex items-center space-x-2 mb-4">
        <Bot className="h-5 w-5 text-blue-600" />
        <span className="text-sm font-semibold text-gray-900">AI Explanation</span>
        <div className="flex-1 h-px bg-blue-200"></div>
      </div>
      <div className="prose prose-sm max-w-none text-gray-800">
        {renderExplanation(explanation)}
      </div>
    </div>
  )
}

// Main component
const OptimizationCard: React.FC<{
  recommendation: OptimizationRecommendation
  onStatusChange: (id: string, status: string, reason?: string) => void
}> = ({ recommendation, onStatusChange }) => {
  const [showAIExplanation, setShowAIExplanation] = useState(false)
  const [aiExplanation, setAiExplanation] = useState<string>('')
  const [aiLoading, setAiLoading] = useState(false)
  const [aiError, setAiError] = useState<string>('')

  const handleAIExplanation = async () => {
    if (showAIExplanation) {
      setShowAIExplanation(false)
      return
    }

    if (aiExplanation) {
      setShowAIExplanation(true)
      return
    }

    setAiLoading(true)
    setAiError('')
    
    try {
      const result = await fetchAIExplanation(recommendation.id, recommendation.resource_id || '')
      setAiExplanation(result.explanation)
      setShowAIExplanation(true)
    } catch (error) {
      setAiError(error instanceof Error ? error.message : 'Failed to generate explanation')
    } finally {
      setAiLoading(false)
    }
  }
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
      case 'low': return 'bg-green-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status?: string) => {
    switch (status) {
      case 'approved': return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'rejected': return <XCircle className="h-5 w-5 text-red-500" />
      case 'implemented': return <CheckCircle className="h-5 w-5 text-blue-500" />
      default: return <Clock className="h-5 w-5 text-gray-400" />
    }
  }

  const getComplexityColor = (complexity: string) => {
    switch (complexity) {
      case 'low': return 'text-green-600'
      case 'medium': return 'text-yellow-600'
      case 'high': return 'text-red-600'
      default: return 'text-gray-600'
    }
  }

  return (
    <div className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start space-x-3">
          {getStatusIcon(recommendation.status)}
          <div className="flex-1">
            <h4 className="text-lg font-medium text-gray-900">{recommendation.title}</h4>
            <p className="text-sm text-gray-600 mt-1">{recommendation.description}</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-2xl font-semibold text-green-600">
            ${recommendation.potential_savings.toFixed(0)}
          </div>
          <div className="text-sm text-gray-500">monthly savings</div>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2 mb-4">
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRiskColor(recommendation.risk_level)}`}>
          {recommendation.risk_level} risk
        </span>
        {recommendation.priority_level && (
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getPriorityColor(recommendation.priority_level)}`}>
            {recommendation.priority_level} priority
          </span>
        )}
        <span className="text-xs text-gray-500">
          {Math.round(recommendation.confidence_score * 100)}% confidence
        </span>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4 text-sm">
        <div>
          <span className="text-gray-500">Complexity:</span>
          <span className={`ml-1 font-medium ${getComplexityColor(recommendation.implementation_complexity || 'medium')}`}>
            {recommendation.implementation_complexity || 'medium'}
          </span>
        </div>
        <div>
          <span className="text-gray-500">Effort:</span>
          <span className="ml-1 font-medium text-gray-900">
            {recommendation.estimated_effort_hours}h
          </span>
        </div>
        <div>
          <span className="text-gray-500">Downtime:</span>
          <span className={`ml-1 font-medium ${recommendation.requires_downtime ? 'text-red-600' : 'text-green-600'}`}>
            {recommendation.requires_downtime ? 'Required' : 'None'}
          </span>
        </div>
        <div>
          <span className="text-gray-500">Status:</span>
          <span className="ml-1 font-medium text-gray-900 capitalize">
            {recommendation.status || 'pending'}
          </span>
        </div>
      </div>

      {recommendation.status === 'rejected' && recommendation.rejection_reason && (
        <div className="mb-4 p-3 bg-red-50 rounded-lg">
          <div className="flex items-center space-x-2">
            <XCircle className="h-4 w-4 text-red-500" />
            <span className="text-sm font-medium text-red-800">Rejection Reason:</span>
          </div>
          <p className="text-sm text-red-700 mt-1">{recommendation.rejection_reason}</p>
        </div>
      )}

      {recommendation.status === 'implemented' && recommendation.implemented_at && (
        <div className="mb-4 p-3 bg-green-50 rounded-lg">
          <div className="flex items-center space-x-2">
            <CheckCircle className="h-4 w-4 text-green-500" />
            <span className="text-sm font-medium text-green-800">
              Implemented on {new Date(recommendation.implemented_at).toLocaleDateString()}
            </span>
          </div>
        </div>
      )}

      {recommendation.status === 'pending' && (
        <div className="flex space-x-2">
          <button
            onClick={() => onStatusChange(recommendation.id, 'approved')}
            className="flex-1 bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 text-sm font-medium"
          >
            Approve
          </button>
          <button
            onClick={() => onStatusChange(recommendation.id, 'rejected')}
            className="flex-1 bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 text-sm font-medium"
          >
            Reject
          </button>
        </div>
      )}

      {recommendation.status === 'approved' && (
        <div className="flex space-x-2">
          <button
            onClick={() => onStatusChange(recommendation.id, 'implemented')}
            className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm font-medium"
          >
            Mark Implemented
          </button>
          <button
            onClick={() => onStatusChange(recommendation.id, 'rejected')}
            className="flex-1 bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 text-sm font-medium"
          >
            Cancel
          </button>
        </div>
      )}

      {/* AI Explanation Button */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <button
          onClick={handleAIExplanation}
          disabled={aiLoading}
          className="flex items-center space-x-2 text-sm text-blue-600 hover:text-blue-800 disabled:text-gray-400 disabled:cursor-not-allowed"
        >
          {aiLoading ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
          ) : showAIExplanation ? (
            <EyeOff className="h-4 w-4" />
          ) : (
            <Bot className="h-4 w-4" />
          )}
          <span>
            {aiLoading ? 'Generating...' : showAIExplanation ? 'Hide AI Explanation' : 'Show AI Explanation'}
          </span>
        </button>
      </div>

      {/* AI Explanation Display */}
      {showAIExplanation && (
        <AIExplanation 
          explanation={aiExplanation} 
          isLoading={aiLoading} 
          error={aiError} 
        />
      )}
    </div>
  )
}

const Optimizations: React.FC = () => {
  const { data: optimizations, isLoading: optimizationsLoading, refetch } = useQuery(
    'optimizations',
    fetchOptimizations
  )

  const { data: stats, isLoading: statsLoading } = useQuery(
    'optimizationStats',
    fetchOptimizationStats
  )

  const [filters, setFilters] = useState({
    status: '',
    risk_level: '',
    priority_level: '',
    type: '',
    search: ''
  })

  const [sortBy, setSortBy] = useState<'savings' | 'priority' | 'created' | 'effort'>('savings')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  const handleStatusChange = async (id: string, status: string, reason?: string) => {
    try {
      const response = await fetch(`${API_ENDPOINTS.OPTIMIZATIONS}/${id}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status,
          rejection_reason: reason
        })
      })

      if (!response.ok) {
        throw new Error('Failed to update optimization status')
      }

      // Refetch optimizations to get updated data
      refetch()
    } catch (error) {
      console.error('Error updating optimization status:', error)
      // For demo purposes, update local state
      console.log(`Updated optimization ${id} to status: ${status}`)
    }
  }

  // Filter and sort optimizations
  const filteredAndSortedOptimizations = React.useMemo(() => {
    if (!optimizations) return []

    let filtered = optimizations.filter(opt => {
      if (filters.status && opt.status !== filters.status) return false
      if (filters.risk_level && opt.risk_level !== filters.risk_level) return false
      if (filters.priority_level && opt.priority_level !== filters.priority_level) return false
      if (filters.type && opt.type !== filters.type) return false
      if (filters.search) {
        const searchTerm = filters.search.toLowerCase()
        const searchableText = `${opt.title} ${opt.description} ${opt.type}`.toLowerCase()
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
        case 'effort':
          aValue = a.estimated_effort_hours || 0
          bValue = b.estimated_effort_hours || 0
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
  }, [optimizations, filters, sortBy, sortOrder])

  if (optimizationsLoading || statsLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Recommendations"
          value={stats?.total_recommendations.toString() || '0'}
          subtitle="active optimizations"
          icon={AlertTriangle}
          color="text-blue-600"
        />
        <StatCard
          title="Approved"
          value={stats?.approved_recommendations.toString() || '0'}
          subtitle="ready for implementation"
          icon={CheckCircle}
          color="text-green-600"
        />
        <StatCard
          title="Implemented"
          value={stats?.implemented_recommendations.toString() || '0'}
          subtitle="savings realized"
          icon={TrendingUp}
          color="text-purple-600"
        />
        <StatCard
          title="Potential Savings"
          value={`$${(stats?.total_potential_savings || 0).toLocaleString()}`}
          subtitle="monthly opportunity"
          icon={DollarSign}
          color="text-green-600"
        />
      </div>

      {/* Filters and Controls */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Optimization Management
            </h3>
            <span className="text-sm text-gray-500">
              {filteredAndSortedOptimizations.length} of {optimizations?.length || 0} recommendations
            </span>
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-4">
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
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                value={filters.status}
                onChange={(e) => setFilters({...filters, status: e.target.value})}
              >
                <option value="">All Status</option>
                <option value="pending">Pending</option>
                <option value="approved">Approved</option>
                <option value="implemented">Implemented</option>
                <option value="rejected">Rejected</option>
              </select>
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
              <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              <select
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                value={filters.priority_level}
                onChange={(e) => setFilters({...filters, priority_level: e.target.value})}
              >
                <option value="">All Priorities</option>
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Sort by</label>
              <select
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
              >
                <option value="savings">Potential Savings</option>
                <option value="priority">Priority</option>
                <option value="effort">Effort</option>
                <option value="created">Date Created</option>
              </select>
            </div>
          </div>

          {/* Sort Order Toggle */}
          <div className="flex items-center space-x-2">
            <span className="text-sm font-medium text-gray-700">Order:</span>
            <button
              onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
              className="text-sm text-indigo-600 hover:text-indigo-800"
            >
              {sortOrder === 'asc' ? '↑ Ascending' : '↓ Descending'}
            </button>
          </div>
        </div>
      </div>

      {/* Optimization Cards */}
      <div className="space-y-4">
        {filteredAndSortedOptimizations.map((optimization) => (
          <OptimizationCard
            key={optimization.id}
            recommendation={optimization}
            onStatusChange={handleStatusChange}
          />
        ))}
      </div>

      {filteredAndSortedOptimizations.length === 0 && (
        <div className="text-center py-12">
          <AlertTriangle className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No optimizations found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Try adjusting your filters or check back later for new recommendations.
          </p>
        </div>
      )}
    </div>
  )
}

export default Optimizations

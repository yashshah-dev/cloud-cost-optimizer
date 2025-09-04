import React, { useState } from 'react'
import { useQuery } from 'react-query'
import { Server, Database, HardDrive, Globe, Cpu, MemoryStick, Zap, AlertTriangle, CheckCircle, XCircle, Clock, Search, Filter, RefreshCw, DollarSign, Bot } from 'lucide-react'
import { API_ENDPOINTS } from '../config'

// Types
interface CloudResource {
  id: string
  name: string
  type: string
  provider: string
  region: string
  status: 'running' | 'stopped' | 'terminated' | 'error'
  cost_per_hour: number
  cost_per_month: number
  utilization?: {
    cpu?: number
    memory?: number
    storage?: number
    network?: number
  }
  tags: Record<string, string>
  created_at: string
  last_seen: string
  optimization_status?: 'optimal' | 'underutilized' | 'overutilized' | 'unused'
  recommendations?: string[]
}

interface ResourceStats {
  total_resources: number
  running_resources: number
  stopped_resources: number
  total_monthly_cost: number
  average_utilization: number
  resources_by_type: Record<string, number>
  resources_by_provider: Record<string, number>
}

// Mock API functions
const fetchResources = async (): Promise<CloudResource[]> => {
  try {
    const response = await fetch(API_ENDPOINTS.RESOURCES)
    
    if (!response.ok) {
      throw new Error('Failed to fetch resources')
    }
    
    const data = await response.json()
    console.log('=== Backend Response Transformation ===')
    console.log('Raw backend data:', data[0])
    
    const transformed = data.map((res: any) => ({
      id: res.id,
      name: res.name || 'Unnamed Resource',
      type: res.resource_type, // Backend uses resource_type
      provider: res.provider,
      region: res.region,
      status: 'running', // Default status since backend doesn't provide it yet
      cost_per_hour: (res.monthly_cost || 0) / 730, // Convert monthly to hourly (730 = 24 * 30.4)
      cost_per_month: Number(res.monthly_cost) || 0,
      utilization: {
        cpu: Math.floor(Math.random() * 80) + 20, // Mock utilization data for now
        memory: Math.floor(Math.random() * 80) + 20,
        storage: Math.floor(Math.random() * 80) + 20,
        network: Math.floor(Math.random() * 50) + 10
      },
      tags: res.tags || {},
      created_at: res.created_at,
      last_seen: res.updated_at,
      optimization_status: (res.monthly_cost || 0) > 500 ? 'overutilized' : (res.monthly_cost || 0) < 50 ? 'underutilized' : 'optimal', // Simple heuristic
      recommendations: (res.monthly_cost || 0) > 300 ? ['rightsizing'] : []
    }))
    
    console.log('Transformed data:', transformed[0])
    return transformed
  } catch (error) {
    console.error('Error fetching resources:', error)
    throw error // Don't fallback to mock data, let the error be handled by react-query
  }
}

const fetchResourceStats = async (): Promise<ResourceStats> => {
  try {
    const response = await fetch(API_ENDPOINTS.RESOURCE_STATS)
    
    if (!response.ok) {
      throw new Error('Failed to fetch resource stats')
    }
    
    return await response.json()
  } catch (error) {
    console.error('Error fetching resource stats:', error)
    // Calculate stats from resources as fallback
    try {
      const resources = await fetchResources()
      const runningResources = resources.filter(r => r.status === 'running').length
      const totalCost = resources.reduce((sum, r) => sum + (r.cost_per_month || 0), 0)
      const avgUtilization = resources.reduce((sum, r) => sum + (r.utilization?.cpu || 0), 0) / resources.length
      
      // Count by type
      const byType: Record<string, number> = {}
      const byProvider: Record<string, number> = {}
      
      resources.forEach(r => {
        byType[r.type] = (byType[r.type] || 0) + 1
        byProvider[r.provider] = (byProvider[r.provider] || 0) + 1
      })
      
      return {
        total_resources: resources.length,
        running_resources: runningResources,
        stopped_resources: resources.length - runningResources,
        total_monthly_cost: totalCost,
        average_utilization: Math.round(avgUtilization),
        resources_by_type: byType,
        resources_by_provider: byProvider
      }
    } catch {
      // Final fallback
      return {
        total_resources: 0,
        running_resources: 0,
        stopped_resources: 0,
        total_monthly_cost: 0,
        average_utilization: 0,
        resources_by_type: {},
        resources_by_provider: {}
      }
    }
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
            <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
            <dd className="flex items-baseline">
              <div className="text-2xl font-semibold text-gray-900">{value}</div>
              {subtitle && (
                <div className="ml-2 text-sm text-gray-500">{subtitle}</div>
              )}
            </dd>
          </dl>
        </div>
      </div>
    </div>
  </div>
)

const ResourceCard: React.FC<{ resource: CloudResource }> = ({ resource }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running': return 'bg-green-100 text-green-800'
      case 'stopped': return 'bg-yellow-100 text-yellow-800'
      case 'terminated': return 'bg-red-100 text-red-800'
      case 'error': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running': return <CheckCircle className="h-4 w-4" />
      case 'stopped': return <Clock className="h-4 w-4" />
      case 'terminated': return <XCircle className="h-4 w-4" />
      case 'error': return <AlertTriangle className="h-4 w-4" />
      default: return <Server className="h-4 w-4" />
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'ec2-instance':
      case 'compute-instance':
        return <Server className="h-5 w-5" />
      case 'rds-instance':
        return <Database className="h-5 w-5" />
      case 's3-bucket':
        return <HardDrive className="h-5 w-5" />
      case 'lambda-function':
        return <Zap className="h-5 w-5" />
      default:
        return <Server className="h-5 w-5" />
    }
  }

  const getOptimizationColor = (status?: string) => {
    switch (status) {
      case 'optimal': return 'bg-green-100 text-green-800'
      case 'underutilized': return 'bg-yellow-100 text-yellow-800'
      case 'overutilized': return 'bg-orange-100 text-orange-800'
      case 'unused': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getUtilizationColor = (value?: number) => {
    if (!value) return 'bg-gray-200'
    if (value < 30) return 'bg-red-400'
    if (value < 70) return 'bg-yellow-400'
    return 'bg-green-400'
  }

  return (
    <div className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            {getTypeIcon(resource.type)}
          </div>
          <div className="flex-1">
            <h4 className="text-lg font-medium text-gray-900">{resource.name}</h4>
            <p className="text-sm text-gray-600">{resource.id}</p>
            <div className="flex items-center space-x-2 mt-1">
              <span className="text-xs text-gray-500 uppercase">{resource.provider}</span>
              <span className="text-xs text-gray-500">•</span>
              <span className="text-xs text-gray-500">{resource.region}</span>
            </div>
          </div>
        </div>
        <div className="text-right">
          <div className="text-lg font-semibold text-gray-900">
            ${(resource.cost_per_month || 0).toFixed(2)}
          </div>
          <div className="text-sm text-gray-500">per month</div>
        </div>
      </div>

      <div className="flex flex-wrap items-center gap-2 mb-4">
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(resource.status)}`}>
          {getStatusIcon(resource.status)}
          <span className="ml-1">{resource.status}</span>
        </span>
        {resource.optimization_status && (
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getOptimizationColor(resource.optimization_status)}`}>
            {resource.optimization_status}
          </span>
        )}
      </div>

      {/* Utilization Bars */}
      {resource.utilization && (
        <div className="mb-4">
          <h5 className="text-sm font-medium text-gray-700 mb-2">Utilization</h5>
          <div className="space-y-2">
            {resource.utilization.cpu !== undefined && (
              <div className="flex items-center space-x-2">
                <span className="text-xs text-gray-500 w-12">CPU</span>
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${getUtilizationColor(resource.utilization.cpu)}`}
                    style={{ width: `${resource.utilization.cpu}%` }}
                  ></div>
                </div>
                <span className="text-xs text-gray-700 w-8">{resource.utilization.cpu}%</span>
              </div>
            )}
            {resource.utilization.memory !== undefined && (
              <div className="flex items-center space-x-2">
                <span className="text-xs text-gray-500 w-12">Memory</span>
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${getUtilizationColor(resource.utilization.memory)}`}
                    style={{ width: `${resource.utilization.memory}%` }}
                  ></div>
                </div>
                <span className="text-xs text-gray-700 w-8">{resource.utilization.memory}%</span>
              </div>
            )}
            {resource.utilization.storage !== undefined && (
              <div className="flex items-center space-x-2">
                <span className="text-xs text-gray-500 w-12">Storage</span>
                <div className="flex-1 bg-gray-200 rounded-full h-2">
                  <div
                    className={`h-2 rounded-full ${getUtilizationColor(resource.utilization.storage)}`}
                    style={{ width: `${resource.utilization.storage}%` }}
                  ></div>
                </div>
                <span className="text-xs text-gray-700 w-8">{resource.utilization.storage}%</span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tags */}
      {resource.tags && Object.keys(resource.tags).length > 0 && (
        <div className="mb-4">
          <h5 className="text-sm font-medium text-gray-700 mb-2">Tags</h5>
          <div className="flex flex-wrap gap-1">
            {Object.entries(resource.tags).map(([key, value]) => (
              <span
                key={key}
                className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-800"
              >
                {key}: {value}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Recommendations */}
      {resource.recommendations && resource.recommendations.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <h5 className="text-sm font-medium text-gray-700">Recommendations</h5>
            <a
              href="#/optimizations"
              className="text-xs text-blue-600 hover:text-blue-800 flex items-center space-x-1"
            >
              <Bot className="h-3 w-3" />
              <span>View AI Explanations</span>
            </a>
          </div>
          <div className="flex flex-wrap gap-1">
            {resource.recommendations.map((rec, index) => (
              <span
                key={index}
                className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800"
              >
                {rec.replace('_', ' ')}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>Created: {new Date(resource.created_at).toLocaleDateString()}</span>
        <span>Last seen: {new Date(resource.last_seen).toLocaleDateString()}</span>
      </div>
    </div>
  )
}

const Resources: React.FC = () => {
  const { data: resources, isLoading: resourcesLoading, refetch } = useQuery(
    'resources',
    fetchResources
  )

  const { data: stats, isLoading: statsLoading } = useQuery(
    'resourceStats',
    fetchResourceStats
  )

  const [filters, setFilters] = useState({
    provider: '',
    type: '',
    status: '',
    region: '',
    optimization_status: '',
    search: ''
  })

  const [sortBy, setSortBy] = useState<'cost' | 'name' | 'created' | 'utilization'>('cost')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  // Filter and sort resources
  const filteredAndSortedResources = React.useMemo(() => {
    if (!resources) return []

    let filtered = resources.filter(res => {
      if (filters.provider && res.provider !== filters.provider) return false
      if (filters.type && res.type !== filters.type) return false
      if (filters.status && res.status !== filters.status) return false
      if (filters.region && res.region !== filters.region) return false
      if (filters.optimization_status && res.optimization_status !== filters.optimization_status) return false
      if (filters.search) {
        const searchTerm = filters.search.toLowerCase()
        const searchableText = `${res.name} ${res.id} ${res.type} ${res.provider}`.toLowerCase()
        if (!searchableText.includes(searchTerm)) return false
      }
      return true
    })

    // Sort
    filtered.sort((a, b) => {
      let aValue: any, bValue: any

      switch (sortBy) {
        case 'cost':
          aValue = a.cost_per_month || 0
          bValue = b.cost_per_month || 0
          break
        case 'name':
          aValue = a.name.toLowerCase()
          bValue = b.name.toLowerCase()
          break
        case 'created':
          aValue = new Date(a.created_at).getTime()
          bValue = new Date(b.created_at).getTime()
          break
        case 'utilization':
          aValue = a.utilization?.cpu || 0
          bValue = b.utilization?.cpu || 0
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
  }, [resources, filters, sortBy, sortOrder])

  if (resourcesLoading || statsLoading) {
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
          title="Total Resources"
          value={stats?.total_resources.toString() || '0'}
          subtitle="across all providers"
          icon={Server}
          color="text-blue-600"
        />
        <StatCard
          title="Running Resources"
          value={stats?.running_resources.toString() || '0'}
          subtitle="currently active"
          icon={CheckCircle}
          color="text-green-600"
        />
        <StatCard
          title="Monthly Cost"
          value={`$${(stats?.total_monthly_cost || 0).toLocaleString()}`}
          subtitle="total expenditure"
          icon={DollarSign}
          color="text-red-600"
        />
        <StatCard
          title="Avg Utilization"
          value={`${stats?.average_utilization || 0}%`}
          subtitle="across all resources"
          icon={Cpu}
          color="text-purple-600"
        />
      </div>

      {/* Filters and Controls */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg leading-6 font-medium text-gray-900">
              Resource Inventory
            </h3>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => refetch()}
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </button>
              <span className="text-sm text-gray-500">
                {filteredAndSortedResources.length} of {resources?.length || 0} resources
              </span>
            </div>
          </div>

          {/* Filters */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  className="pl-10 w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                  placeholder="Search resources..."
                  value={filters.search}
                  onChange={(e) => setFilters({...filters, search: e.target.value})}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Provider</label>
              <select
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                value={filters.provider}
                onChange={(e) => setFilters({...filters, provider: e.target.value})}
              >
                <option value="">All Providers</option>
                <option value="aws">AWS</option>
                <option value="gcp">GCP</option>
                <option value="azure">Azure</option>
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
                <option value="compute">Compute</option>
                <option value="database">Database</option>
                <option value="storage">Storage</option>
                <option value="network">Network</option>
                <option value="serverless">Serverless</option>
                <option value="container">Container</option>
                <option value="other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                value={filters.status}
                onChange={(e) => setFilters({...filters, status: e.target.value})}
              >
                <option value="">All Status</option>
                <option value="running">Running</option>
                <option value="stopped">Stopped</option>
                <option value="terminated">Terminated</option>
                <option value="error">Error</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Optimization</label>
              <select
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                value={filters.optimization_status}
                onChange={(e) => setFilters({...filters, optimization_status: e.target.value})}
              >
                <option value="">All Status</option>
                <option value="optimal">Optimal</option>
                <option value="underutilized">Underutilized</option>
                <option value="overutilized">Overutilized</option>
                <option value="unused">Unused</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Sort by</label>
              <select
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
              >
                <option value="cost">Cost</option>
                <option value="name">Name</option>
                <option value="created">Created</option>
                <option value="utilization">Utilization</option>
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

      {/* Resource Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {filteredAndSortedResources.map((resource) => (
          <ResourceCard key={resource.id} resource={resource} />
        ))}
      </div>

      {filteredAndSortedResources.length === 0 && (
        <div className="text-center py-12">
          <Server className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No resources found</h3>
          <p className="mt-1 text-sm text-gray-500">
            Try adjusting your filters or check back later.
          </p>
        </div>
      )}
    </div>
  )
}

export default Resources

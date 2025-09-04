import React, { useState } from 'react'
import { useQuery } from 'react-query'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell, AreaChart, Area } from 'recharts'
import { FileText, Download, Calendar, TrendingUp, TrendingDown, DollarSign, Server, AlertTriangle, CheckCircle, Filter, RefreshCw } from 'lucide-react'
import { format, subDays, startOfMonth, endOfMonth, eachDayOfInterval } from 'date-fns'
import { API_ENDPOINTS } from '../config'

// Types
interface CostReport {
  period: string
  total_cost: number
  cost_by_provider: Record<string, number>
  cost_by_service: Record<string, number>
  cost_by_resource: Array<{
    resource_id: string
    resource_name: string
    cost: number
    provider: string
    type: string
  }>
  top_cost_resources: Array<{
    resource_id: string
    resource_name: string
    cost: number
    percentage: number
  }>
  cost_trends: Array<{
    date: string
    cost: number
    projected_cost?: number
  }>
  savings_opportunities: {
    total_potential_savings: number
    implemented_savings: number
    pending_savings: number
  }
}

interface OptimizationReport {
  total_recommendations: number
  implemented_recommendations: number
  pending_recommendations: number
  rejected_recommendations: number
  total_potential_savings: number
  total_realized_savings: number
  average_implementation_time: number
  recommendations_by_type: Record<string, number>
  recommendations_by_risk: Record<string, number>
  monthly_trends: Array<{
    month: string
    recommendations: number
    implemented: number
    savings: number
  }>
}

// Mock API functions
const fetchCostReport = async (startDate: string, endDate: string): Promise<CostReport> => {
  try {
    const response = await fetch(API_ENDPOINTS.COST_REPORT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        start_date: startDate,
        end_date: endDate
      })
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch cost report')
    }
    
    return await response.json()
  } catch (error) {
    console.error('Error fetching cost report:', error)
    throw error // Don't fallback to mock data
  }
}

const fetchOptimizationReport = async (startDate: string, endDate: string): Promise<OptimizationReport> => {
  try {
    const response = await fetch(API_ENDPOINTS.OPTIMIZATION_REPORT, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        start_date: startDate,
        end_date: endDate
      })
    })
    
    if (!response.ok) {
      throw new Error('Failed to fetch optimization report')
    }
    
    return await response.json()
  } catch (error) {
    console.error('Error fetching optimization report:', error)
    throw error // Don't fallback to mock data
  }
}

// Components
const ReportCard: React.FC<{
  title: string
  value: string
  subtitle?: string
  icon: React.ComponentType<any>
  color: string
  trend?: {
    value: number
    isPositive: boolean
  }
}> = ({ title, value, subtitle, icon: Icon, color, trend }) => (
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
              {trend && (
                <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                  trend.isPositive ? 'text-green-600' : 'text-red-600'
                }`}>
                  {trend.isPositive ? (
                    <TrendingUp className="flex-shrink-0 self-center h-4 w-4" />
                  ) : (
                    <TrendingDown className="flex-shrink-0 self-center h-4 w-4" />
                  )}
                  <span className="ml-1">{Math.abs(trend.value)}%</span>
                </div>
              )}
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

const CostBreakdownChart: React.FC<{ data: Record<string, number>; title: string }> = ({ data, title }) => {
  const chartData = Object.entries(data).map(([name, value]) => ({ name, value }))
  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4']

  return (
    <div className="bg-white p-6 rounded-lg shadow">
      <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip formatter={(value: number) => [`$${value.toFixed(2)}`, 'Cost']} />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}

const CostTrendChart: React.FC<{ data: Array<{ date: string; cost: number; projected_cost?: number }> }> = ({ data }) => (
  <div className="bg-white p-6 rounded-lg shadow">
    <h3 className="text-lg font-medium text-gray-900 mb-4">Cost Trends</h3>
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => format(new Date(value), 'MM/dd')}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip 
            formatter={(value: number, name: string) => {
              if (name === 'projected_cost') {
                return [`$${value.toFixed(2)}`, 'Projected Cost']
              }
              return [`$${value.toFixed(2)}`, 'Actual Cost']
            }}
            labelFormatter={(label) => format(new Date(label), 'MMM dd, yyyy')}
          />
          <Area 
            type="monotone" 
            dataKey="cost" 
            stackId="1"
            stroke="#3B82F6" 
            fill="#3B82F6"
            fillOpacity={0.6}
          />
          <Area 
            type="monotone" 
            dataKey="projected_cost" 
            stackId="2"
            stroke="#8B5CF6" 
            fill="#8B5CF6"
            fillOpacity={0.4}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  </div>
)

const TopResourcesTable: React.FC<{ resources: Array<{ resource_id: string; resource_name: string; cost: number; percentage: number }> }> = ({ resources }) => (
  <div className="bg-white shadow rounded-lg">
    <div className="px-4 py-5 sm:p-6">
      <h3 className="text-lg leading-6 font-medium text-gray-900 mb-4">
        Top Cost Resources
      </h3>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Resource
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Cost
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                % of Total
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {resources.map((resource) => (
              <tr key={resource.resource_id}>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div>
                    <div className="text-sm font-medium text-gray-900">{resource.resource_name}</div>
                    <div className="text-sm text-gray-500">{resource.resource_id}</div>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${resource.cost.toFixed(2)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                      <div
                        className="bg-indigo-600 h-2 rounded-full"
                        style={{ width: `${resource.percentage}%` }}
                      ></div>
                    </div>
                    <span className="text-sm text-gray-900">{resource.percentage.toFixed(1)}%</span>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  </div>
)

const Reports: React.FC = () => {
  const [dateRange, setDateRange] = useState({
    startDate: format(startOfMonth(new Date()), 'yyyy-MM-dd'),
    endDate: format(endOfMonth(new Date()), 'yyyy-MM-dd')
  })

  const [reportType, setReportType] = useState<'cost' | 'optimization'>('cost')

  const { data: costReport, isLoading: costLoading, refetch: refetchCost } = useQuery(
    ['costReport', dateRange],
    () => fetchCostReport(dateRange.startDate, dateRange.endDate),
    { enabled: reportType === 'cost' }
  )

  const { data: optimizationReport, isLoading: optimizationLoading, refetch: refetchOptimization } = useQuery(
    ['optimizationReport', dateRange],
    () => fetchOptimizationReport(dateRange.startDate, dateRange.endDate),
    { enabled: reportType === 'optimization' }
  )

  const handleExportReport = () => {
    const reportData = reportType === 'cost' ? costReport : optimizationReport
    if (!reportData) return

    const dataStr = JSON.stringify(reportData, null, 2)
    const dataUri = 'data:application/json;charset=utf-8,'+ encodeURIComponent(dataStr)
    
    const exportFileDefaultName = `${reportType}-report-${dateRange.startDate}-to-${dateRange.endDate}.json`
    
    const linkElement = document.createElement('a')
    linkElement.setAttribute('href', dataUri)
    linkElement.setAttribute('download', exportFileDefaultName)
    linkElement.click()
  }

  const isLoading = (reportType === 'cost' && costLoading) || (reportType === 'optimization' && optimizationLoading)

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Report Controls */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-2xl font-bold text-gray-900">Reports & Analytics</h2>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleExportReport}
                className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <Download className="h-4 w-4 mr-2" />
                Export Report
              </button>
              <button
                onClick={() => {
                  if (reportType === 'cost') refetchCost()
                  else refetchOptimization()
                }}
                className="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </button>
            </div>
          </div>

          {/* Report Type and Date Range */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Report Type</label>
              <select
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                value={reportType}
                onChange={(e) => setReportType(e.target.value as 'cost' | 'optimization')}
              >
                <option value="cost">Cost Analysis Report</option>
                <option value="optimization">Optimization Report</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
              <input
                type="date"
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                value={dateRange.startDate}
                onChange={(e) => setDateRange({...dateRange, startDate: e.target.value})}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">End Date</label>
              <input
                type="date"
                className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
                value={dateRange.endDate}
                onChange={(e) => setDateRange({...dateRange, endDate: e.target.value})}
              />
            </div>
          </div>
        </div>
      </div>

      {reportType === 'cost' && costReport && (
        <>
          {/* Cost Report Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <ReportCard
              title="Total Cost"
              value={`$${costReport.total_cost.toLocaleString()}`}
              subtitle={costReport.period}
              icon={DollarSign}
              color="text-red-600"
            />
            <ReportCard
              title="Potential Savings"
              value={`$${costReport.savings_opportunities.total_potential_savings.toLocaleString()}`}
              subtitle="optimization opportunities"
              icon={TrendingDown}
              color="text-green-600"
            />
            <ReportCard
              title="Implemented Savings"
              value={`$${costReport.savings_opportunities.implemented_savings.toLocaleString()}`}
              subtitle="already realized"
              icon={CheckCircle}
              color="text-blue-600"
            />
            <ReportCard
              title="Top Resource Cost"
              value={`$${costReport.top_cost_resources[0]?.cost.toFixed(2) || '0.00'}`}
              subtitle={costReport.top_cost_resources[0]?.resource_name || 'N/A'}
              icon={Server}
              color="text-purple-600"
            />
          </div>

          {/* Cost Analysis Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CostBreakdownChart data={costReport.cost_by_provider} title="Cost by Provider" />
            <CostBreakdownChart data={costReport.cost_by_service} title="Cost by Service" />
          </div>

          {/* Cost Trends and Top Resources */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <CostTrendChart data={costReport.cost_trends} />
            <TopResourcesTable resources={costReport.top_cost_resources} />
          </div>
        </>
      )}

      {reportType === 'optimization' && optimizationReport && (
        <>
          {/* Optimization Report Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <ReportCard
              title="Total Recommendations"
              value={optimizationReport.total_recommendations.toString()}
              subtitle="optimization opportunities"
              icon={AlertTriangle}
              color="text-orange-600"
            />
            <ReportCard
              title="Implemented"
              value={optimizationReport.implemented_recommendations.toString()}
              subtitle={`${((optimizationReport.implemented_recommendations / optimizationReport.total_recommendations) * 100).toFixed(1)}% success rate`}
              icon={CheckCircle}
              color="text-green-600"
            />
            <ReportCard
              title="Potential Savings"
              value={`$${optimizationReport.total_potential_savings.toLocaleString()}`}
              subtitle="total opportunity"
              icon={TrendingUp}
              color="text-blue-600"
            />
            <ReportCard
              title="Realized Savings"
              value={`$${optimizationReport.total_realized_savings.toLocaleString()}`}
              subtitle="already implemented"
              icon={DollarSign}
              color="text-purple-600"
            />
          </div>

          {/* Optimization Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Recommendations by Type</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={Object.entries(optimizationReport.recommendations_by_type).map(([type, count]) => ({ type: type.replace('_', ' '), count }))}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="type" tick={{ fontSize: 12 }} />
                    <YAxis tick={{ fontSize: 12 }} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#3B82F6" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="bg-white p-6 rounded-lg shadow">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Recommendations by Risk Level</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={Object.entries(optimizationReport.recommendations_by_risk).map(([risk, count]) => ({ name: risk, value: count }))}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {Object.entries(optimizationReport.recommendations_by_risk).map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={['#10B981', '#F59E0B', '#EF4444', '#7C3AED'][index % 4]} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>

          {/* Monthly Trends */}
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Monthly Optimization Trends</h3>
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={optimizationReport.monthly_trends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 12 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="recommendations" stroke="#3B82F6" strokeWidth={2} name="Recommendations" />
                  <Line type="monotone" dataKey="implemented" stroke="#10B981" strokeWidth={2} name="Implemented" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default Reports

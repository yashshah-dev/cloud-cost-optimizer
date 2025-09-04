// Test script to verify chart data merging logic

// Mock data similar to what the APIs return
const mockCostSummary = {
  daily_costs: [
    { date: "2025-09-01", cost: 130 },
    { date: "2025-09-02", cost: 135 },
    { date: "2025-09-03", cost: 140 },
    { date: "2025-09-04", cost: 143 },
  ]
}

const mockAiTrends = [
  { date: "2025-09-04", actual_cost: 100, predicted_cost: 105, ai_insight: "Stable spending pattern" },
  { date: "2025-09-05", actual_cost: 88, predicted_cost: 93, ai_insight: "Potential optimization opportunity" },
  { date: "2025-09-06", actual_cost: 91, predicted_cost: 96, ai_insight: "Stable spending pattern" }
]

// Chart data merger logic (same as in Dashboard.tsx)
function mergeChartData(costSummary, aiTrends) {
  if (!costSummary?.daily_costs) return []
  
  // Create a map of AI predictions by date for faster lookup
  const aiPredictionMap = new Map()
  if (aiTrends && aiTrends.length > 0) {
    aiTrends.forEach(trend => {
      aiPredictionMap.set(trend.date, trend)
    })
  }
  
  // Merge the data
  const merged = costSummary.daily_costs.map(dailyCost => {
    const aiPrediction = aiPredictionMap.get(dailyCost.date)
    return {
      date: dailyCost.date,
      cost: dailyCost.cost,
      predicted_cost: aiPrediction?.predicted_cost || null,
      ai_insight: aiPrediction?.ai_insight || null
    }
  })
  
  return merged
}

// Test the merger
const chartData = mergeChartData(mockCostSummary, mockAiTrends)

console.log('=== Chart Data Merge Test ===')
console.log('Input - Cost Summary entries:', mockCostSummary.daily_costs.length)
console.log('Input - AI Trends entries:', mockAiTrends.length)
console.log('Output - Merged entries:', chartData.length)
console.log('Output - Entries with predictions:', chartData.filter(d => d.predicted_cost !== null).length)
console.log('\n=== Merged Data ===')
chartData.forEach((entry, index) => {
  console.log(`${index + 1}. ${entry.date}: cost=$${entry.cost}, predicted=${entry.predicted_cost || 'null'}, insight=${entry.ai_insight || 'null'}`)
})

// Expected result:
// - 4 total entries (matching cost summary)
// - 1 entry should have prediction (Sep 4, which exists in both datasets)
// - 3 entries should have null predictions (Sep 1-3, which only exist in cost summary)

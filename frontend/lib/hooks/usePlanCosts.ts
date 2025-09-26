import { useState, useEffect } from 'react'
import { apiService } from '../api'

export interface CostBreakdown {
  server_cost: number
  ai_cost: number
  email_cost: number
  domain_cost: number
  total_cost: number
}

export interface PlanCost {
  name: string
  price: number
  currency: string
  cost_breakdown: CostBreakdown
  profit_margin: number
}

export interface PlanCostsResponse {
  cost_analysis: PlanCost[]
}

export const usePlanCosts = () => {
  const [costs, setCosts] = useState<PlanCost[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchCosts = async () => {
      try {
        setLoading(true)
        setError(null)
        const response: PlanCostsResponse = await apiService.getPlanCosts()
        setCosts(response.cost_analysis || [])
      } catch (err) {
        console.error('Plan costs yüklenirken hata:', err)
        setError('Maliyet bilgileri yüklenirken bir hata oluştu')
        setCosts([
          {
            name: "Free",
            price: 0,
            currency: "USD",
            cost_breakdown: {
              server_cost: 0,
              ai_cost: 0,
              email_cost: 0,
              domain_cost: 0,
              total_cost: 0
            },
            profit_margin: 0
          },
          {
            name: "Starter",
            price: 29,
            currency: "USD",
            cost_breakdown: {
              server_cost: 5.0,
              ai_cost: 3.0,
              email_cost: 2.0,
              domain_cost: 0.1,
              total_cost: 10.1
            },
            profit_margin: 65.2
          },
          {
            name: "Professional",
            price: 79,
            currency: "USD",
            cost_breakdown: {
              server_cost: 15.0,
              ai_cost: 12.0,
              email_cost: 8.0,
              domain_cost: 0.1,
              total_cost: 35.1
            },
            profit_margin: 55.6
          },
          {
            name: "Enterprise",
            price: 199,
            currency: "USD",
            cost_breakdown: {
              server_cost: 40.0,
              ai_cost: 30.0,
              email_cost: 25.0,
              domain_cost: 0.1,
              total_cost: 95.1
            },
            profit_margin: 52.2
          }
        ])
      } finally {
        setLoading(false)
      }
    }

    fetchCosts()
  }, [])

  return { costs, loading, error }
}

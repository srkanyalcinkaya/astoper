import { useState, useEffect } from 'react'
import { apiService } from '../api'

export interface Plan {
  _id: string
  name: string
  price: number
  currency: string
  max_queries_per_month: number
  max_file_uploads: number
  max_results_per_query: number
  max_emails_per_month: number
  max_templates: number
  max_file_size_mb: number
  features: string[]
  is_active: boolean
  cost_breakdown?: {
    server_cost: number
    ai_cost: number
    email_cost: number
    domain_cost: number
    total_cost: number
  }
}

export interface PlansResponse {
  plans: Plan[]
}

export const usePlans = () => {
  const [plans, setPlans] = useState<Plan[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        setLoading(true)
        setError(null)
        const response: PlansResponse = await apiService.getPlans()
        setPlans(response.plans || [])
      } catch (err) {
        console.error('Plans yüklenirken hata:', err)
        setError('Planlar yüklenirken bir hata oluştu')
        setPlans([
          {
            _id: '1',
            name: 'Free',
            price: 0,
            currency: 'USD',
            max_queries_per_month: 1,
            max_file_uploads: 1,
            max_results_per_query: 10,
            max_emails_per_month: 10,
            max_templates: 1,
            max_file_size_mb: 5,
            features: ['1 monthly query', '10 results per query', '1 file upload', '10 emails/month', '1 template', '5MB file size'],
            is_active: true,
            cost_breakdown: {
              server_cost: 0,
              ai_cost: 0,
              email_cost: 0,
              domain_cost: 0,
              total_cost: 0
            }
          },
          {
            _id: '2',
            name: 'Starter',
            price: 29,
            currency: 'USD',
            max_queries_per_month: 10,
            max_file_uploads: 10,
            max_results_per_query: 100,
            max_emails_per_month: 500,
            max_templates: 5,
            max_file_size_mb: 10,
            features: [
              '10 monthly queries', 
              '100 results per query',
              '10 file uploads',
              '500 emails/month',
              '5 templates',
              '10MB file size',
              'SerpAPI integration',
              'Priority support', 
              'Basic analytics', 
              'CSV export'
            ],
            is_active: true,
            cost_breakdown: {
              server_cost: 5.0,
              ai_cost: 3.0,
              email_cost: 2.0,
              domain_cost: 0.1,
              total_cost: 10.1
            }
          },
          {
            _id: '3',
            name: 'Professional',
            price: 79,
            currency: 'USD',
            max_queries_per_month: 50,
            max_file_uploads: 50,
            max_results_per_query: 250,
            max_emails_per_month: 2500,
            max_templates: 20,
            max_file_size_mb: 25,
            features: [
              '50 monthly queries',
              '250 results per query',
              '50 file uploads',
              '2500 emails/month',
              '20 templates',
              '25MB file size',
              'API access',
              '24/7 live support',
              'Advanced analytics',
              'White-label option',
              'Custom integrations'
            ],
            is_active: true,
            cost_breakdown: {
              server_cost: 15.0,
              ai_cost: 12.0,
              email_cost: 8.0,
              domain_cost: 0.1,
              total_cost: 35.1
            }
          },
          {
            _id: '4',
            name: 'Enterprise',
            price: 199,
            currency: 'USD',
            max_queries_per_month: 250,
            max_file_uploads: 250,
            max_results_per_query: 500,
            max_emails_per_month: 10000,
            max_templates: 100,
            max_file_size_mb: 100,
            features: [
              '250 monthly queries',
              '500 results per query',
              '250 file uploads',
              '10000 emails/month',
              '100 templates',
              '100MB file size',
              'Unlimited features',
              'Custom API limits',
              'Dedicated account manager',
              'Custom reporting',
              'SLA guarantee',
              'Custom development'
            ],
            is_active: true,
            cost_breakdown: {
              server_cost: 40.0,
              ai_cost: 30.0,
              email_cost: 25.0,
              domain_cost: 0.1,
              total_cost: 95.1
            }
          }
        ])
      } finally {
        setLoading(false)
      }
    }

    fetchPlans()
  }, [])

  return { plans, loading, error }
}

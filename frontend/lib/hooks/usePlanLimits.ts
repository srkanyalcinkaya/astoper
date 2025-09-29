import { useState, useEffect } from 'react'
import { api } from '@/lib/api'

interface PlanLimits {
  email_limit: {
    can_send: boolean
    remaining: number
    used: number
    limit: number
  }
  template_limit: {
    can_create: boolean
    remaining: number
    used: number
    limit: number
  }
  query_limit: {
    can_query: boolean
    remaining: number
    used: number
    limit: number
  }
  file_limit: {
    can_upload: boolean
    remaining: number
    used: number
    limit: number
  }
  plan_name: string
  plan_price: number
}

export function usePlanLimits() {
  const [limits, setLimits] = useState<PlanLimits | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchLimits = async () => {
    try {
      setLoading(true)
      const response = await api.get('/plans/limits')
      setLimits(response.data)
      setError(null)
    } catch (err: any) {
      console.error('Plan limitleri yüklenemedi:', err)
      setError(err.response?.data?.detail || 'Plan limitleri yüklenemedi')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchLimits()
  }, [])

  return {
    limits,
    loading,
    error,
    refetch: fetchLimits
  }
}

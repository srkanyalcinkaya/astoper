import axios from 'axios'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  },
})

let isRedirecting = false

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
      console.log('Token added to request:', token.substring(0, 20) + '...')
    } else {
      console.warn('No token found in localStorage')
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const token = localStorage.getItem('access_token')
      if (token && typeof window !== 'undefined') {
        localStorage.removeItem('access_token')
        
        try {
          const { useAppStore } = await import('./store')
          useAppStore.getState().logout()
        } catch (e) {
          console.error('Error clearing store:', e)
        }
      }
    }
    return Promise.reject(error)
  }
)

export const apiService = {
  async get(url: string, config?: any) {
    const response = await api.get(url, config)
    return response.data
  },

  async post(url: string, data?: any, config?: any) {
    const response = await api.post(url, data, config)
    return response.data
  },

  async put(url: string, data?: any, config?: any) {
    const response = await api.put(url, data, config)
    return response.data
  },

  async delete(url: string, config?: any) {
    const response = await api.delete(url, config)
    return response.data
  },

  async getDashboardData() {
    const response = await api.get('/users/dashboard')
    return response.data
  },

  async getAutomations() {
    const response = await api.get('/automation/')
    return response.data
  },

  async getAutomationStats() {
    const response = await api.get('/automation/stats')
    return response.data
  },

  async createAutomation(data: {
    automation_type: 'search' | 'file'
    search_queries?: string[]
    target_urls?: string[]
    file_id?: string
    use_serpapi: boolean
    selected_emails?: string[]
    template_id?: string
    ai_template_prompt?: string
    custom_data?: Record<string, any>
  }) {
    const response = await api.post('/automation/', data)
    return response.data
  },

  async searchEmails(data: {
    search_queries?: string[]
    target_urls?: string[]
    use_serpapi: boolean
    max_results?: number
  }) {
    const response = await api.post('/automation/search-emails', data)
    return response.data
  },

  async getAutomation(queryId: string) {
    const response = await api.get(`/automation/${queryId}`)
    return response.data
  },

  async getAutomationLogs() {
    const response = await api.get('/automation/user-logs')
    return response.data
  },

  async getLogsStats() {
    const response = await api.get('/automation/logs/stats')
    return response.data
  },

  async getFiles() {
    const response = await api.get('/files/')
    return response.data
  },

  async uploadFile(file: File) {
    const formData = new FormData()
    formData.append('file', file)
    
    const response = await api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async deleteFile(fileId: string) {
    const response = await api.delete(`/files/${fileId}`)
    return response.data
  },

  async getFileStats() {
    const response = await api.get('/files/stats/summary')
    return response.data
  },

  async getAnalytics() {
    const response = await api.get('/users/analytics')
    return response.data
  },

  async getUserProfile() {
    const response = await api.get('/users/me')
    return response.data
  },

  async updateUserProfile(data: {
    email?: string
    full_name?: string
  }) {
    const response = await api.put('/users/me', data)
    return response.data
  },

  async getSubscription() {
    const response = await api.get('/subscriptions/')
    return response.data
  },

  async getPlans() {
    const response = await api.get('/plans/')
    return response.data
  },

  async getPlanCosts() {
    const response = await api.get('/plans/costs')
    return response.data
  },


  async getSubscriptionUsage() {
    const response = await api.get('/subscriptions/usage')
    return response.data
  },

  async getEmailProviders() {
    const response = await api.get('/email-providers/')
    return response.data
  },

  async createEmailProvider(data: {
    provider_name: 'gmail' | 'outlook' | 'yahoo' | 'custom'
    email_address: string
    smtp_config?: {
      host: string
      port: number
      username: string
      password: string
      use_ssl: boolean
      use_tls: boolean
    }
  }) {
    const response = await api.post('/email-providers/', data)
    return response.data
  },

  async testEmailProvider(providerId: string) {
    const response = await api.post(`/email-providers/${providerId}/test`)
    return response.data
  },

  async deleteEmailProvider(providerId: string) {
    const response = await api.delete(`/email-providers/${providerId}`)
    return response.data
  },

  async getProviderInfo() {
    const response = await api.get('/email-providers/providers/info')
    return response.data
  },

  async createCheckoutSession(data: {
    plan_id: string
  }) {
    const response = await api.post('/subscriptions/create-checkout-session', data)
    return response.data
  },

  async upgradeSubscription(new_plan_id: string) {
    const response = await api.post('/subscriptions/upgrade-subscription', { new_plan_id })
    return response.data
  },

  async cancelSubscription() {
    const response = await api.post('/subscriptions/cancel-subscription')
    return response.data
  },

  async getBillingHistory() {
    const response = await api.get('/subscriptions/billing-history')
    return response.data
  },

  async getTemplates() {
    const response = await api.get('/templates/')
    return response.data
  },

  async getDefaultTemplates() {
    const response = await api.get('/templates/default')
    return response.data
  },

  async createTemplate(data: {
    name: string
    subject: string
    content: string
    category?: string
  }) {
    const response = await api.post('/templates/', data)
    return response.data
  },

  async generateAITemplate(data: {
    prompt: string
    template_name: string
    category?: string
  }) {
    const response = await api.post('/templates/ai-generate', data)
    return response.data
  },

  async updateTemplate(templateId: string, data: {
    name?: string
    subject?: string
    content?: string
    category?: string
  }) {
    const response = await api.put(`/templates/${templateId}`, data)
    return response.data
  },

  async deleteTemplate(templateId: string) {
    const response = await api.delete(`/templates/${templateId}`)
    return response.data
  },

  async uploadTemplate(formData: FormData) {
    const response = await api.post('/templates/upload-template', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  async previewTemplate(templateId: string) {
    const response = await api.get(`/templates/preview/${templateId}`)
    return response.data
  },

  async getTemplate(templateId: string) {
    const response = await api.get(`/templates/${templateId}`)
    return response.data
  },

  async extractEmailsFromFile(fileId: string) {
    const response = await api.post(`/files/${fileId}/extract-emails`)
    return response.data
  },

  async serpSearch(data: {
    query: string
    target_url?: string
    max_results?: number
  }) {
    const response = await api.post('/search/serp-search', data)
    return response.data
  },

  async extractEmailsFromUrls(data: {
    urls: string[]
  }) {
    const response = await api.post('/search/extract-emails', data)
    return response.data
  },

  async getSearchHistory(limit?: number) {
    const response = await api.get(`/search/history${limit ? `?limit=${limit}` : ''}`)
    return response.data
  },

  async getSearchStats() {
    const response = await api.get('/search/stats')
    return response.data
  },

  async googleLogin(token: string) {
    const response = await api.post('/auth/google/login', { token })
    return response.data
  },

  async linkGoogleAccount(token: string) {
    const response = await api.post('/auth/google/link-account', { token })
    return response.data
  },

  async getEmailTrackingStats(startDate?: string, endDate?: string) {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    
    const response = await api.get(`/email-sending/tracking/stats?${params}`)
    return response.data
  },

  async getEmailTrackingHistory(limit?: number, offset?: number, status?: string) {
    const params = new URLSearchParams()
    if (limit) params.append('limit', limit.toString())
    if (offset) params.append('offset', offset.toString())
    if (status) params.append('status', status)
    
    const response = await api.get(`/email-sending/tracking/history?${params}`)
    return response.data
  },

  async getUserLimits() {
    const response = await api.get('/email-sending/limits')
    return response.data
  },
}

export { api }
export default api


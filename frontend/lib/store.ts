import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface User {
  id: string
  username: string
  email: string
  full_name?: string
  is_active: boolean
  created_at: string
}

export interface Plan {
  _id: string
  name: string
  price: number
  max_queries_per_month: number
  max_file_uploads: number
  features: string[]
}

export interface Subscription {
  id: string
  status: 'active' | 'cancelled' | 'past_due' | 'incomplete'
  current_period_end: string
  plan: Plan
  payment_method?: any
}

export interface Automation {
  _id: string
  search_terms?: string
  target_urls: string[]
  status: 'pending' | 'running' | 'completed' | 'failed'
  created_at: string
  completed_at?: string
  results?: any
}

export interface FileUpload {
  _id: string
  filename: string
  file_type: string
  file_size: number
  upload_date: string
  status: 'uploaded' | 'processing' | 'processed' | 'failed'
}

interface AppState {
  // Auth state
  user: User | null
  isAuthenticated: boolean
  
  // Subscription state
  subscription: Subscription | null
  
  // App data
  automations: Automation[]
  files: FileUpload[]
  
  // UI state
  isLoading: boolean
  error: string | null
  
  // Actions
  setUser: (user: User | null) => void
  setSubscription: (subscription: Subscription | null) => void
  setAutomations: (automations: Automation[]) => void
  addAutomation: (automation: Automation) => void
  setFiles: (files: FileUpload[]) => void
  addFile: (file: FileUpload) => void
  setLoading: (loading: boolean) => void
  setError: (error: string | null) => void
  logout: () => void
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      // Initial state
      user: null,
      isAuthenticated: false,
      subscription: null,
      automations: [],
      files: [],
      isLoading: false,
      error: null,
      
      // Actions
      setUser: (user) => set({ user, isAuthenticated: !!user }),
      setSubscription: (subscription) => set({ subscription }),
      setAutomations: (automations) => set({ automations }),
      addAutomation: (automation) => set((state) => ({ 
        automations: [automation, ...state.automations] 
      })),
      setFiles: (files) => set({ files }),
      addFile: (file) => set((state) => ({ 
        files: [file, ...state.files] 
      })),
      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
      logout: () => {
        localStorage.removeItem('access_token')
        set({ 
          user: null, 
          isAuthenticated: false, 
          subscription: null,
          automations: [],
          files: []
        })
      }
    }),
    {
      name: 'email-automation-store',
      partialize: (state) => ({ 
        user: state.user, 
        isAuthenticated: state.isAuthenticated,
        subscription: state.subscription 
      }),
    }
  )
)


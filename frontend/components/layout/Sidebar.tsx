'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import { useAppStore } from '@/lib/store'

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: '📊' },
    { name: 'Arama Motoru', href: '/search', icon: '🔍' },
    { name: 'Dosya Otomasyonu', href: '/files', icon: '📁' },
    { name: 'Email Şablonları', href: '/templates', icon: '📝' },
    { name: 'Email Provider\'lar', href: '/email-providers', icon: '🔐' },
    { name: 'Email Takibi', href: '/email-tracking', icon: '📧' },
    { name: 'Planlar', href: '/plans', icon: '💎' },
    { name: 'Abonelik Yönetimi', href: '/subscription/manage', icon: '⚙️' },
    { name: 'Analitik', href: '/analytics', icon: '📈' },
    { name: 'Profil', href: '/profile', icon: '👤' },
  ]

export default function Sidebar() {
  const pathname = usePathname()
  const { user, logout } = useAppStore()

  const handleLogout = () => {
    logout()
    window.location.href = '/login'
  }

  return (
    <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0">
      <div className="flex flex-col flex-grow pt-5 bg-white border-r border-gray-200">
        <div className="flex items-center flex-shrink-0 px-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">A</span>
            </div>
            <span className="font-bold text-xl text-gray-900">Astoper</span>
          </div>
        </div>
        
        <div className="mt-8 flex-grow flex flex-col">
          <nav className="flex-1 px-2 space-y-1">
            {navigation.map((item) => {
              const isActive = pathname === item.href
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={cn(
                    'group flex items-center px-2 py-2 text-sm font-medium rounded-md transition-colors',
                    isActive
                      ? 'bg-blue-100 text-blue-900'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  )}
                >
                  <span className="mr-3 text-lg">{item.icon}</span>
                  {item.name}
                </Link>
              )
            })}
          </nav>
        </div>

        <div className="flex-shrink-0 p-4 border-t border-gray-200">
          <div className="flex items-center">
            <div className="flex-shrink-0">
              <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                <span className="text-sm font-medium text-gray-700">
                  {user?.full_name?.charAt(0).toUpperCase() || user?.email?.charAt(0).toUpperCase()}
                </span>
              </div>
            </div>
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-700">{user?.full_name || user?.email}</p>
              <p className="text-xs text-gray-500">{user?.email}</p>
            </div>
          </div>
          <Button 
            onClick={handleLogout}
            variant="outline" 
            size="sm" 
            className="w-full mt-3"
          >
            Çıkış Yap
          </Button>
        </div>
      </div>
    </div>
  )
}


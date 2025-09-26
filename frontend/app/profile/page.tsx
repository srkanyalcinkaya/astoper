'use client'

import { useState } from 'react'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { useAppStore } from '@/lib/store'
import { toast } from 'sonner'

export default function ProfilePage() {
  const { user, setUser } = useAppStore()
  const [isEditing, setIsEditing] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [formData, setFormData] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  const handleProfileUpdate = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)

    try {
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      setUser({
        ...user!,
        full_name: formData.full_name,
        email: formData.email
      })

      toast.success('Profil bilgileri güncellendi')
      setIsEditing(false)
    } catch (error) {
      toast.error('Profil güncellenemedi')
    } finally {
      setIsLoading(false)
    }
  }

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (formData.newPassword !== formData.confirmPassword) {
      toast.error('Yeni şifreler eşleşmiyor')
      return
    }

    if (formData.newPassword.length < 6) {
      toast.error('Yeni şifre en az 6 karakter olmalıdır')
      return
    }

    setIsLoading(true)

    try {
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      toast.success('Şifre başarıyla değiştirildi')
      setFormData(prev => ({
        ...prev,
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }))
    } catch (error) {
      toast.error('Şifre değiştirilemedi')
    } finally {
      setIsLoading(false)
    }
  }

  const handleAccountDeactivation = async () => {
    const confirmed = window.confirm(
      'Hesabınızı devre dışı bırakmak istediğinizden emin misiniz? Bu işlem geri alınamaz.'
    )

    if (!confirmed) return

    setIsLoading(true)

    try {
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      toast.success('Hesap devre dışı bırakıldı')
      window.location.href = '/login'
    } catch (error) {
      toast.error('Hesap devre dışı bırakılamadı')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Profil ve Ayarlar</h1>
          <p className="text-gray-600">
            Hesap bilgilerinizi yönetin ve güvenlik ayarlarınızı düzenleyin
          </p>
        </div>

        {/* Profile Information */}
        <Card>
          <CardHeader>
            <CardTitle>Kişisel Bilgiler</CardTitle>
            <CardDescription>
              Hesap bilgilerinizi görüntüleyin ve düzenleyin
            </CardDescription>
          </CardHeader>
          <CardContent>
            {!isEditing ? (
              <div className="space-y-4">
                <div className="flex items-center space-x-4">
                  <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-2xl font-bold text-blue-600">
                      {user?.email?.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <h3 className="text-lg font-medium">{user?.full_name || 'Ad Soyad Belirtilmemiş'}</h3>
                    <p className="text-gray-500">{user?.email}</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Email</label>
                    <p className="mt-1 text-sm text-gray-900">{user?.email}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Ad Soyad</label>
                    <p className="mt-1 text-sm text-gray-900">{user?.full_name || 'Belirtilmemiş'}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Hesap Durumu</label>
                    <p className="mt-1 text-sm">
                      <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                        Aktif
                      </span>
                    </p>
                  </div>
                </div>

                <Button onClick={() => setIsEditing(true)} className="mt-4">
                  Bilgileri Düzenle
                </Button>
              </div>
            ) : (
              <form onSubmit={handleProfileUpdate} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                      Email
                    </label>
                    <Input
                      id="email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>
                
                <div>
                  <label htmlFor="full_name" className="block text-sm font-medium text-gray-700 mb-2">
                    Ad Soyad
                  </label>
                  <Input
                    id="full_name"
                    name="full_name"
                    value={formData.full_name}
                    onChange={handleChange}
                  />
                </div>

                <div className="flex space-x-4">
                  <Button type="submit" disabled={isLoading}>
                    {isLoading ? 'Güncelleniyor...' : 'Değişiklikleri Kaydet'}
                  </Button>
                  <Button 
                    type="button" 
                    variant="outline" 
                    onClick={() => setIsEditing(false)}
                  >
                    İptal
                  </Button>
                </div>
              </form>
            )}
          </CardContent>
        </Card>

        {/* Password Change */}
        <Card>
          <CardHeader>
            <CardTitle>Şifre Değiştir</CardTitle>
            <CardDescription>
              Hesabınızın güvenliği için şifrenizi düzenli olarak değiştirin
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handlePasswordChange} className="space-y-4">
              <div>
                <label htmlFor="currentPassword" className="block text-sm font-medium text-gray-700 mb-2">
                  Mevcut Şifre
                </label>
                <Input
                  id="currentPassword"
                  name="currentPassword"
                  type="password"
                  value={formData.currentPassword}
                  onChange={handleChange}
                  required
                />
              </div>
              
              <div>
                <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700 mb-2">
                  Yeni Şifre
                </label>
                <Input
                  id="newPassword"
                  name="newPassword"
                  type="password"
                  value={formData.newPassword}
                  onChange={handleChange}
                  required
                />
              </div>
              
              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-2">
                  Yeni Şifre Tekrar
                </label>
                <Input
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  required
                />
              </div>

              <Button type="submit" disabled={isLoading}>
                {isLoading ? 'Değiştiriliyor...' : 'Şifreyi Değiştir'}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* API Keys */}
        <Card>
          <CardHeader>
            <CardTitle>API Anahtarları</CardTitle>
            <CardDescription>
              Üçüncü taraf entegrasyonlar için API anahtarlarınızı yönetin
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  API Anahtarı
                </label>
                <div className="flex space-x-2">
                  <Input 
                    value="ea_xxxxxxxxxxxxxxxxxxxxxxxx" 
                    readOnly 
                    className="font-mono text-sm"
                  />
                  <Button variant="outline">Kopyala</Button>
                  <Button variant="outline">Yenile</Button>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  API anahtarınızı güvenli bir yerde saklayın ve kimseyle paylaşmayın
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Account Actions */}
        <Card className="border-red-200">
          <CardHeader>
            <CardTitle className="text-red-600">Tehlikeli Bölge</CardTitle>
            <CardDescription>
              Geri alınamaz hesap işlemleri
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium text-red-600">Hesabı Devre Dışı Bırak</h4>
                <p className="text-sm text-gray-600 mb-3">
                  Hesabınızı kalıcı olarak devre dışı bırakır. Bu işlem geri alınamaz.
                </p>
                <Button 
                  variant="destructive"
                  onClick={handleAccountDeactivation}
                  disabled={isLoading}
                >
                  Hesabı Devre Dışı Bırak
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}


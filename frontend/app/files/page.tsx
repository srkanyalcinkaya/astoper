'use client'

import { useState, useEffect, useRef } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Upload, FileText, Mail, Send, CheckCircle, AlertCircle, Download, Trash2 } from 'lucide-react'
import { useAuth } from '@/lib/hooks/useAuth'
import { api } from '@/lib/api'
import DashboardLayout from '@/components/layout/DashboardLayout'

interface FileUpload {
  _id: string
  filename: string
  file_type: string
  file_size: number
  upload_date: string
  status: string
  processed_data?: {
    emails_found: number
    categories: string[]
  }
}

interface EmailResult {
  email: string
  category: string
  confidence: number
  website_url?: string
  company_name?: string
  industry?: string
}

export default function FilesPage() {
  const { user } = useAuth()
  const [files, setFiles] = useState<FileUpload[]>([])
  const [selectedFile, setSelectedFile] = useState<FileUpload | null>(null)
  const [emails, setEmails] = useState<EmailResult[]>([])
  const [selectedEmails, setSelectedEmails] = useState<string[]>([])
  const [templates, setTemplates] = useState<any[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState('')
  const [providers, setProviders] = useState<any[]>([])
  const [selectedProvider, setSelectedProvider] = useState('')
  const [customData, setCustomData] = useState<Record<string, string>>({
    company_name: 'Astoper',
    company_tagline: 'Dijital Dönüşüm Partneriniz',
    email: 'syalcinkaya895@gmail.com',
    phone: '+90 XXX XXX XX XX',
    website_url: 'https://www.astoper.com',
    greeting_message: 'Şirketinizin dijital varlığını güçlendirmek için profesyonel web tasarım hizmetlerimizi sunuyoruz.',
    service_1: 'Modern ve responsive web tasarımı',
    service_2: 'SEO optimizasyonu',
    service_3: 'E-ticaret çözümleri',
    service_4: 'Web sitesi bakım ve güncelleme',
    offer_title: 'Ücretsiz Danışmanlık',
    offer_description: 'Projeniz için detaylı analiz ve teklif sunuyoruz'
  })
  const [isUploading, setIsUploading] = useState(false)
  const [isExtracting, setIsExtracting] = useState(false)
  const [isStartingAutomation, setIsStartingAutomation] = useState(false)
  const [isSendingEmails, setIsSendingEmails] = useState(false)
  const [automationStatus, setAutomationStatus] = useState('')
  const [emailSendingStatus, setEmailSendingStatus] = useState('')
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    loadFiles()
    loadTemplates()
    loadProviders()
  }, [])

  const loadFiles = async () => {
    try {
      const response = await api.get('/files/')
      setFiles(response.data)
    } catch (error) {
      console.error('Dosya yükleme hatası:', error)
    }
  }

  const loadTemplates = async () => {
    try {
      const response = await api.get('/templates/')
      setTemplates(response.data)
    } catch (error) {
      console.error('Şablon yükleme hatası:', error)
    }
  }

  const loadProviders = async () => {
    try {
      const response = await api.get('/email-providers/')
      setProviders(response.data)
    } catch (error) {
      console.error('Email provider yükleme hatası:', error)
    }
  }

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setIsUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await api.post('/files/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      setFiles(prev => [response.data, ...prev])
      setSelectedFile(response.data)
    } catch (error) {
      console.error('Dosya yükleme hatası:', error)
      alert('Dosya yüklenemedi. Lütfen tekrar deneyin.')
    } finally {
      setIsUploading(false)
    }
  }

  const extractEmails = async (fileId: string) => {
    setIsExtracting(true)
    try {
      const response = await api.post(`/files/${fileId}/extract-emails`)
      setEmails(response.data.emails || [])
    } catch (error) {
      console.error('Email çıkarma hatası:', error)
      alert('Email adresleri çıkarılamadı. Lütfen tekrar deneyin.')
    } finally {
      setIsExtracting(false)
    }
  }

  const toggleEmailSelection = (email: string) => {
    setSelectedEmails(prev => 
      prev.includes(email) 
        ? prev.filter(e => e !== email)
        : [...prev, email]
    )
  }

  const toggleAllEmails = () => {
    if (selectedEmails.length === emails.length) {
      setSelectedEmails([])
    } else {
      setSelectedEmails(emails.map(e => e.email))
    }
  }

  const deleteFile = async (fileId: string) => {
    if (!confirm('Bu dosyayı silmek istediğinizden emin misiniz?')) return

    try {
      await api.delete(`/files/${fileId}`)
      setFiles(prev => prev.filter(f => f._id !== fileId))
      if (selectedFile?._id === fileId) {
        setSelectedFile(null)
        setEmails([])
        setSelectedEmails([])
      }
    } catch (error) {
      console.error('Dosya silme hatası:', error)
    }
  }

  const startAutomation = async () => {
    if (!selectedFile) {
      alert('Bir dosya seçmelisiniz')
      return
    }

    if (selectedEmails.length === 0) {
      alert('En az bir email seçmelisiniz')
      return
    }

    if (!selectedTemplate) {
      alert('Bir şablon seçmelisiniz')
      return
    }

    setIsStartingAutomation(true)
    try {
      const response = await api.post('/automation/', {
        automation_type: 'file',
        file_id: selectedFile._id,
        selected_emails: selectedEmails,
        template_id: selectedTemplate
      })

      setAutomationStatus('Otomasyon başlatıldı! Email gönderimi arka planda devam ediyor.')
    } catch (error) {
      console.error('Otomasyon hatası:', error)
      setAutomationStatus('Otomasyon başlatılamadı. Lütfen tekrar deneyin.')
    } finally {
      setIsStartingAutomation(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }


  const sendBulkEmails = async () => {
    if (!selectedTemplate || !selectedProvider || selectedEmails.length === 0) {
      alert('Lütfen şablon, email provider ve gönderilecek email adreslerini seçin')
      return
    }

    setIsSendingEmails(true)
    setEmailSendingStatus('')

    try {
      const response = await api.post('/email-sending/send-bulk', {
        provider_id: selectedProvider,
        template_id: selectedTemplate,
        recipient_emails: selectedEmails,
        custom_data: customData,
        delay_between_emails: 1.0
      })

      const { successful, failed, total_emails } = response.data
      setEmailSendingStatus(`${successful}/${total_emails} email başarıyla gönderildi. ${failed} başarısız.`)
    } catch (error: any) {
      console.error('Toplu email gönderme hatası:', error)
      setEmailSendingStatus(`Hata: ${error.response?.data?.detail || 'Bilinmeyen hata'}`)
    } finally {
      setIsSendingEmails(false)
    }
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Dosya Otomasyonu</h1>
          <p className="text-gray-600">Dosyalarınızdan email adreslerini çıkarın ve otomatik gönderim yapın</p>
        </div>

        <div className="space-y-6">
          {/* Dosya Yükleme */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Upload className="w-5 h-5" />
                Dosya Yükle
              </CardTitle>
              <CardDescription>
                Excel, CSV, PDF veya Word dosyalarınızı yükleyin
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <input
                  ref={fileInputRef}
                  type="file"
                  onChange={handleFileUpload}
                  accept=".xlsx,.csv,.pdf,.docx"
                  className="hidden"
                />
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Dosya Yüklemek İçin Tıklayın
                </h3>
                <p className="text-gray-600 mb-4">
                  Excel, CSV, PDF veya Word dosyaları kabul edilir
                </p>
                <Button
                  onClick={() => fileInputRef.current?.click()}
                  disabled={isUploading}
                >
                  {isUploading ? 'Yükleniyor...' : 'Dosya Seç'}
                </Button>
              </div>
            </CardContent>
          </Card>

          {/* Dosya Listesi */}
          {files.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Yüklenen Dosyalar ({files.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {files.map((file) => (
                    <div key={file._id} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-2">
                            <h3 className="font-medium">{file.filename}</h3>
                            <Badge variant="secondary">
                              {file.file_type.split('/')[1]?.toUpperCase()}
                            </Badge>
                            <Badge variant="outline">
                              {formatFileSize(file.file_size)}
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-500">
                            Yüklenme: {new Date(file.upload_date).toLocaleDateString('tr-TR')}
                          </p>
                          {file.processed_data && (
                            <p className="text-sm text-green-600 mt-1">
                              {file.processed_data.emails_found} email adresi bulundu
                            </p>
                          )}
                        </div>
                        <div className="flex items-center gap-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => {
                              setSelectedFile(file)
                              if (file.processed_data?.emails_found) {
                                extractEmails(file._id)
                              }
                            }}
                          >
                            Seç
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => deleteFile(file._id)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Otomasyon */}
          {!selectedFile ? (
            <Card>
              <CardContent className="text-center py-8">
                <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Dosya Seçin
                </h3>
                <p className="text-gray-600">
                  Otomasyon başlatmak için önce bir dosya seçmelisiniz
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-6">
              {/* Seçilen Dosya */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Seçilen Dosya
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-medium">{selectedFile.filename}</h3>
                      <p className="text-sm text-gray-500">
                        {formatFileSize(selectedFile.file_size)} • 
                        {new Date(selectedFile.upload_date).toLocaleDateString('tr-TR')}
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      onClick={() => extractEmails(selectedFile._id)}
                      disabled={isExtracting}
                    >
                      {isExtracting ? 'Çıkarılıyor...' : 'Email Adreslerini Çıkar'}
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Email Sonuçları */}
              {emails.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Mail className="w-5 h-5" />
                      Bulunan Email Adresleri ({emails.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="mb-4">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={toggleAllEmails}
                      >
                        {selectedEmails.length === emails.length ? 'Tümünü Kaldır' : 'Tümünü Seç'}
                      </Button>
                    </div>

                    <div className="space-y-2 max-h-96 overflow-y-auto">
                      {emails.map((emailData, index) => (
                        <div key={index} className="flex items-center space-x-3 p-3 border rounded-lg">
                          <Checkbox
                            id={`email-${index}`}
                            checked={selectedEmails.includes(emailData.email)}
                            onCheckedChange={() => toggleEmailSelection(emailData.email)}
                          />
                          <div className="flex-1">
                            <div className="flex items-center gap-2">
                              <span className="font-medium">{emailData.email}</span>
                              <Badge variant="secondary" className="text-xs">
                                {emailData.category}
                              </Badge>
                              <Badge variant="outline" className="text-xs">
                                %{Math.round(emailData.confidence * 100)}
                              </Badge>
                            </div>
                            {emailData.company_name && (
                              <p className="text-sm text-gray-500">{emailData.company_name}</p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Email Gönderme */}
              {selectedEmails.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Send className="w-5 h-5" />
                      Email Gönder
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="template">Email Şablonu</Label>
                        <select
                          id="template"
                          value={selectedTemplate}
                          onChange={(e) => setSelectedTemplate(e.target.value)}
                          className="w-full mt-1 p-2 border rounded-md"
                        >
                          <option value="">Şablon seçin...</option>
                          {templates.map((template) => (
                            <option key={template._id} value={template._id}>
                              {template.name}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div>
                        <Label htmlFor="provider">Email Provider</Label>
                        <select
                          id="provider"
                          value={selectedProvider}
                          onChange={(e) => setSelectedProvider(e.target.value)}
                          className="w-full mt-1 p-2 border rounded-md"
                        >
                          <option value="">Provider seçin...</option>
                          {providers.map((provider) => (
                            <option key={provider.id} value={provider.id}>
                              {provider.email_address} ({provider.provider_name})
                            </option>
                          ))}
                        </select>
                      </div>
                    </div>


                    <div className="bg-blue-50 p-4 rounded-lg">
                      <div className="flex items-center gap-2 mb-2">
                        <CheckCircle className="w-5 h-5 text-blue-600" />
                        <span className="font-medium">Gönderim Özeti</span>
                      </div>
                      <p className="text-sm text-gray-600">
                        <strong>{selectedEmails.length}</strong> email adresine 
                        <strong> {templates.find(t => t._id === selectedTemplate)?.name || 'Seçilen şablon'}</strong> 
                        şablonu ile email gönderilecek.
                      </p>
                    </div>

                    <Button
                      onClick={sendBulkEmails}
                      disabled={!selectedTemplate || !selectedProvider || isSendingEmails}
                      className="w-full"
                    >
                      {isSendingEmails ? 'Gönderiliyor...' : `Seçilen ${selectedEmails.length} Email'i Gönder`}
                    </Button>

                    {emailSendingStatus && (
                      <div className={`p-3 rounded-lg flex items-center gap-2 ${
                        emailSendingStatus.includes('başarıyla') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                      }`}>
                        {emailSendingStatus.includes('başarıyla') ? (
                          <CheckCircle className="w-5 h-5" />
                        ) : (
                          <AlertCircle className="w-5 h-5" />
                        )}
                        <span className="text-sm">{emailSendingStatus}</span>
                      </div>
                    )}
                  </CardContent>
                </Card>
              )}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}
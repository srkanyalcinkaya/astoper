'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Search, Mail, Globe, FileText, Send, CheckCircle, AlertCircle } from 'lucide-react'
import { useAuth } from '@/lib/hooks/useAuth'
import { api } from '@/lib/api'
import DashboardLayout from '@/components/layout/DashboardLayout'

interface EmailResult {
  email: string
  source_url: string
  source_title: string
  source_snippet: string
}

interface SearchResult {
  title: string
  url: string
  snippet: string
  position: number
}

export default function SearchPage() {
  const { user } = useAuth()
  const [searchQuery, setSearchQuery] = useState('')
  const [targetUrl, setTargetUrl] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [searchResults, setSearchResults] = useState<SearchResult[]>([])
  const [emails, setEmails] = useState<EmailResult[]>([])
  const [selectedEmails, setSelectedEmails] = useState<string[]>([])
  const [templates, setTemplates] = useState<any[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState('')
  const [isStartingAutomation, setIsStartingAutomation] = useState(false)
  const [automationStatus, setAutomationStatus] = useState('')

  const handleSearch = async () => {
    if (!searchQuery.trim()) return

    setIsSearching(true)
    try {
      const response = await api.post('/search/serp-search', {
        query: searchQuery,
        target_url: targetUrl || null,
        max_results: 20
      })

      setSearchResults(response.data.search_results || [])
      setEmails(response.data.emails || [])
    } catch (error) {
      console.error('Arama hatası:', error)
    } finally {
      setIsSearching(false)
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

  useEffect(() => {
    const loadTemplates = async () => {
      try {
        const response = await api.get('/templates/')
        setTemplates(response.data)
      } catch (error) {
        console.error('Şablon yükleme hatası:', error)
      }
    }
    loadTemplates()
  }, [])

  const startAutomation = async () => {
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
        automation_type: 'search',
        search_queries: [searchQuery],
        target_urls: targetUrl ? [targetUrl] : [],
        use_serpapi: true,
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

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Arama Motoru</h1>
          <p className="text-gray-600">Hedef müşterilerinizi bulun ve onlara ulaşın</p>
        </div>

        <div className="space-y-6">
          {/* Arama Sorgusu */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Search className="w-5 h-5" />
                Arama Sorgusu
              </CardTitle>
              <CardDescription>
                Google'da arama yapın ve hedef sitelerden email adreslerini bulun
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="searchQuery">Arama Sorgusu *</Label>
                <Input
                  id="searchQuery"
                  placeholder="Örn: web tasarım şirketleri İstanbul"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="mt-1"
                />
              </div>

              <div>
                <Label htmlFor="targetUrl">Hedef URL (Opsiyonel)</Label>
                <Input
                  id="targetUrl"
                  placeholder="Örn: https://example.com"
                  value={targetUrl}
                  onChange={(e) => setTargetUrl(e.target.value)}
                  className="mt-1"
                />
                <p className="text-sm text-gray-500 mt-1">
                  Belirli bir site içinde arama yapmak için URL girin
                </p>
              </div>

              <Button 
                onClick={handleSearch} 
                disabled={!searchQuery.trim() || isSearching}
                className="w-full"
              >
                {isSearching ? 'Aranıyor...' : 'Arama Yap'}
              </Button>
            </CardContent>
          </Card>

          {/* Arama Sonuçları */}
          {searchResults.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Globe className="w-5 h-5" />
                  Arama Sonuçları ({searchResults.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {searchResults.map((result, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <h3 className="font-semibold text-blue-600 hover:underline">
                        <a href={result.url} target="_blank" rel="noopener noreferrer">
                          {result.title}
                        </a>
                      </h3>
                      <p className="text-sm text-gray-600 mt-1">{result.snippet}</p>
                      <p className="text-xs text-gray-400 mt-2">{result.url}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

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
                            {emailData.source_title}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-500">{emailData.source_url}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Şablon Seçimi ve Otomasyon */}
          {selectedEmails.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Email Şablonu Seçin
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="template">Şablon Seçin</Label>
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

                <div className="bg-blue-50 p-4 rounded-lg">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-5 h-5 text-blue-600" />
                    <span className="font-medium">Otomasyon Özeti</span>
                  </div>
                  <p className="text-sm text-gray-600">
                    <strong>{selectedEmails.length}</strong> email adresine 
                    <strong> {templates.find(t => t._id === selectedTemplate)?.name || 'Seçilen şablon'}</strong> 
                    şablonu ile email gönderilecek.
                  </p>
                </div>

                <Button
                  onClick={startAutomation}
                  disabled={!selectedTemplate || isStartingAutomation}
                  className="w-full"
                >
                  {isStartingAutomation ? 'Başlatılıyor...' : 'Email Otomasyonu Başlat'}
                </Button>

                {automationStatus && (
                  <div className={`p-3 rounded-lg flex items-center gap-2 ${
                    automationStatus.includes('başarıyla') ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'
                  }`}>
                    {automationStatus.includes('başarıyla') ? (
                      <CheckCircle className="w-5 h-5" />
                    ) : (
                      <AlertCircle className="w-5 h-5" />
                    )}
                    <span className="text-sm">{automationStatus}</span>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </DashboardLayout>
  )
}

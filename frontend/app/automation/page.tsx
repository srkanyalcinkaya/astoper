'use client'

import { useState, useEffect } from 'react'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Badge } from '@/components/ui/badge'
import { Checkbox } from '@/components/ui/checkbox'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useAppStore } from '@/lib/store'
import { apiService } from '@/lib/api'
import { toast } from 'sonner'

interface EmailData {
  email: string
  category: string
  confidence: number
  website_url?: string
  company_name?: string
  industry?: string
}

interface TemplateField {
  name: string
  label: string
  type: string
  required: boolean
  default: string
}

interface Template {
  _id: string
  name: string
  subject: string
  content: string
  category: string
  is_ai_generated: boolean
  template_fields?: TemplateField[]
}

export default function AutomationPage() {
  const [automationType, setAutomationType] = useState<'search' | 'file'>('search')
  const [searchQueries, setSearchQueries] = useState<string[]>([''])
  const [targetUrls, setTargetUrls] = useState<string[]>([''])
  const [selectedFile, setSelectedFile] = useState<string>('')
  const [useSerpapi, setUseSerpapi] = useState(true)
  
  const [emails, setEmails] = useState<EmailData[]>([])
  const [selectedEmails, setSelectedEmails] = useState<string[]>([])
  const [categories, setCategories] = useState<string[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('all')
  
  const [templates, setTemplates] = useState<Template[]>([])
  const [selectedTemplate, setSelectedTemplate] = useState<string>('')
  const [aiPrompt, setAiPrompt] = useState('')
  const [showAiPrompt, setShowAiPrompt] = useState(false)
  const [showTemplatePreview, setShowTemplatePreview] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState<Template | null>(null)
  const [templateContent, setTemplateContent] = useState('')
  const [templateFields, setTemplateFields] = useState<Record<string, string>>({})
  
  const [files, setFiles] = useState<any[]>([])
  
  const [isSearching, setIsSearching] = useState(false)
  const [isExtracting, setIsExtracting] = useState(false)
  const [isRunning, setIsRunning] = useState(false)
  
  const { user } = useAppStore()

  useEffect(() => {
    loadInitialData()
  }, [])

  const loadInitialData = async () => {
      try {
      const [templatesData, filesData] = await Promise.all([
        apiService.getDefaultTemplates(),
          apiService.getFiles()
        ])
      
      setTemplates(templatesData)
      setFiles(filesData)
      } catch (error) {
      console.error('Veri yükleme hatası:', error)
      toast.error('Veri yüklenemedi')
    }
  }

  const handleSearchEmails = async () => {
    if (!searchQueries.some(q => q.trim()) && !targetUrls.some(u => u.trim())) {
      toast.error('En az bir arama sorgusu veya hedef URL girin')
      return
    }

    setIsSearching(true)
    try {
      const result = await apiService.searchEmails({
        search_queries: searchQueries.filter(q => q.trim()),
        target_urls: targetUrls.filter(u => u.trim()),
        use_serpapi: useSerpapi,
        max_results: 50
      })

      setEmails(result.emails)
      setCategories(result.categories)
      toast.success(`${result.total_found} email adresi bulundu`)
    } catch (error: any) {
      console.error('Email arama hatası:', error)
      toast.error(error.response?.data?.detail || 'Email arama başarısız')
    } finally {
      setIsSearching(false)
    }
  }

  const handleExtractEmails = async () => {
    if (!selectedFile) {
      toast.error('Lütfen bir dosya seçin')
      return
    }

    setIsExtracting(true)
    try {
      const result = await apiService.extractEmailsFromFile(selectedFile)
      
      setEmails(result.emails)
      setCategories(result.categories)
      toast.success(`${result.total_found} email adresi çıkarıldı`)
    } catch (error: any) {
      console.error('Email çıkarma hatası:', error)
      toast.error(error.response?.data?.detail || 'Email çıkarma başarısız')
    } finally {
      setIsExtracting(false)
    }
  }

  const handleEmailSelect = (email: string, checked: boolean) => {
    if (checked) {
      setSelectedEmails(prev => [...prev, email])
    } else {
      setSelectedEmails(prev => prev.filter(e => e !== email))
    }
  }

  const handleSelectAll = (checked: boolean) => {
    const filteredEmails = getFilteredEmails()
    if (checked) {
      setSelectedEmails(filteredEmails.map(e => e.email))
    } else {
      setSelectedEmails([])
    }
  }

  const getFilteredEmails = () => {
    if (selectedCategory === 'all') {
      return emails
    }
    return emails.filter(email => email.category === selectedCategory)
  }

  const handleGenerateAITemplate = async () => {
    if (!aiPrompt.trim()) {
      toast.error('Lütfen bir prompt girin')
      return
    }

    try {
      const result = await apiService.generateAITemplate({
        prompt: aiPrompt,
        template_name: 'AI Oluşturulan Şablon',
        category: 'custom'
      })

      const newTemplate = {
        _id: result.template_id,
        name: 'AI Oluşturulan Şablon',
        subject: result.subject,
        content: result.content,
        category: 'custom',
        is_ai_generated: true,
        template_fields: [
          {"name": "company_name", "label": "Şirket Adı", "type": "text", "required": true, "default": "Şirket Adınız"},
          {"name": "company_tagline", "label": "Şirket Sloganı", "type": "text", "required": false, "default": "Dijital Dönüşüm Partneriniz"},
          {"name": "greeting_message", "label": "Karşılama Mesajı", "type": "textarea", "required": true, "default": "Merhaba! Size nasıl yardımcı olabiliriz?"},
          {"name": "service_1", "label": "Hizmet 1", "type": "text", "required": true, "default": "Profesyonel hizmetlerimiz"},
          {"name": "service_2", "label": "Hizmet 2", "type": "text", "required": true, "default": "Kaliteli çözümlerimiz"},
          {"name": "service_3", "label": "Hizmet 3", "type": "text", "required": true, "default": "Güvenilir hizmetlerimiz"},
          {"name": "offer_title", "label": "Teklif Başlığı", "type": "text", "required": true, "default": "Özel Teklif"},
          {"name": "offer_description", "label": "Teklif Açıklaması", "type": "textarea", "required": true, "default": "Size özel çözümler sunuyoruz"},
          {"name": "email", "label": "Email Adresi", "type": "email", "required": true, "default": "info@example.com"},
          {"name": "phone", "label": "Telefon", "type": "text", "required": true, "default": "+90 XXX XXX XX XX"},
          {"name": "website_url", "label": "Website URL", "type": "url", "required": true, "default": "https://www.example.com"}
        ]
      }
      
      setTemplates(prev => [...prev, newTemplate])
      setSelectedTemplate(result.template_id)
      setShowAiPrompt(false)
      setAiPrompt('')
      
      toast.success('AI şablonu oluşturuldu!')
    } catch (error: any) {
      console.error('AI şablon hatası:', error)
      toast.error(error.response?.data?.detail || 'AI şablon oluşturulamadı')
    }
  }

  const handlePreviewTemplate = (template: Template) => {
    setEditingTemplate(template)
    setTemplateContent(template.content)
    
    const fields: Record<string, string> = {}
    if (template.template_fields) {
      template.template_fields.forEach(field => {
        fields[field.name] = field.default
      })
    }
    setTemplateFields(fields)
    setShowTemplatePreview(true)
  }

  const renderTemplateWithFields = (content: string, fields: Record<string, string>) => {
    let rendered = content
    Object.entries(fields).forEach(([key, value]) => {
      const placeholder = `{{${key}}}`
      rendered = rendered.replace(new RegExp(placeholder, 'g'), value)
    })
    return rendered
  }

  const handleSaveTemplate = async () => {
    if (!editingTemplate) return

    try {
      await apiService.updateTemplate(editingTemplate._id, {
        content: templateContent
      })
      
      setTemplates(prev => prev.map(t => 
        t._id === editingTemplate._id 
          ? { ...t, content: templateContent }
          : t
      ))
      
      setShowTemplatePreview(false)
      setEditingTemplate(null)
      toast.success('Şablon güncellendi!')
    } catch (error: any) {
      console.error('Şablon güncelleme hatası:', error)
      toast.error(error.response?.data?.detail || 'Şablon güncellenemedi')
    }
  }

  const handleRunAutomation = async () => {
    if (selectedEmails.length === 0) {
      toast.error('Lütfen en az bir email seçin')
      return
    }

    if (!selectedTemplate) {
      toast.error('Lütfen bir şablon seçin')
      return
    }

    setIsRunning(true)
    try {
      const automationData: any = {
        automation_type: automationType,
        selected_emails: selectedEmails,
        template_id: selectedTemplate,
        use_serpapi: useSerpapi,
        custom_data: templateFields
      }

      if (automationType === 'search') {
        automationData.search_queries = searchQueries.filter(q => q.trim())
        automationData.target_urls = targetUrls.filter(u => u.trim())
      } else {
        automationData.file_id = selectedFile
      }

      const result = await apiService.createAutomation(automationData)
      
      toast.success('Otomasyon başlatıldı! Sonuçları Automation History sayfasından takip edebilirsiniz.')
      
      setSelectedEmails([])
      setSelectedTemplate('')
      
    } catch (error: any) {
      console.error('Otomasyon hatası:', error)
      toast.error(error.response?.data?.detail || 'Otomasyon başlatılamadı')
    } finally {
      setIsRunning(false)
    }
  }

  const addSearchQuery = () => {
    setSearchQueries(prev => [...prev, ''])
  }

  const removeSearchQuery = (index: number) => {
    setSearchQueries(prev => prev.filter((_, i) => i !== index))
  }

  const updateSearchQuery = (index: number, value: string) => {
    setSearchQueries(prev => prev.map((q, i) => i === index ? value : q))
  }

  const addTargetUrl = () => {
    setTargetUrls(prev => [...prev, ''])
  }

  const removeTargetUrl = (index: number) => {
    setTargetUrls(prev => prev.filter((_, i) => i !== index))
  }

  const updateTargetUrl = (index: number, value: string) => {
    setTargetUrls(prev => prev.map((u, i) => i === index ? value : u))
  }

  const getCategoryColor = (category: string) => {
    const colors: Record<string, string> = {
      web_design: 'bg-blue-100 text-blue-800',
      seo: 'bg-green-100 text-green-800',
      ecommerce: 'bg-purple-100 text-purple-800',
      marketing: 'bg-orange-100 text-orange-800',
      tech: 'bg-gray-100 text-gray-800',
      general: 'bg-gray-100 text-gray-800'
    }
    return colors[category] || colors.general
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900">Email Otomasyonu</h1>
          <p className="text-gray-600 mt-2">
            Arama sorguları veya dosyalardan email adreslerini toplayın ve otomatik kampanyalar başlatın
          </p>
        </div>

        <Tabs defaultValue="search" className="w-full">
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger 
              value="search" 
              onClick={() => setAutomationType('search')}
            >
              🔍 Arama Otomasyonu
            </TabsTrigger>
            <TabsTrigger 
              value="file" 
              onClick={() => setAutomationType('file')}
            >
              📁 Dosya Otomasyonu
            </TabsTrigger>
          </TabsList>

          <TabsContent value="search" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>1. Arama Sorguları</CardTitle>
                <CardDescription>
                  Hangi terimlerle arama yapılacağını belirleyin
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>SerpAPI Kullan</Label>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="serpapi"
                      checked={useSerpapi}
                      onCheckedChange={(checked) => setUseSerpapi(checked === true)}
                    />
                    <Label htmlFor="serpapi" className="text-sm">
                      Google arama sonuçlarını kullan (önerilen)
                    </Label>
                  </div>
                  </div>

                <div className="space-y-3">
                  <Label>Arama Sorguları</Label>
                  {searchQueries.map((query, index) => (
                            <div key={index} className="flex gap-2">
                              <Input
                        placeholder="Örn: web tasarım şirketi İstanbul"
                                value={query}
                                onChange={(e) => updateSearchQuery(index, e.target.value)}
                              />
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => removeSearchQuery(index)}
                                >
                                  ✕
                                </Button>
                            </div>
                          ))}
                  <Button variant="outline" onClick={addSearchQuery}>
                            + Sorgu Ekle
                          </Button>
                      </div>

                <div className="space-y-3">
                  <Label>Hedef URL'ler (İsteğe bağlı)</Label>
                  {targetUrls.map((url, index) => (
                            <div key={index} className="flex gap-2">
                              <Input
                        placeholder="https://example.com"
                                value={url}
                                onChange={(e) => updateTargetUrl(index, e.target.value)}
                              />
                                <Button
                                  variant="outline"
                                  size="sm"
                                  onClick={() => removeTargetUrl(index)}
                                >
                                  ✕
                                </Button>
                            </div>
                          ))}
                  <Button variant="outline" onClick={addTargetUrl}>
                            + URL Ekle
                          </Button>
                      </div>

                <Button 
                  onClick={handleSearchEmails}
                  disabled={isSearching}
                  className="w-full"
                >
                  {isSearching ? 'Aranıyor...' : '🔍 Email Adreslerini Ara'}
                  </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="file" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>1. Dosya Seçimi</CardTitle>
                <CardDescription>
                  Email adreslerini çıkarmak istediğiniz dosyayı seçin
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Yüklenmiş Dosyalar</Label>
                  <Select value={selectedFile} onValueChange={setSelectedFile}>
                    <SelectTrigger>
                      <SelectValue placeholder="Dosya seçin..." />
                    </SelectTrigger>
                    <SelectContent>
                      {files.map((file) => (
                        <SelectItem key={file._id} value={file._id}>
                          {file.filename} ({file.file_size} bytes)
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                    </div>
                    
                <Button 
                  onClick={handleExtractEmails}
                  disabled={isExtracting || !selectedFile}
                  className="w-full"
                >
                  {isExtracting ? 'İşleniyor...' : '📧 Email Adreslerini Çıkar'}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Email Listesi */}
        {emails.length > 0 && (
          <Card>
              <CardHeader>
              <CardTitle>2. Email Adreslerini Seçin</CardTitle>
              <CardDescription>
                {emails.length} email bulundu. İstediklerinizi seçin.
              </CardDescription>
              </CardHeader>
            <CardContent className="space-y-4">
              {/* Filtreleme */}
              <div className="flex gap-4 items-center">
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="selectAll"
                    checked={selectedEmails.length === getFilteredEmails().length && getFilteredEmails().length > 0}
                    onCheckedChange={handleSelectAll}
                  />
                  <Label htmlFor="selectAll">Tümünü Seç</Label>
                      </div>

                <Select value={selectedCategory} onValueChange={setSelectedCategory}>
                  <SelectTrigger className="w-48">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Tüm Kategoriler</SelectItem>
                    {categories.map(category => (
                      <SelectItem key={category} value={category}>
                        {category.replace('_', ' ').toUpperCase()}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              {/* Email Listesi */}
              <div className="max-h-96 overflow-y-auto space-y-2">
                {getFilteredEmails().map((emailData, index) => (
                  <div key={index} className="flex items-center space-x-3 p-3 border rounded-lg">
                    <Checkbox
                      checked={selectedEmails.includes(emailData.email)}
                      onCheckedChange={(checked) => handleEmailSelect(emailData.email, checked as boolean)}
                    />
                    <div className="flex-1">
                      <div className="font-medium">{emailData.email}</div>
                      {emailData.company_name && (
                        <div className="text-sm text-gray-600">{emailData.company_name}</div>
                      )}
                      {emailData.website_url && (
                        <div className="text-sm text-blue-600">{emailData.website_url}</div>
                      )}
                    </div>
                    <Badge className={getCategoryColor(emailData.category)}>
                      {emailData.category.replace('_', ' ')}
                    </Badge>
                    <Badge variant="outline">
                      %{(emailData.confidence * 100).toFixed(0)}
                    </Badge>
                  </div>
                ))}
              </div>

              <div className="text-sm text-gray-600">
                {selectedEmails.length} email seçildi
              </div>
              </CardContent>
            </Card>
        )}

        {/* Şablon Seçimi */}
        {selectedEmails.length > 0 && (
          <Card>
              <CardHeader>
              <CardTitle>3. Email Şablonu Seçin</CardTitle>
              <CardDescription>
                Gönderilecek email'in şablonunu belirleyin
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {templates.map((template) => (
                  <div
                    key={template._id}
                    className={`p-4 border rounded-lg transition-colors ${
                      selectedTemplate === template._id
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div 
                      className="cursor-pointer"
                      onClick={() => setSelectedTemplate(template._id)}
                    >
                      <div className="font-medium">{template.name}</div>
                      <div className="text-sm text-gray-600 mt-1">
                        {template.subject}
                      </div>
                      <Badge variant="outline" className="mt-2">
                        {template.category}
                      </Badge>
                      {template.is_ai_generated && (
                        <Badge className="mt-1">AI</Badge>
                      )}
                    </div>
                    
                    <div className="flex gap-2 mt-3">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handlePreviewTemplate(template)}
                        className="flex-1"
                      >
                        👁️ Önizle
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handlePreviewTemplate(template)}
                        className="flex-1"
                      >
                        ✏️ Düzenle
                      </Button>
                          </div>
                        </div>
                      ))}
                    </div>

              {/* AI Şablon Oluşturma */}
              <div className="border-t pt-4">
                    <Button
                      variant="outline"
                  onClick={() => setShowAiPrompt(!showAiPrompt)}
                >
                  🤖 AI ile Şablon Oluştur
                </Button>

                {showAiPrompt && (
                  <div className="mt-4 space-y-3">
                    <Textarea
                      placeholder="Şablon için prompt yazın... Örn: Restoran sahipleri için özel bir email şablonu oluştur..."
                      value={aiPrompt}
                      onChange={(e) => setAiPrompt(e.target.value)}
                      rows={3}
                    />
                    <Button onClick={handleGenerateAITemplate}>
                      AI Şablonu Oluştur
                    </Button>
                  </div>
                )}
              </div>

              <Button 
                onClick={handleRunAutomation}
                disabled={isRunning || !selectedTemplate}
                className="w-full mt-4"
                size="lg"
              >
                {isRunning ? 'Otomasyon Başlatılıyor...' : '🚀 Otomasyonu Başlat'}
              </Button>
                </CardContent>
          </Card>
        )}

        {/* Template Preview/Edit Modal */}
        {showTemplatePreview && editingTemplate && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg max-w-7xl w-full max-h-[90vh] overflow-hidden">
              <div className="p-6 border-b">
                <div className="flex justify-between items-center">
                  <h2 className="text-xl font-bold">
                    {editingTemplate.name} - {editingTemplate.subject}
                  </h2>
                  <Button
                    variant="outline"
                    onClick={() => setShowTemplatePreview(false)}
                  >
                    ✕ Kapat
                  </Button>
                </div>
              </div>
              
              <div className="flex h-[calc(90vh-120px)]">
                {/* Form Fields */}
                <div className="w-2/5 p-6 border-r overflow-y-auto">
                  <h3 className="font-semibold mb-4">📝 Bilgilerinizi Doldurun</h3>
                  <div className="space-y-4">
                    {editingTemplate.template_fields?.map((field) => (
                      <div key={field.name} className="space-y-2">
                        <label className="text-sm font-medium text-gray-700">
                          {field.label}
                          {field.required && <span className="text-red-500 ml-1">*</span>}
                        </label>
                        {field.type === 'textarea' ? (
                          <Textarea
                            value={templateFields[field.name] || ''}
                            onChange={(e) => setTemplateFields(prev => ({
                              ...prev,
                              [field.name]: e.target.value
                            }))}
                            placeholder={field.default}
                            className="min-h-[80px]"
                          />
                        ) : (
                          <Input
                            type={field.type}
                            value={templateFields[field.name] || ''}
                            onChange={(e) => setTemplateFields(prev => ({
                              ...prev,
                              [field.name]: e.target.value
                            }))}
                            placeholder={field.default}
                          />
                        )}
                      </div>
                    ))}
                  </div>
                </div>
                
                {/* Preview */}
                <div className="w-3/5 p-6">
                  <h3 className="font-semibold mb-3">📱 Email Önizleme</h3>
                  <div className="h-full overflow-auto border rounded-lg p-4 bg-gray-50">
                    <div 
                      dangerouslySetInnerHTML={{ 
                        __html: renderTemplateWithFields(templateContent, templateFields) 
                      }}
                      className="max-w-none"
                    />
                  </div>
                </div>
              </div>
              
              <div className="p-6 border-t flex justify-end gap-3">
                <Button
                  variant="outline"
                  onClick={() => setShowTemplatePreview(false)}
                >
                  İptal
                </Button>
                <Button
                  onClick={() => {
                    setSelectedTemplate(editingTemplate._id)
                    setShowTemplatePreview(false)
                    toast.success('Template seçildi ve bilgiler kaydedildi!')
                  }}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  ✅ Bu Template'i Kullan
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}
'use client'

import { useState, useEffect, useRef } from 'react'
import DashboardLayout from '@/components/layout/DashboardLayout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  Upload, 
  FileText, 
  Edit, 
  Eye, 
  Trash2, 
  Plus, 
  Download,
  Save,
  X
} from 'lucide-react'
import { useAuth } from '@/lib/hooks/useAuth'
import { api } from '@/lib/api'

interface EmailTemplate {
  _id: string
  name: string
  subject: string
  content: string
  is_uploaded?: boolean
  created_at: string
  updated_at: string
}

export default function TemplatesPage() {
  const { user } = useAuth()
  const [templates, setTemplates] = useState<EmailTemplate[]>([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [editingTemplate, setEditingTemplate] = useState<EmailTemplate | null>(null)
  const [previewTemplate, setPreviewTemplate] = useState<EmailTemplate | null>(null)
  const [showCreateForm, setShowCreateForm] = useState(false)
  
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [uploadForm, setUploadForm] = useState({
    template_name: '',
    subject: '',
    file: null as File | null
  })
  
  const [createForm, setCreateForm] = useState({
    name: '',
    subject: '',
    content: ''
  })

  useEffect(() => {
    loadTemplates()
  }, [])

  const loadTemplates = async () => {
    try {
      setLoading(true)
      const response = await api.get('/templates/')
      setTemplates(response.data)
    } catch (error) {
      console.error('Error loading templates:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setUploadForm(prev => ({
        ...prev,
        file,
        template_name: file.name.split('.')[0]
      }))
    }
  }

  const uploadTemplate = async () => {
    if (!uploadForm.file || !uploadForm.template_name) {
      alert('Lütfen dosya seçin ve şablon adı girin')
      return
    }

    try {
      setUploading(true)
      const formData = new FormData()
      formData.append('file', uploadForm.file)
      formData.append('template_name', uploadForm.template_name)
      if (uploadForm.subject) {
        formData.append('subject', uploadForm.subject)
      }

      await api.post('/templates/upload-template', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      alert('Şablon başarıyla yüklendi!')
      setUploadForm({ template_name: '', subject: '', file: null })
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
      loadTemplates()
    } catch (error: any) {
      console.error('Error uploading template:', error)
      alert(error.response?.data?.detail || 'Şablon yüklenirken hata oluştu')
    } finally {
      setUploading(false)
    }
  }

  const createTemplate = async () => {
    if (!createForm.name || !createForm.subject || !createForm.content) {
      alert('Lütfen tüm alanları doldurun')
      return
    }

    try {
      await api.post('/templates/', createForm)
      alert('Şablon başarıyla oluşturuldu!')
      setCreateForm({ name: '', subject: '', content: '' })
      setShowCreateForm(false)
      loadTemplates()
    } catch (error: any) {
      console.error('Error creating template:', error)
      alert(error.response?.data?.detail || 'Şablon oluşturulurken hata oluştu')
    }
  }

  const updateTemplate = async () => {
    if (!editingTemplate) return

    try {
      await api.put(`/templates/${editingTemplate._id}`, {
        name: editingTemplate.name,
        subject: editingTemplate.subject,
        content: editingTemplate.content
      })
      alert('Şablon başarıyla güncellendi!')
      setEditingTemplate(null)
      loadTemplates()
    } catch (error: any) {
      console.error('Error updating template:', error)
      alert(error.response?.data?.detail || 'Şablon güncellenirken hata oluştu')
    }
  }

  const deleteTemplate = async (templateId: string) => {
    if (!confirm('Bu şablonu silmek istediğinizden emin misiniz?')) {
      return
    }

    try {
      await api.delete(`/templates/${templateId}`)
      alert('Şablon başarıyla silindi!')
      loadTemplates()
    } catch (error: any) {
      console.error('Error deleting template:', error)
      alert(error.response?.data?.detail || 'Şablon silinirken hata oluştu')
    }
  }

  const previewTemplateContent = async (templateId: string) => {
    try {
      const response = await api.get(`/templates/preview/${templateId}`)
      setPreviewTemplate(response.data)
    } catch (error: any) {
      console.error('Error previewing template:', error)
      alert(error.response?.data?.detail || 'Şablon önizlenirken hata oluştu')
    }
  }

  const downloadTemplate = (template: EmailTemplate) => {
    const blob = new Blob([template.content], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${template.name}.html`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Email Şablonları</h1>
          <p className="text-gray-600">Email şablonlarınızı yönetin ve düzenleyin</p>
        </div>

        <Tabs defaultValue="templates" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="templates">Şablonlarım</TabsTrigger>
            <TabsTrigger value="upload">Şablon Yükle</TabsTrigger>
            <TabsTrigger value="create">Şablon Oluştur</TabsTrigger>
          </TabsList>

          <TabsContent value="templates">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Email Şablonları ({templates.length})
                </CardTitle>
                <CardDescription>
                  Mevcut email şablonlarınızı görüntüleyin, düzenleyin ve yönetin
                </CardDescription>
              </CardHeader>
              <CardContent>
                {templates.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    <FileText className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <p>Henüz şablon oluşturmamışsınız</p>
                    <p className="text-sm">Şablon yükleyin veya oluşturun</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {templates.map((template) => (
                      <div key={template._id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <h3 className="font-medium">{template.name}</h3>
                              {template.is_uploaded && (
                                <Badge variant="secondary" className="text-xs">
                                  Yüklenen
                                </Badge>
                              )}
                            </div>
                            <p className="text-sm text-gray-500 mb-1">
                              <strong>Konu:</strong> {template.subject}
                            </p>
                            <p className="text-xs text-gray-400">
                              Oluşturulma: {new Date(template.created_at).toLocaleDateString('tr-TR')}
                            </p>
                          </div>
                          <div className="flex items-center gap-2">
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => previewTemplateContent(template._id)}
                            >
                              <Eye className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => setEditingTemplate(template)}
                            >
                              <Edit className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => downloadTemplate(template)}
                            >
                              <Download className="w-4 h-4" />
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => deleteTemplate(template._id)}
                              className="text-red-600 hover:text-red-700"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="upload">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="w-5 h-5" />
                  Hazır Şablon Yükle
                </CardTitle>
                <CardDescription>
                  HTML veya TXT formatında hazır email şablonlarınızı yükleyin
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="template_name">Şablon Adı</Label>
                  <Input
                    id="template_name"
                    value={uploadForm.template_name}
                    onChange={(e) => setUploadForm(prev => ({ ...prev, template_name: e.target.value }))}
                    placeholder="Şablon adını girin"
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="template_subject">Email Konusu (İsteğe Bağlı)</Label>
                  <Input
                    id="template_subject"
                    value={uploadForm.subject}
                    onChange={(e) => setUploadForm(prev => ({ ...prev, subject: e.target.value }))}
                    placeholder="Email konusunu girin"
                    className="mt-1"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Boş bırakılırsa varsayılan konu kullanılır
                  </p>
                </div>

                <div>
                  <Label>Dosya Seç</Label>
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                    <input
                      ref={fileInputRef}
                      type="file"
                      onChange={handleFileUpload}
                      accept=".html,.txt"
                      className="hidden"
                    />
                    <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-600 mb-2">
                      HTML veya TXT dosyası seçin
                    </p>
                    <Button
                      variant="outline"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      Dosya Seç
                    </Button>
                    {uploadForm.file && (
                      <p className="text-sm text-green-600 mt-2">
                        Seçilen: {uploadForm.file.name}
                      </p>
                    )}
                  </div>
                </div>

                <Button
                  onClick={uploadTemplate}
                  disabled={!uploadForm.file || !uploadForm.template_name || uploading}
                  className="w-full"
                >
                  {uploading ? 'Yükleniyor...' : 'Şablon Yükle'}
                </Button>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="create">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Plus className="w-5 h-5" />
                  Yeni Şablon Oluştur
                </CardTitle>
                <CardDescription>
                  Sıfırdan yeni bir email şablonu oluşturun
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="name">Şablon Adı</Label>
                  <Input
                    id="name"
                    value={createForm.name}
                    onChange={(e) => setCreateForm(prev => ({ ...prev, name: e.target.value }))}
                    placeholder="Şablon adını girin"
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="subject">Email Konusu</Label>
                  <Input
                    id="subject"
                    value={createForm.subject}
                    onChange={(e) => setCreateForm(prev => ({ ...prev, subject: e.target.value }))}
                    placeholder="Email konusunu girin"
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="content">Email İçeriği</Label>
                  <Textarea
                    id="content"
                    value={createForm.content}
                    onChange={(e) => setCreateForm(prev => ({ ...prev, content: e.target.value }))}
                    placeholder="Email içeriğini girin (HTML formatında)"
                    className="mt-1 min-h-[200px]"
                  />
                </div>

                <Button
                  onClick={createTemplate}
                  disabled={!createForm.name || !createForm.subject || !createForm.content}
                  className="w-full"
                >
                  Şablon Oluştur
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>

        {/* Edit Modal */}
        {editingTemplate && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium">Şablon Düzenle</h3>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setEditingTemplate(null)}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <Label htmlFor="edit_name">Şablon Adı</Label>
                  <Input
                    id="edit_name"
                    value={editingTemplate.name}
                    onChange={(e) => setEditingTemplate(prev => prev ? { ...prev, name: e.target.value } : null)}
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="edit_subject">Email Konusu</Label>
                  <Input
                    id="edit_subject"
                    value={editingTemplate.subject}
                    onChange={(e) => setEditingTemplate(prev => prev ? { ...prev, subject: e.target.value } : null)}
                    className="mt-1"
                  />
                </div>

                <div>
                  <Label htmlFor="edit_content">Email İçeriği</Label>
                  <Textarea
                    id="edit_content"
                    value={editingTemplate.content}
                    onChange={(e) => setEditingTemplate(prev => prev ? { ...prev, content: e.target.value } : null)}
                    className="mt-1 min-h-[300px]"
                  />
                </div>

                <div className="flex justify-end gap-2">
                  <Button
                    variant="outline"
                    onClick={() => setEditingTemplate(null)}
                  >
                    İptal
                  </Button>
                  <Button onClick={updateTemplate}>
                    <Save className="w-4 h-4 mr-2" />
                    Kaydet
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Preview Modal */}
        {previewTemplate && (
          <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
            <div className="relative top-20 mx-auto p-5 border w-full max-w-4xl shadow-lg rounded-md bg-white">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium">Şablon Önizleme: {previewTemplate.name}</h3>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPreviewTemplate(null)}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <Label>Email Konusu</Label>
                  <div className="p-3 bg-gray-50 rounded-md mt-1">
                    {previewTemplate.subject}
                  </div>
                </div>

                <div>
                  <Label>Email İçeriği</Label>
                  <div 
                    className="p-4 border rounded-md mt-1 min-h-[400px] bg-white"
                    dangerouslySetInnerHTML={{ __html: previewTemplate.content }}
                  />
                </div>

                <div className="flex justify-end">
                  <Button
                    variant="outline"
                    onClick={() => setPreviewTemplate(null)}
                  >
                    Kapat
                  </Button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  )
}

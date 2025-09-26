"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import DashboardLayout from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { API_ENDPOINTS } from "@/lib/config";
import { authService } from "@/lib/auth";
import { Calendar, Clock, AlertTriangle, CheckCircle } from "lucide-react";

interface SubscriptionStatus {
  has_subscription: boolean;
  subscription?: {
    id: string;
    status: string;
    current_period_end: string;
    days_remaining: number;
    auto_renewal: boolean;
    cancellation_requested: boolean;
    service_end_date?: string;
  };
}

interface CancellationReason {
  id: string;
  label: string;
}

export default function CancelSubscriptionPage() {
  const router = useRouter();
  const [subscription, setSubscription] = useState<SubscriptionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [cancellationReasons, setCancellationReasons] = useState<CancellationReason[]>([]);
  
  const [selectedReason, setSelectedReason] = useState("");
  const [customReason, setCustomReason] = useState("");
  const [feedback, setFeedback] = useState("");
  const [autoRenewal, setAutoRenewal] = useState(true);
  const [confirmCancellation, setConfirmCancellation] = useState(false);

  useEffect(() => {
    fetchSubscriptionStatus();
    fetchCancellationReasons();
  }, []);

  const fetchSubscriptionStatus = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.SUBSCRIPTION_STATUS, {
        headers: {
          "Authorization": `Bearer ${authService.getToken()}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSubscription(data);
        setAutoRenewal(data.subscription?.auto_renewal ?? true);
      }
    } catch (error) {
      console.error("Abonelik durumu alınamadı:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCancellationReasons = async () => {
    try {
      const response = await fetch(API_ENDPOINTS.CANCELLATION_REASONS);
      if (response.ok) {
        const data = await response.json();
        setCancellationReasons(data.reasons);
      }
    } catch (error) {
      console.error("İptal nedenleri alınamadı:", error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!confirmCancellation) {
      alert("Lütfen iptal işlemini onaylayın.");
      return;
    }

    setSubmitting(true);

    try {
      const response = await fetch(API_ENDPOINTS.SUBSCRIPTION_CANCEL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${authService.getToken()}`
        },
        body: JSON.stringify({
          cancellation_reason: selectedReason === "other" ? customReason : selectedReason,
          feedback: feedback,
          auto_renewal: autoRenewal
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(result.message);
        router.push("/dashboard");
      } else {
        const error = await response.json();
        alert(`Hata: ${error.detail}`);
      }
    } catch (error) {
      console.error("İptal işlemi başarısız:", error);
      alert("İptal işlemi sırasında bir hata oluştu.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Abonelik durumu kontrol ediliyor...</p>
        </div>
      </div>
    );
  }

  if (!subscription?.has_subscription) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <AlertTriangle className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
            <CardTitle>Aktif Abonelik Bulunamadı</CardTitle>
            <CardDescription>
              İptal edilecek bir aboneliğiniz bulunmuyor.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={() => router.push("/dashboard")} 
              className="w-full"
            >
              Dashboard'a Dön
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (subscription.subscription?.cancellation_requested) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardHeader className="text-center">
            <CheckCircle className="h-12 w-12 text-green-500 mx-auto mb-4" />
            <CardTitle>İptal Talebi Zaten Gönderildi</CardTitle>
            <CardDescription>
              Aboneliğiniz için iptal talebi daha önce gönderilmiş.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={() => router.push("/dashboard")} 
              className="w-full"
            >
              Dashboard'a Dön
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const serviceEndDate = new Date(subscription.subscription?.current_period_end || "");
  const daysRemaining = subscription.subscription?.days_remaining || 0;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-2xl mx-auto px-4">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Abonelik İptal Et
          </h1>
          <p className="text-gray-600">
            Aboneliğinizi iptal etmeden önce lütfen aşağıdaki bilgileri okuyun.
          </p>
        </div>

        {/* Mevcut Abonelik Bilgileri */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Mevcut Abonelik Bilgileri
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium text-gray-500">Durum</Label>
                <Badge variant={subscription.subscription?.status === "active" ? "default" : "secondary"}>
                  {subscription.subscription?.status === "active" ? "Aktif" : "Beklemede"}
                </Badge>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-500">Kalan Süre</Label>
                <p className="text-lg font-semibold text-blue-600">
                  {daysRemaining} gün
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-500">Hizmet Bitiş Tarihi</Label>
                <p className="text-sm">
                  {serviceEndDate.toLocaleDateString("tr-TR")}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-500">Otomatik Yenileme</Label>
                <Badge variant={subscription.subscription?.auto_renewal ? "default" : "secondary"}>
                  {subscription.subscription?.auto_renewal ? "Açık" : "Kapalı"}
                </Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Önemli Bilgiler */}
        <Alert className="mb-6">
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            <strong>Önemli:</strong> Aboneliğinizi iptal etseniz bile, ödediğiniz süre boyunca 
            hizmetlerimizi kullanmaya devam edebilirsiniz. Hizmetiniz mevcut dönem sonuna kadar 
            aktif kalacaktır.
          </AlertDescription>
        </Alert>

        {/* İptal Formu */}
        <Card>
          <CardHeader>
            <CardTitle>İptal Talebi</CardTitle>
            <CardDescription>
              Lütfen iptal nedeninizi belirtin ve geri bildiriminizi paylaşın.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* İptal Nedeni */}
              <div>
                <Label htmlFor="reason">İptal Nedeni *</Label>
                <Select value={selectedReason} onValueChange={setSelectedReason}>
                  <SelectTrigger>
                    <SelectValue placeholder="İptal nedeninizi seçin" />
                  </SelectTrigger>
                  <SelectContent>
                    {cancellationReasons.map((reason) => (
                      <SelectItem key={reason.id} value={reason.id}>
                        {reason.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                
                {selectedReason === "other" && (
                  <Input
                    className="mt-2"
                    placeholder="Lütfen nedeninizi açıklayın"
                    value={customReason}
                    onChange={(e) => setCustomReason(e.target.value)}
                    required
                  />
                )}
              </div>

              {/* Ek Geri Bildirim */}
              <div>
                <Label htmlFor="feedback">Ek Geri Bildirim</Label>
                <Textarea
                  id="feedback"
                  placeholder="Geri bildiriminizi buraya yazabilirsiniz..."
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  rows={4}
                />
              </div>

              {/* Otomatik Yenileme Seçeneği */}
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="auto-renewal"
                  checked={autoRenewal}
                  onCheckedChange={(checked) => setAutoRenewal(checked as boolean)}
                />
                <Label htmlFor="auto-renewal">
                  Otomatik yenileme seçeneğini açık tut (önerilen)
                </Label>
              </div>

              {/* Onay */}
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="confirm"
                  checked={confirmCancellation}
                  onCheckedChange={(checked) => setConfirmCancellation(checked as boolean)}
                />
                <Label htmlFor="confirm">
                  İptal işlemini onaylıyorum ve yukarıdaki bilgileri okudum
                </Label>
              </div>

              {/* Butonlar */}
              <div className="flex gap-4 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.push("/dashboard")}
                  className="flex-1"
                >
                  İptal Et
                </Button>
                <Button
                  type="submit"
                  disabled={!confirmCancellation || submitting}
                  className="flex-1 bg-red-600 hover:bg-red-700"
                >
                  {submitting ? "İşleniyor..." : "Aboneliği İptal Et"}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

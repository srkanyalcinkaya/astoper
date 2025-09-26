"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import DashboardLayout from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Label } from "@/components/ui/label";
import { API_ENDPOINTS } from "@/lib/config";
import { authService } from "@/lib/auth";
import { 
  Calendar, 
  Clock, 
  CreditCard, 
  Settings, 
  AlertTriangle, 
  CheckCircle,
  RefreshCw,
  X
} from "lucide-react";

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

export default function ManageSubscriptionPage() {
  const router = useRouter();
  const [subscription, setSubscription] = useState<SubscriptionStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    fetchSubscriptionStatus();
  }, []);

  const fetchSubscriptionStatus = async () => {
    try {
      if (!authService.isAuthenticated()) {
        alert("Giriş yapmanız gerekiyor");
        router.push("/login");
        return;
      }
      
      const response = await fetch(API_ENDPOINTS.SUBSCRIPTION_STATUS, {
        headers: {
          "Authorization": `Bearer ${authService.getToken()}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSubscription(data);
      } else {
        if (response.status === 401) {
          alert("Oturum süreniz dolmuş. Lütfen tekrar giriş yapın.");
          router.push("/login");
          return;
        }
      }
    } catch (error) {
      console.error("Abonelik durumu alınamadı:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleReactivate = async () => {
    setActionLoading("reactivate");
    
    try {
      const response = await fetch(API_ENDPOINTS.SUBSCRIPTION_REACTIVATE, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${authService.getToken()}`
        }
      });

      if (response.ok) {
        const result = await response.json();
        alert(result.message);
        fetchSubscriptionStatus();
      } else {
        const error = await response.json();
        alert(`Hata: ${error.detail}`);
      }
    } catch (error) {
      console.error("Yeniden aktifleştirme başarısız:", error);
      alert("İşlem sırasında bir hata oluştu.");
    } finally {
      setActionLoading(null);
    }
  };

  const handleUpdateAutoRenewal = async (autoRenewal: boolean) => {
    setActionLoading("update");
    
    try {
      const response = await fetch(API_ENDPOINTS.SUBSCRIPTION_UPDATE, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${authService.getToken()}`
        },
        body: JSON.stringify({
          auto_renewal: autoRenewal
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(result.message);
        fetchSubscriptionStatus();
      } else {
        const error = await response.json();
        alert(`Hata: ${error.detail}`);
      }
    } catch (error) {
      console.error("Güncelleme başarısız:", error);
      alert("İşlem sırasında bir hata oluştu.");
    } finally {
      setActionLoading(null);
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
              Yönetilecek bir aboneliğiniz bulunmuyor.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Button 
              onClick={() => router.push("/plans")} 
              className="w-full"
            >
              Plan Seç
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const serviceEndDate = new Date(subscription.subscription?.current_period_end || "");
  const daysRemaining = subscription.subscription?.days_remaining || 0;
  const isCancelled = subscription.subscription?.cancellation_requested;

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Abonelik Yönetimi
          </h1>
          <p className="text-gray-600">
            Aboneliğinizi yönetin ve ayarlarınızı güncelleyin.
          </p>
        </div>

        {/* Abonelik Durumu */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <CreditCard className="h-5 w-5" />
              Abonelik Durumu
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <Label className="text-sm font-medium text-gray-500">Durum</Label>
                <div className="mt-1">
                  <Badge 
                    variant={
                      subscription.subscription?.status === "active" 
                        ? "default" 
                        : isCancelled 
                        ? "destructive" 
                        : "secondary"
                    }
                  >
                    {subscription.subscription?.status === "active" 
                      ? "Aktif" 
                      : isCancelled 
                      ? "İptal Edildi" 
                      : "Beklemede"}
                  </Badge>
                </div>
              </div>
              
              <div>
                <Label className="text-sm font-medium text-gray-500">Kalan Süre</Label>
                <p className="text-lg font-semibold text-blue-600 mt-1">
                  {daysRemaining} gün
                </p>
              </div>
              
              <div>
                <Label className="text-sm font-medium text-gray-500">Hizmet Bitiş Tarihi</Label>
                <p className="text-sm mt-1">
                  {serviceEndDate.toLocaleDateString("tr-TR")}
                </p>
              </div>
              
              <div>
                <Label className="text-sm font-medium text-gray-500">Otomatik Yenileme</Label>
                <div className="mt-1">
                  <Badge variant={subscription.subscription?.auto_renewal ? "default" : "secondary"}>
                    {subscription.subscription?.auto_renewal ? "Açık" : "Kapalı"}
                  </Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* İptal Durumu Uyarısı */}
        {isCancelled && (
          <Alert className="mb-6">
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <strong>Aboneliğiniz iptal edildi.</strong> Hizmetiniz mevcut dönem sonuna kadar 
              devam edecek. İsterseniz aboneliğinizi yeniden aktifleştirebilirsiniz.
            </AlertDescription>
          </Alert>
        )}

        {/* Abonelik Ayarları */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Abonelik Ayarları
            </CardTitle>
            <CardDescription>
              Aboneliğinizin ayarlarını buradan yönetebilirsiniz.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Otomatik Yenileme */}
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h3 className="font-medium">Otomatik Yenileme</h3>
                <p className="text-sm text-gray-500">
                  Aboneliğinizin otomatik olarak yenilenmesini sağlar
                </p>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant={subscription.subscription?.auto_renewal ? "default" : "secondary"}>
                  {subscription.subscription?.auto_renewal ? "Açık" : "Kapalı"}
                </Badge>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleUpdateAutoRenewal(!subscription.subscription?.auto_renewal)}
                  disabled={actionLoading === "update"}
                >
                  {actionLoading === "update" ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    subscription.subscription?.auto_renewal ? "Kapat" : "Aç"
                  )}
                </Button>
              </div>
            </div>

            {/* İptal/Reaktif Etme */}
            <div className="flex items-center justify-between p-4 border rounded-lg">
              <div>
                <h3 className="font-medium">
                  {isCancelled ? "Aboneliği Yeniden Aktifleştir" : "Aboneliği İptal Et"}
                </h3>
                <p className="text-sm text-gray-500">
                  {isCancelled 
                    ? "İptal edilmiş aboneliğinizi yeniden aktifleştirin"
                    : "Aboneliğinizi iptal edin (mevcut dönem sonuna kadar hizmet devam eder)"
                  }
                </p>
              </div>
              <div className="flex gap-2">
                {isCancelled ? (
                  <Button
                    onClick={handleReactivate}
                    disabled={actionLoading === "reactivate"}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    {actionLoading === "reactivate" ? (
                      <RefreshCw className="h-4 w-4 animate-spin" />
                    ) : (
                      <>
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Yeniden Aktifleştir
                      </>
                    )}
                  </Button>
                ) : (
                  <Button
                    onClick={() => router.push("/subscription/cancel")}
                    variant="destructive"
                  >
                    <X className="h-4 w-4 mr-2" />
                    İptal Et
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Önemli Bilgiler */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Önemli Bilgiler
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3 text-sm text-gray-600">
              <div className="flex items-start gap-2">
                <Clock className="h-4 w-4 mt-0.5 text-blue-500" />
                <div>
                  <strong>Hizmet Süresi:</strong> Aboneliğinizi iptal etseniz bile, 
                  ödediğiniz süre boyunca hizmetlerimizi kullanmaya devam edebilirsiniz.
                </div>
              </div>
              
              <div className="flex items-start gap-2">
                <Calendar className="h-4 w-4 mt-0.5 text-green-500" />
                <div>
                  <strong>Otomatik Yenileme:</strong> Bu seçenek kapalıysa, aboneliğiniz 
                  mevcut dönem sonunda otomatik olarak yenilenmeyecektir.
                </div>
              </div>
              
              <div className="flex items-start gap-2">
                <RefreshCw className="h-4 w-4 mt-0.5 text-purple-500" />
                <div>
                  <strong>Yeniden Aktifleştirme:</strong> İptal edilmiş aboneliğinizi 
                  istediğiniz zaman yeniden aktifleştirebilirsiniz.
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Geri Dön Butonu */}
        <div className="mt-8 text-center">
          <Button 
            onClick={() => router.push("/dashboard")} 
            variant="outline"
          >
            Dashboard'a Dön
          </Button>
        </div>
      </div>
    </DashboardLayout>
  );
}

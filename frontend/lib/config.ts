export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const API_ENDPOINTS = {
  SUBSCRIPTION_STATUS: `${API_BASE_URL}/subscription/status`,
  SUBSCRIPTION_CANCEL: `${API_BASE_URL}/subscription/cancel`,
  SUBSCRIPTION_REACTIVATE: `${API_BASE_URL}/subscription/reactivate`,
  SUBSCRIPTION_UPDATE: `${API_BASE_URL}/subscription/update`,
  CANCELLATION_REASONS: `${API_BASE_URL}/subscription/cancellation-reasons`,
} as const;

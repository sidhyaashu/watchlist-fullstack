export interface BaseAPIResponse<T> {
  success: boolean;
  message: string;
  data: T | null;
}

export interface MessageResponse {
  status: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token?: string;
}

export interface VerifyResetOTPResponse {
  reset_token: string;
}

export interface ProfileResponse {
  user_id: number;
  email: string;
  name: string;
  phone: string | null;
  auth_provider: "local" | "google" | "both";
}

export interface ApiError {
  message: string;
  status?: number;
  errors?: unknown;
  originalError?: unknown;
}

export interface AuthState {
  user: ProfileResponse | null;
  access_token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

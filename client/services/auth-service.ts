import { apiClient, refreshClient } from "../lib/api-client";
import { 
  BaseAPIResponse, 
  TokenResponse, 
  MessageResponse, 
  VerifyResetOTPResponse, 
  ProfileResponse 
} from "../types/api";
import { 
  LoginInput, 
  RegisterInput, 
  ForgotPasswordInput, 
  VerifyResetOTPInput, 
  ResetPasswordInput,
  ChangePasswordInput,
  SetupPasswordInput
} from "../schemas/auth";

export const authService = {
  // Local Auth
  register: async (data: RegisterInput) => {
    const response = await apiClient.post<BaseAPIResponse<MessageResponse>>(
      "/api/v1/auth/register", 
      data
    );
    return response.data;
  },

  login: async (data: LoginInput) => {
    const response = await apiClient.post<BaseAPIResponse<TokenResponse>>(
      "/api/v1/auth/login", 
      data
    );
    return response.data;
  },

  forgotPassword: async (data: ForgotPasswordInput) => {
    const response = await apiClient.post<BaseAPIResponse<MessageResponse>>(
      "/api/v1/auth/forgot-password", 
      data
    );
    return response.data;
  },

  verifyResetOtp: async (data: VerifyResetOTPInput) => {
    const response = await apiClient.post<BaseAPIResponse<VerifyResetOTPResponse>>(
      "/api/v1/auth/verify-reset-otp", 
      data
    );
    return response.data;
  },

  resetPassword: async (data: ResetPasswordInput) => {
    const response = await apiClient.post<BaseAPIResponse<MessageResponse>>(
      "/api/v1/auth/reset-password", 
      data
    );
    return response.data;
  },

  verifyEmail: async (token: string) => {
    const response = await apiClient.get<BaseAPIResponse<null>>(
      `/api/v1/auth/verify-email?token=${token}`
    );
    return response.data;
  },

  resendVerification: async (email: string) => {
    const response = await apiClient.post<BaseAPIResponse<MessageResponse>>(
      "/api/v1/auth/resend-verification", 
      { email }
    );
    return response.data;
  },

  // Session
  logout: async () => {
    const response = await apiClient.post<BaseAPIResponse<MessageResponse>>(
      "/api/v1/auth/logout", 
      {}
    );
    return response.data;
  },

  logoutAll: async () => {
    const response = await apiClient.post<BaseAPIResponse<MessageResponse>>(
      "/api/v1/auth/logout-all"
    );
    return response.data;
  },

  refresh: async () => {
    try {
      // We use refreshClient which shares the base config but lacks interceptors
      const response = await refreshClient.post<BaseAPIResponse<TokenResponse>>(
        "/api/v1/auth/refresh"
      );
      return response.data;
    } catch (error: any) {
      const isFatal = error.response?.status === 403 || error.response?.status === 401;
      if (isFatal) {
        const { setRefreshFailed } = await import("../lib/api-client");
        setRefreshFailed(true);
      }
      throw error;
    }
  },

  // Social
  getGoogleLoginUrl: () => `${process.env.NEXT_PUBLIC_API_URL || "http://localhost"}/api/v1/auth/google/login`,

  // User Profile
  getProfile: async () => {
    const response = await apiClient.get<BaseAPIResponse<ProfileResponse>>(
      "/api/v1/user/"
    );
    return response.data;
  },

  changePassword: async (data: ChangePasswordInput) => {
    const response = await apiClient.post<BaseAPIResponse<MessageResponse>>(
      "/api/v1/user/change-password", 
      data
    );
    return response.data;
  },

  requestSetupPasswordOtp: async () => {
    const response = await apiClient.post<BaseAPIResponse<MessageResponse>>(
      "/api/v1/user/setup-password/request-otp"
    );
    return response.data;
  },

  setupPasswordVerify: async (data: SetupPasswordInput) => {
    const response = await apiClient.post<BaseAPIResponse<MessageResponse>>(
      "/api/v1/user/setup-password/verify", 
      data
    );
    return response.data;
  },

  deleteAccount: async () => {
    const response = await apiClient.delete<BaseAPIResponse<MessageResponse>>(
      "/api/v1/user/"
    );
    return response.data;
  },
};

import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import { TokenResponse, BaseAPIResponse, ApiError } from "../types/api";
import { store } from "../store";
import { updateTokens, logout } from "../store/slices/auth-slice";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

export const refreshClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

// Response Interceptor for Token Refresh
let isRefreshing = false;
export let refreshFailed = false; // Persistent flag to stop loops

export const setRefreshFailed = (val: boolean) => {
  refreshFailed = val;
};
let failedQueue: Array<{ 
  resolve: (token: string | null) => void; 
  reject: (error: unknown) => void; 
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Request Interceptor
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // If we know a refresh recently failed, don't even try with the old token
    if (refreshFailed) {
      delete config.headers.Authorization;
      return config;
    }

    const access = store.getState().auth.access_token;
    if (access && config.headers) {
      config.headers.Authorization = `Bearer ${access}`;
    } else if (config.headers) {
      delete config.headers.Authorization;
      delete apiClient.defaults.headers.common["Authorization"];
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (!originalRequest) return Promise.reject(error);

    const isAuthEndpoint = originalRequest.url?.includes('/auth/login') || 
                           originalRequest.url?.includes('/auth/register') ||
                           originalRequest.url?.includes('/auth/refresh');

    // 1. Handle 403 Forbidden (Account Banned/Inactive) - Fatal Error
    if (error.response?.status === 403 && !isAuthEndpoint) {
        refreshFailed = true; // Block further refresh attempts
        store.dispatch(logout());
        if (typeof window !== "undefined") {
            window.location.href = "/login?error=account_invalid";
        }
        return new Promise(() => {}); // Stop error bubbling
    }

    // 2. Handle 401 Unauthorized (Token Expired)
    if (error.response?.status === 401 && !originalRequest._retry && !isAuthEndpoint) {
      // If we already failed a refresh, don't try again
      if (refreshFailed) {
          store.dispatch(logout());
          return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise<string | null>((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            if (originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${token}`;
            }
            return apiClient(originalRequest);
          })
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const response = await refreshClient.post<BaseAPIResponse<TokenResponse>>(
          "/api/v1/auth/refresh",
          {}
        );

        if (response.data.success && response.data.data) {
          const { access_token } = response.data.data;
          store.dispatch(updateTokens({ access_token }));
          
          apiClient.defaults.headers.common["Authorization"] = `Bearer ${access_token}`;
          if (originalRequest.headers) {
            originalRequest.headers["Authorization"] = `Bearer ${access_token}`;
          }
          
          processQueue(null, access_token);
          return apiClient(originalRequest);
        }
      } catch (refreshError: any) {
        refreshFailed = true; // Mark as failed permanently for this session
        processQueue(refreshError, null);
        store.dispatch(logout());
        
        if (typeof window !== "undefined") {
          const path = window.location.pathname;
          const isAuthPage = path.startsWith('/login') || 
                             path.startsWith('/register') ||
                             path.startsWith('/forgot-password') ||
                             path.startsWith('/reset-password') ||
                             path.startsWith('/verify-email');
          
          if (!isAuthPage) {
            const isForbidden = refreshError.response?.status === 403;
            window.location.href = `/login?session_expired=true${isForbidden ? '&error=account_invalid' : ''}`;
            // Return an unresolved promise to prevent the error from bubbling up 
            return new Promise(() => {});
          }
        }
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // Standardize Error Output
    const responseData = error.response?.data as any;
    const errorMessage = responseData?.message || responseData?.detail || error.message || "An unexpected error occurred";

    const apiError: ApiError = {
      message: errorMessage,
      status: error.response?.status,
      errors: responseData?.data?.errors || responseData?.errors || null,
      originalError: error
    };

    return Promise.reject(apiError);
  }
);

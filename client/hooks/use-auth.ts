"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { authService } from "../services/auth-service";
import { useAppDispatch, useAppSelector } from "../store";
import { setCredentials, logout as logoutAction, updateUser, setError, setLoading, updateTokens } from "../store/slices/auth-slice";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { LoginInput, RegisterInput } from "../schemas/auth";
import { ApiError } from "../types/api";

export const useAuth = () => {
  const dispatch = useAppDispatch();
  const { user, isAuthenticated, isLoading, error } = useAppSelector((state) => state.auth);
  const router = useRouter();
  const queryClient = useQueryClient();

  // Profile Query
  const profileQuery = useQuery({
    queryKey: ["profile"],
    queryFn: authService.getProfile,
    enabled: typeof window !== "undefined" && 
             !window.location.pathname.startsWith('/login') && 
             !window.location.pathname.startsWith('/register') &&
             !window.location.pathname.startsWith('/forgot-password') &&
             !window.location.pathname.startsWith('/reset-password') &&
             !window.location.pathname.startsWith('/verify-email') &&
             !window.location.pathname.startsWith('/auth/callback'),
    onSuccess: (response) => {
      if (response.success && response.data) {
        dispatch(updateUser(response.data));
      }
    },
    onError: () => {
      // Handled automatically by the axios interceptor on 401
    },
  });

  // Login Mutation
  const loginMutation = useMutation({
    mutationFn: authService.login,
    onSuccess: (response) => {
      if (response.success && response.data) {
        const { access_token } = response.data;
        dispatch(setLoading(true));
        
        // Set the token first so getProfile can use it in the Authorization header
        dispatch(updateTokens({ access_token }));

        authService.getProfile().then((profileRes) => {
          if (profileRes.success && profileRes.data) {
            dispatch(setCredentials({
              user: profileRes.data,
              access_token
            }));
            toast.success("Welcome back!");
            router.push("/dashboard");
          }
        }).catch((err: ApiError) => {
          toast.error(err.message || "Failed to load profile after login");
        }).finally(() => {
          dispatch(setLoading(false));
        });
      }
    },
    onError: (err: ApiError) => {
      const msg = err.message || "Login failed";
      toast.error(msg);
      dispatch(setError(msg));
    },
  });

  // Register Mutation
  const registerMutation = useMutation({
    mutationFn: authService.register,
    onSuccess: (response) => {
      if (response.success) {
        toast.success(response.message || "Registration request received. Please check your email.");
        router.push("/login");
      }
    },
    onError: (err: ApiError) => {
      toast.error(err.message || "Registration failed");
    },
  });

  // Logout Mutation
  const logoutMutation = useMutation({
    mutationFn: () => authService.logout(),
    onSettled: () => {
      dispatch(logoutAction());
      queryClient.clear();
      router.push("/login");
      toast.success("Logged out successfully");
    },
  });

  return {
    user,
    isAuthenticated,
    isLoading: isLoading || profileQuery.isFetching || loginMutation.isLoading,
    error,
    login: (data: LoginInput) => loginMutation.mutate(data),
    register: (data: RegisterInput) => registerMutation.mutate(data),
    logout: () => logoutMutation.mutate(),
    isLoggingIn: loginMutation.isLoading,
    isRegistering: registerMutation.isLoading,
    authProvider: user?.auth_provider
  };
};

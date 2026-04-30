"use client";

import { useEffect, useRef } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useAppDispatch } from "@/store";
import { setCredentials, setError, updateTokens } from "@/store/slices/auth-slice";
import { authService } from "@/services/auth-service";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";
import { apiClient } from "@/lib/api-client";

/**
 * OAuth Callback Page
 * Handles the redirect from Google OAuth after backend authentication.
 * Backend redirects to: /auth/callback?success=true and sets HttpOnly cookie.
 */
export default function AuthCallbackPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const dispatch = useAppDispatch();
  const handled = useRef(false);

  useEffect(() => {
    if (handled.current) return;
    handled.current = true;

    const error = searchParams.get("error");
    const success = searchParams.get("success");

    if (error || !success) {
      toast.error("Google authentication failed. Please try again.");
      dispatch(setError("OAuth authentication failed."));
      router.replace("/login?error=auth_failed");
      return;
    }

    // Explicitly call refresh to get the access token from the newly set HttpOnly cookie
    apiClient.post("/api/v1/auth/refresh", {}, { withCredentials: true })
      .then((response: any) => {
        if (response.data?.success && response.data?.data) {
           const { access_token } = response.data.data;
           
           // Fetch profile using the new access token
           // (Interceptor will attach the token once we dispatch to Redux, but we can also just rely on interceptor logic if we dispatched)
           dispatch(updateTokens({ access_token }));
           
           return authService.getProfile().then((profileRes) => {
              if (profileRes.success && profileRes.data) {
                 dispatch(setCredentials({ user: profileRes.data, access_token }));
                 toast.success("Welcome! Signed in with Google.");
                 router.replace("/dashboard");
              }
           });
        }
      })
      .catch((err) => {
         toast.error("Failed to load your profile. Please try again.");
         router.replace("/login?error=auth_failed");
      });
  }, [searchParams, router, dispatch]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 gap-4">
      <Loader2 className="h-10 w-10 text-indigo-600 animate-spin" />
      <p className="text-slate-600 text-sm font-medium">
        Completing Google sign-in...
      </p>
    </div>
  );
}

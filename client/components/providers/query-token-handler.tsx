"use client";

import { useEffect, useRef } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { useAppDispatch } from "../../store";
import { setCredentials, setLoading } from "../../store/slices/auth-slice";
import { authService } from "../../services/auth-service";
import { toast } from "sonner";

export function QueryTokenHandler() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const dispatch = useAppDispatch();
  const processingRef = useRef(false);

  useEffect(() => {
    if (processingRef.current) return;

    // OAuth Token handling removed - now handled by /auth/callback/page.tsx

    // 2. Handle Email Verification Token (Legacy Redirect)
    const verifyToken = searchParams.get("verify_token");
    if (verifyToken) {
      router.replace(`/verify-email?token=${verifyToken}`);
    }

    // 3. Handle Session Expired
    if (searchParams.get("session_expired") === "true") {
      toast.error("Your session has expired. Please log in again.");
      router.replace("/login");
    }
  }, [searchParams, dispatch, router]);

  return null;
}

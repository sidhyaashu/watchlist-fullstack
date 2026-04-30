"use client";

import { useEffect, useState, useCallback, useRef } from "react";
import { useSearchParams } from "next/navigation";
import { authService } from "@/services/auth-service";
import { AuthLayout } from "@/components/layouts/auth-layout";
import { Button } from "@/components/ui/button";
import { Loader2, CheckCircle, XCircle } from "lucide-react";
import { toast } from "sonner";
import Link from "next/link";
import { ApiError } from "@/types/api";

export default function VerifyEmailPage() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");
  const [status, setStatus] = useState<"verifying" | "success" | "error">("verifying");
  const [message, setMessage] = useState("We are verifying your email address...");
  const verifyAttempted = useRef(false);

  const verify = useCallback(async (tokenValue: string) => {
    try {
      const response = await authService.verifyEmail(tokenValue);
      if (response.success) {
        setStatus("success");
        setMessage("Email verified successfully! You can now login.");
        toast.success("Email verified!");
      } else {
        setStatus("error");
        setMessage(response.message || "Verification failed.");
      }
    } catch (err: unknown) {
      const apiError = err as ApiError;
      setStatus("error");
      setMessage(apiError.message || "Invalid or expired verification link.");
    }
  }, []);

  useEffect(() => {
    if (!token) {
      setStatus("error");
      setMessage("Missing verification token.");
      return;
    }

    if (!verifyAttempted.current) {
      verifyAttempted.current = true;
      verify(token);
    }
  }, [token, verify]);

  return (
    <AuthLayout title="Email Verification">
      <div className="flex flex-col items-center justify-center space-y-6 text-center">
        {status === "verifying" && (
          <>
            <Loader2 className="h-12 w-12 text-indigo-600 animate-spin" />
            <p className="text-slate-600">{message}</p>
          </>
        )}

        {status === "success" && (
          <>
            <CheckCircle className="h-12 w-12 text-green-500" />
            <p className="text-slate-600">{message}</p>
            <Button asChild className="w-full">
              <Link href="/login">Continue to Login</Link>
            </Button>
          </>
        )}

        {status === "error" && (
          <>
            <XCircle className="h-12 w-12 text-red-500" />
            <p className="text-slate-600">{message}</p>
            <Button asChild variant="outline" className="w-full">
              <Link href="/login">Back to Login</Link>
            </Button>
          </>
        )}
      </div>
    </AuthLayout>
  );
}

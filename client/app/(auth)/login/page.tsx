"use client";

import { AuthLayout } from "@/components/layouts/auth-layout";
import { LoginForm } from "@/components/auth/login-form";
import { useAuth } from "@/hooks/use-auth";
import { useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";

export default function LoginPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const searchParams = useSearchParams();

  // Handle redirects
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isLoading, isAuthenticated, router]);

  // Handle error messages from query params
  useEffect(() => {
    const error = searchParams.get("error");
    const sessionExpired = searchParams.get("session_expired");

    if (error || sessionExpired) {
      if (sessionExpired) {
        toast.error("Your session has expired. Please login again.");
      } else if (error === "auth_failed") {
        toast.error("Authentication failed. Please try again.");
      } else if (error === "mismatched_provider") {
        toast.error("Account already exists with a different login method. Please use your email and password.");
      } else if (error === "account_banned") {
        toast.error("Your account has been deactivated or banned.");
      }

      // Clear the query params after a small delay
      const timer = setTimeout(() => {
        router.replace("/login");
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [searchParams, router]);

  return (
    <AuthLayout 
      title="Welcome back" 
      subtitle="Enter your credentials to access your account"
    >
      <LoginForm />
    </AuthLayout>
  );
}

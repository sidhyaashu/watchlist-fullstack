"use client";

import { AuthLayout } from "@/components/layouts/auth-layout";
import { RegisterForm } from "@/components/auth/register-form";
import { useAuth } from "@/hooks/use-auth";
import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function RegisterPage() {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push("/dashboard");
    }
  }, [isLoading, isAuthenticated, router]);

  return (
    <AuthLayout 
      title="Create an account" 
      subtitle="Join InvestCode to start managing your investments"
    >
      <RegisterForm />
    </AuthLayout>
  );
}

"use client";

import { AuthLayout } from "@/components/layouts/auth-layout";
import { ResetPasswordForm } from "@/components/auth/reset-password-form";

export default function ResetPasswordPage() {
  return (
    <AuthLayout 
      title="Reset your password" 
      subtitle="Follow the instructions to regain access to your account"
    >
      <ResetPasswordForm />
    </AuthLayout>
  );
}

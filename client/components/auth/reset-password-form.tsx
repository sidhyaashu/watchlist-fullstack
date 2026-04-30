"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { resetPasswordSchema, ResetPasswordInput, verifyResetOTPSchema, VerifyResetOTPInput } from "../../schemas/auth";
import { authService } from "../../services/auth-service";
import { Button } from "../ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "../ui/form";
import { Input } from "../ui/input";
import { Loader2 } from "lucide-react";
import { useState, useEffect } from "react";
import { toast } from "sonner";
import { useRouter, useSearchParams } from "next/navigation";
import { ApiError } from "../../types/api";

export function ResetPasswordForm() {
  const [step, setStep] = useState<1 | 2>(1);
  const [isOtpSubmitting, setIsOtpSubmitting] = useState(false);
  const [isResetSubmitting, setIsResetSubmitting] = useState(false);
  const [resetToken, setResetToken] = useState<string | null>(null);
  
  const searchParams = useSearchParams();
  const router = useRouter();
  const emailParam = searchParams.get("email") || "";

  const otpForm = useForm<VerifyResetOTPInput>({
    resolver: zodResolver(verifyResetOTPSchema),
    defaultValues: {
      email: emailParam,
      otp: "",
    },
  });

  const resetForm = useForm<ResetPasswordInput>({
    resolver: zodResolver(resetPasswordSchema),
    defaultValues: {
      reset_token: "",
      new_password: "",
      confirm_password: "",
    },
  });

  // Sync resetToken to form state when it changes
  useEffect(() => {
    if (resetToken) {
      resetForm.setValue("reset_token", resetToken);
    }
  }, [resetToken, resetForm]);

  const onOtpSubmit = async (data: VerifyResetOTPInput) => {
    setIsOtpSubmitting(true);
    try {
      const response = await authService.verifyResetOtp(data);
      if (response.success && response.data) {
        setResetToken(response.data.reset_token);
        setStep(2);
        toast.success("OTP verified! Set your new password.");
      }
    } catch (err: unknown) {
      const apiError = err as ApiError;
      toast.error(apiError.message || "Invalid or expired OTP");
    } finally {
      setIsOtpSubmitting(false);
    }
  };

  const onResetSubmit = async (data: ResetPasswordInput) => {
    // Double check token is present
    if (!data.reset_token && resetToken) {
      data.reset_token = resetToken;
    }

    if (!data.reset_token) {
      toast.error("Session expired. Please start over.");
      setStep(1);
      return;
    }

    setIsResetSubmitting(true);
    try {
      const response = await authService.resetPassword(data);
      if (response.success) {
        toast.success("Password reset successful! You can now login.");
        router.push("/login");
      }
    } catch (err: unknown) {
      const apiError = err as ApiError;
      toast.error(apiError.message || "Failed to reset password");
      if (apiError.status === 401) {
        setStep(1); // Token might have expired
      }
    } finally {
      setIsResetSubmitting(false);
    }
  };

  if (step === 1) {
    return (
      <Form {...otpForm}>
        <form onSubmit={otpForm.handleSubmit(onOtpSubmit)} className="space-y-4">
          <FormField
            control={otpForm.control}
            name="email"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Email</FormLabel>
                <FormControl>
                  <Input {...field} disabled={!!emailParam || isOtpSubmitting} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <FormField
            control={otpForm.control}
            name="otp"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Enter 6-digit OTP</FormLabel>
                <FormControl>
                  <Input placeholder="123456" {...field} maxLength={6} disabled={isOtpSubmitting} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
          <Button type="submit" className="w-full" disabled={isOtpSubmitting}>
            {isOtpSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Verify OTP
          </Button>
        </form>
      </Form>
    );
  }

  return (
    <Form {...resetForm} key="reset-step">
      <form onSubmit={resetForm.handleSubmit(onResetSubmit)} className="space-y-4">

        <FormField
          control={resetForm.control}
          name="new_password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>New Password</FormLabel>
              <FormControl>
                <Input type="password" placeholder="••••••••" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={resetForm.control}
          name="confirm_password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Confirm New Password</FormLabel>
              <FormControl>
                <Input type="password" placeholder="••••••••" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" className="w-full" disabled={isResetSubmitting}>
          {isResetSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Reset Password
        </Button>
      </form>
    </Form>
  );
}

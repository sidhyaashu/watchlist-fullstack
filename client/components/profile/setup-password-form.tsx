"use client";

import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { setupPasswordSchema, SetupPasswordInput } from "../../schemas/auth";
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
import { useState } from "react";
import { toast } from "sonner";
import { ApiError } from "../../types/api";

export function SetupPasswordForm() {
  const [step, setStep] = useState<1 | 2>(1);
  const [isLoading, setIsLoading] = useState(false);

  const form = useForm<SetupPasswordInput>({
    resolver: zodResolver(setupPasswordSchema),
    defaultValues: {
      otp: "",
      new_password: "",
      confirm_password: "",
    },
  });

  const handleRequestOtp = async () => {
    setIsLoading(true);
    try {
      const response = await authService.requestSetupPasswordOtp();
      if (response.success) {
        setStep(2);
        toast.success("OTP sent to your email!");
      }
    } catch (err: unknown) {
      const apiError = err as ApiError;
      toast.error(apiError.message || "Failed to request OTP");
    } finally {
      setIsLoading(false);
    }
  };

  const onSubmit = async (data: SetupPasswordInput) => {
    setIsLoading(true);
    try {
      const response = await authService.setupPasswordVerify(data);
      if (response.success) {
        toast.success("Password set successfully! You can now login with your password too.");
        window.location.reload();
      }
    } catch (err: unknown) {
      const apiError = err as ApiError;
      toast.error(apiError.message || "Failed to set password");
    } finally {
      setIsLoading(false);
    }
  };

  if (step === 1) {
    return (
      <div className="space-y-4">
        <p className="text-sm text-slate-600">
          Since you signed up with Google, you don&apos;t have a local password. 
          Set one up to enable direct login.
        </p>
        <Button onClick={handleRequestOtp} disabled={isLoading}>
          {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Request Setup OTP
        </Button>
      </div>
    );
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="otp"
          render={({ field }) => (
            <FormItem>
              <FormLabel>OTP from Email</FormLabel>
              <FormControl>
                <Input placeholder="123456" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <FormField
          control={form.control}
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
          control={form.control}
          name="confirm_password"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Confirm Password</FormLabel>
              <FormControl>
                <Input type="password" placeholder="••••••••" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={isLoading}>
          {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          Set Password
        </Button>
      </form>
    </Form>
  );
}

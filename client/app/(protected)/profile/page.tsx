"use client";

import { DashboardLayout } from "@/components/layouts/dashboard-layout";
import { useAuth } from "@/hooks/use-auth";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ChangePasswordForm } from "@/components/profile/change-password-form";
import { SetupPasswordForm } from "@/components/profile/setup-password-form";
import { Button } from "@/components/ui/button";
import { authService } from "@/services/auth-service";
import { useState } from "react";
import { toast } from "sonner";
import { ApiError } from "@/types/api";

export default function ProfilePage() {
  const { user, logout } = useAuth();
  const [isDeleting, setIsDeleting] = useState(false);

  const canChangePassword = user?.auth_provider === "local" || user?.auth_provider === "both";
  const needsPasswordSetup = user?.auth_provider === "google";

  const handleDeleteAccount = async () => {
    if (confirm("Are you absolutely sure you want to delete your account? This action cannot be undone.")) {
      setIsDeleting(true);
      try {
        const response = await authService.deleteAccount();
        if (response.success) {
          toast.success("Account deleted successfully.");
          logout();
        }
      } catch (err: unknown) {
        const apiError = err as ApiError;
        toast.error(apiError.message || "Failed to delete account");
      } finally {
        setIsDeleting(false);
      }
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-3xl space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Profile Settings</h1>
          <p className="text-slate-500">Manage your account information and security.</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Personal Information</CardTitle>
            <CardDescription>Your basic account details.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-1">
                <p className="text-sm font-medium text-slate-500">Full Name</p>
                <p className="text-base font-semibold">{user?.name}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-slate-500">Email Address</p>
                <p className="text-base font-semibold">{user?.email}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-slate-500">Phone Number</p>
                <p className="text-base font-semibold">{user?.phone || "Not provided"}</p>
              </div>
              <div className="space-y-1">
                <p className="text-sm font-medium text-slate-500">Auth Method</p>
                <p className="text-base font-semibold capitalize">{user?.auth_provider}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{needsPasswordSetup ? "Setup Password" : "Security"}</CardTitle>
            <CardDescription>
              {needsPasswordSetup 
                ? "Set a local password for your Google account." 
                : "Change your password to keep your account secure."}
            </CardDescription>
          </CardHeader>
          <CardContent>
            {canChangePassword && <ChangePasswordForm />}
            {needsPasswordSetup && <SetupPasswordForm />}
          </CardContent>
        </Card>

        <Card className="border-red-100 bg-red-50/30">
          <CardHeader>
            <CardTitle className="text-red-600">Danger Zone</CardTitle>
            <CardDescription>Irreversible actions for your account.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex flex-col space-y-2">
              <p className="text-sm text-slate-600">
                This will invalidate all your active sessions on other devices.
              </p>
              <Button 
                variant="outline" 
                className="w-fit border-red-200 text-red-600 hover:bg-red-100 hover:text-red-700"
                onClick={async () => {
                  try {
                    await authService.logoutAll();
                    toast.success("Signed out from all devices");
                    logout();
                  } catch (err: unknown) {
                    const apiError = err as ApiError;
                    toast.error(apiError.message || "Logout failed");
                  }
                }}
              >
                Sign out from all devices
              </Button>
            </div>
            
            <div className="pt-4 border-t border-red-100">
              <p className="text-sm text-slate-600 mb-2">
                Once you delete your account, there is no going back. Please be certain.
              </p>
              <Button 
                variant="destructive" 
                onClick={handleDeleteAccount}
                disabled={isDeleting}
              >
                Delete My Account
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}

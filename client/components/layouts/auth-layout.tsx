"use client";

import { ReactNode } from "react";
import Link from "next/link";

interface AuthLayoutProps {
  children: ReactNode;
  title: string;
  subtitle?: string;
}

export function AuthLayout({ children, title, subtitle }: AuthLayoutProps) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-2xl shadow-xl border border-slate-100">
        <div className="text-center">
          <Link href="/" className="inline-block">
            <h1 className="text-3xl font-extrabold text-indigo-600 tracking-tight">InvestCode</h1>
          </Link>
          <h2 className="mt-6 text-2xl font-bold text-slate-900">{title}</h2>
          {subtitle && (
            <p className="mt-2 text-sm text-slate-600">
              {subtitle}
            </p>
          )}
        </div>
        {children}
      </div>
    </div>
  );
}

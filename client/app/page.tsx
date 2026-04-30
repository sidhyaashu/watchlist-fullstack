import Link from "next/link";
import { Button } from "@/components/ui/button";
import { 
  Shield, 
  Zap, 
  BarChart3, 
  ArrowRight, 
  Globe, 
  Lock 
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="flex flex-col min-h-screen bg-white">
      {/* Navigation */}
      <header className="px-4 lg:px-6 h-16 flex items-center border-b border-slate-100 sticky top-0 bg-white/80 backdrop-blur-md z-50">
        <Link className="flex items-center justify-center" href="/">
          <span className="text-2xl font-bold text-indigo-600 tracking-tight">InvestCode</span>
        </Link>
        <nav className="ml-auto flex gap-4 sm:gap-6 items-center">
          <Link className="text-sm font-medium hover:text-indigo-600 transition-colors" href="/login">
            Login
          </Link>
          <Button asChild size="sm" className="bg-indigo-600 hover:bg-indigo-700">
            <Link href="/register">Get Started</Link>
          </Button>
        </nav>
      </header>

      <main className="flex-1">
        {/* Hero Section */}
        <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48 bg-slate-50">
          <div className="container px-4 md:px-6 mx-auto">
            <div className="flex flex-col items-center space-y-4 text-center">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl/none text-slate-900">
                  Secure Your Financial Future with <span className="text-indigo-600">InvestCode</span>
                </h1>
                <p className="mx-auto max-w-[700px] text-slate-500 md:text-xl dark:text-slate-400">
                  A production-grade investment platform designed for security, performance, and global access. 
                  Start managing your assets with confidence today.
                </p>
              </div>
              <div className="space-x-4">
                <Button asChild size="lg" className="bg-indigo-600 hover:bg-indigo-700 h-12 px-8">
                  <Link href="/register">
                    Create Account <ArrowRight className="ml-2 h-4 w-4" />
                  </Link>
                </Button>
                <Button asChild variant="outline" size="lg" className="h-12 px-8">
                  <Link href="/login">Sign In</Link>
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="w-full py-12 md:py-24 lg:py-32 bg-white">
          <div className="container px-4 md:px-6 mx-auto">
            <div className="grid gap-10 sm:grid-cols-2 lg:grid-cols-3">
              <div className="flex flex-col items-center space-y-4 text-center p-6 rounded-2xl hover:bg-slate-50 transition-colors">
                <div className="p-3 bg-indigo-100 rounded-xl text-indigo-600">
                  <Shield className="h-8 w-8" />
                </div>
                <h3 className="text-xl font-bold">Bank-Grade Security</h3>
                <p className="text-slate-500">
                  Your data is protected with HS256 JWT encryption, refresh token rotation, and multi-layered authentication.
                </p>
              </div>
              <div className="flex flex-col items-center space-y-4 text-center p-6 rounded-2xl hover:bg-slate-50 transition-colors">
                <div className="p-3 bg-indigo-100 rounded-xl text-indigo-600">
                  <Zap className="h-8 w-8" />
                </div>
                <h3 className="text-xl font-bold">Lightning Fast</h3>
                <p className="text-slate-500">
                  Powered by Next.js and high-performance backend microservices for near-instant responses and real-time updates.
                </p>
              </div>
              <div className="flex flex-col items-center space-y-4 text-center p-6 rounded-2xl hover:bg-slate-50 transition-colors">
                <div className="p-3 bg-indigo-100 rounded-xl text-indigo-600">
                  <BarChart3 className="h-8 w-8" />
                </div>
                <h3 className="text-xl font-bold">Smart Analytics</h3>
                <p className="text-slate-500">
                  Gain deep insights into your portfolio performance with our advanced analytical tools and historical tracking.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Trust Section */}
        <section className="w-full py-12 md:py-24 lg:py-32 bg-slate-900 text-white overflow-hidden">
          <div className="container px-4 md:px-6 mx-auto">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <h2 className="text-3xl font-bold tracking-tighter sm:text-5xl">Global Access, Local Security</h2>
                <p className="max-w-[900px] text-slate-400 md:text-xl/relaxed lg:text-base/relaxed xl:text-xl/relaxed">
                  Join thousands of users worldwide who trust InvestCode for their financial operations. 
                  Our infrastructure is distributed globally but secured with local precision.
                </p>
              </div>
              <div className="flex flex-wrap justify-center gap-8 md:gap-16 pt-8 opacity-50">
                <div className="flex items-center gap-2">
                  <Globe className="h-6 w-6" />
                  <span className="font-bold">Global Infrastructure</span>
                </div>
                <div className="flex items-center gap-2">
                  <Lock className="h-6 w-6" />
                  <span className="font-bold">HS256 Verified</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="w-full py-12 md:py-24 lg:py-32 bg-indigo-600">
          <div className="container px-4 md:px-6 mx-auto">
            <div className="flex flex-col items-center justify-center space-y-4 text-center text-white">
              <div className="space-y-2">
                <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">Ready to Start?</h2>
                <p className="mx-auto max-w-[600px] text-indigo-100 md:text-xl">
                  Sign up now and get full access to our investment suite. No credit card required to start.
                </p>
              </div>
              <Button asChild size="lg" className="bg-white text-indigo-600 hover:bg-slate-100 h-12 px-8 font-bold">
                <Link href="/register">Join Now — It&apos;s Free</Link>
              </Button>
            </div>
          </div>
        </section>
      </main>

      <footer className="flex flex-col gap-2 sm:flex-row py-6 w-full shrink-0 items-center px-4 md:px-6 border-t border-slate-100">
        <p className="text-xs text-slate-500">© 2026 InvestCode Inc. All rights reserved.</p>
        <nav className="sm:ml-auto flex gap-4 sm:gap-6">
          <Link className="text-xs hover:underline underline-offset-4 text-slate-500" href="#">
            Terms of Service
          </Link>
          <Link className="text-xs hover:underline underline-offset-4 text-slate-500" href="#">
            Privacy
          </Link>
        </nav>
      </footer>
    </div>
  );
}

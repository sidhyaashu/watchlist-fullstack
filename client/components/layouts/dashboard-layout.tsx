"use client";

import { ReactNode, useEffect } from "react";
import { useAuth } from "../../hooks/use-auth";
import { useRouter } from "next/navigation";
import { 
  User, 
  LogOut, 
  LayoutDashboard, 
  Settings, 
  Bell,
  ListEnd,
  Activity,
  Sun,
  Moon
} from "lucide-react";
import { useTheme } from "../providers/theme-provider";
import Link from "next/link";
import { Button } from "../ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "../ui/dropdown-menu";
import { Avatar, AvatarFallback } from "../ui/avatar";

interface DashboardLayoutProps {
  children: ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  const { user, isAuthenticated, isLoading, logout } = useAuth();
  const { theme, setTheme, resolvedTheme } = useTheme();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/login");
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading || !isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-bg-1">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-stretch">
      {/* ── SIDE RAIL ── */}
      <aside className="hidden md:flex flex-col items-center w-[var(--side-rail-width)] bg-white/40 dark:bg-black/20 backdrop-blur-md border-r border-rule py-4 gap-2 z-30">
        <Link href="/dashboard" className="w-9 h-9 rounded-xl bg-accent-soft flex items-center justify-center text-accent hover:bg-accent hover:text-white transition-all mb-4">
          <LayoutDashboard size={20} />
        </Link>
        <Link href="/watchlists" className="w-9 h-9 rounded-xl bg-accent flex items-center justify-center text-white dark:text-bg-1 shadow-lg shadow-accent/30 mb-2">
          <ListEnd size={20} />
        </Link>
        <Link href="/dashboard" className="w-9 h-9 rounded-xl flex items-center justify-center text-ink-3 hover:bg-white/70 dark:hover:bg-white/5 hover:text-accent dark:hover:text-white transition-all">
          <Activity size={20} />
        </Link>
        
        <div className="mt-auto flex flex-col gap-2">
          <Link href="/settings" className="w-9 h-9 rounded-xl flex items-center justify-center text-ink-3 hover:bg-white/70 dark:hover:bg-white/5 hover:text-accent dark:hover:text-white transition-all">
            <Settings size={20} />
          </Link>
          <Button variant="ghost" size="icon" className="w-9 h-9 text-ink-3 hover:text-danger hover:bg-danger-soft dark:hover:bg-danger/10" onClick={logout}>
            <LogOut size={20} />
          </Button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 bg-transparent">
        {/* ── TOPBAR ── */}
        <header className="h-[var(--topbar-height)] border-b border-rule flex items-center justify-between px-6 bg-white/50 dark:bg-black/30 backdrop-blur-xl sticky top-0 z-20">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-accent to-accent-2 flex items-center justify-center text-white dark:text-bg-1 font-bold text-sm shadow-md shadow-accent/20">i</div>
              <span className="text-base font-bold text-ink tracking-tight">InvestKaro</span>
            </div>
            <div className="h-4 w-px bg-rule mx-1 hidden sm:block" />
            <span className="ts-eyebrow text-[10px] hidden sm:block">Watchlist</span>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="hidden lg:flex items-center gap-2">
              <span className="pill-dot text-[10.5px] px-3 py-1 bg-white/40 dark:bg-white/5 border border-rule rounded-full ts-mono flex items-center gap-1.5">
                <span className="w-1.5 h-1.5 rounded-full bg-good animate-pulse" />
                MARKET OPEN · NSE
              </span>
              <span className="text-[10.5px] px-3 py-1 bg-white/40 dark:bg-white/5 border border-rule rounded-full ts-mono">
                SENSEX <span className="text-good font-bold">+0.42%</span>
              </span>
            </div>
            
            <button 
              className="theme-toggle" 
              onClick={() => setTheme(resolvedTheme === 'dark' ? 'light' : 'dark')}
              title="Toggle theme"
            >
              {resolvedTheme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
            </button>

            <Button variant="ghost" size="icon" className="w-8 h-8 text-ink-3 hover:text-accent hover:bg-white/70 dark:hover:bg-white/5">
              <Bell size={18} />
            </Button>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="h-8 p-0 hover:bg-transparent">
                  <Avatar className="h-8 w-8 border border-white/80 shadow-sm">
                    <AvatarFallback className="bg-gradient-to-br from-accent-soft to-accent-2/10 text-accent font-bold text-xs">
                      {user?.name?.charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56 glass-card mt-2" align="end">
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-semibold leading-none">{user?.name}</p>
                    <p className="text-[11px] leading-none text-ink-3">{user?.email}</p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator className="bg-rule" />
                <DropdownMenuItem className="focus:bg-accent-soft focus:text-accent-deep cursor-pointer ts-body py-2.5">
                  <User size={16} className="mr-2 opacity-60" />
                  Profile
                </DropdownMenuItem>
                <DropdownMenuItem className="focus:bg-accent-soft focus:text-accent-deep cursor-pointer ts-body py-2.5">
                  <Settings size={16} className="mr-2 opacity-60" />
                  Settings
                </DropdownMenuItem>
                <DropdownMenuSeparator className="bg-rule" />
                <DropdownMenuItem className="text-danger focus:bg-danger-soft focus:text-danger-deep cursor-pointer ts-body py-2.5" onClick={logout}>
                  <LogOut size={16} className="mr-2 opacity-60" />
                  Sign Out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* ── PAGE BODY ── */}
        <main className="flex-1 overflow-auto p-6 md:p-8">
          <div className="max-w-[1320px] mx-auto w-full">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}

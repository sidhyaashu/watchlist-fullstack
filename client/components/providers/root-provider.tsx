"use client";

import { ReactNode, useState, useEffect } from "react";
import { Provider } from "react-redux";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { store, useAppDispatch, useAppSelector } from "../../store";
import { setCredentials, updateTokens, logout, setLoading } from "../../store/slices/auth-slice";
import { authService } from "../../services/auth-service";
import { Toaster } from "sonner";
import NextTopLoader from "nextjs-toploader";
import { QueryTokenHandler } from "./query-token-handler";
import { Suspense } from "react";

interface RootProviderProps {
  children: ReactNode;
}

function AuthInitializer({ children }: { children: ReactNode }) {
  const dispatch = useAppDispatch();
  const { isLoading } = useAppSelector((state) => state.auth);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // 1. Silent refresh check (looks for HttpOnly cookie)
        const refreshRes = await authService.refresh(); 
        if (refreshRes.success && refreshRes.data) {
          dispatch(updateTokens({ access_token: refreshRes.data.access_token }));
          
          // 2. Fetch profile immediately
          const profileRes = await authService.getProfile();
          if (profileRes.success && profileRes.data) {
             dispatch(setCredentials({ 
               user: profileRes.data, 
               access_token: refreshRes.data.access_token 
             }));
          }
        }
      } catch (err) {
        // No valid session found, which is fine for public pages
        dispatch(logout()); 
      } finally {
        dispatch(setLoading(false)); // Initialization complete
      }
    };

    initializeAuth();
  }, [dispatch]);

  // Prevent flicker: Don't show the app content until we know the auth status
  if (isLoading) {
    return null; // Or a FullScreenLoader if available
  }

  return <>{children}</>;
}

import { ThemeProvider } from "./theme-provider";

export function RootProvider({ children }: RootProviderProps) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: 1,
            refetchOnWindowFocus: false,
            staleTime: 5 * 60 * 1000, // 5 minutes
          },
        },
      })
  );

  return (
    <Provider store={store}>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider>
          <NextTopLoader
            color="var(--accent)"
            initialPosition={0.08}
            crawlSpeed={200}
            height={3}
            crawl={true}
            showSpinner={false}
            easing="ease"
            speed={200}
            shadow="0 0 10px var(--accent),0 0 5px var(--accent)"
          />
          <Suspense fallback={null}>
            <QueryTokenHandler />
          </Suspense>
          <AuthInitializer>
            {children}
          </AuthInitializer>
          <Toaster richColors position="top-right" closeButton />
        </ThemeProvider>
      </QueryClientProvider>
    </Provider>
  );
}

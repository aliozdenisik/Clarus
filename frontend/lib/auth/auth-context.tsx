"use client";

import { createContext, useContext, useState, useEffect } from "react";
import { logger } from "@/lib/logger";

interface User {
  id: number;
  email: string;
  name: string;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  backendStatus: 'online' | 'offline' | 'unknown';
  login: (email: string, password: string) => Promise<void>;
  loginWithGoogle: (credential: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [backendStatus, setBackendStatus] = useState<'online' | 'offline' | 'unknown'>('unknown');

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 10000); // 10s timeout
    
    try {
      const token = localStorage.getItem("access_token");
      if (token) {
        const response = await fetch("http://localhost:8000/api/auth/me", {
          headers: { Authorization: `Bearer ${token}` },
          signal: controller.signal,
        });
        clearTimeout(timeoutId);
        
        if (response.ok) {
          const data = await response.json();
          setUser(data);
          setBackendStatus('online');
        } else {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          setBackendStatus('online');  // Backend reachable, just auth failed
        }
      } else {
        setBackendStatus('online');  // No token, but backend assumed online
      }
    } catch (error) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        logger.error("Auth check timed out after 10s", error, {
          component: "AuthContext",
          action: "checkAuth",
          reason: "timeout",
        });
        setBackendStatus('offline');
      } else if (error instanceof TypeError && error.message === 'Failed to fetch') {
        logger.error("Auth check failed: network error", error, {
          component: "AuthContext",
          action: "checkAuth",
          reason: "network_error",
        });
        setBackendStatus('offline');
      } else {
        logger.error("Auth check failed", error, {
          component: "AuthContext",
          action: "checkAuth",
        });
        setBackendStatus('offline');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await fetch("http://localhost:8000/api/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error("Login failed");
    }

    const data = await response.json();
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    setUser(data.user);
  };

  const loginWithGoogle = async (credential: string) => {
    try {
      const response = await fetch("http://localhost:8000/api/auth/google", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: credential }),
      });

      if (!response.ok) {
        if (response.status === 400) {
          throw new Error("Google login failed. Please try again.");
        } else if (response.status >= 500) {
          throw new Error("Server error. Please try again later.");
        }
        const error = await response.json();
        throw new Error(error.detail || "Login failed");
      }

      const data = await response.json();
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      setUser(data.user);
    } catch (error) {
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        throw new Error("Connection failed. Please check your internet.");
      }
      throw error;
    }
  };

  const register = async (email: string, password: string, name: string) => {
    const response = await fetch("http://localhost:8000/api/auth/register", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, name }),
    });

    if (!response.ok) {
      throw new Error("Registration failed");
    }

    const data = await response.json();
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
    setUser(data.user);
  };

  const logout = async () => {
    try {
      const token = localStorage.getItem("access_token");
      if (token) {
        await fetch("http://localhost:8000/api/auth/logout", {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
        });
      }
    } finally {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, backendStatus, login, loginWithGoogle, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return context;
}

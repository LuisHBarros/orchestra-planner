import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { apiClient, User } from "@/lib/api";

/**
 * AuthContext
 * 
 * Manages user authentication state and provides methods for login/logout.
 */

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string) => Promise<void>;
  verifyToken: (token: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing token on mount
  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (token) {
      // In a real app, you'd verify the token with the backend
      // For now, we'll just assume it's valid
      apiClient.setToken(token);
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string) => {
    setIsLoading(true);
    try {
      await apiClient.requestMagicLink(email);
      // Magic link sent, user will verify via email
    } finally {
      setIsLoading(false);
    }
  };

  const verifyToken = async (token: string) => {
    setIsLoading(true);
    try {
      const userData = await apiClient.verifyMagicLink(token);
      setUser(userData);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    apiClient.clearToken();
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        verifyToken,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

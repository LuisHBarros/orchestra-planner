import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  ReactNode,
} from "react";
import { apiClient, User } from "@/lib/api";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string) => Promise<void>;
  verifyToken: (token: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (!apiClient.hasTokens()) {
      setIsLoading(false);
      return;
    }

    // Validate existing tokens with a lightweight call
    apiClient
      .getProjects(1, 0)
      .then(() => {
        // Tokens valid - restore user from session
        const stored = sessionStorage.getItem("user");
        if (stored) {
          try {
            setUser(JSON.parse(stored));
          } catch {
            apiClient.clearTokens();
          }
        }
      })
      .catch(() => {
        apiClient.clearTokens();
      })
      .finally(() => setIsLoading(false));
  }, []);

  const login = useCallback(async (email: string) => {
    await apiClient.requestMagicLink(email);
  }, []);

  const verifyToken = useCallback(async (token: string) => {
    setIsLoading(true);
    try {
      const authResponse = await apiClient.verifyMagicLink(token);
      const userData: User = {
        user_id: authResponse.user_id,
        email: authResponse.email,
        name: authResponse.email.split("@")[0], // Fallback name from email
      };
      setUser(userData);
      sessionStorage.setItem("user", JSON.stringify(userData));
    } finally {
      setIsLoading(false);
    }
  }, []);

  const logout = useCallback(async () => {
    await apiClient.revokeToken();
    apiClient.clearTokens();
    setUser(null);
  }, []);

  const isAuthenticated = !!user || apiClient.hasTokens();
  const value = useMemo(
    () => ({
      user,
      isLoading,
      isAuthenticated,
      login,
      verifyToken,
      logout,
    }),
    [user, isLoading, isAuthenticated, login, verifyToken, logout],
  );

  return (
    <AuthContext.Provider value={value}>
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

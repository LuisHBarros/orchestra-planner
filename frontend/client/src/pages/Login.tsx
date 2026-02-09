import { useEffect, useRef, useState } from "react";
import { useLocation, useSearch } from "wouter";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { toast } from "sonner";
import { Mail, ArrowRight } from "lucide-react";
import { useAuth } from "@/contexts/AuthContext";
import { ApiError } from "@/lib/api";

export default function Login() {
  const [email, setEmail] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const { login, verifyToken, isAuthenticated } = useAuth();
  const [, navigate] = useLocation();
  const searchString = useSearch();
  const processedTokenRef = useRef<string | null>(null);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate("/dashboard");
    }
  }, [isAuthenticated, navigate]);

  // Check for ?token= query param for magic link verification
  useEffect(() => {
    const params = new URLSearchParams(searchString);
    const token = params.get("token");
    if (!token || processedTokenRef.current === token) {
      return;
    }

    processedTokenRef.current = token;
    if (token) {
      setIsLoading(true);
      verifyToken(token)
        .then(() => {
          toast.success("Login realizado com sucesso!");
          navigate("/dashboard");
        })
        .catch((err) => {
          if (err instanceof ApiError) {
            if (err.status === 401) {
              toast.error("Link de acesso expirado ou invalido");
            } else {
              toast.error("Erro ao verificar link de acesso");
            }
          } else {
            toast.error("Erro ao verificar link de acesso");
          }
        })
        .finally(() => setIsLoading(false));
    }
  }, [searchString, verifyToken, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email) {
      toast.error("Por favor, insira seu email");
      return;
    }

    setIsLoading(true);

    try {
      await login(email);
      setSubmitted(true);
      toast.success("Link de acesso enviado para seu email!");
    } catch (error) {
      if (error instanceof ApiError && error.status === 429) {
        toast.error("Muitas tentativas. Aguarde antes de tentar novamente.");
      } else {
        toast.error("Erro ao enviar link de acesso");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center justify-center p-4">
      {/* Hero Section */}
      <div className="w-full max-w-md mb-8 text-center">
        <h1 className="text-4xl font-bold text-foreground mb-2">
          Orchestra Planner
        </h1>
        <p className="text-muted-foreground">
          Gerencie projetos e equipes com inteligencia
        </p>
      </div>

      {/* Login Card */}
      <Card className="w-full max-w-md shadow-lg">
        <CardHeader>
          <CardTitle>Acesso com Magic Link</CardTitle>
          <CardDescription>
            Insira seu email para receber um link de acesso seguro
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!submitted ? (
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <label htmlFor="email" className="text-sm font-medium text-foreground">
                  Email
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <Input
                    id="email"
                    type="email"
                    placeholder="seu@email.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="pl-10"
                    disabled={isLoading}
                  />
                </div>
              </div>

              <Button
                type="submit"
                className="w-full bg-primary text-primary-foreground hover:bg-primary/90 flex items-center justify-center gap-2"
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <div className="w-4 h-4 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
                    Enviando...
                  </>
                ) : (
                  <>
                    Enviar Link
                    <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </Button>

              <p className="text-xs text-muted-foreground text-center">
                Voce recebera um link seguro para acessar sua conta
              </p>
            </form>
          ) : (
            <div className="text-center space-y-4">
              <div className="w-12 h-12 bg-primary/10 rounded-full flex items-center justify-center mx-auto">
                <Mail className="w-6 h-6 text-primary" />
              </div>
              <div>
                <h3 className="font-semibold text-foreground mb-1">
                  Email enviado!
                </h3>
                <p className="text-sm text-muted-foreground">
                  Verifique seu email para o link de acesso
                </p>
              </div>
              <Button
                variant="outline"
                className="w-full"
                onClick={() => {
                  setSubmitted(false);
                  setEmail("");
                }}
              >
                Voltar
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Footer */}
      <div className="mt-8 text-center text-sm text-muted-foreground">
        <p>&copy; 2026 Orchestra Planner. Todos os direitos reservados.</p>
      </div>
    </div>
  );
}

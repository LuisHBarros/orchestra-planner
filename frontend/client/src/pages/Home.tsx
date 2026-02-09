import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Link } from "wouter";
import { ArrowRight, CheckCircle2, Users, Zap, BarChart3 } from "lucide-react";

/**
 * Home Page - Landing Page
 * 
 * Design: Minimalismo Funcional com Acentos Modernos
 * - Hero section com imagem gerada
 * - Seção de features
 * - Call-to-action clara
 * - Tipografia hierárquica
 */

export default function Home() {
  const features = [
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Agendamento Inteligente",
      description:
        "Otimize automaticamente o cronograma de seus projetos com IA",
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "Gestão de Equipe",
      description:
        "Aloque recursos com inteligência baseada em habilidades e disponibilidade",
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: "Análise em Tempo Real",
      description:
        "Acompanhe progresso e identifique gargalos instantaneamente",
    },
    {
      icon: <CheckCircle2 className="w-6 h-6" />,
      title: "Rastreamento de Tarefas",
      description:
        "Gerencie dependências e prioridades com facilidade",
    },
  ];

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <nav className="h-16 border-b border-border flex items-center justify-between px-6">
        <h1 className="text-2xl font-bold text-foreground">Orchestra Planner</h1>
        <Link href="/login">
          <a className="text-primary hover:text-primary/80 font-medium">
            Entrar
          </a>
        </Link>
      </nav>

      {/* Hero Section */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
          {/* Left: Text Content */}
          <div className="space-y-6">
            <div>
              <h2 className="text-5xl font-bold text-foreground leading-tight mb-4">
                Gerencie Projetos com Inteligência
              </h2>
              <p className="text-xl text-muted-foreground">
                Orchestra Planner utiliza IA para otimizar agendamento, alocar
                recursos inteligentemente e manter sua equipe sincronizada.
              </p>
            </div>

            <div className="flex flex-col sm:flex-row gap-4">
              <Link href="/login">
                <a>
                  <Button className="bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-2 w-full sm:w-auto">
                    Começar Agora
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </a>
              </Link>
              <Button variant="outline" className="w-full sm:w-auto">
                Ver Demo
              </Button>
            </div>

            {/* Trust Indicators */}
            <div className="pt-4 space-y-2 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-primary" />
                <span>Sem cartão de crédito necessário</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-primary" />
                <span>Comece em menos de 2 minutos</span>
              </div>
              <div className="flex items-center gap-2">
                <CheckCircle2 className="w-4 h-4 text-primary" />
                <span>Suporte dedicado incluído</span>
              </div>
            </div>
          </div>

          {/* Right: Hero Image */}
          <div className="relative">
            <div className="bg-gradient-to-br from-primary/10 to-primary/5 rounded-2xl p-6 min-h-96">
              <img
                src="/images/hero-dashboard.svg"
                alt="Orchestra Planner dashboard"
                className="w-full h-full object-cover rounded-xl shadow-lg"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-secondary/30 py-20">
        <div className="max-w-6xl mx-auto px-6">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-foreground mb-4">
              Recursos Poderosos
            </h3>
            <p className="text-lg text-muted-foreground">
              Tudo que você precisa para gerenciar projetos complexos
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="border-border hover:shadow-lg transition-shadow">
                <CardContent className="pt-6">
                  <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mb-4 text-primary">
                    {feature.icon}
                  </div>
                  <h4 className="font-semibold text-foreground mb-2">
                    {feature.title}
                  </h4>
                  <p className="text-sm text-muted-foreground">
                    {feature.description}
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-2xl mx-auto px-6 text-center">
          <h3 className="text-3xl font-bold text-foreground mb-4">
            Pronto para começar?
          </h3>
          <p className="text-lg text-muted-foreground mb-8">
            Junte-se a equipes que já estão otimizando seus projetos com
            Orchestra Planner.
          </p>
          <Link href="/login">
            <a>
              <Button className="bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-2 mx-auto">
                Entrar ou Criar Conta
                <ArrowRight className="w-4 h-4" />
              </Button>
            </a>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border bg-secondary/20 py-8">
        <div className="max-w-6xl mx-auto px-6 text-center text-sm text-muted-foreground">
          <p>© 2026 Orchestra Planner. Todos os direitos reservados.</p>
        </div>
      </footer>
    </div>
  );
}

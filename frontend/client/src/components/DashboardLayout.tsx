import { ReactNode, useState } from "react";
import { Menu, X, LogOut, Settings, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Link } from "wouter";

/**
 * DashboardLayout Component
 * 
 * Provides persistent sidebar navigation for authenticated users.
 * Design: Minimalismo Funcional
 * - Sidebar esquerda com navegação fixa
 * - Ícones + labels para clareza
 * - Colapsável em mobile
 * - Branco com acentos em azul-índigo
 */

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const navItems = [
    { label: "Dashboard", href: "/dashboard", icon: "📊" },
    { label: "Projetos", href: "/projects", icon: "📁" },
    { label: "Tarefas", href: "/tasks", icon: "✓" },
    { label: "Equipe", href: "/team", icon: "👥" },
  ];

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? "w-64" : "w-20"
        } bg-sidebar border-r border-sidebar-border transition-all duration-300 flex flex-col`}
      >
        {/* Logo / Brand */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-sidebar-border">
          {sidebarOpen && (
            <h1 className="text-lg font-bold text-sidebar-foreground">
              Orchestra
            </h1>
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1 hover:bg-sidebar-accent rounded transition-colors"
          >
            {sidebarOpen ? (
              <X className="w-5 h-5 text-sidebar-foreground" />
            ) : (
              <Menu className="w-5 h-5 text-sidebar-foreground" />
            )}
          </button>
        </div>

        {/* Navigation Items */}
        <nav className="flex-1 px-3 py-4 space-y-2">
          {navItems.map((item) => (
            <Link key={item.href} href={item.href}>
              <a className="flex items-center gap-3 px-3 py-2 rounded-md text-sidebar-foreground hover:bg-sidebar-accent transition-colors group">
                <span className="text-xl">{item.icon}</span>
                {sidebarOpen && (
                  <span className="text-sm font-medium group-hover:text-sidebar-primary">
                    {item.label}
                  </span>
                )}
              </a>
            </Link>
          ))}
        </nav>

        {/* Action Button */}
        <div className="p-3 border-t border-sidebar-border">
          <Button
            className="w-full flex items-center justify-center gap-2 bg-sidebar-primary text-sidebar-primary-foreground hover:bg-primary"
            size="sm"
          >
            <Plus className="w-4 h-4" />
            {sidebarOpen && <span>Novo Projeto</span>}
          </Button>
        </div>

        {/* User Menu */}
        <div className="p-3 border-t border-sidebar-border space-y-2">
          <button className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-sidebar-foreground hover:bg-sidebar-accent transition-colors">
            <Settings className="w-5 h-5" />
            {sidebarOpen && <span className="text-sm">Configurações</span>}
          </button>
          <button className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-sidebar-foreground hover:bg-destructive/10 transition-colors">
            <LogOut className="w-5 h-5" />
            {sidebarOpen && <span className="text-sm">Sair</span>}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        {/* Top Header */}
        <header className="h-16 bg-background border-b border-border flex items-center px-6 shadow-sm">
          <h2 className="text-xl font-semibold text-foreground">
            Bem-vindo ao Orchestra Planner
          </h2>
        </header>

        {/* Page Content */}
        <div className="p-6">
          {children}
        </div>
      </main>
    </div>
  );
}

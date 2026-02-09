import { ReactNode } from "react";
import { Menu, X, LogOut, LayoutDashboard } from "lucide-react";
import { Link, useLocation } from "wouter";
import { useAuth } from "@/contexts/AuthContext";
import { useState } from "react";

interface DashboardLayoutProps {
  children: ReactNode;
}

export default function DashboardLayout({ children }: DashboardLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const { logout, user } = useAuth();
  const [location, navigate] = useLocation();

  const navItems = [
    { label: "Dashboard", href: "/dashboard", icon: LayoutDashboard },
  ];

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const getPageTitle = () => {
    if (location === "/dashboard") return "Dashboard";
    if (location.startsWith("/projects/")) return "Projeto";
    return "Orchestra Planner";
  };

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
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location === item.href;
            return (
              <Link key={item.href} href={item.href}>
                <a
                  className={`flex items-center gap-3 px-3 py-2 rounded-md transition-colors group ${
                    isActive
                      ? "bg-sidebar-accent text-sidebar-primary"
                      : "text-sidebar-foreground hover:bg-sidebar-accent"
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  {sidebarOpen && (
                    <span className="text-sm font-medium">
                      {item.label}
                    </span>
                  )}
                </a>
              </Link>
            );
          })}
        </nav>

        {/* User Menu */}
        <div className="p-3 border-t border-sidebar-border space-y-2">
          {sidebarOpen && user && (
            <div className="px-3 py-2 text-xs text-sidebar-foreground/70 truncate">
              {user.email}
            </div>
          )}
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2 rounded-md text-sidebar-foreground hover:bg-destructive/10 transition-colors"
          >
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
            {getPageTitle()}
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

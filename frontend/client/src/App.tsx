import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import ProjectDetail from "./pages/ProjectDetail";
import DashboardLayout from "./components/DashboardLayout";

/**
 * Orchestra Planner Frontend
 * 
 * Design: Minimalismo Funcional com Acentos Modernos
 * - Sidebar persistente com navegação
 * - Cards elevados com sombras sutis
 * - Tipografia Geist Sans para clareza
 * - Cores: Branco, Cinza, Azul-índigo (#4F46E5)
 */

function Router() {
  return (
    <Switch>
      {/* Public routes */}
      <Route path={"/"} component={Home} />
      <Route path={"/login"} component={Login} />
      
      {/* Protected routes with dashboard layout */}
      <Route path={"/dashboard"}>
        {() => (
          <DashboardLayout>
            <Dashboard />
          </DashboardLayout>
        )}
      </Route>
      
      <Route path={"/projects/:projectId"}>
        {(params) => (
          <DashboardLayout>
            <ProjectDetail projectId={params.projectId} />
          </DashboardLayout>
        )}
      </Route>

      {/* 404 fallback */}
      <Route path={"/404"} component={NotFound} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="light">
        <TooltipProvider>
          <Toaster />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;

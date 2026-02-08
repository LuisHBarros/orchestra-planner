import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, Calendar, Users, CheckCircle2, AlertCircle } from "lucide-react";
import { toast } from "sonner";
import { Link } from "wouter";

/**
 * Dashboard Page
 * 
 * Design: Minimalismo Funcional
 * - Grid layout com cards elevados
 * - Estatísticas em destaque
 * - Lista de projetos recentes
 * - Tarefas pendentes
 */

interface Project {
  id: string;
  name: string;
  description: string;
  manager_id: string;
  expected_end_date: string | null;
  created_at: string;
  task_count?: number;
  member_count?: number;
}

interface Task {
  id: string;
  title: string;
  project_id: string;
  status: "Todo" | "Doing" | "Blocked" | "Done" | "Cancelled";
  progress_percent: number;
  assignee_id: string | null;
  expected_end_date: string | null;
}

export default function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // TODO: Integrar com API backend
    // Dados simulados para demonstração
    const mockProjects: Project[] = [
      {
        id: "1",
        name: "Redesign do Portal",
        description: "Atualizar interface do portal de clientes",
        manager_id: "user1",
        expected_end_date: "2026-03-15",
        created_at: "2026-01-15",
        task_count: 12,
        member_count: 5,
      },
      {
        id: "2",
        name: "API REST v2",
        description: "Nova versão da API com melhorias de performance",
        manager_id: "user1",
        expected_end_date: "2026-04-30",
        created_at: "2026-02-01",
        task_count: 8,
        member_count: 3,
      },
    ];

    const mockTasks: Task[] = [
      {
        id: "t1",
        title: "Implementar autenticação OAuth",
        project_id: "1",
        status: "Doing",
        progress_percent: 65,
        assignee_id: "user2",
        expected_end_date: "2026-02-20",
      },
      {
        id: "t2",
        title: "Design de componentes UI",
        project_id: "1",
        status: "Done",
        progress_percent: 100,
        assignee_id: "user3",
        expected_end_date: "2026-02-10",
      },
      {
        id: "t3",
        title: "Testes de integração",
        project_id: "2",
        status: "Todo",
        progress_percent: 0,
        assignee_id: null,
        expected_end_date: "2026-03-01",
      },
    ];

    setProjects(mockProjects);
    setTasks(mockTasks);
    setIsLoading(false);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Done":
        return "text-green-600 bg-green-50";
      case "Doing":
        return "text-blue-600 bg-blue-50";
      case "Blocked":
        return "text-red-600 bg-red-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const getStatusLabel = (status: string) => {
    const labels: Record<string, string> = {
      Done: "Concluída",
      Doing: "Em Progresso",
      Todo: "Pendente",
      Blocked: "Bloqueada",
      Cancelled: "Cancelada",
    };
    return labels[status] || status;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Visão geral de seus projetos e tarefas
          </p>
        </div>
        <Button className="bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Novo Projeto
        </Button>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Projetos Ativos</p>
                <p className="text-2xl font-bold text-foreground">{projects.length}</p>
              </div>
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                <Calendar className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Tarefas Totais</p>
                <p className="text-2xl font-bold text-foreground">{tasks.length}</p>
              </div>
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                <CheckCircle2 className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Em Progresso</p>
                <p className="text-2xl font-bold text-foreground">
                  {tasks.filter(t => t.status === "Doing").length}
                </p>
              </div>
              <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
                <AlertCircle className="w-6 h-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Concluídas</p>
                <p className="text-2xl font-bold text-foreground">
                  {tasks.filter(t => t.status === "Done").length}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
                <CheckCircle2 className="w-6 h-6 text-green-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Projects Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Projetos Recentes</CardTitle>
              <CardDescription>
                Seus projetos ativos e próximos
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoading ? (
                <div className="text-center py-8 text-muted-foreground">
                  Carregando projetos...
                </div>
              ) : projects.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-muted-foreground mb-4">Nenhum projeto criado ainda</p>
                  <Button className="bg-primary text-primary-foreground">
                    Criar Primeiro Projeto
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {projects.map((project) => (
                    <Link key={project.id} href={`/projects/${project.id}`}>
                      <a className="block p-4 border border-border rounded-lg hover:bg-secondary transition-colors">
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="font-semibold text-foreground">{project.name}</h3>
                          <span className="text-xs bg-primary/10 text-primary px-2 py-1 rounded">
                            {project.task_count} tarefas
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground mb-3">
                          {project.description}
                        </p>
                        <div className="flex items-center justify-between text-xs text-muted-foreground">
                          <div className="flex items-center gap-4">
                            <span className="flex items-center gap-1">
                              <Users className="w-4 h-4" />
                              {project.member_count} membros
                            </span>
                            {project.expected_end_date && (
                              <span className="flex items-center gap-1">
                                <Calendar className="w-4 h-4" />
                                {new Date(project.expected_end_date).toLocaleDateString("pt-BR")}
                              </span>
                            )}
                          </div>
                        </div>
                      </a>
                    </Link>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Tasks Sidebar */}
        <Card>
          <CardHeader>
            <CardTitle>Tarefas Pendentes</CardTitle>
            <CardDescription>
              Suas próximas ações
            </CardDescription>
          </CardHeader>
          <CardContent>
            {tasks.length === 0 ? (
              <p className="text-sm text-muted-foreground text-center py-4">
                Nenhuma tarefa pendente
              </p>
            ) : (
              <div className="space-y-3">
                {tasks.slice(0, 5).map((task) => (
                  <div
                    key={task.id}
                    className="p-3 border border-border rounded-lg hover:bg-secondary transition-colors"
                  >
                    <p className="text-sm font-medium text-foreground mb-1">
                      {task.title}
                    </p>
                    <div className="flex items-center justify-between">
                      <span className={`text-xs px-2 py-1 rounded ${getStatusColor(task.status)}`}>
                        {getStatusLabel(task.status)}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {task.progress_percent}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

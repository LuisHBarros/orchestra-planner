import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Plus, ArrowLeft, Users, Calendar, Settings } from "lucide-react";
import { toast } from "sonner";

/**
 * ProjectDetail Page
 * 
 * Design: Minimalismo Funcional
 * - Visualização detalhada do projeto
 * - Lista de tarefas com status
 * - Membros da equipe
 * - Configurações do projeto
 */

interface ProjectDetailProps {
  projectId: string;
}

interface Task {
  id: string;
  title: string;
  description: string;
  status: "Todo" | "Doing" | "Blocked" | "Done" | "Cancelled";
  progress_percent: number;
  assignee_id: string | null;
  difficulty_points: number | null;
  expected_end_date: string | null;
}

interface ProjectMember {
  id: string;
  user_id: string;
  role_id: string;
  seniority_level: "Junior" | "Mid" | "Senior" | "Specialist" | "Lead";
  name: string;
  email: string;
}

export default function ProjectDetail({ projectId }: ProjectDetailProps) {
  const [, navigate] = useLocation();
  const [projectName, setProjectName] = useState("Carregando...");
  const [projectDescription, setProjectDescription] = useState("");
  const [tasks, setTasks] = useState<Task[]>([]);
  const [members, setMembers] = useState<ProjectMember[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<"tasks" | "members" | "settings">("tasks");

  useEffect(() => {
    // TODO: Integrar com API backend
    // Dados simulados para demonstração
    const mockProject = {
      id: projectId,
      name: "Redesign do Portal",
      description: "Atualizar interface do portal de clientes com novas funcionalidades",
      expected_end_date: "2026-03-15",
    };

    const mockTasks: Task[] = [
      {
        id: "t1",
        title: "Implementar autenticação OAuth",
        description: "Integrar OAuth2 para login seguro",
        status: "Doing",
        progress_percent: 65,
        assignee_id: "user2",
        difficulty_points: 8,
        expected_end_date: "2026-02-20",
      },
      {
        id: "t2",
        title: "Design de componentes UI",
        description: "Criar biblioteca de componentes reutilizáveis",
        status: "Done",
        progress_percent: 100,
        assignee_id: "user3",
        difficulty_points: 5,
        expected_end_date: "2026-02-10",
      },
      {
        id: "t3",
        title: "Testes de integração",
        description: "Implementar testes automatizados",
        status: "Todo",
        progress_percent: 0,
        assignee_id: null,
        difficulty_points: 6,
        expected_end_date: "2026-03-01",
      },
    ];

    const mockMembers: ProjectMember[] = [
      {
        id: "m1",
        user_id: "user1",
        role_id: "role1",
        seniority_level: "Senior",
        name: "João Silva",
        email: "joao@example.com",
      },
      {
        id: "m2",
        user_id: "user2",
        role_id: "role2",
        seniority_level: "Mid",
        name: "Maria Santos",
        email: "maria@example.com",
      },
      {
        id: "m3",
        user_id: "user3",
        role_id: "role2",
        seniority_level: "Junior",
        name: "Pedro Costa",
        email: "pedro@example.com",
      },
    ];

    setProjectName(mockProject.name);
    setProjectDescription(mockProject.description);
    setTasks(mockTasks);
    setMembers(mockMembers);
    setIsLoading(false);
  }, [projectId]);

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

  const getSeniorityLabel = (level: string) => {
    const labels: Record<string, string> = {
      Junior: "Junior",
      Mid: "Pleno",
      Senior: "Senior",
      Specialist: "Especialista",
      Lead: "Lead",
    };
    return labels[level] || level;
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <button
          onClick={() => navigate("/dashboard")}
          className="p-2 hover:bg-secondary rounded-lg transition-colors"
        >
          <ArrowLeft className="w-5 h-5 text-foreground" />
        </button>
        <div className="flex-1">
          <h1 className="text-3xl font-bold text-foreground">{projectName}</h1>
          <p className="text-muted-foreground mt-1">{projectDescription}</p>
        </div>
        <Button
          variant="outline"
          className="flex items-center gap-2"
        >
          <Settings className="w-4 h-4" />
          Configurar
        </Button>
      </div>

      {/* Project Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total de Tarefas</p>
                <p className="text-2xl font-bold text-foreground">{tasks.length}</p>
              </div>
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                <span className="text-xl">✓</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Membros da Equipe</p>
                <p className="text-2xl font-bold text-foreground">{members.length}</p>
              </div>
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                <Users className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Progresso Geral</p>
                <p className="text-2xl font-bold text-foreground">
                  {Math.round(
                    tasks.reduce((sum, t) => sum + t.progress_percent, 0) / tasks.length || 0
                  )}%
                </p>
              </div>
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                <span className="text-xl">📊</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border">
        {["tasks", "members", "settings"].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab as typeof activeTab)}
            className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
              activeTab === tab
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab === "tasks" && "Tarefas"}
            {tab === "members" && "Membros"}
            {tab === "settings" && "Configurações"}
          </button>
        ))}
      </div>

      {/* Tasks Tab */}
      {activeTab === "tasks" && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Tarefas do Projeto</CardTitle>
              <CardDescription>Gerencie as tarefas e seu progresso</CardDescription>
            </div>
            <Button className="bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Nova Tarefa
            </Button>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-8 text-muted-foreground">
                Carregando tarefas...
              </div>
            ) : tasks.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-muted-foreground">Nenhuma tarefa criada ainda</p>
              </div>
            ) : (
              <div className="space-y-3">
                {tasks.map((task) => (
                  <div
                    key={task.id}
                    className="p-4 border border-border rounded-lg hover:bg-secondary transition-colors"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-foreground">{task.title}</h3>
                      <span className={`text-xs px-2 py-1 rounded ${getStatusColor(task.status)}`}>
                        {getStatusLabel(task.status)}
                      </span>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">{task.description}</p>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <div className="flex items-center gap-4">
                        {task.difficulty_points && (
                          <span>Dificuldade: {task.difficulty_points}</span>
                        )}
                        {task.expected_end_date && (
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3 h-3" />
                            {new Date(task.expected_end_date).toLocaleDateString("pt-BR")}
                          </span>
                        )}
                      </div>
                      <div className="w-24 h-2 bg-border rounded-full overflow-hidden">
                        <div
                          className="h-full bg-primary transition-all"
                          style={{ width: `${task.progress_percent}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Members Tab */}
      {activeTab === "members" && (
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Membros da Equipe</CardTitle>
              <CardDescription>Gerencie os membros do projeto</CardDescription>
            </div>
            <Button className="bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Adicionar Membro
            </Button>
          </CardHeader>
          <CardContent>
            {members.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-muted-foreground">Nenhum membro adicionado</p>
              </div>
            ) : (
              <div className="space-y-3">
                {members.map((member) => (
                  <div
                    key={member.id}
                    className="p-4 border border-border rounded-lg flex items-center justify-between hover:bg-secondary transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-primary/10 rounded-full flex items-center justify-center">
                        <span className="text-sm font-semibold text-primary">
                          {member.name.charAt(0)}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium text-foreground">{member.name}</p>
                        <p className="text-sm text-muted-foreground">{member.email}</p>
                      </div>
                    </div>
                    <span className="text-xs bg-primary/10 text-primary px-3 py-1 rounded-full">
                      {getSeniorityLabel(member.seniority_level)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Settings Tab */}
      {activeTab === "settings" && (
        <Card>
          <CardHeader>
            <CardTitle>Configurações do Projeto</CardTitle>
            <CardDescription>Gerencie as configurações e integrações</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 border border-border rounded-lg">
                <h3 className="font-semibold text-foreground mb-2">Integração com LLM</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  Configure um provedor de LLM para otimização inteligente de agendamento
                </p>
                <Button variant="outline">Configurar LLM</Button>
              </div>

              <div className="p-4 border border-border rounded-lg">
                <h3 className="font-semibold text-foreground mb-2">Convites</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  Convide novos membros para o projeto
                </p>
                <Button variant="outline">Gerar Link de Convite</Button>
              </div>

              <div className="p-4 border border-destructive rounded-lg bg-destructive/5">
                <h3 className="font-semibold text-destructive mb-2">Zona de Perigo</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  Ações irreversíveis para este projeto
                </p>
                <Button variant="destructive">Deletar Projeto</Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

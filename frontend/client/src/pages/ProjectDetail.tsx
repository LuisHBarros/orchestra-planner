import { useState, useCallback } from "react";
import { useLocation } from "wouter";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, ArrowLeft, Users, Calendar, Settings } from "lucide-react";
import { toast } from "sonner";
import { useFetch } from "@/hooks/useFetch";
import {
  apiClient,
  ProjectDetails,
  Task,
  ProjectMemberEnriched,
  PaginatedResponse,
} from "@/lib/api";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

interface ProjectDetailProps {
  projectId: string;
}

export default function ProjectDetail({ projectId }: ProjectDetailProps) {
  const [, navigate] = useLocation();
  const [activeTab, setActiveTab] = useState<"tasks" | "members" | "settings">("tasks");
  const [taskDialogOpen, setTaskDialogOpen] = useState(false);
  const [newTaskTitle, setNewTaskTitle] = useState("");
  const [newTaskDesc, setNewTaskDesc] = useState("");
  const [creating, setCreating] = useState(false);

  const fetchDetails = useCallback(
    (signal?: AbortSignal) => apiClient.getProjectDetails(projectId, signal),
    [projectId],
  );
  const fetchTasks = useCallback(
    (signal?: AbortSignal) => apiClient.getProjectTasks(projectId, 50, 0, signal),
    [projectId],
  );
  const fetchMembers = useCallback(
    (signal?: AbortSignal) => apiClient.getProjectMembers(projectId, 50, 0, signal),
    [projectId],
  );

  const {
    data: details,
    isLoading: detailsLoading,
    error: detailsError,
  } = useFetch<ProjectDetails>(fetchDetails, [projectId]);
  const {
    data: tasksData,
    isLoading: tasksLoading,
    refetch: refetchTasks,
  } = useFetch<PaginatedResponse<Task>>(fetchTasks, [projectId]);
  const {
    data: membersData,
    isLoading: membersLoading,
  } = useFetch<PaginatedResponse<ProjectMemberEnriched>>(fetchMembers, [projectId]);

  const project = details?.project;
  const tasks = tasksData?.items ?? [];
  const members = membersData?.items ?? [];

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
      Done: "Concluida",
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

  const handleCreateTask = async () => {
    if (!newTaskTitle.trim()) {
      toast.error("Titulo da tarefa e obrigatorio");
      return;
    }
    setCreating(true);
    try {
      await apiClient.createTask(projectId, newTaskTitle.trim(), newTaskDesc.trim());
      toast.success("Tarefa criada com sucesso!");
      setTaskDialogOpen(false);
      setNewTaskTitle("");
      setNewTaskDesc("");
      refetchTasks();
    } catch {
      toast.error("Erro ao criar tarefa");
    } finally {
      setCreating(false);
    }
  };

  if (detailsLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (detailsError || !project) {
    return (
      <div className="text-center py-20">
        <p className="text-destructive mb-4">Erro ao carregar projeto</p>
        <Button variant="outline" onClick={() => navigate("/dashboard")}>
          Voltar ao Dashboard
        </Button>
      </div>
    );
  }

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
          <h1 className="text-3xl font-bold text-foreground">{project.name}</h1>
          <p className="text-muted-foreground mt-1">{project.description}</p>
        </div>
        <Button
          variant="outline"
          className="flex items-center gap-2"
          onClick={() => setActiveTab("settings")}
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
                <p className="text-2xl font-bold text-foreground">
                  {tasksData?.total ?? 0}
                </p>
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
                <p className="text-sm text-muted-foreground">Membros da Equipe</p>
                <p className="text-2xl font-bold text-foreground">
                  {membersData?.total ?? 0}
                </p>
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
                  {tasks.length > 0
                    ? Math.round(
                        tasks.reduce((sum, t) => sum + t.progress_percent, 0) /
                          tasks.length,
                      )
                    : 0}
                  %
                </p>
              </div>
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                <Calendar className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-border">
        {(["tasks", "members", "settings"] as const).map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 font-medium text-sm border-b-2 transition-colors ${
              activeTab === tab
                ? "border-primary text-primary"
                : "border-transparent text-muted-foreground hover:text-foreground"
            }`}
          >
            {tab === "tasks" && "Tarefas"}
            {tab === "members" && "Membros"}
            {tab === "settings" && "Configuracoes"}
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
            <Dialog open={taskDialogOpen} onOpenChange={setTaskDialogOpen}>
              <DialogTrigger asChild>
                <Button className="bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  Nova Tarefa
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Criar Nova Tarefa</DialogTitle>
                  <DialogDescription>
                    Preencha os dados da nova tarefa
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium">Titulo</label>
                    <Input
                      value={newTaskTitle}
                      onChange={(e) => setNewTaskTitle(e.target.value)}
                      placeholder="Titulo da tarefa"
                      disabled={creating}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">Descricao</label>
                    <Input
                      value={newTaskDesc}
                      onChange={(e) => setNewTaskDesc(e.target.value)}
                      placeholder="Descricao da tarefa (opcional)"
                      disabled={creating}
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button
                    variant="outline"
                    onClick={() => setTaskDialogOpen(false)}
                    disabled={creating}
                  >
                    Cancelar
                  </Button>
                  <Button onClick={handleCreateTask} disabled={creating}>
                    {creating ? "Criando..." : "Criar"}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </CardHeader>
          <CardContent>
            {tasksLoading ? (
              <div className="text-center py-8 text-muted-foreground">
                <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-2" />
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
                      <span
                        className={`text-xs px-2 py-1 rounded ${getStatusColor(task.status)}`}
                      >
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
          </CardHeader>
          <CardContent>
            {membersLoading ? (
              <div className="text-center py-8 text-muted-foreground">
                <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-2" />
                Carregando membros...
              </div>
            ) : members.length === 0 ? (
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
                          {member.user_name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <p className="font-medium text-foreground">{member.user_name}</p>
                        <p className="text-sm text-muted-foreground">{member.user_email}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs bg-secondary text-secondary-foreground px-2 py-1 rounded">
                        {member.role_name}
                      </span>
                      <span className="text-xs bg-primary/10 text-primary px-3 py-1 rounded-full">
                        {getSeniorityLabel(member.seniority_level)}
                      </span>
                    </div>
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
            <CardTitle>Configuracoes do Projeto</CardTitle>
            <CardDescription>Gerencie as configuracoes e integracoes</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="p-4 border border-border rounded-lg">
                <h3 className="font-semibold text-foreground mb-2">Integracao com LLM</h3>
                <p className="text-sm text-muted-foreground mb-3">
                  Configure um provedor de LLM para otimizacao inteligente de agendamento
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
                  Acoes irreversiveis para este projeto
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

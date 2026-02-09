import { useState, useCallback } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Plus, Calendar, Users, FolderOpen, AlertCircle } from "lucide-react";
import { toast } from "sonner";
import { Link } from "wouter";
import { useFetch } from "@/hooks/useFetch";
import { apiClient, Project, PaginatedResponse } from "@/lib/api";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";

export default function Dashboard() {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [creating, setCreating] = useState(false);

  const fetchProjects = useCallback(
    (signal?: AbortSignal) => apiClient.getProjects(20, 0, signal),
    [],
  );
  const { data, isLoading, error, refetch } = useFetch<PaginatedResponse<Project>>(
    fetchProjects,
    [],
  );

  const projects = data?.items ?? [];

  const handleCreateProject = async () => {
    if (!newName.trim()) {
      toast.error("Nome do projeto e obrigatorio");
      return;
    }
    setCreating(true);
    try {
      await apiClient.createProject(newName.trim(), newDesc.trim());
      toast.success("Projeto criado com sucesso!");
      setDialogOpen(false);
      setNewName("");
      setNewDesc("");
      refetch();
    } catch {
      toast.error("Erro ao criar projeto");
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Visao geral de seus projetos
          </p>
        </div>
        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogTrigger asChild>
            <Button className="bg-primary text-primary-foreground hover:bg-primary/90 flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Novo Projeto
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Criar Novo Projeto</DialogTitle>
              <DialogDescription>
                Preencha os dados do novo projeto
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div>
                <label className="text-sm font-medium">Nome</label>
                <Input
                  value={newName}
                  onChange={(e) => setNewName(e.target.value)}
                  placeholder="Nome do projeto"
                  disabled={creating}
                />
              </div>
              <div>
                <label className="text-sm font-medium">Descricao</label>
                <Input
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  placeholder="Descricao do projeto (opcional)"
                  disabled={creating}
                />
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDialogOpen(false)} disabled={creating}>
                Cancelar
              </Button>
              <Button onClick={handleCreateProject} disabled={creating}>
                {creating ? "Criando..." : "Criar"}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Projetos Ativos</p>
                <p className="text-2xl font-bold text-foreground">
                  {data?.total ?? 0}
                </p>
              </div>
              <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center">
                <FolderOpen className="w-6 h-6 text-primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Ultimo Criado</p>
                <p className="text-lg font-bold text-foreground truncate">
                  {projects[0]?.name ?? "-"}
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
                <p className="text-sm text-muted-foreground">Status</p>
                <p className="text-lg font-bold text-foreground">
                  {error ? "Erro" : isLoading ? "Carregando..." : "Online"}
                </p>
              </div>
              <div className="w-12 h-12 bg-green-50 rounded-lg flex items-center justify-center">
                <AlertCircle className={`w-6 h-6 ${error ? "text-red-600" : "text-green-600"}`} />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Projects Section */}
      <Card>
        <CardHeader>
          <CardTitle>Projetos Recentes</CardTitle>
          <CardDescription>
            Seus projetos ativos e proximos
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="text-center py-8 text-muted-foreground">
              <div className="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin mx-auto mb-2" />
              Carregando projetos...
            </div>
          ) : error ? (
            <div className="text-center py-8">
              <p className="text-destructive mb-4">Erro ao carregar projetos</p>
              <Button variant="outline" onClick={refetch}>
                Tentar novamente
              </Button>
            </div>
          ) : projects.length === 0 ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground mb-4">Nenhum projeto criado ainda</p>
              <Button
                className="bg-primary text-primary-foreground"
                onClick={() => setDialogOpen(true)}
              >
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
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">
                      {project.description || "Sem descricao"}
                    </p>
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <div className="flex items-center gap-4">
                        {project.expected_end_date && (
                          <span className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            {new Date(project.expected_end_date).toLocaleDateString("pt-BR")}
                          </span>
                        )}
                        <span className="flex items-center gap-1">
                          <Users className="w-4 h-4" />
                          {new Date(project.created_at).toLocaleDateString("pt-BR")}
                        </span>
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
  );
}

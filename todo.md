# Plano P0+P1: Integração Real Frontend-Backend, Auth Funcional e Limpeza de Produção

## Resumo
Implementar a primeira versão funcional completa do frontend com backend real, cobrindo autenticação por magic link, proteção de rotas, dashboard/projeto sem mocks, e limpeza dos artefatos Manus/debug para readiness de deploy.  
Como o backend atual não expõe todas as listagens necessárias, o plano inclui extensão de API no backend (paginação padrão) para suportar o frontend sem dados hardcoded.

## Escopo desta rodada (fechado)
- Incluído: todo P0 + P1.
- Excluído nesta rodada: P2 (testes de hooks/auth UI e padronização total de idioma) e P3 (hardening de server com nginx/caching/compressão).

## Mudanças de API/backend (necessárias para remover mocks)

### 1) Novos endpoints para listagem de projetos e membros
1. `GET /projects?limit={int}&offset={int}`
- Auth obrigatória.
- Retorno paginado:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string",
      "manager_id": "uuid",
      "expected_end_date": "datetime|null",
      "created_at": "datetime"
    }
  ],
  "total": 0,
  "limit": 20,
  "offset": 0
}
```

2. `GET /projects/{project_id}/members?limit={int}&offset={int}`
- Auth obrigatória; acesso apenas a membro/manager do projeto.
- Retorno paginado enriquecido para UI:
```json
{
  "items": [
    {
      "id": "uuid",
      "project_id": "uuid",
      "user_id": "uuid",
      "role_id": "uuid",
      "seniority_level": "Junior|Mid|Senior|Specialist|Lead",
      "joined_at": "datetime",
      "user_name": "string",
      "user_email": "string",
      "role_name": "string"
    }
  ],
  "total": 0,
  "limit": 20,
  "offset": 0
}
```

### 2) Reaproveitar endpoint já existente
- `GET /projects/{project_id}/tasks?limit&offset` já existe e será usado no frontend.

### 3) Camada de aplicação/backend
- Criar use cases de listagem paginada (projetos e membros).
- Repositórios necessários:
  - `ProjectRepository.list_by_user(...)` + `count_by_user(...)`
  - `ProjectMemberRepository.list_by_project(...)` + `count_by_project(...)` (já existe parte paginada; reaproveitar)
  - leitura de `UserRepository` e `RoleRepository` para enriquecer membros.
- Router e schemas novos em `projects.py` e `members.py`.

## Mudanças de frontend (P0 + P1)

### 1) API client tipado (`frontend/client/src/lib/api.ts`)
- Criar `axios` client com:
  - `baseURL = import.meta.env.VITE_API_BASE_URL` (fallback `http://localhost:8000`)
  - interceptor de request: injeta `Authorization: Bearer <access_token>`
  - interceptor de response: em `401`, tenta `POST /auth/refresh` com `refresh_token`, repete request uma vez.
- Armazenamento de tokens: `sessionStorage`.
- Contratos tipados:
  - `requestMagicLink(email)`
  - `verifyMagicLink(token)` -> `{ user, accessToken, refreshToken }`
  - `refreshToken()`
  - `revokeToken()`
  - `getProjects(limit, offset)`
  - `getProjectDetails(projectId)`
  - `getProjectTasks(projectId, limit, offset)`
  - `getProjectMembers(projectId, limit, offset)`
  - `createProject(payload)`
  - `createTask(projectId, payload)`

### 2) `AuthContext` funcional
- Corrigir import inexistente (`@/lib/api`) com implementação real.
- Estado:
  - `user`, `accessToken`, `refreshToken`, `isAuthenticated`, `isLoading`.
- Bootstrapping:
  - lê tokens do `sessionStorage`;
  - define sessão no `apiClient`;
  - valida sessão via chamada autenticada leve (ex.: `GET /projects?limit=1&offset=0`) com fallback para logout.
- Ações:
  - `requestMagicLink(email)`
  - `verifyMagicLink(token)` (persistir tokens + user no contexto)
  - `logout()` (chama revoke quando possível, limpa storage e estado)

### 3) Fluxo de login real
- `Login.tsx`:
  - remover `setTimeout` mock;
  - usar `requestMagicLink`;
  - suportar leitura de token por query param `?token=...` para auto-`verifyMagicLink`;
  - mensagens de erro/sucesso reais (429, 401, 5xx).

### 4) Provider tree e proteção de rotas
- Envolver app com `AuthProvider` em `main.tsx`/`App.tsx`.
- Criar `ProtectedRoute`:
  - se `isLoading`: estado de carregamento;
  - se não autenticado: redirect `/login`;
  - se autenticado: renderiza conteúdo.
- Aplicar em `/dashboard` e `/projects/:projectId`.

### 5) Dashboard e ProjectDetail sem mocks
- `Dashboard.tsx`:
  - substituir mocks por `getProjects`;
  - estatísticas derivadas de dados reais disponíveis;
  - CTA “Novo Projeto” chama `createProject` via modal/form simples.
- `ProjectDetail.tsx`:
  - dados do projeto via `getProjectDetails`;
  - tarefas via `getProjectTasks`;
  - membros via `getProjectMembers`;
  - CTA “Nova Tarefa” chama `createTask` (form mínimo).
- Estados de loading/error/empty reais em cada seção.

### 6) `DashboardLayout` funcional
- Header dinâmico por rota (`Dashboard`, `Projeto`, etc.).
- Botão “Novo Projeto”: ação real.
- “Sair”: chama `logout`.
- “Configurações”: navegar para rota existente (ou ocultar temporariamente).
- Sidebar com ícones Lucide (remover emojis).
- Corrigir links inválidos.

### 7) Limpeza de artefatos Manus/debug
- Remover de `vite.config.ts`:
  - `vite-plugin-manus-runtime`
  - plugin custom `manus-debug-collector`
  - allowed hosts manus.
- Remover arquivos:
  - `client/public/__manus__/debug-collector.js`
  - `client/src/components/ManusDialog.tsx` (se não usado)
  - todos `:Zone.Identifier`.
- Remover `@builder.io/vite-plugin-jsx-loc`.
- Remover script Umami de `client/index.html`.
- Remover patch de debug de rotas `wouter`.

### 8) Imagem hero estável
- Mover hero para `client/public/images/hero-dashboard.webp`.
- Atualizar `Home.tsx` para usar asset local.

### 9) `useFetch` com cancelamento
- Atualizar hook para `AbortController`, cleanup em `useEffect`.
- Compatibilizar assinatura para `fetchFn(signal?: AbortSignal)`.

## Mudanças de interfaces/tipos públicas (frontend)
1. Novo módulo `@/lib/api` exportando:
- `ApiClient` methods citados acima.
- tipos: `User`, `TokenPair`, `PaginatedResponse<T>`, `Project`, `Task`, `ProjectMemberEnriched`.
2. `AuthContextType` atualizado:
- `requestMagicLink`, `verifyMagicLink`, `logout`, `isAuthenticated`, `isLoading`, `user`.
3. `ProtectedRoute` novo componente reutilizável.

## Sequência de implementação (ordem fechada)
1. Backend: adicionar endpoints/use-cases/repositórios para listagem de projetos e membros.
2. Backend: testes desses endpoints e regras de autorização.
3. Frontend: criar `lib/api.ts` + interceptor + token lifecycle.
4. Frontend: ajustar `AuthContext` + provider no app.
5. Frontend: implementar `ProtectedRoute` e aplicar nas rotas privadas.
6. Frontend: integrar `Login` com fluxo real de magic link.
7. Frontend: integrar `Dashboard` e `ProjectDetail` com API (remover mocks).
8. Frontend: ajustar `DashboardLayout`.
9. Frontend: limpar tooling Manus/Umami/Zone.Identifier/patch wouter.
10. Frontend: trocar hero para asset local.
11. Frontend: corrigir `useFetch` com abort.
12. Rodar checks e validação manual.

## Testes e cenários de aceite

### Backend
1. `GET /projects`:
- retorna apenas projetos acessíveis ao usuário autenticado.
- paginação correta (`limit/offset/total`).
2. `GET /projects/{id}/members`:
- retorna 403 para usuário sem acesso.
- retorna lista enriquecida com `user_email` e `role_name`.
- paginação correta.

### Frontend (funcional)
1. Login:
- solicitar magic link chama API real e exibe feedback.
- `?token=...` faz verify real e autentica sessão.
2. Sessão:
- refresh automático em 401 funciona.
- logout limpa sessão e redireciona.
3. Guard:
- acessar `/dashboard` sem auth redireciona para `/login`.
- autenticado acessa rotas privadas normalmente.
4. Dashboard:
- sem mocks; dados vêm da API.
- criar projeto atualiza lista.
5. ProjectDetail:
- sem mocks; tarefas e membros vêm da API.
- criar tarefa atualiza lista.
6. Tooling:
- build sem dependências Manus/debug/Umami.
- sem referências a arquivos `:Zone.Identifier`.
7. Hook:
- `useFetch` não dispara atualização após unmount.

### Comandos de validação
- Frontend: `pnpm --dir frontend check`, `pnpm --dir frontend build`.
- Backend: `source backend/venv/bin/activate && pytest -q`.

## Assunções e defaults explícitos
1. Idioma permanece misto nesta rodada (P2 fora do escopo), priorizando funcionalidade.
2. Armazenamento de token será `sessionStorage` (não `localStorage`).
3. Não será implementado auth com cookies httpOnly nesta rodada.
4. Rotas inexistentes de sidebar serão removidas/ocultadas até existir backend/UI correspondente.
5. Produção continua com server atual, sem nginx/caddy nesta rodada (P3 fora).

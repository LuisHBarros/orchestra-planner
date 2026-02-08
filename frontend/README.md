# Orchestra Planner - Frontend

Frontend moderno para o MVP Orchestra Planner, construído com React 19, Tailwind CSS 4 e Wouter para roteamento.

## 🎨 Design

**Minimalismo Funcional com Acentos Modernos** - Uma abordagem Bauhaus Digital que prioriza clareza, funcionalidade e acessibilidade.

### Características de Design

- **Tipografia Hierárquica**: Geist Sans para UI, IBM Plex Mono para dados técnicos
- **Paleta de Cores**: Branco puro, cinza neutro, azul-índigo vibrante (#4F46E5)
- **Layout**: Sidebar persistente com navegação, conteúdo fluido
- **Componentes**: Cards elevados com sombras sutis, badges de status, ícones minimalistas
- **Animações**: Transições suaves de 150ms, feedback visual imediato

## 🚀 Começando

### Pré-requisitos

- Node.js 18+
- pnpm 10+

### Instalação

```bash
# Instalar dependências
pnpm install

# Iniciar servidor de desenvolvimento
pnpm dev

# Build para produção
pnpm build

# Preview da build
pnpm preview
```

O servidor estará disponível em `http://localhost:3000`.

## 📁 Estrutura do Projeto

```
client/
├── public/              # Ativos estáticos
├── src/
│   ├── components/      # Componentes reutilizáveis
│   │   ├── DashboardLayout.tsx
│   │   └── ErrorBoundary.tsx
│   ├── contexts/        # React Contexts
│   │   ├── AuthContext.tsx
│   │   └── ThemeContext.tsx
│   ├── hooks/           # Custom Hooks
│   │   └── useFetch.ts
│   ├── lib/             # Utilitários
│   │   └── api.ts       # Cliente API
│   ├── pages/           # Componentes de página
│   │   ├── Home.tsx
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── ProjectDetail.tsx
│   │   └── NotFound.tsx
│   ├── App.tsx          # Componente raiz
│   ├── main.tsx         # Ponto de entrada
│   └── index.css        # Estilos globais
├── index.html           # Template HTML
└── package.json
```

## 🔌 Integração com Backend

O frontend está configurado para se conectar com o backend Orchestra Planner. As variáveis de ambiente necessárias são:

```env
VITE_FRONTEND_FORGE_API_URL=http://localhost:8000
VITE_FRONTEND_FORGE_API_KEY=your-api-key
```

### Endpoints Implementados

#### Autenticação
- `POST /auth/magic-link` - Solicitar link de acesso
- `POST /auth/verify` - Verificar token de acesso

#### Projetos
- `POST /projects` - Criar novo projeto
- `GET /projects/{project_id}` - Obter detalhes do projeto
- `POST /projects/{project_id}/llm` - Configurar integração LLM

#### Tarefas
- `POST /projects/{project_id}/tasks` - Criar tarefa
- `POST /projects/{project_id}/tasks/{task_id}/select` - Selecionar tarefa
- `POST /projects/{project_id}/tasks/{task_id}/complete` - Marcar como concluída
- `POST /projects/{project_id}/tasks/{task_id}/abandon` - Abandonar tarefa
- `POST /projects/{project_id}/tasks/{task_id}/report` - Adicionar relatório

#### Membros
- `POST /projects/{project_id}/members/{user_id}/fire` - Remover membro
- `POST /projects/{project_id}/members/me/resign` - Sair do projeto

#### Convites
- `POST /projects/{project_id}/invites` - Criar convite
- `POST /invites/{token}/accept` - Aceitar convite

#### Papéis
- `POST /projects/{project_id}/roles` - Criar novo papel

## 🎯 Páginas Principais

### Home (`/`)
Landing page com apresentação do produto, features e call-to-action.

### Login (`/login`)
Autenticação via magic link - usuário insere email e recebe link de acesso seguro.

### Dashboard (`/dashboard`)
Visão geral de projetos, tarefas e estatísticas. Requer autenticação.

### Project Detail (`/projects/:projectId`)
Detalhes completos do projeto com abas para tarefas, membros e configurações.

## 🔐 Autenticação

O sistema utiliza **Magic Link Authentication**:

1. Usuário insere email na página de login
2. Backend envia link seguro por email
3. Usuário clica no link com token
4. Frontend verifica token e armazena sessão

Token é armazenado em `localStorage` e incluído em todas as requisições subsequentes.

## 🎨 Componentes Disponíveis

O projeto inclui componentes shadcn/ui pré-configurados:

- Button
- Card
- Input
- Dialog
- Tabs
- Select
- Toast (Sonner)
- E muitos mais...

Importe-os de `@/components/ui/*`.

## 📊 Dados Simulados

Atualmente, o frontend utiliza dados simulados para demonstração. Para integração real:

1. Remova os dados mock nos hooks `useEffect`
2. Substitua por chamadas ao `apiClient`
3. Implemente tratamento de erros apropriado

Exemplo:

```typescript
// Antes (mock)
const mockProjects = [...]
setProjects(mockProjects)

// Depois (real)
const projects = await apiClient.getProjects()
setProjects(projects)
```

## 🚢 Deployment

### Build

```bash
pnpm build
```

Gera arquivos otimizados em `dist/`.

### Ambiente de Produção

1. Configure variáveis de ambiente
2. Execute `pnpm build`
3. Deploy dos arquivos em `dist/`

## 🛠️ Desenvolvimento

### Adicionar Nova Página

1. Crie arquivo em `client/src/pages/NovaPage.tsx`
2. Adicione rota em `App.tsx`
3. Implemente layout com `DashboardLayout` se necessário

### Adicionar Novo Componente

1. Crie arquivo em `client/src/components/NovoComponente.tsx`
2. Exporte como default
3. Importe onde necessário

### Estilização

- Use Tailwind CSS classes
- Tokens de design em `client/src/index.css`
- Cores semânticas: `bg-primary`, `text-foreground`, etc.

## 📝 Checklist de Desenvolvimento

- [x] Setup inicial do projeto
- [x] Configuração de design tokens
- [x] Componentes base (DashboardLayout, etc.)
- [x] Páginas principais (Home, Login, Dashboard, ProjectDetail)
- [x] Cliente API com tipos TypeScript
- [x] Contexto de autenticação
- [x] Hooks customizados
- [ ] Integração real com backend
- [ ] Testes unitários
- [ ] Testes E2E
- [ ] Documentação de componentes

## 🐛 Troubleshooting

### Erro de CORS

Se encontrar erros de CORS ao chamar o backend:

1. Verifique se o backend está rodando
2. Confirme `VITE_FRONTEND_FORGE_API_URL` está correto
3. Verifique configuração CORS no backend

### Estilo não aplicado

1. Limpe cache: `pnpm clean`
2. Reinstale dependências: `pnpm install`
3. Reinicie servidor: `pnpm dev`

### Erro de TypeScript

Execute `pnpm check` para verificar erros de tipo.

## 📚 Recursos

- [React 19 Docs](https://react.dev)
- [Tailwind CSS](https://tailwindcss.com)
- [shadcn/ui](https://ui.shadcn.com)
- [Wouter](https://github.com/molefrog/wouter)
- [Sonner](https://sonner.emilkowal.ski/)

## 📄 Licença

MIT

## 👥 Suporte

Para dúvidas ou problemas, abra uma issue no repositório.

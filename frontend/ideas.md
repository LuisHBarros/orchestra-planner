# Orchestra Planner Frontend - Design Concepts

## Análise do Projeto

O Orchestra Planner é um sistema de gerenciamento de projetos e tarefas com foco em alocação de recursos, agendamento inteligente e colaboração em equipe. O backend oferece funcionalidades de:

- Autenticação com magic links
- Gerenciamento de projetos
- Gestão de tarefas com dependências
- Alocação de membros com diferentes níveis de senioridade
- Integração com LLM para otimização de agendamento
- Sistema de convites e papéis

---

## Resposta 1: Minimalismo Funcional com Acentos Modernos

<response>
<probability>0.08</probability>
<text>

### Design Movement
**Bauhaus Digital** - Simplicidade radical com foco em funcionalidade, inspirado em design de sistemas e interfaces de ferramentas profissionais modernas.

### Core Principles
1. **Clareza Radical**: Cada elemento serve um propósito claro; nada é decorativo
2. **Hierarquia Tipográfica Forte**: Distinção clara entre títulos, subtítulos e corpo de texto
3. **Espaçamento Generoso**: Respiro visual entre componentes para reduzir cognitivo
4. **Acessibilidade Primeiro**: Contraste alto, estados visuais claros, navegação intuitiva

### Color Philosophy
- **Palette**: Monocromático com acentos em uma cor primária única
  - Fundo: Branco puro (`#FFFFFF`)
  - Texto: Cinza escuro profundo (`#1A1A1A`)
  - Acentos: Azul-índigo vibrante (`#4F46E5`)
  - Secundários: Cinzas neutros para estados inativos
- **Reasoning**: Reduz carga visual, permite que dados e conteúdo brilhem. Azul-índigo transmite confiança e profissionalismo.

### Layout Paradigm
- **Sidebar Esquerda Persistente**: Navegação fixa com ícones + labels, colapsável em mobile
- **Conteúdo Fluido Direito**: Grid responsivo que se adapta ao tamanho da tela
- **Cards Elevados**: Uso de sombras sutis para criar profundidade sem distrair
- **Tabelas e Listas**: Estruturadas com linhas divisórias leves, sem bordas pesadas

### Signature Elements
1. **Ícones Minimalistas**: Stroke-based, peso consistente, 24px padrão
2. **Badges de Status**: Pequenas cápsulas coloridas para status de tarefas (em progresso, concluída, bloqueada)
3. **Linhas Divisórias Sutis**: Separadores em cinza muito claro para estruturar sem pesar

### Interaction Philosophy
- **Feedback Imediato**: Hover states em azul-índigo claro, transições suaves de 150ms
- **Confirmação Visual**: Toasts discretos no canto inferior direito
- **Modais Focados**: Diálogos com fundo semi-transparente, conteúdo centralizado
- **Micro-interações**: Botões que mudam de cor ao hover, ícones que se animam levemente

### Animation
- **Transições Globais**: 150ms ease-out para hover/focus
- **Entrada de Componentes**: Fade-in de 200ms ao carregar
- **Carregamento**: Spinner minimalista (apenas um ícone girando)
- **Confirmações**: Checkmark animado com scale-up suave

### Typography System
- **Display (Títulos Principais)**: Geist Sans Bold, 32px, line-height 1.2
- **Heading 1 (Seções)**: Geist Sans SemiBold, 24px, line-height 1.3
- **Heading 2 (Subsections)**: Geist Sans SemiBold, 18px, line-height 1.4
- **Body (Padrão)**: Geist Sans Regular, 14px, line-height 1.6
- **Small (Labels/Captions)**: Geist Sans Regular, 12px, line-height 1.5
- **Monospace (Dados/IDs)**: IBM Plex Mono, 12px (para UUIDs, tokens, etc.)

</text>
</response>

---

## Resposta 2: Design Elegante com Gradientes Subtis

<response>
<probability>0.07</probability>
<text>

### Design Movement
**Soft Modernism** - Elegância contemporânea com gradientes suaves, tipografia sofisticada e um toque de luxo acessível.

### Core Principles
1. **Profundidade Sutil**: Gradientes e sombras criam dimensão sem parecer pesado
2. **Tipografia Expressiva**: Fontes com personalidade que comunicam confiança
3. **Espaçamento Respirável**: Layout generoso que não sente apertado
4. **Transições Fluidas**: Cada interação é suave e satisfatória

### Color Philosophy
- **Palette**: Gradiente de azul para roxo com neutros quentes
  - Fundo: Branco com toque de azul muito claro (`#F8FAFC`)
  - Primário: Azul-roxo (`#6366F1` a `#8B5CF6`)
  - Acentos: Âmbar suave para ações positivas (`#F59E0B`)
  - Texto: Cinza azulado escuro (`#1E293B`)
- **Reasoning**: Gradientes criam movimento visual, cores quentes (âmbar) contrastam com fundo frio, transmitindo sofisticação.

### Layout Paradigm
- **Two-Column Asymmetric**: Sidebar esquerda com 280px, conteúdo direito fluido
- **Cards com Gradientes Sutis**: Fundo branco com gradiente muito leve (azul para roxo)
- **Separadores Visuais**: Linhas com gradiente ao invés de cores sólidas
- **Floating Action Buttons**: Botões de ação flutuam sobre o conteúdo com sombra profunda

### Signature Elements
1. **Gradientes de Fundo**: Cada card tem um gradiente sutil de azul a roxo
2. **Ícones com Cor**: Ícones primários em azul-roxo, secundários em cinza
3. **Badges Gradientes**: Status badges com gradientes (sucesso = verde-esmeralda, erro = vermelho-coral)

### Interaction Philosophy
- **Hover Elevation**: Cards sobem com sombra maior ao hover
- **Ripple Effects**: Efeito de ondulação ao clicar em botões
- **Transições Suaves**: 300ms ease-out para todas as transições
- **Confirmações Animadas**: Checkmarks com bounce suave

### Animation
- **Entrada de Página**: Fade-in + slide-up de 400ms
- **Hover de Cards**: Elevação com sombra crescente
- **Carregamento**: Spinner com gradiente animado
- **Confirmações**: Confetti sutil ou checkmark com bounce

### Typography System
- **Display**: Poppins Bold, 36px, line-height 1.2, cor primária
- **Heading 1**: Poppins SemiBold, 28px, line-height 1.3
- **Heading 2**: Poppins Medium, 20px, line-height 1.4
- **Body**: Inter Regular, 14px, line-height 1.6, cor texto
- **Small**: Inter Regular, 12px, line-height 1.5, cor muted
- **Monospace**: JetBrains Mono, 12px (dados técnicos)

</text>
</response>

---

## Resposta 3: Design Corporativo Robusto com Dados em Destaque

<response>
<probability>0.06</probability>
<text>

### Design Movement
**Enterprise Modern** - Design corporativo sem parecer entediante, com foco em legibilidade de dados e eficiência visual.

### Core Principles
1. **Dados Legíveis**: Tabelas e gráficos com contraste máximo e espaçamento claro
2. **Navegação Intuitiva**: Estrutura de informação clara, sem surpresas
3. **Densidade Controlada**: Mais informação sem parecer apertado
4. **Profissionalismo Consistente**: Cores corporativas, tipografia séria

### Color Philosophy
- **Palette**: Azul corporativo com acentos em verde (sucesso) e vermelho (alerta)
  - Fundo: Cinza muito claro (`#F5F7FA`)
  - Primário: Azul corporativo (`#0052CC`)
  - Sucesso: Verde profissional (`#2ECC71`)
  - Alerta: Vermelho corporativo (`#E74C3C`)
  - Texto: Cinza escuro (`#2C3E50`)
- **Reasoning**: Cores corporativas transmitem confiança, verde/vermelho são universalmente reconhecidos para status.

### Layout Paradigm
- **Dashboard Grid**: Layout em grid 12 colunas para máxima flexibilidade
- **Tabelas Estruturadas**: Linhas alternadas com fundo claro/escuro para legibilidade
- **Painéis Informativos**: Cards com ícones grandes, números em destaque
- **Sidebar Compacta**: Navegação vertical com ícones + texto, sem expansão

### Signature Elements
1. **Ícones Corporativos**: Solid-filled, 20px, em azul primário
2. **Indicadores de Status**: Círculos coloridos (verde/amarelo/vermelho) + texto
3. **Gráficos Integrados**: Mini-gráficos em cards para visualizar tendências

### Interaction Philosophy
- **Cliques Óbvios**: Botões com bordas claras, hover com fundo preenchido
- **Confirmações Explícitas**: Modais de confirmação para ações destrutivas
- **Feedback Textual**: Mensagens claras em toasts
- **Navegação Breadcrumb**: Caminho claro até a página atual

### Animation
- **Transições Rápidas**: 100ms ease-out (eficiência)
- **Carregamento**: Skeleton screens ao invés de spinners
- **Hover**: Mudança de cor + sombra leve
- **Confirmações**: Checkmark com fade-in

### Typography System
- **Display**: Roboto Bold, 32px, line-height 1.2, azul primário
- **Heading 1**: Roboto Bold, 24px, line-height 1.3
- **Heading 2**: Roboto Medium, 18px, line-height 1.4
- **Body**: Roboto Regular, 14px, line-height 1.6
- **Small**: Roboto Regular, 12px, line-height 1.5
- **Monospace**: Courier New, 12px (dados/IDs)

</text>
</response>

---

## Design Escolhido: **Minimalismo Funcional com Acentos Modernos**

Escolhi a **Resposta 1** por ser a mais adequada para um sistema de gerenciamento de projetos. Razões:

1. **Clareza para Dados**: Interfaces minimalistas deixam dados e tarefas em primeiro plano
2. **Profissionalismo**: Azul-índigo transmite confiança em ferramentas corporativas
3. **Escalabilidade**: Design simples é fácil de estender com novos recursos
4. **Acessibilidade**: Contraste alto e hierarquia clara beneficiam todos os usuários
5. **Performance Cognitiva**: Menos elementos visuais = menos distração, mais foco em trabalho

### Implementação
- **Tipografia**: Geist Sans para UI (moderna, legível), IBM Plex Mono para dados técnicos
- **Cores**: Branco puro, cinza neutro, azul-índigo vibrante (`#4F46E5`)
- **Componentes**: Sidebar persistente, cards elevados, badges de status
- **Animações**: Transições suaves de 150ms, feedback visual imediato
- **Espaçamento**: Generoso, com respiro entre componentes

Este design será aplicado em todas as páginas, componentes e interações do Orchestra Planner.

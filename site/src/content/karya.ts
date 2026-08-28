export const repositoryUrl = 'https://github.com/viniciusjsdev/karya'
export const siteBase = '/karya/'

export const docs = {
  readme: `${repositoryUrl}#readme`,
  architecture: `${repositoryUrl}/blob/main/docs/karya-architecture.md`,
  routing: `${repositoryUrl}/blob/main/docs/karya-routing.md`,
  workflowMap: `${repositoryUrl}/blob/main/docs/factory-workflow-map.md`,
  harness: `${repositoryUrl}/blob/main/docs/project-harness-factory.md`,
  product: `${repositoryUrl}/blob/main/docs/product-workflow.md`,
  research: `${repositoryUrl}/blob/main/docs/research-workflow.md`,
  marketing: `${repositoryUrl}/blob/main/docs/marketing-workflow.md`,
  contributing: `${repositoryUrl}/blob/main/CONTRIBUTING.md`,
} as const

export const navigation = [
  { id: 'concept', label: 'Concept' },
  { id: 'workflow', label: 'Workflow' },
  { id: 'architecture', label: 'Architecture' },
  { id: 'routing', label: 'Routing' },
  { id: 'factories', label: 'Factories' },
  { id: 'why', label: 'Why Karya' },
  { id: 'start', label: 'Get started' },
] as const

export type DetailItem = {
  id: string
  label: string
  summary: string
  input: string
  output: string
  owner: string
  constraints: string
  documentation: { label: string; href: string }[]
}

export const workflowSteps: DetailItem[] = [
  {
    id: 'objective',
    label: 'User objective',
    summary: 'The immediate desired outcome—not merely the project type—starts routing.',
    input: 'A request plus relevant project or artifact state.',
    output: 'A bounded understanding of what should change now.',
    owner: 'Human owner and Karya conversation.',
    constraints:
      'A multi-outcome request still needs one primary route and explicit optional handoffs.',
    documentation: [{ label: 'Routing', href: docs.routing }],
  },
  {
    id: 'classification',
    label: 'Classification',
    summary: 'Karya classifies the objective as direct work or as one independent Factory outcome.',
    input: 'Immediate outcome and observed artifact state.',
    output: 'Direct, MVP, Research, Marketing, or Project Harness classification.',
    owner: '$karya coordination.',
    constraints: 'Classification is not execution and does not authorize work.',
    documentation: [{ label: 'Routing model', href: docs.routing }],
  },
  {
    id: 'recommendation',
    label: 'Route + runtime',
    summary:
      'Karya recommends the smallest suitable route, advisory model/reasoning, and optional economic executor eligibility.',
    input: 'Classification, project state, cost preference, risk, and complexity of reasoning.',
    output:
      'Entry skill, planned capabilities, rationale, downshift condition, economic option, fallback, and audit requirement.',
    owner: '$karya coordination.',
    constraints: 'Without a resolved Harness manifest, the runtime recommendation is advisory.',
    documentation: [{ label: 'Routing', href: docs.routing }],
  },
  {
    id: 'approval',
    label: 'Explicit approval',
    summary: 'The human approves, rejects, or revises the exact recommended scope.',
    input: 'A recommendation with reasons, exclusions, and scope.',
    output: 'Approved scope—or a revised route.',
    owner: 'Human owner.',
    constraints:
      'Approval never silently includes another Factory, publication, spend, credentials, or external writes.',
    documentation: [{ label: 'Conversation contract', href: docs.routing }],
  },
  {
    id: 'capability',
    label: 'Specialist capability',
    summary:
      'Approved specialist skills retain their own prerequisites, contracts, and safety gates.',
    input: 'Explicitly approved route and durable project artifacts.',
    output:
      'A domain-correct plan, implementation, research, launch artifact, or Harness operation.',
    owner: 'The selected specialist capability; Karya remains the user-facing coordinator.',
    constraints:
      'Internal specialist use normally stays in the conversation; it does not imply subagents.',
    documentation: [{ label: 'Architecture', href: docs.architecture }],
  },
  {
    id: 'execution',
    label: 'Execution',
    summary: 'The approved contract is acted on inside its declared boundaries.',
    input:
      'Contracts, Specs, knowledge, selected skill, and materialized runtime when Harness is used.',
    output: 'Changed artifacts and command results.',
    owner: 'Codex or an explicitly approved bounded executor such as OpenCode.',
    constraints:
      'OpenCode is optional and cannot redefine decisions, authorize external actions, broaden scope, or approve itself.',
    documentation: [
      { label: 'Karya method', href: `${repositoryUrl}/blob/main/docs/karya-method.md` },
    ],
  },
  {
    id: 'evidence',
    label: 'Evidence',
    summary:
      'Claims of completion are connected to tests, artifacts, commands, and structured receipts.',
    input: 'Execution outputs and required validation identifiers.',
    output: 'Reconciled completion evidence or an explicit gap such as needs_design.',
    owner: 'Executor produces evidence; validators reconcile it.',
    constraints:
      '“Executed” is not the same as “proved.” Prose alone is insufficient when artifacts must reconcile.',
    documentation: [{ label: 'Project Harness', href: docs.harness }],
  },
  {
    id: 'audit',
    label: 'Review + audit',
    summary:
      'Independent review checks the Spec, reality, validation, and evidence before the result is trusted.',
    input: 'Spec, resolved runtime, diff or artifacts, tests, and completion evidence.',
    output:
      'Approved, changes requested, blocked, or failed—with a unified result reported by Karya.',
    owner: 'Independent reviewer or Factory-specific auditor.',
    constraints: 'The author or executor cannot self-approve missing evidence.',
    documentation: [{ label: 'Harness audit', href: docs.harness }],
  },
]

export const beforeFlow = [
  ['Chat', 'Important context begins inside one conversation.'],
  ['Agent', 'Decisions may remain implicit or be rediscovered.'],
  ['Code', 'The result can outlive the reasoning that produced it.'],
] as const

export const structuredFlow = [
  ['Intent', 'The immediate outcome is made explicit.'],
  ['Durable knowledge', 'Project truth survives the conversation.'],
  ['Spec / contract', 'A bounded change becomes executable.'],
  ['Skill', 'A reusable capability applies the contract.'],
  ['Routing', 'The smallest capable path and runtime are selected.'],
  ['Execution', 'Approved work changes artifacts.'],
  ['Evidence', 'Claims reconcile with commands and outputs.'],
  ['Audit', 'Independent review checks contract against reality.'],
] as const

export const architectureItems = [
  {
    id: 'project',
    label: 'Project',
    kind: 'truth',
    x: 245,
    y: 0,
    what: 'The product, system, automation, or repository being built and evolved.',
    why: 'It is the subject Karya helps humans and AI work on reliably.',
    contains: 'Code, product/domain truth, decisions, contracts, tests, and history.',
    relationship: 'Knowledge, Specs, and Skills organize how the project can be changed safely.',
    not: 'Karya itself.',
    href: docs.architecture,
  },
  {
    id: 'knowledge',
    label: 'Knowledge',
    kind: 'artifact',
    x: 40,
    y: 130,
    what: 'Durable project truth, architecture, rules, decisions, Docs, and ADRs.',
    why: 'A clean Thread can continue without inheriting a design conversation.',
    contains: 'Persistent context; Codex-facing operational knowledge may live under .codex/.',
    relationship: 'Knowledge informs Specs and gives isolated Threads durable context.',
    not: 'Chat history or ephemeral runtime status.',
    href: docs.harness,
  },
  {
    id: 'specs',
    label: 'Specs',
    kind: 'artifact',
    x: 245,
    y: 130,
    what: 'Bounded executable units of change, with human intent and resolved execution policy.',
    why: 'They let a clean implementation Thread act without silently redesigning the work.',
    contains: 'SPEC.md plus SPEC.execution.json when Project Harness materializes runtime.',
    relationship:
      'Specs bind human intent to a declared Thread, runtime, validation, and evidence.',
    not: 'A general knowledge base or an implementation transcript.',
    href: docs.harness,
  },
  {
    id: 'skills',
    label: 'Skills',
    kind: 'capability',
    x: 450,
    y: 130,
    what: 'Specialized, reusable capabilities centered on SKILL.md and optional references, scripts, schemas, and assets.',
    why: 'They preserve repeatable expertise without multiplying agents.',
    contains: 'Executable instructions and capability-specific supporting resources.',
    relationship:
      'Skills apply reusable capability to approved Specs without replacing project truth.',
    not: 'Project truth, one temporary task, or a Factory.',
    href: docs.architecture,
  },
  {
    id: 'threads',
    label: 'Threads',
    kind: 'runtime',
    x: 125,
    y: 285,
    what: 'Temporary, isolated design, implementation, worker, or review contexts.',
    why: 'Isolation keeps responsibilities clear and makes handoff artifacts testable.',
    contains: 'The smallest useful context for one purpose.',
    relationship: 'Threads consume durable artifacts and return implementation or review evidence.',
    not: 'Durable knowledge; Threads communicate through artifacts, not chat history.',
    href: docs.harness,
  },
  {
    id: 'runtime',
    label: 'Runtime',
    kind: 'runtime',
    x: 365,
    y: 285,
    what: 'The selected model, reasoning level, working context, thread mode, and execution policy.',
    why: 'A resolved Spec makes execution reproducible and prevents silent default drift.',
    contains: 'Materialized runtime policy and ephemeral mappings/status under .harness/runtime/.',
    relationship: 'Runtime resolves how an approved Spec is executed without changing its intent.',
    not: 'Persistent domain truth, secrets, transcripts, or an advisory recommendation alone.',
    href: docs.harness,
  },
  {
    id: 'karya',
    label: 'Karya',
    kind: 'foundation',
    x: 70,
    y: 450,
    what: 'The framework, system, and umbrella that coordinates durable AI-native development.',
    why: 'It connects intent, durable artifacts, reusable capabilities, runtime, validation, and evidence.',
    contains: 'An optional conversational coordinator and four independent Factories.',
    relationship:
      'Karya is the foundation connecting intent, artifacts, execution, evidence, and audit.',
    not: 'The product, a universal autonomous agent, a mandatory gateway, or a fifth Factory.',
    href: docs.architecture,
  },
] as const

export const architectureEdges = [
  ['project', 'knowledge'],
  ['project', 'specs'],
  ['project', 'skills'],
  ['knowledge', 'threads'],
  ['specs', 'threads'],
  ['specs', 'runtime'],
  ['skills', 'runtime'],
  ['threads', 'karya'],
  ['runtime', 'karya'],
] as const

export const knowledgeChain = [
  {
    label: 'Knowledge',
    role: 'Preserves truth',
    text: 'Docs, ADRs, architecture, business rules, and operational context survive transient Threads.',
  },
  {
    label: 'Spec',
    role: 'Bounds a change',
    text: 'Human intent and acceptance become one clean-thread-executable unit; runtime can be resolved separately.',
  },
  {
    label: 'Skill',
    role: 'Applies capability',
    text: 'A stable, specialized procedure acts on the Spec without becoming the source of project truth.',
  },
  {
    label: 'Runtime + Thread',
    role: 'Executes in isolation',
    text: 'The declared model, reasoning, context, and thread purpose carry out the bounded work.',
  },
  {
    label: 'Evidence + audit',
    role: 'Makes completion verifiable',
    text: 'Commands, artifacts, tests, and independent review reconcile the contract with reality.',
  },
] as const

export const routingExamples = [
  {
    objective: 'Build a new product from an idea or PRD',
    route: 'MVP Factory',
    entry: 'product-brief-architect',
    reason: 'The immediate outcome is product definition and construction.',
  },
  {
    objective: 'Challenge demand for a market hypothesis',
    route: 'Research Factory',
    entry: 'market-research-architect',
    reason: 'The immediate outcome is evidence and a market decision, not construction.',
  },
  {
    objective: 'Prepare and evaluate a commercial launch',
    route: 'Marketing Factory',
    entry: 'commercial-launch-architect',
    reason: 'The immediate outcome is positioning, launch execution boundaries, and learning.',
  },
  {
    objective: 'Make an existing project resumable across clean AI Threads',
    route: 'Project Harness Factory',
    entry: 'project-harness-architect',
    reason: 'The immediate outcome is durable AI operating structure for a project.',
  },
  {
    objective: 'Fix one bounded, sufficiently defined implementation issue',
    route: 'Direct execution',
    entry: 'Codex or one matching specialist',
    reason: 'No Factory contract is needed for a bounded and resolved task.',
  },
] as const

export const workflowTrace = [
  [
    'Request',
    '“I want to create an automation that monitors processes and produces a daily report.”',
  ],
  ['Understand', 'Karya identifies creation of a product/system as the immediate outcome.'],
  [
    'Classify',
    'MVP Factory is primary; Harness is not inferred merely because the product is an automation.',
  ],
  [
    'Recommend',
    'Start with product definition, name the planned capabilities, runtime rationale, exclusions, and audit.',
  ],
  ['Approve', 'The human approves or revises that exact scope.'],
  [
    'Execute',
    'Approved product specialists produce contracts and implementation; Karya remains the conversational coordinator.',
  ],
  ['Prove', 'Validation, artifacts, and explicit remaining gaps become the unified result.'],
] as const

export type Factory = {
  id: string
  name: string
  summary: string
  purpose: string
  when: string
  input: string
  result: string
  flow: string[]
  href: string
  accent: string
}

export const factories: Factory[] = [
  {
    id: 'mvp',
    name: 'MVP Factory',
    summary: 'Define and build a testable product.',
    purpose:
      'Turn product intent into a hosted, testable MVP through explicit frontend, backend, infrastructure, and validation contracts.',
    when: 'Define, build, integrate, host, or validate a product, system, or automation.',
    input: 'Idea, PRD, client notes, screen list, or existing partial project.',
    result: 'A validated MVP with explicit remaining gaps and preserved API/product semantics.',
    flow: [
      'Product contract',
      'React frontend',
      'Django contract + approval',
      'Implementation + audit',
      'Infrastructure + validation',
    ],
    href: docs.product,
    accent: '#C45A3C',
  },
  {
    id: 'research',
    name: 'Research Factory',
    summary: 'Investigate and challenge a market hypothesis.',
    purpose:
      'Investigate and challenge a bounded market hypothesis with traceable, normalized evidence.',
    when: 'Research demand, competitors, users, evidence, a category, an app, or a market hypothesis.',
    input: 'Idea, PRD, existing product, app, cohort, or explicit market question.',
    result:
      'An auditable evidence bundle and proceed, experiment, revise, pause, or reject decision.',
    flow: [
      'Research contract',
      'Evidence routing',
      'Specialized collection',
      'Normalization',
      'Adversarial validation',
    ],
    href: docs.research,
    accent: '#1F6670',
  },
  {
    id: 'marketing',
    name: 'Marketing Factory',
    summary: 'Prepare, operate, and evaluate a launch.',
    purpose:
      'Prepare a commercial launch, create artifacts, execute only bounded approved operations, and learn from measured results.',
    when: 'Position, launch, publish, operate, or evaluate commercial work for an existing product.',
    input: 'Existing product, service, launch brief, or accepted market decision.',
    result:
      'Launch contract, creative pack, verifiable receipts, metrics, and a scale/iterate/pivot/pause/stop decision.',
    flow: [
      'Launch contract',
      'Human account setup',
      'Creative pack',
      'Approved operation',
      'Commercial validation',
    ],
    href: docs.marketing,
    accent: '#B58A3C',
  },
  {
    id: 'harness',
    name: 'Project Harness Factory',
    summary: 'Make AI project operations durable.',
    purpose:
      'Make a project operable and scalable with AI through durable knowledge, Specs, Skills, runtime, optional economic execution, evidence, and audit.',
    when: 'Structure how an empty or existing project works durably across clean AI Threads.',
    input: 'Idea, repository, existing project, or artifact from any workflow.',
    result:
      'A minimal durable harness, executable Specs, resolved runtime, evidence, review, and reconciled audit.',
    flow: [
      'Harness audit',
      'Durable context',
      'READY Spec',
      'Codex runtime or optional OpenCode executor',
      'Evidence + independent audit',
    ],
    href: docs.harness,
    accent: '#74866B',
  },
]

export const harnessFlow = [
  ['Audit + plan', 'Inspect what exists; classify mechanisms as reuse, specialize, or create.'],
  [
    'Durable context',
    'Materialize the minimum accepted AGENTS/.codex/docs structure without flattening project truth.',
  ],
  ['Design Thread', 'Resolve consequential decisions into Docs, ADRs, and a bounded SPEC.'],
  [
    'READY Spec',
    'Pair human-readable intent with SPEC.execution.json and clean-thread validation.',
  ],
  ['Runtime router', 'Start or resume the mapped isolated Thread using the materialized policy.'],
  [
    'Completion evidence',
    'Reconcile IDs, commands, artifacts, tests, runtime identity, and gaps such as needs_design.',
  ],
  [
    'Independent review',
    'Review receives the Spec, manifest, changes, tests, and completion evidence.',
  ],
  [
    'Harness audit',
    'Audit durable truth, runtime state, implementation reality, and review receipt.',
  ],
] as const

export const benefits = [
  {
    title: 'Durable knowledge',
    summary: 'Important context should survive the conversation.',
    problem: 'Important project context disappears between conversations.',
    mechanism:
      'Project truth, Docs, ADRs, and Codex-facing context live outside transient Threads.',
    result:
      'A clean Thread can continue from explicit artifacts instead of rediscovering the project.',
  },
  {
    title: 'Explicit contracts',
    summary: 'Intent should stay bounded while implementation moves.',
    problem: 'An executor can silently reinterpret intent while changing code.',
    mechanism:
      'Specs and specialist contracts separate human intent, acceptance, and resolved execution policy.',
    result: 'Implementation can be checked against a bounded, durable definition of done.',
  },
  {
    title: 'Reusable capabilities',
    summary: 'Stable expertise should not be improvised every time.',
    problem: 'Specialized procedures are repeatedly improvised inside prompts.',
    mechanism:
      'Independent Skills package stable instructions, references, scripts, schemas, and assets.',
    result: 'Expertise becomes reusable while project truth remains in its proper artifacts.',
  },
  {
    title: 'Deliberate routing',
    summary: 'The route should match the immediate outcome.',
    problem: 'Every objective is treated as the same kind of agent task.',
    mechanism:
      'Karya classifies the immediate outcome and recommends the smallest capable route and runtime.',
    result:
      'Bounded work stays direct; Factory workflows are used only when their contracts add value.',
  },
  {
    title: 'Human approval boundaries',
    summary: 'Recommendation should never become implicit permission.',
    problem: 'A recommendation can be mistaken for permission to act or broaden scope.',
    mechanism: 'Karya explains route, runtime, rationale, exclusions, and exact scope, then waits.',
    result:
      'Factories, external writes, spend, credentials, and consequential choices remain human-controlled.',
  },
  {
    title: 'Evidence-driven delivery',
    summary: 'Completion claims should reconcile with reality.',
    problem:
      'A passing narrative can hide missing files, tests, receipts, or mismatched execution.',
    mechanism:
      'Completion evidence and independent audit reconcile contracts with commands and reality.',
    result: '“Executed” and “proved” remain visibly different states.',
  },
] as const

export const isAndIsNot = [
  ['An open-source development system for Codex', 'The application being built'],
  ['A structural framework and umbrella project', 'A universal autonomous agent'],
  ['An optional conversational coordinator', 'A mandatory gateway or fifth Factory'],
  ['Four independent, opt-in workflow families', 'One mandatory end-to-end pipeline'],
  ['Durable artifacts shared across clean Threads', 'Persistent chat treated as project knowledge'],
  ['Recommendation followed by explicit approval', 'Implicit authorization or automatic handoff'],
] as const

export const getStartedLinks = [
  { label: 'Repository', href: repositoryUrl },
  { label: 'README', href: docs.readme },
  { label: 'Routing docs', href: docs.routing },
  { label: 'Architecture docs', href: docs.architecture },
  { label: 'Contributing', href: docs.contributing },
] as const

import { lazy, Suspense, useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { ArrowDown, ExternalLink, Github, ShieldCheck } from 'lucide-react'
import { Header } from './components/Header'
import { BenefitDisclosure } from './components/BenefitDisclosure'
import { ProblemFlow } from './components/ProblemFlow'
import { ProjectNavigation } from './components/ProjectNavigation'
import { Section, Arrow } from './components/Section'
import { WorkflowDiagram } from './components/WorkflowDiagram'
import {
  docs,
  factories,
  getStartedLinks,
  harnessFlow,
  isAndIsNot,
  knowledgeChain,
  repositoryUrl,
  routingExamples,
  workflowTrace,
} from './content/karya'

const ArchitectureDiagram = lazy(() => import('./components/ArchitectureDiagram'))

type Theme = 'amphora' | 'papyrus'

function resolveInitialTheme(): Theme {
  const saved = localStorage.getItem('karya-theme')
  if (saved === 'amphora' || saved === 'papyrus') return saved
  return 'amphora'
}

function App() {
  const [theme, setTheme] = useState<Theme>(resolveInitialTheme)
  const [routingIndex, setRoutingIndex] = useState(0)
  const [factoryId, setFactoryId] = useState('mvp')
  const selectedRouting = routingExamples[routingIndex] ?? routingExamples[0]!
  const selectedFactory = factories.find((factory) => factory.id === factoryId) ?? factories[0]!

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('karya-theme', theme)
  }, [theme])

  return (
    <>
      <a className="skip-link" href="#main-content">
        Skip to content
      </a>
      <Header
        theme={theme}
        onThemeChange={() => setTheme((value) => (value === 'amphora' ? 'papyrus' : 'amphora'))}
      />
      <main id="main-content">
        <section id="concept" className="hero scroll-mt-24">
          <div className="hero-grid" aria-hidden="true" />
          <motion.div
            className="hero-figure"
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.65 }}
          >
            <span className="hero-frame-label">IDENTITY / STRUCTURAL SUPPORT</span>
            <span className="hero-support-line hero-support-line-top" aria-hidden="true" />
            <img
              src="brand/icon/karya-caryatid-capital-master.png"
              alt="Karya Caryatid supporting an architectural capital"
              width="1254"
              height="1254"
            />
            <span className="hero-support-line hero-support-line-bottom" aria-hidden="true" />
            <span className="structural-caption">STRUCTURAL SUPPORT / 01</span>
          </motion.div>
          <motion.div
            className="hero-copy"
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.65, delay: 0.08 }}
          >
            <span className="eyebrow">Open-source / AI-native development system</span>
            <h1 aria-label="Karya">KARYA</h1>
            <p className="hero-statement">The structure behind AI-native development.</p>
            <p className="hero-description">
              Karya gives AI-native development durable structure through project knowledge, living
              navigation maps, executable Specs, reusable Skills, isolated Threads, deliberate
              routing, validation, evidence, and audit.
            </p>
            <div className="hero-actions">
              <a className="button primary" href="#navigation-map">
                Explore living project navigation <ArrowDown size={17} />
              </a>
              <a className="button secondary" href={repositoryUrl} target="_blank" rel="noreferrer">
                <Github size={17} /> View on GitHub
              </a>
            </div>
          </motion.div>
          <div className="hero-foundation">
            {['INTENT', 'DURABLE ARTIFACTS', 'EXECUTION', 'EVIDENCE'].map((label, index) => (
              <motion.span
                key={label}
                initial={{ opacity: 0, y: 6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.28 + index * 0.08 }}
              >
                <small>{String(index + 1).padStart(2, '0')}</small>
                {label}
              </motion.span>
            ))}
          </div>
        </section>

        <Section
          eyebrow="01 / The problem"
          title="AI can produce code. The structure around that work is what disappears."
          intro="When decisions live only inside conversation, context is lost, architecture drifts, and completion becomes difficult to reproduce or audit."
        >
          <ProblemFlow />
        </Section>

        <Section
          id="why"
          eyebrow="02 / Why Karya"
          title="Structure changes what survives the session."
          intro="Each benefit is tied to a mechanism in Karya’s documented architecture—not to an abstract promise."
        >
          <BenefitDisclosure />
        </Section>

        <Section
          id="workflow"
          eyebrow="03 / Main workflow"
          title="How work moves through Karya"
          intro="Select each stage to inspect its input, output, owner, constraint, and source documentation. The human approval boundary is part of the architecture—not a footnote."
        >
          <WorkflowDiagram />
          <div className="boundary-statement">
            <span>Recommendation ≠ approval</span>
            <span>Routing ≠ execution</span>
            <span>Classification ≠ authorization</span>
          </div>
        </Section>

        <Section
          eyebrow="04 / Concrete trace"
          title="One objective, followed through the system"
          intro="This example comes from the repository README and demonstrates why the immediate outcome matters more than the word “automation.”"
        >
          <ol className="trace-list">
            {workflowTrace.map(([label, text], index) => (
              <li key={label}>
                <span>{String(index + 1).padStart(2, '0')}</span>
                <div>
                  <strong>{label}</strong>
                  <p>{text}</p>
                </div>
              </li>
            ))}
          </ol>
        </Section>

        <Section
          id="architecture"
          eyebrow="05 / Architecture"
          title="The system Karya holds together"
          intro="Karya is shown as the structural foundation, not as another peer box. Pan, zoom, focus, and select nodes; the essential relationships are also described below the graph."
        >
          <Suspense
            fallback={<div className="diagram-loading">Loading the interactive architecture…</div>}
          >
            <ArchitectureDiagram />
          </Suspense>
          <p className="diagram-summary">
            Project truth is preserved as Knowledge. Specs bound change. Skills apply reusable
            capabilities. Threads isolate responsibilities. Runtime materializes execution policy.
            Karya coordinates the structure without becoming the product or a fifth Factory.
          </p>
        </Section>

        <Section
          id="navigation-map"
          eyebrow="06 / Living navigation"
          title="Give models a map. Keep project context within reach."
          intro="As an application grows, relevant knowledge spreads across code, contracts, and decisions. Karya makes that context discoverable and keeps its navigation under review."
        >
          <ProjectNavigation />
        </Section>

        <Section
          eyebrow="07 / Durable transformation"
          title="Knowledge, Spec, and Skill are not synonyms"
          intro="Information becomes executable through a chain of artifacts and responsibilities. Each layer has one job."
        >
          <div className="knowledge-chain">
            {knowledgeChain.map((item, index) => (
              <div className="contents" key={item.label}>
                <article>
                  <span>{item.role}</span>
                  <h3>{item.label}</h3>
                  <p>{item.text}</p>
                </article>
                {index < knowledgeChain.length - 1 ? <Arrow /> : null}
              </div>
            ))}
          </div>
        </Section>

        <Section
          id="routing"
          eyebrow="08 / Routing"
          title="Karya recommends. The user approves."
          intro="Routing starts from the immediate desired outcome and current artifact state. These are illustrative routing examples, not a live classifier."
        >
          <div className="routing-layout">
            <div
              className="routing-options"
              role="group"
              aria-label="Illustrative routing examples"
            >
              <span className="eyebrow route-inspector-label">Route inspector / Input</span>
              {routingExamples.map((example, index) => (
                <button
                  type="button"
                  key={example.objective}
                  data-selected={index === routingIndex}
                  onClick={() => setRoutingIndex(index)}
                >
                  <span>{String(index + 1).padStart(2, '0')}</span>
                  {example.objective}
                </button>
              ))}
            </div>
            <aside className="routing-result" aria-live="polite">
              <span className="eyebrow route-inspector-label">
                Route inspector / Recommended route
              </span>
              <h3>{selectedRouting.route}</h3>
              <p>{selectedRouting.reason}</p>
              <dl>
                <div>
                  <dt>Entry</dt>
                  <dd>{selectedRouting.entry}</dd>
                </div>
                <div>
                  <dt>Next boundary</dt>
                  <dd>Explain the recommendation and wait for explicit approval.</dd>
                </div>
              </dl>
            </aside>
          </div>
          <div className="routing-sequence" aria-label="Routing sequence">
            <span>Objective</span>
            <Arrow />
            <span>Classification</span>
            <Arrow />
            <span>Possible route</span>
            <Arrow />
            <span>Runtime + reason</span>
            <Arrow />
            <strong>Human approval</strong>
          </div>
        </Section>

        <Section
          id="factories"
          eyebrow="09 / Factories"
          title="Four independent workflow families"
          intro="Every Factory is opt-in. None is a prerequisite, hidden stage, or automatic continuation of another."
        >
          <div className="factory-tabs" role="tablist" aria-label="Karya Factories">
            {factories.map((factory, index) => (
              <button
                type="button"
                role="tab"
                aria-selected={factory.id === factoryId}
                aria-controls="factory-detail"
                key={factory.id}
                onClick={() => setFactoryId(factory.id)}
                style={{ '--factory-accent': factory.accent } as React.CSSProperties}
              >
                <span className="factory-id">F.{String(index + 1).padStart(2, '0')}</span>
                <span className="factory-indicator" aria-hidden="true" />
                <strong>{factory.name}</strong>
                <span>{factory.summary}</span>
                <small>{factory.when}</small>
              </button>
            ))}
          </div>
          <article
            id="factory-detail"
            className="factory-detail"
            style={{ '--factory-accent': selectedFactory.accent } as React.CSSProperties}
          >
            <div className="factory-copy">
              <span className="eyebrow">{selectedFactory.name}</span>
              <h3>{selectedFactory.purpose}</h3>
              <dl>
                <div>
                  <dt>When to use</dt>
                  <dd>{selectedFactory.when}</dd>
                </div>
                <div>
                  <dt>Input</dt>
                  <dd>{selectedFactory.input}</dd>
                </div>
                <div>
                  <dt>Expected result</dt>
                  <dd>{selectedFactory.result}</dd>
                </div>
              </dl>
              <a href={selectedFactory.href} target="_blank" rel="noreferrer">
                Read the workflow <ExternalLink size={14} />
              </a>
            </div>
            <ol className="factory-flow">
              {selectedFactory.flow.map((step, index) => (
                <li key={step}>
                  <span>{String(index + 1).padStart(2, '0')}</span>
                  <strong>{step}</strong>
                </li>
              ))}
            </ol>
          </article>
          <div className="factory-map">
            <div className="karya-umbrella">
              <img
                src={`brand/icon/karya-icon-${theme === 'amphora' ? 'dark' : 'light'}-64.png`}
                alt=""
              />
              <div>
                <span>KARYA / COORDINATION</span>
                <strong>$karya</strong>
                <p>Classify → recommend → explain → approve → coordinate</p>
              </div>
            </div>
            <div className="factory-branches">
              {factories.map((factory) => (
                <div key={factory.id} style={{ borderTopColor: factory.accent }}>
                  <strong>{factory.name}</strong>
                  <span>Independent / opt-in</span>
                </div>
              ))}
            </div>
            <p>
              <strong>Direct skill invocation remains valid.</strong> Compatible artifacts may cross
              boundaries only through an explicit approved handoff with{' '}
              <code>automatic_handoff: false</code>. Karya is not a fifth Factory.
            </p>
          </div>
        </Section>

        <Section
          eyebrow="10 / Project Harness"
          title="A project that can survive the Thread that designed it"
          intro="Project Harness makes project knowledge, Specs, runtime, completion evidence, and review explicit—without turning chat history into durable truth."
        >
          <div className="harness-grid">
            {harnessFlow.map(([label, text], index) => (
              <article
                key={label}
                className={
                  label === 'Design Thread' || label === 'Independent review' ? 'emphasis' : ''
                }
              >
                <span>{String(index + 1).padStart(2, '0')}</span>
                <h3>{label}</h3>
                <p>{text}</p>
              </article>
            ))}
          </div>
          <div className="harness-boundary">
            <code>.codex/</code>
            <span>persistent operational knowledge</span>
            <div aria-hidden="true" />
            <code>.harness/runtime/</code>
            <span>gitignored ephemeral state</span>
          </div>
          <a className="text-link" href={docs.harness} target="_blank" rel="noreferrer">
            Explore the Project Harness contract <ExternalLink size={14} />
          </a>
        </Section>

        <Section
          id="evidence"
          eyebrow="11 / Evidence and audit"
          title="Execution is not the end."
          intro="Karya keeps an important distinction visible: a task can run without its completion claim being proved."
        >
          <div className="evidence-flow">
            <article>
              <span>01</span>
              <small>OUTPUT / EXECUTION</small>
              <h3>Execution</h3>
              <p>Approved work produces changed artifacts and command results.</p>
            </article>
            <Arrow />
            <article>
              <span>02</span>
              <small>SYSTEM / EVIDENCE</small>
              <h3>Evidence</h3>
              <p>IDs, files, tests, receipts, runtime identity, and required commands reconcile.</p>
            </article>
            <Arrow />
            <article>
              <span>03</span>
              <small>CONTROL / REVIEW</small>
              <h3>Independent review</h3>
              <p>
                Contract, changes, tests, and evidence are checked by the appropriate reviewer or
                auditor.
              </p>
            </article>
          </div>
          <div className="proof-callout">
            <ShieldCheck size={26} />
            <div>
              <strong>Structured prose is not sufficient evidence.</strong>
              <p>
                When a contract requires artifacts, commands, exact IDs, or an independent receipt,
                they must exist and agree with implementation reality.
              </p>
            </div>
          </div>
        </Section>

        <Section
          eyebrow="12 / Boundaries"
          title="What Karya is—and what it deliberately is not"
          intro="Clear boundaries keep coordination from becoming implicit authority."
        >
          <div className="is-grid">
            <div>
              <span className="eyebrow">Karya is</span>
              {isAndIsNot.map(([yes]) => (
                <p key={yes}>{yes}</p>
              ))}
            </div>
            <div>
              <span className="eyebrow">Karya is not</span>
              {isAndIsNot.map(([, no]) => (
                <p key={no}>{no}</p>
              ))}
            </div>
          </div>
        </Section>

        <Section
          eyebrow="13 / The name"
          title="The Caryatid is not decoration. She is structure."
          intro="In classical architecture, Caryatids are female figures used as structural supports. Karya uses that history as metaphor and identity—not as a literal translation or decorative Greek theme."
          className="story-section"
        >
          <div className="name-section">
            <img
              src="brand/icon/karya-caryatid-capital-master.png"
              alt="Karya Caryatid and capital master mark"
              width="1254"
              height="1254"
            />
            <div>
              <span className="eyebrow">IDENTITY / STRUCTURE</span>
              <p>
                The figure holds a construction. Karya holds the durable layer that lets humans and
                AI build, validate, and evolve a project without depending on one conversation’s
                memory.
              </p>
              <blockquote>“Karya is the structure behind AI-native development.”</blockquote>
            </div>
          </div>
        </Section>

        <Section
          id="start"
          eyebrow="14 / Get started"
          title="Start with Karya"
          intro="You do not need to know the catalog. Use the documented optional coordinator when the route is unclear—or invoke a specialist directly when you already know it."
        >
          <div className="start-grid">
            <div className="terminal" aria-label="Documented Karya invocation example">
              <div>
                <span />
                <span />
                <span />
                <small>OBJECTIVE.txt</small>
              </div>
              <pre>
                <code>
                  <b>$karya</b> I want to create an automation{`\n`}that monitors processes and
                  produces{`\n`}a daily report.
                </code>
              </pre>
              <p>Expected behavior: inspect → recommend → explain → wait for approval.</p>
            </div>
            <div className="start-copy">
              <h3>Install the skills, then describe the objective.</h3>
              <pre>
                <code>git clone https://github.com/viniciusjsdev/karya.git{`\n`}cd karya</code>
              </pre>
              <p>
                The README contains the documented Windows, Linux, and macOS installation steps.
                Karya is designed and tested for OpenAI Codex.
              </p>
              <div className="link-grid">
                {getStartedLinks.map((link) => (
                  <a href={link.href} key={link.label} target="_blank" rel="noreferrer">
                    {link.label}
                    <ExternalLink size={14} />
                  </a>
                ))}
              </div>
            </div>
          </div>
        </Section>

        <section className="open-source-cta">
          <img src="brand/logo/karya-mark-terracotta-transparent.png" alt="Karya" />
          <div>
            <span className="eyebrow">OPEN SOURCE / MIT</span>
            <span className="cta-wordmark">KARYA</span>
            <h2>Inspect the structure. Use the skills. Help evolve the system.</h2>
            <p>
              The website is the visual map. The repository remains the technical source of truth.
            </p>
          </div>
          <div className="cta-links">
            <a href={repositoryUrl} target="_blank" rel="noreferrer">
              <Github size={17} /> View on GitHub
            </a>
            <a href={docs.architecture} target="_blank" rel="noreferrer">
              Read the documentation <ExternalLink size={14} />
            </a>
            <a href={docs.contributing} target="_blank" rel="noreferrer">
              Contribute <ExternalLink size={14} />
            </a>
          </div>
        </section>
      </main>
      <footer>
        <span>KARYA</span>
        <p>The structure behind AI-native development.</p>
        <a href="#concept">Back to top ↑</a>
      </footer>
    </>
  )
}

export default App

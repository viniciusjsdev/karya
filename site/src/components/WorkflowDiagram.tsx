import { useState } from 'react'
import { ExternalLink, UserRound } from 'lucide-react'
import { workflowSteps } from '../content/karya'
import { Arrow } from './Section'

export function WorkflowDiagram() {
  const [selectedId, setSelectedId] = useState('objective')
  const selected = workflowSteps.find((step) => step.id === selectedId) ?? workflowSteps[0]!
  return (
    <div className="interactive-layout">
      <div className="workflow-rail" role="group" aria-label="How work moves through Karya">
        {workflowSteps.map((step, index) => (
          <div className="workflow-stage" data-human={step.id === 'approval'} key={step.id}>
            {step.id === 'approval' ? (
              <span className="approval-boundary">
                <span>Human approval boundary</span>
                Nothing crosses implicitly
              </span>
            ) : null}
            <button
              type="button"
              className="workflow-node"
              data-selected={step.id === selectedId}
              data-human={step.id === 'approval'}
              onClick={() => setSelectedId(step.id)}
              aria-pressed={step.id === selectedId}
            >
              <span>{String(index + 1).padStart(2, '0')}</span>
              <strong>{step.label}</strong>
              {step.id === 'approval' ? <UserRound aria-label="Human boundary" size={18} /> : null}
            </button>
            {index < workflowSteps.length - 1 ? <Arrow /> : null}
          </div>
        ))}
      </div>
      <aside className="detail-panel" aria-live="polite">
        <span className="eyebrow">Selected stage</span>
        <h3>{selected.label}</h3>
        <p className="detail-lead">{selected.summary}</p>
        <dl>
          <div>
            <dt>Input</dt>
            <dd>{selected.input}</dd>
          </div>
          <div>
            <dt>Output</dt>
            <dd>{selected.output}</dd>
          </div>
          <div>
            <dt>Owner</dt>
            <dd>{selected.owner}</dd>
          </div>
          <div>
            <dt>Constraint</dt>
            <dd>{selected.constraints}</dd>
          </div>
        </dl>
        <div className="detail-links">
          {selected.documentation.map((link) => (
            <a key={link.href} href={link.href} target="_blank" rel="noreferrer">
              {link.label}
              <ExternalLink size={14} />
            </a>
          ))}
        </div>
      </aside>
    </div>
  )
}

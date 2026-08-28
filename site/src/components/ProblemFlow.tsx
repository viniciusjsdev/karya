import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { beforeFlow, structuredFlow } from '../content/karya'
import { Arrow } from './Section'

export function ProblemFlow() {
  const [mode, setMode] = useState<'without' | 'with'>('without')
  const items = mode === 'without' ? beforeFlow : structuredFlow
  return (
    <div className="problem-panel">
      <div className="segmented-control" aria-label="Compare AI development flows">
        <button type="button" aria-pressed={mode === 'without'} onClick={() => setMode('without')}>
          Without structure
        </button>
        <button type="button" aria-pressed={mode === 'with'} onClick={() => setMode('with')}>
          With Karya
        </button>
      </div>
      <div className={`problem-flow ${mode}`} aria-live="polite">
        <AnimatePresence mode="wait">
          <motion.div
            key={mode}
            className="flow-stack"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.25 }}
          >
            {items.map(([label, text], index) => (
              <div className="contents" key={label}>
                <article className="flow-card">
                  <span className="node-index">{String(index + 1).padStart(2, '0')}</span>
                  <div>
                    <h3>{label}</h3>
                    <p>{text}</p>
                  </div>
                </article>
                {index < items.length - 1 ? <Arrow /> : null}
              </div>
            ))}
          </motion.div>
        </AnimatePresence>
      </div>
      <p className="diagram-summary">
        Karya moves critical context out of transient conversation and into durable artifacts. The
        interaction changes emphasis; the full sequence remains available as text.
      </p>
    </div>
  )
}

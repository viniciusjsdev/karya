import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { ChevronDown } from 'lucide-react'
import { benefits } from '../content/karya'

export function BenefitDisclosure() {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null)

  return (
    <div className="benefit-grid">
      {benefits.map((benefit, index) => {
        const expanded = expandedIndex === index
        const panelId = `benefit-panel-${index}`

        return (
          <article className="benefit-card" data-expanded={expanded} key={benefit.title}>
            <button
              type="button"
              className="benefit-trigger"
              aria-expanded={expanded}
              aria-controls={panelId}
              onClick={() => setExpandedIndex(expanded ? null : index)}
            >
              <span className="node-index">{String(index + 1).padStart(2, '0')}</span>
              <span className="benefit-summary">
                <strong>{benefit.title}</strong>
                <span>{benefit.summary}</span>
              </span>
              <span className="benefit-action">
                {expanded ? 'Close mechanism' : 'Explore mechanism'}
                <ChevronDown size={17} aria-hidden="true" />
              </span>
            </button>
            <AnimatePresence initial={false}>
              {expanded ? (
                <motion.div
                  id={panelId}
                  className="benefit-detail"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  exit={{ opacity: 0, height: 0 }}
                  transition={{ duration: 0.24, ease: 'easeOut' }}
                >
                  <dl>
                    <div>
                      <dt>Problem</dt>
                      <dd>{benefit.problem}</dd>
                    </div>
                    <div>
                      <dt>How Karya handles it</dt>
                      <dd>{benefit.mechanism}</dd>
                    </div>
                    <div>
                      <dt>Expected result</dt>
                      <dd>{benefit.result}</dd>
                    </div>
                  </dl>
                </motion.div>
              ) : null}
            </AnimatePresence>
          </article>
        )
      })}
    </div>
  )
}

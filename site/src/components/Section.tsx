import type { ReactNode } from 'react'
import { motion } from 'framer-motion'

type SectionProps = {
  id?: string
  eyebrow: string
  title: string
  intro?: string
  children: ReactNode
  className?: string
}

export function Section({ id, eyebrow, title, intro, children, className = '' }: SectionProps) {
  return (
    <section id={id} className={`section-shell scroll-mt-24 ${className}`}>
      <motion.div
        className="section-heading"
        initial={{ opacity: 0, y: 14 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, margin: '-80px' }}
        transition={{ duration: 0.45 }}
      >
        <span className="eyebrow">{eyebrow}</span>
        <h2>{title}</h2>
        {intro ? <p>{intro}</p> : null}
      </motion.div>
      {children}
    </section>
  )
}

export function Arrow() {
  return (
    <span className="flow-arrow" aria-hidden="true">
      ↓
    </span>
  )
}

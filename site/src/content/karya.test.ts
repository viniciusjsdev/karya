import { describe, expect, it } from 'vitest'
import { factories, routingExamples, workflowSteps } from './karya'

describe('Karya content contract', () => {
  it('preserves four independent Factories', () => {
    expect(factories.map((factory) => factory.name)).toEqual([
      'MVP Factory',
      'Research Factory',
      'Marketing Factory',
      'Project Harness Factory',
    ])
  })

  it('keeps approval before specialist execution', () => {
    expect(workflowSteps.findIndex((step) => step.id === 'approval')).toBeLessThan(
      workflowSteps.findIndex((step) => step.id === 'capability'),
    )
  })

  it('includes direct execution in illustrative routing', () => {
    expect(routingExamples.some((example) => example.route === 'Direct execution')).toBe(true)
  })
})

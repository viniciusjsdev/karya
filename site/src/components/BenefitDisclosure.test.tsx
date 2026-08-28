import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { BenefitDisclosure } from './BenefitDisclosure'

describe('BenefitDisclosure', () => {
  it('reveals and closes mechanism details from an accessible button', () => {
    render(<BenefitDisclosure />)

    const trigger = screen.getByRole('button', { name: /Durable knowledge/i })
    expect(trigger).toHaveAttribute('aria-expanded', 'false')
    expect(screen.queryByText('How Karya handles it')).not.toBeInTheDocument()

    fireEvent.click(trigger)
    expect(trigger).toHaveAttribute('aria-expanded', 'true')
    expect(screen.getByText('How Karya handles it')).toBeInTheDocument()

    fireEvent.click(trigger)
    expect(trigger).toHaveAttribute('aria-expanded', 'false')
  })
})

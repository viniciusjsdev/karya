import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { ProjectNavigation } from './ProjectNavigation'

describe('project navigation demonstration', () => {
  it('explains the cycle and loads the isolated viewer only on request', () => {
    render(<ProjectNavigation />)
    expect(screen.getByRole('list', { name: 'Living map maintenance cycle' })).toBeInTheDocument()
    expect(screen.queryByTitle('Karya project navigation map')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Explore the interactive map' }))
    const frame = screen.getByTitle('Karya project navigation map')
    expect(frame).toHaveAttribute('src', '/karya/project-map.html')
    expect(frame).toHaveAttribute('sandbox', 'allow-scripts')
    expect(screen.getByRole('button', { name: 'Close interactive map' })).toHaveAttribute(
      'aria-expanded',
      'true',
    )
    expect(screen.getByRole('link', { name: /Open map in a new tab/ })).toHaveAttribute(
      'href',
      '/karya/project-map.html',
    )
    fireEvent.click(screen.getByRole('button', { name: 'Close interactive map' }))
    expect(screen.queryByTitle('Karya project navigation map')).not.toBeInTheDocument()
  })
})

import { readFileSync } from 'node:fs'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'
import { describe, expect, it } from 'vitest'
// @ts-expect-error plain ESM build utility outside the browser bundle
import { renderProjectMapSnapshot } from './build-project-map.mjs'

describe('public map snapshot', () => {
  it('uses the distributed template, escapes embedded data and never claims a live check', () => {
    const template = readFileSync(
      resolve(
        dirname(fileURLToPath(import.meta.url)),
        '../../skills/project-harness-architect/assets/project-map.html',
      ),
      'utf8',
    )
    const label = '</script><script>alert(1)</script> $&'
    const map = {
      schema_version: '1.0',
      project: { name: label },
      nodes: [{ id: 'n', label, path: 'docs/architecture.md', fingerprint: 'private-hash' }],
      relations: [],
      maintenance: { review_note: 'local-only note' },
    }
    const html = renderProjectMapSnapshot({
      map,
      template,
      logo: Buffer.from('logo'),
      generatedAt: '2026-09-06T00:00:00Z',
    })
    const embedded = html.match(
      /<script id="map-data" type="application\/json">(.*?)<\/script>/s,
    )?.[1]
    const payload = JSON.parse(embedded!)
    expect(payload.map.project.name).toBe(label)
    expect(payload.check.status).toBe('snapshot')
    expect(payload.map.nodes[0]).not.toHaveProperty('fingerprint')
    expect(payload.map).not.toHaveProperty('maintenance')
    expect(html).not.toContain(label)
    expect(html).not.toContain('__MAP_DATA__')
    expect(html).toContain('id="view-atomic"')
    expect(html).toContain('id="view-sphere"')
    expect(html).toContain('manualPositions')
  })
})

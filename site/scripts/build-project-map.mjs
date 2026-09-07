/** Build a public snapshot using the viewer template shipped by Project Harness. */
import { createHash } from 'node:crypto'
import { mkdir, readFile, writeFile } from 'node:fs/promises'
import { dirname, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

export function renderProjectMapSnapshot({ map, template, logo, generatedAt }) {
  const publicMap = {
    schema_version: map.schema_version,
    project: map.project,
    nodes: map.nodes.map(({ fingerprint: _fingerprint, ...node }) => node),
    relations: map.relations,
    ...(map.navigation ? { navigation: map.navigation } : {}),
  }
  const payload = {
    map: publicMap,
    check: { status: 'snapshot', pending: [] },
    generated_at: generatedAt,
    digest: createHash('sha256').update(JSON.stringify(publicMap)).digest('hex'),
  }
  const encoded = JSON.stringify(payload).replace(
    /[<>&\u2028\u2029]/g,
    (character) => `\\u${character.charCodeAt(0).toString(16).padStart(4, '0')}`,
  )
  if (!template.includes('__MAP_DATA__') || !template.includes('__KARYA_LOGO__')) {
    throw new Error('Project map template placeholders are missing')
  }
  return template
    .replace('__KARYA_LOGO__', () => logo.toString('base64'))
    .replace('__MAP_DATA__', () => encoded)
}

export async function buildProjectMap() {
  const siteRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
  const root = resolve(siteRoot, '..')
  const assets = resolve(root, 'skills/project-harness-architect/assets')
  const [source, template, logo] = await Promise.all([
    readFile(resolve(root, '.codex/references/project-map.json'), 'utf8'),
    readFile(resolve(assets, 'project-map.html'), 'utf8'),
    readFile(resolve(assets, 'karya-icon.png')),
  ])
  const output = resolve(siteRoot, 'public/project-map.html')
  const html = renderProjectMapSnapshot({
    map: JSON.parse(source),
    template,
    logo,
    generatedAt: new Date().toISOString(),
  })
  await mkdir(dirname(output), { recursive: true })
  await writeFile(output, html)
  return output
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  console.log(`Generated website navigation snapshot: ${await buildProjectMap()}`)
}

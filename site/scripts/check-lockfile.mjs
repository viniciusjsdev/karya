import { readFile } from 'node:fs/promises'

const manifest = JSON.parse(await readFile(new URL('../package.json', import.meta.url), 'utf8'))
const lock = JSON.parse(await readFile(new URL('../package-lock.json', import.meta.url), 'utf8'))
const direct = { ...manifest.dependencies, ...manifest.devDependencies }

for (const [name, version] of Object.entries(direct)) {
  if (!/^\d+\.\d+\.\d+/.test(version)) throw new Error(`${name} is not pinned exactly`)
}
for (const [path, entry] of Object.entries(lock.packages ?? {})) {
  if (!path || !entry.resolved) continue
  if (!entry.resolved.startsWith('https://registry.npmjs.org/')) {
    throw new Error(`Unapproved registry source: ${entry.resolved}`)
  }
  if (!entry.integrity?.startsWith('sha512-')) throw new Error(`Missing sha512 integrity: ${path}`)
}
console.log('Lockfile sources, integrity hashes, and direct dependency pins are valid.')

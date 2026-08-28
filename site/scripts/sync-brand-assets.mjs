import { copyFile, mkdir, rm } from 'node:fs/promises'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const siteRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const source = resolve(siteRoot, '..', 'assets', 'brand')
const destination = resolve(siteRoot, 'public', 'brand')
const requiredAssets = [
  'icon/karya-caryatid-capital-master.png',
  'icon/karya-icon-dark.png',
  'icon/karya-icon-light.png',
  'icon/karya-icon-dark-64.png',
  'icon/karya-icon-light-64.png',
  'logo/karya-mark-terracotta-transparent.png',
  'social/karya-social-preview-1280x640.png',
]

await rm(destination, { recursive: true, force: true })
for (const asset of requiredAssets) {
  const target = join(destination, asset)
  await mkdir(dirname(target), { recursive: true })
  await copyFile(join(source, asset), target)
}
console.log(`Synced official brand assets to ${destination}`)

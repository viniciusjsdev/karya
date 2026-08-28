import { readFile } from 'node:fs/promises'

const lock = JSON.parse(await readFile(new URL('../package-lock.json', import.meta.url), 'utf8'))
const packagesWithScripts = Object.entries(lock.packages ?? {})
  .filter(([, entry]) => entry.hasInstallScript)
  .map(([path]) => path.replace(/^node_modules\//, ''))

if (packagesWithScripts.length) {
  console.log(
    `Install scripts remain blocked by ignore-scripts=true: ${packagesWithScripts.join(', ')}`,
  )
} else {
  console.log('No dependency install scripts are declared in the lockfile.')
}

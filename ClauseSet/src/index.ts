import { createInterface } from 'node:readline'
import fs from 'fs/promises'

import { parse } from './parser'
import { showFormula } from './show'
import { reduceToClauseSet } from './reduce'

function onLine(line: string) {
  const parseResult = parse(line)
  if (parseResult.isErr) {
    console.error('ParseError:', parseResult.err)
    return
  }

  const formula = parseResult.val.val

  reduceToClauseSet(formula, { debugPipeline: true })
  console.log()
}

async function loadHistory() {
  try {
    const history = await fs.readFile('.history', 'utf-8')
    return history.split('\n')
  }
  catch {
    return []
  }
}

async function saveHistory(history: string[]) {
  try {
    await fs.writeFile('.history', history.join('\n'), 'utf-8')
  }
  catch {}
}

function prompt() {
  if (! process.stdin.isTTY) return
  rln.prompt()
}

function welcome() {
  if (! process.stdin.isTTY) return
  console.log('ClauseSet REPL')
  console.log('Enter a first-order logic formula to see it reduced to clause set form.')
  console.log()
  prompt()
}

const rln = createInterface({
  input: process.stdin,
  output: process.stdout,
  prompt: '> ',
  history: await loadHistory(),
})

welcome()

rln.on('line', line => {
  onLine(line)
  prompt()
})

rln.on('history', saveHistory)
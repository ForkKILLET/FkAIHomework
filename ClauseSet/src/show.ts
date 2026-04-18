import { Formula, Node } from './node'

import { match } from 'ts-pattern'
import pc from 'picocolors'

export const needParen = (node: Node, parent: Node): boolean => match(parent)
  .with({ ty: 'forall' }, { ty: 'exists' }, { ty: 'neg' }, () => match(node)
    .with({ ty: 'pred' }, { ty: 'forall' }, { ty: 'exists' }, { ty: 'neg' }, () => false)
    .otherwise(() => true)
  )
  .with({ ty: 'conj' }, () => match(node)
    .with({ ty: 'conj' }, { ty: 'pred' }, { ty: 'neg' }, () => false)
    .otherwise(() => true)
  )
  .with({ ty: 'disj' }, () => match(node)
    .with({ ty: 'disj' }, { ty: 'pred' }, { ty: 'neg' }, () => false)
    .otherwise(() => true)
  )
  .with({ ty: 'impl' }, () => match(node)
    .with({ ty: 'disj' }, { ty: 'pred' }, { ty: 'neg' }, () => false)
    .otherwise(() => true)
  )
  .with({ ty: 'equiv' }, () => match(node)
    .with({ ty: 'impl' }, { ty: 'disj' }, { ty: 'conj' }, { ty: 'pred' }, { ty: 'neg' }, () => false)
    .otherwise(() => true)
  )
  .with({ ty: 'pred' }, { ty: 'func' }, { ty: 'atom' }, () => false)
  .exhaustive()

const _showNode = (node: Node, parent: Node | null): string => {
  const str = match(node)
    .with({ ty: 'atom' }, ({ id }) => pc.whiteBright(id))
    .with({ ty: 'func' }, { ty: 'pred' }, ({ ty, id, args }) =>
      `${ty === 'func' ? pc.italic(pc.whiteBright(id)) : pc.magenta(id)}(${args.map(arg => _showNode(arg, node)).join(', ')})`
    )
    .with({ ty: 'neg' }, ({ arg }) => `${pc.green('¬')}${_showNode(arg, node)}`)
    .with({ ty: 'conj' }, ({ lhs, rhs }) => `${_showNode(lhs, node)} ${pc.green('∧')} ${_showNode(rhs, node)}`)
    .with({ ty: 'disj' }, ({ lhs, rhs }) => `${_showNode(lhs, node)} ${pc.green('∨')} ${_showNode(rhs, node)}`)
    .with({ ty: 'impl' }, ({ lhs, rhs }) => `${_showNode(lhs, node)} ${pc.green('→')} ${_showNode(rhs, node)}`)
    .with({ ty: 'equiv' }, ({ lhs, rhs }) => `${_showNode(lhs, node)} ${pc.green('↔')} ${_showNode(rhs, node)}`)
    .with({ ty: 'forall' }, ({ bvar, body }) => `${pc.cyan('∀')}${pc.whiteBright(bvar)} ${_showNode(body, node)}`)
    .with({ ty: 'exists' }, ({ bvar, body }) => `${pc.cyan('∃')}${pc.whiteBright(bvar)} ${_showNode(body, node)}`)
    .exhaustive()
  return parent && needParen(node, parent) ? `(${str})` : str
}

export const showFormula = (formula: Formula): string => _showNode(formula, null)

export const showClauseSet = (clauseSet: Formula[]): string => `{ ${clauseSet.map(clause => `${showFormula(clause)}`).join(', ')} }`

export const showConsoleStep = (name: string) => name.padEnd(22, ' ')
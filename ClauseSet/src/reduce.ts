import { match } from 'ts-pattern'

import { Atom, Formula, Func, Pred, QuantHead, Term } from './node'
import { showClauseSet, showConsoleStep, showFormula } from './show'
import { id, Endo } from './utils'

export type ClauseSet = Formula[]

export const unreachableFormula = (formula: Formula): never => {
  throw new Error(`Unreachable formula: ${showFormula(formula)}`)
}

export const shallowMapFormula = (transform: Endo<Formula>) => (formula: Formula) => match<Formula, Formula>(formula)
  .with({ ty: 'forall' }, ({ bvar, body }) => ({ ty: 'forall', bvar, body: transform(body) }))
  .with({ ty: 'exists' }, ({ bvar, body }) => ({ ty: 'exists', bvar, body: transform(body) }))
  .with({ ty: 'conj' }, ({ lhs, rhs }) => ({ ty: 'conj', lhs: transform(lhs), rhs: transform(rhs) }))
  .with({ ty: 'disj' }, ({ lhs, rhs }) => ({ ty: 'disj', lhs: transform(lhs), rhs: transform(rhs) }))
  .with({ ty: 'impl' }, ({ lhs, rhs }) => ({ ty: 'impl', lhs: transform(lhs), rhs: transform(rhs) }))
  .with({ ty: 'equiv' }, ({ lhs, rhs }) => ({ ty: 'equiv', lhs: transform(lhs), rhs: transform(rhs) }))
  .with({ ty: 'neg' }, ({ arg }) => ({ ty: 'neg', arg: transform(arg) }))
  .with({ ty: 'pred' }, id)
  .exhaustive()

export const rewriteUpFormula = (transform: Endo<Formula>) => {
  const _rewrite = (formula: Formula) => transform(shallowMapFormula(_rewrite)(formula))
  return _rewrite
}

export const rewriteDownFormula = (transform: Endo<Formula>) => {
  const _rewrite = (formula: Formula) => shallowMapFormula(_rewrite)(transform(formula))
  return _rewrite
}

export const mapTermAtom = (transform: (atom: Atom) => Term) => (term: Term): Term => match<Term, Term>(term)
  .with({ ty: 'atom' }, transform)
  .with({ ty: 'func' }, ({ id, args }) => ({ ty: 'func', id, args: args.map(mapTermAtom(transform)) }))
  .exhaustive()

export const mapPredAtom = (transform: (atom: Atom) => Term) => (pred: Pred): Pred => ({
  ty: 'pred',
  id: pred.id,
  args: pred.args.map(mapTermAtom(transform)),
})

export const mapFormulaAtom = (transform: (atom: Atom) => Term) => rewriteUpFormula(formula => match<Formula, Formula>(formula)
  .with({ ty: 'pred' }, mapPredAtom(transform))
  .otherwise(id)
)

export const mapAtomId = (transform: Endo<string>) => (atom: Atom): Atom => ({
  ty: 'atom',
  id: transform(atom.id)
})

export const mapFormulaAtomAndBvarId = (transform: Endo<string>) => rewriteUpFormula(formula => match<Formula, Formula>(formula)
  .with({ ty: 'forall' }, { ty: 'exists' }, ({ ty, bvar, body }) => ({ ty, bvar: transform(bvar), body }))
  .with({ ty: 'pred' }, mapPredAtom(mapAtomId(transform)))
  .otherwise(id)
)

export const createIdGenerator = () => {
  let id = 0

  return {
    next: () => {
      return String(id ++)
    },
    getPrettifier: () => {
      if (id > 4) return (id: string) => `v${Number(id) + 1}`
      return (id: string) => 'xyzw'[Number(id)]
    },
  }
}

export interface ReduceToClauseSetOptions {
  debugPipeline?: boolean
}

export const reduceToClauseSet = (
  formula: Formula,
  { debugPipeline = false }: ReduceToClauseSetOptions = {}
) => {
  // Step 1: Eliminate implications and equivalences

  const elimImplEquiv = rewriteUpFormula(formula => match<Formula, Formula>(formula)
    .with({ ty: 'impl' }, ({ lhs, rhs }) => ({
      ty: 'disj',
      lhs: { ty: 'neg', arg: elimImplEquiv(lhs) },
      rhs: elimImplEquiv(rhs),
    }))
    .with({ ty: 'equiv' }, ({ lhs, rhs }) => {
      const lhs_ = elimImplEquiv(lhs)
      const rhs_ = elimImplEquiv(rhs)
      return elimImplEquiv({
        ty: 'conj',
        lhs: {
          ty: 'impl',
          lhs: lhs_,
          rhs: rhs_,
        },
        rhs: {
          ty: 'impl',
          lhs: rhs_,
          rhs: lhs_,
        },
      })
    })
    .otherwise(id)
  )

  // Step 2: Move negations inward (Negation Normal Form)

  const toNNF = rewriteUpFormula(formula => match<Formula, Formula>(formula)
    .with({ ty: 'neg' }, ({ arg }, neg) => match<Formula, Formula>(arg)
      .with({ ty: 'neg' }, ({ arg }) => toNNF(arg))
      .with({ ty: 'conj' }, ({ lhs, rhs }) => ({
        ty: 'disj',
        lhs: toNNF({ ty: 'neg', arg: lhs }),
        rhs: toNNF({ ty: 'neg', arg: rhs }),
      }))
      .with({ ty: 'disj' }, ({ lhs, rhs }) => ({
        ty: 'conj',
        lhs: toNNF({ ty: 'neg', arg: lhs }),
        rhs: toNNF({ ty: 'neg', arg: rhs }),
      }))
      .with({ ty: 'forall' }, ({ bvar, body }) => ({
        ty: 'exists',
        bvar,
        body: toNNF({ ty: 'neg', arg: body }),
      }))
      .with({ ty: 'exists' }, ({ bvar, body }) => ({
        ty: 'forall',
        bvar,
        body: toNNF({ ty: 'neg', arg: body }),
      }))
      .with({ ty: 'pred' }, () => neg)
      .otherwise(unreachableFormula)
    )
    .otherwise(id)
  )

  // Step 3: Standardize bound variables

  const standardizeBvars = (formula: Formula): Formula => {
    const idGen = createIdGenerator()

    const getVar = (id: string, bvarMap: Map<string, string>): string => {
      if (bvarMap.has(id)) return bvarMap.get(id)!

      const idNew = idGen.next()
      return idNew
    }

    const _standardizeBvars = (bvarMap: Map<string, string>) => (formula: Formula): Formula => match<Formula, Formula>(formula)
      .with({ ty: 'forall' }, { ty: 'exists' }, ({ ty, bvar, body }) => {
        const bvarMapNew = new Map(bvarMap)
        const bvarNew = getVar(bvar, bvarMapNew)
        bvarMapNew.set(bvar, bvarNew)
        return {
          ty,
          bvar: bvarNew,
          body: _standardizeBvars(bvarMapNew)(body),
        }
      })
      .with({ ty: 'pred' }, mapPredAtom(mapAtomId(id => getVar(id, bvarMap))))
      .otherwise(shallowMapFormula(_standardizeBvars(bvarMap)))

    formula = _standardizeBvars(new Map())(formula)

    const prettifyId = idGen.getPrettifier()

    formula = mapFormulaAtomAndBvarId(prettifyId)(formula)

    return formula
  }

  // Step 4: Eliminate existential quantifiers (Skolem Normal Form)

  const skolemize = (formula: Formula): Formula => {
    const _skolemize = (bvars: string[]) => (formula: Formula): Formula => match<Formula, Formula>(formula)
      .with({ ty: 'forall' }, ({ bvar, body }) => ({
        ty: 'forall',
        bvar,
        body: _skolemize([...bvars, bvar])(body),
      }))
      .with({ ty: 'exists' }, ({ bvar, body }) => {
        const skolemFuncArgs: Atom[] = bvars.map(bvar => ({ ty: 'atom', id: bvar }))
        const skolemFunc: Func = {
          ty: 'func',
          id: `ƒ${bvar}`,
          args: skolemFuncArgs,
        }
        const bodySkolemized = mapFormulaAtom(atom => atom.id === bvar ? skolemFunc : atom)(body)
        return _skolemize(bvars)(bodySkolemized)
      })
      .otherwise(shallowMapFormula(_skolemize(bvars)))

    return _skolemize([])(formula)
  }

  // Step 5: Drop universal quantifiers

  const dropForall = rewriteUpFormula(formula => match<Formula, Formula>(formula)
    .with({ ty: 'forall' }, ({ body }) => body)
    .otherwise(id)
  )

  // Step 6: Distribute disjunctions over conjunctions (Conjunctive Normal Form)

  const toCNF = rewriteDownFormula(formula => match<Formula, Formula>(formula)
    .with({ ty: 'disj', lhs: { ty: 'conj' } }, ({ lhs, rhs }) => ({
      ty: 'conj',
      lhs: toCNF({ ty: 'disj', lhs: lhs.lhs, rhs }),
      rhs: toCNF({ ty: 'disj', lhs: lhs.rhs, rhs }),
    }))
    .with({ ty: 'disj', rhs: { ty: 'conj' } }, ({ lhs, rhs }) => ({
      ty: 'conj',
      lhs: toCNF({ ty: 'disj', lhs, rhs: rhs.lhs }),
      rhs: toCNF({ ty: 'disj', lhs, rhs: rhs.rhs }),
    }))
    .otherwise(id)
  )

  if (debugPipeline) {
    console.log(`${showConsoleStep('Input')}: ${showFormula(formula)}`)
  }

  const pipeline = [
    { name: 'Eliminate → and ↔', transform: elimImplEquiv },
    { name: 'To Negation NF', transform: toNNF },
    { name: 'Std bound vars', transform: standardizeBvars },
    { name: 'Skolemize', transform: skolemize },
    { name: 'Drop ∀', transform: dropForall },
    { name: 'To Conjunctive NF', transform: toCNF },
  ]
  
  formula = pipeline.reduce((formula, { name, transform }) => {
    formula = transform(formula)
    if (debugPipeline) {
      console.log(`${showConsoleStep(name)}: ${showFormula(formula)}`)
    }
    return formula
  }, formula)

  // Step 7: Convert conjunctions of disjunctions to sets of clauses

  const flattenConj = (formula: Formula): Formula[] => match<Formula, Formula[]>(formula)
    .with({ ty: 'conj' }, ({ lhs, rhs }) => [...flattenConj(lhs), ...flattenConj(rhs)])
    .otherwise(formula => [formula])

  let clauseSet = flattenConj(formula)

  if (debugPipeline) {
    console.log(`${showConsoleStep('Create clause set')}: ${showClauseSet(clauseSet)}`)
  }

  // Step 8: Standardize apart variables in clauses

  const standardizeClauseVars = (clauseSet: ClauseSet): ClauseSet => {
    const idGen = createIdGenerator()

    const _standardizeVars = (varMap: Map<string, string>) => (formula: Formula): Formula => match<Formula, Formula>(formula)
      .with({ ty: 'pred' }, mapPredAtom(mapAtomId(id => {
        if (varMap.has(id)) return varMap.get(id)!

        const idNew = idGen.next()
        varMap.set(id, idNew)
        return idNew
      })))
      .otherwise(shallowMapFormula(_standardizeVars(varMap)))

    clauseSet = clauseSet.map(clause => _standardizeVars(new Map())(clause))

    const prettifyId = idGen.getPrettifier()

    return clauseSet.map(mapFormulaAtomAndBvarId(prettifyId))
  }

  clauseSet = standardizeClauseVars(clauseSet)

  if (debugPipeline) {
    console.log(`${showConsoleStep('Std clause vars')}: ${showClauseSet(clauseSet)}`)
  }

  return clauseSet
}
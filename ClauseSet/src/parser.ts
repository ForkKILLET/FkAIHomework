
import { p, Parser, runParser } from 'parsecond'
import { NodeOf, Formula, Atom, Func, Term, Pred, Neg, Conj, Disj, Impl, Equiv, Forall, Exists } from './node'

// Utility parser combinators

export const pCall = <K extends 'func' | 'pred'>(
  ty: K, pId: Parser<string>
): Parser<NodeOf<K>> =>
  p.lazy(() => p.map(
    p.seq([pId, p.spaced(p.parens(p.spaced(pTermList)))]),
    ([id, args]) => ({ ty, id, args }) as NodeOf<K>
  ))

export const pPrimary = <T extends Formula>(pBase: Parser<T>): Parser<Formula> =>
  p.lazy(() => p.alt([pBase, pForall, pExists, pParen]))

export const pInfix = <K extends 'conj' | 'disj' | 'impl' | 'equiv'>(
  ty: K, pArg: Parser<Formula>, pSym: Parser<string>
): Parser<NodeOf<K>> => {
  const pArgPrimary = pPrimary(pArg)
  return p.lazy(() => p.map(
    p.seq([pArgPrimary, p.spaced(pSym), pArgPrimary]),
    ([lhs, , rhs]) => ({ ty, lhs, rhs }) as NodeOf<K>
  ))
}

export const pQuant = <K extends 'forall' | 'exists'>(
  ty: K, pSym: Parser<string>
): Parser<NodeOf<K>> => p.lazy(() => p.map(
  p.seq([pSym, p.spaced(pAtom), pQuantBody]),
  ([, { id }, body]) => ({ ty, bvar: id, body }) as NodeOf<K>
))

export const pQualified = (pBase: Parser<Formula>) => p.alt([pBase, pForall, pExists])

export const pKeyword = (kw: string): Parser<string> => p.followedBy(p.str(kw), p.regex(/[^A-Za-z0-9]/))

// Parsers

export const pAtom: Parser<Atom> = p.map(
  p.regex(/[A-Za-z][A-Za-z0-9]*/),
  id => ({ ty: 'atom', id })
)

export const pFunc: Parser<Func> = pCall('func', p.regex(/[a-z][A-Za-z0-9]*/))

export const pTerm: Parser<Term> = p.alt([pFunc, pAtom])
export const pTermList: Parser<Term[]> = p.sep1(pTerm, p.spaced(p.char(',')))

export const pPred: Parser<Pred> = pCall('pred', p.regex(/[A-Z][A-Za-z0-9]*/))

export const pNeg: Parser<Neg> = p.lazy(() => p.map(
  p.seq([p.spaced(p.oneOf('¬!')), pPrimary(pPred)]),
  ([, arg]) => ({ ty: 'neg', arg })
))
export const pNeg1 = p.alt([pNeg, pPred])

export const pConj: Parser<Conj> = pInfix('conj', pNeg1, p.oneOf('∧&'))
export const pConj1 = p.alt([pConj, pNeg1])

export const pDisj: Parser<Disj> = pInfix('disj', pConj1, p.oneOf('∨|'))
export const pDisj1 = p.alt([pDisj, pConj1])

export const pImpl: Parser<Impl> = pInfix('impl', pDisj1, p.alt([p.str('→'), p.str('->')]))
export const pImpl1 = p.alt([pImpl, pDisj1])

export const pEquiv: Parser<Equiv> = pInfix('equiv', pImpl1, p.alt([p.str('↔'), p.str('<->')]))
export const pEquiv1 = p.alt([pEquiv, pImpl1])

export const pFormulaQF: Parser<Formula> = pEquiv1

export const pForall: Parser<Forall> = pQuant('forall', p.alt([p.str('∀'), pKeyword('forall')]))
export const pExists: Parser<Exists> = pQuant('exists', p.alt([p.str('∃'), pKeyword('exists')]))

export const pQuantBody: Parser<Formula> = p.lazy(() => pPrimary(pNeg1))

export const pFormula: Parser<Formula> = pPrimary(pFormulaQF)

export const pParen: Parser<Formula> = p.parens(p.spaced(pFormula))

// Interface

export const pInput = p.ended(p.spaced(pFormula))
export const parse = runParser(pInput)
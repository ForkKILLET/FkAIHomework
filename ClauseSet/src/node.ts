export interface Atom {
  ty: 'atom'
  id: string
}

export interface Func {
  ty: 'func'
  id: string
  args: Term[]
}

export type Term = Atom | Func

export interface Pred {
  ty: 'pred'
  id: string
  args: Term[]
}

export interface Neg {
  ty: 'neg'
  arg: Formula
}

export interface Conj {
  ty: 'conj'
  lhs: Formula
  rhs: Formula
}

export interface Disj {
  ty: 'disj'
  lhs: Formula
  rhs: Formula
}

export interface Impl {
  ty: 'impl'
  lhs: Formula
  rhs: Formula
}

export interface Equiv {
  ty: 'equiv'
  lhs: Formula
  rhs: Formula
}

export type FormulaQF =
  | Pred | Neg | Conj | Disj | Impl | Equiv

export interface ForallHead {
  ty: 'forall'
  bvar: string
}

export interface Forall extends ForallHead {
  body: Formula
}

export interface ExistsHead {
  ty: 'exists'
  bvar: string
}

export interface Exists extends ExistsHead {
  body: Formula
}

export type QuantHead = ForallHead | ExistsHead

export type Formula = FormulaQF | Forall | Exists

export type Node = Term | Formula
export type NodeTy = Node['ty']
export type NodeOf<K extends NodeTy = NodeTy> = Extract<Node, { ty: K }>


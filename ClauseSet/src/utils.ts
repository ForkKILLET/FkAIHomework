export const id = <T>(x: T): T => x

export type Endo<T> = (x: T) => T
import Mathlib
import RequestProject.SetPairs.Basic

/-!
# Order enumerations of a finite ground type

An *order enumeration* of a finite type `α` is a bijection `α ≃ Fin (card α)`,
i.e. a ranking assigning to each element its position in a total order.  The number
of order enumerations is `(card α)!`.
-/

open scoped BigOperators

namespace SetPairs

variable {α : Type*} [Fintype α] [DecidableEq α]

/-- An order enumeration of `α`: a bijective ranking `α ≃ Fin (card α)`. -/
abbrev OrderEnumeration (α : Type*) [Fintype α] := α ≃ Fin (Fintype.card α)

/-- The number of order enumerations of `α` is `(card α)!`. -/
theorem card_orderEnumerations :
    Fintype.card (OrderEnumeration α) = Nat.factorial (Fintype.card α) := by
  simpa using Fintype.card_equiv (Equiv.refl (Fin (Fintype.card α)))

end SetPairs

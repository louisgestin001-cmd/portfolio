/-
Axiom audit for the five principal theorems.

Run these `#print axioms` commands (e.g. by appending them to `RequestProject/Main.lean`
or loading this file in an editor with the project imports). Each principal theorem
should depend only on `propext`, `Classical.choice`, `Quot.sound`.
-/
import RequestProject.Main

#print axioms SetPairs.weighted_bollobas
#print axioms SetPairs.uniform_bollobas
#print axioms TwoFamilies.lovasz_frankl_subspaces
#print axioms GeneralPosition.momentCurve_linearIndependent
#print axioms SetPairs.frankl_kalai_skew

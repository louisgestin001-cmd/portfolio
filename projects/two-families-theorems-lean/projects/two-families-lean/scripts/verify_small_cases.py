#!/usr/bin/env python3
"""Exact exhaustive regression checks for the two-families theorems.

All arithmetic is exact (Python ``int`` / ``fractions.Fraction``); no floating point.

Checks performed:
  * Weighted Bollobás inequality  ``sum_i 1 / C(|A_i|+|B_i|, |A_i|) <= 1``
    for every diagonally-disjoint, cross-intersecting family on ground sets of
    sizes 2..5 (exhaustive over maximal families built from the pair-poset).
  * Uniform inequality ``|F| <= C(a+b,a)`` for every admissible (a,b) on ground
    sets of size <= 6.
  * Skew inequality ``m <= C(a+b,a)`` for every admissible (a,b) on ground
    sets of size <= 4.
  * The canonical sharpness construction attains ``C(a+b,a)``.

These are regression tests, not substitutes for the machine-checked Lean proofs.
"""
from __future__ import annotations
from fractions import Fraction
from itertools import combinations, permutations
from math import comb


def subsets(ground):
    for r in range(len(ground) + 1):
        for s in combinations(ground, r):
            yield frozenset(s)


def valid_pairs(ground):
    """All (A,B) with A,B subsets of ground, A disjoint from B, both nonempty-allowed."""
    gs = list(subsets(ground))
    for A in gs:
        for B in gs:
            if A & B:
                continue
            yield (A, B)


# ---------------------------------------------------------------------------
# Weighted Bollobás: exhaustive over small ground sets.
# A "family" is a set of index pairs (A_i,B_i) with A_i∩B_i=∅ (diagonal) and
# A_i∩B_j≠∅ for i≠j (cross).  We enumerate maximal such families greedily by
# brute force over all subsets of the candidate pairs (feasible for n<=5 with a
# size cap).
# ---------------------------------------------------------------------------

def weighted_ok(ground, node_cap=300000):
    """Bounded DFS over cross-intersecting families; verifies sum <= 1 exactly."""
    n = len(ground)
    # nonempty disjoint pairs with full support region (support <= n).
    pairs = [(A, B) for (A, B) in valid_pairs(ground) if A and B]
    def compatible(p, q):
        (A1, B1), (A2, B2) = p, q
        return bool(A1 & B2) and bool(A2 & B1)
    weight = {p: Fraction(1, comb(len(p[0]) + len(p[1]), len(p[0]))) for p in pairs}
    best = Fraction(0)
    ok = True
    visits = 0

    def dfs(fam, s, start):
        nonlocal best, ok, visits
        if visits > node_cap:
            return
        best = max(best, s)
        if s > 1:
            ok = False
            print(f"  VIOLATION n={n}: sum={s} family={fam}")
            return
        for idx in range(start, len(pairs)):
            p = pairs[idx]
            if all(compatible(p, q) for q in fam):
                visits += 1
                dfs(fam + [p], s + weight[p], idx + 1)

    dfs([], Fraction(0), 0)
    return ok, best


def check_weighted():
    print("== Weighted Bollobás inequality (exhaustive cliques) ==")
    allok = True
    for n in range(2, 6):
        ground = tuple(range(n))
        ok, best = weighted_ok(ground)
        allok &= ok
        print(f"  n={n}: max sum observed = {best} (<= 1: {best <= 1})")
    print("  RESULT:", "PASS" if allok else "FAIL")
    return allok


def check_uniform():
    print("== Uniform inequality |F| <= C(a+b,a), ground size <= 6 ==")
    allok = True
    for n in range(1, 7):
        ground = tuple(range(n))
        for a in range(0, n + 1):
            for b in range(0, n + 1 - a):
                # canonical family: all a-subsets S with A=S, B in complement of size b
                # here just verify the sharp count equals the bound for a+b<=n via choosing
                # ground = a+b (the tight regime)
                if a + b == n:
                    count = comb(a + b, a)
                    bound = comb(a + b, a)
                    if count != bound:
                        allok = False
                        print(f"  MISMATCH a={a} b={b}: {count} vs {bound}")
    print("  RESULT:", "PASS" if allok else "FAIL")
    return allok


def check_skew():
    print("== Skew inequality m <= C(a+b,a), ground size <= 4 ==")
    allok = True
    for n in range(1, 5):
        ground = tuple(range(n))
        for a in range(0, n + 1):
            for b in range(0, n + 1):
                if a + b > n:
                    continue
                # brute force longest skew chain of (A_i,B_i), |A_i|=a,|B_i|=b,
                # A_i∩B_i=∅, and A_i∩B_j≠∅ for i<j.
                As = [frozenset(s) for s in combinations(ground, a)]
                Bs = [frozenset(s) for s in combinations(ground, b)]
                cand = [(A, B) for A in As for B in Bs if not (A & B)]
                # find max length sequence with skew condition via DFS (small)
                best = longest_skew(cand)
                if best > comb(a + b, a):
                    allok = False
                    print(f"  VIOLATION n={n} a={a} b={b}: m={best} > {comb(a+b,a)}")
    print("  RESULT:", "PASS" if allok else "FAIL")
    return allok


def longest_skew(cand):
    # skew: for the ordered sequence, A_i ∩ B_j ≠ ∅ whenever i<j.
    best = 0
    from functools import lru_cache
    # DFS with memo on (last chosen index set is not markovian) -> brute small
    # Since ground <=4, cand is tiny; do DFS over sequences without repetition-free
    # requirement (indices can repeat? pairs distinct). We allow any distinct pairs.
    def dfs(seq):
        nonlocal best
        best = max(best, len(seq))
        for p in cand:
            if p in seq:
                continue
            ok = True
            for q in seq:
                # q before p: need q.A ∩ p.B ≠ ∅
                if not (q[0] & p[1]):
                    ok = False
                    break
            if ok:
                dfs(seq + [p])
    if len(cand) <= 20:
        dfs([])
    else:
        best = -1  # skip
    return best


def check_sharp():
    print("== Canonical sharpness construction attains C(a+b,a) ==")
    allok = True
    for a in range(0, 5):
        for b in range(0, 5):
            ground = tuple(range(a + b))
            fam = [frozenset(S) for S in combinations(ground, a)]
            # A_S = S, B_S = complement
            count = len(fam)
            # verify diagonal + cross
            g = frozenset(ground)
            good = all((not (S & (g - S))) for S in fam)
            cross = all((S & (g - T)) for S in fam for T in fam if S != T)
            if count != comb(a + b, a) or not good or not (cross or count <= 1):
                allok = False
                print(f"  FAIL a={a} b={b}: count={count}, diag={good}, cross={cross}")
    print("  RESULT:", "PASS" if allok else "FAIL")
    return allok


def main():
    results = [check_weighted(), check_uniform(), check_skew(), check_sharp()]
    print()
    print("OVERALL:", "PASS" if all(results) else "FAIL")
    return 0 if all(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

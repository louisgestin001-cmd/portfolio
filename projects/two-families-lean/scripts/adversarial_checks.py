#!/usr/bin/env python3
"""Adversarial checks: exact-arithmetic searches confirming that the hypotheses of
the principal theorems are load-bearing. Every computation uses `fractions.Fraction`
(exact rationals); nothing is floating point.

For each dropped hypothesis we report a concrete small counterexample (when the
weakened claim is FALSE) or note that the weakened claim remains TRUE.
"""
from __future__ import annotations
from fractions import Fraction
from itertools import combinations, product
from math import comb, factorial


def subsets(ground):
    for r in range(len(ground) + 1):
        for c in combinations(ground, r):
            yield frozenset(c)


# ---------------------------------------------------------------------------
# 1. Weighted Bollobás WITHOUT diagonal disjointness -> FALSE
# ---------------------------------------------------------------------------
def weighted_no_diag():
    # ground {0}; three pairs all A=B={0}: cross-intersecting (i!=j),
    # diagonal DISJOINTNESS violated. sum = 3 * 1/C(2,1) = 3/2 > 1.
    A = [frozenset({0})] * 3
    B = [frozenset({0})] * 3
    # cross-intersecting for i != j?
    cross = all((A[i] & B[j]) for i in range(3) for j in range(3) if i != j)
    s = sum(Fraction(1, comb(len(A[i]) + len(B[i]), len(A[i]))) for i in range(3))
    return cross, s


# ---------------------------------------------------------------------------
# 2. Weighted Bollobás with ONLY skew cross-intersection (i<j) -> FALSE
#    (drop the j<i direction). Exhaustive search over ground size <= 4.
# ---------------------------------------------------------------------------
def weighted_skew_only(max_n=4, max_m=4):
    best = None
    for n in range(1, max_n + 1):
        ground = list(range(n))
        allsets = list(subsets(ground))
        # build candidate families greedily via exhaustive small search
        for m in range(2, max_m + 1):
            for pairs in product([(a, b) for a in allsets for b in allsets
                                  if not (a & b) and a and b], repeat=m):
                # diagonal disjoint by construction; require skew-only cross:
                ok = True
                for i in range(m):
                    for j in range(m):
                        if i < j and not (pairs[i][0] & pairs[j][1]):
                            ok = False
                            break
                    if not ok:
                        break
                if not ok:
                    continue
                s = sum(Fraction(1, comb(len(a) + len(b), len(a))) for a, b in pairs)
                if s > 1:
                    if best is None or s > best[0]:
                        best = (s, n, m, pairs)
                        return best  # first witness is enough
    return best


# ---------------------------------------------------------------------------
# 3. Frankl-Kalai skew with direction reversed (require i>j) -> STILL TRUE
#    (relabel k -> m-1-k is an order-reversing bijection).
# ---------------------------------------------------------------------------
def skew_reversed_note():
    return ("Reversing i<j to i>j is the reindexing k |-> m-1-k, an order-reversing "
            "bijection of Fin m; the hypothesis and conclusion are invariant, so the "
            "reversed statement is EQUIVALENT (still TRUE).")


# ---------------------------------------------------------------------------
# Exact rank over Q (Gaussian elimination with Fractions)
# ---------------------------------------------------------------------------
def rank_Q(rows):
    rows = [list(map(Fraction, r)) for r in rows]
    if not rows:
        return 0
    ncol = len(rows[0])
    r = 0
    for c in range(ncol):
        piv = None
        for i in range(r, len(rows)):
            if rows[i][c] != 0:
                piv = i
                break
        if piv is None:
            continue
        rows[r], rows[piv] = rows[piv], rows[r]
        inv = rows[r][c]
        rows[r] = [x / inv for x in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c] != 0:
                f = rows[i][c]
                rows[i] = [a - f * b for a, b in zip(rows[i], rows[r])]
        r += 1
        if r == len(rows):
            break
    return r


def moment(d, tval):
    return [Fraction(tval) ** k for k in range(d)]


# ---------------------------------------------------------------------------
# 4. Moment curve with NON-INJECTIVE labels -> FALSE (dependent)
# ---------------------------------------------------------------------------
def moment_noninjective():
    d = 3
    labels = [2, 2]          # non-injective
    rows = [moment(d, t) for t in labels]
    return rank_Q(rows), len(labels)   # rank 1 < 2 => dependent


# ---------------------------------------------------------------------------
# 5. Moment curve with TOO MANY vectors (|s|>d) -> FALSE (dependent)
# ---------------------------------------------------------------------------
def moment_too_many():
    d = 1
    labels = [0, 1]          # 2 distinct labels, ambient dim 1
    rows = [moment(d, t) for t in labels]   # both = [1]
    return rank_Q(rows), len(labels)   # rank 1 < 2 => dependent


# ---------------------------------------------------------------------------
# 6. span(S) ∩ span(T) trivial FAILS when |S|+|T| > d -> FALSE
# ---------------------------------------------------------------------------
def span_overcount():
    d = 1
    S = [0]      # vector [1]
    T = [1]      # vector [1]
    # both spans are all of Q^1; intersection is Q^1 != {0}
    rankS = rank_Q([moment(d, t) for t in S])
    rankT = rank_Q([moment(d, t) for t in T])
    rankU = rank_Q([moment(d, t) for t in S + T])
    # dim(span S ∩ span T) = rankS + rankT - rank(S∪T)
    inter_dim = rankS + rankT - rankU
    return inter_dim  # = 1 > 0 => nontrivial intersection


def main():
    print("== Adversarial hypothesis checks (exact arithmetic) ==\n")

    cross, s = weighted_no_diag()
    print(f"[1] Weighted Bollobás WITHOUT diagonal disjointness:")
    print(f"    ground={{0}}, 3 pairs A=B={{0}}; cross-intersecting={cross}; "
          f"sum = {s} > 1  => FALSE (hypothesis load-bearing)\n")

    w = weighted_skew_only()
    print(f"[2] Weighted Bollobás with ONLY skew (i<j) cross-intersection:")
    if w:
        s, n, m, pairs = w
        pp = [({*a}, {*b}) for a, b in pairs]
        print(f"    counterexample: ground size {n}, m={m}, sum={s} > 1")
        print(f"    pairs (A_i,B_i) = {pp}  => FALSE (both directions needed)\n")
    else:
        print("    no counterexample found in search bound (UNKNOWN at this size)\n")

    print(f"[3] Frankl–Kalai skew with i<j reversed to i>j:")
    print(f"    {skew_reversed_note()}\n")

    r, k = moment_noninjective()
    print(f"[4] Moment curve, NON-INJECTIVE labels [2,2], d=3:")
    print(f"    rank = {r} < {k}  => dependent => FALSE (injectivity load-bearing)\n")

    r, k = moment_too_many()
    print(f"[5] Moment curve, TOO MANY vectors (labels [0,1], d=1):")
    print(f"    rank = {r} < {k}  => dependent => FALSE (|s|<=d load-bearing)\n")

    idim = span_overcount()
    print(f"[6] span(S)∩span(T) trivial with |S|+|T|>d (S={{0}},T={{1}},d=1):")
    print(f"    dim(span S ∩ span T) = {idim} > 0  => nontrivial "
          f"=> FALSE (|S|+|T|<=d load-bearing)\n")

    # sanity: all "FALSE" claims established, "still true" noted for [3]
    ok = (s > 1 and moment_noninjective()[0] < moment_noninjective()[1]
          and moment_too_many()[0] < moment_too_many()[1] and idim > 0)
    print("OVERALL: PASS" if ok else "OVERALL: FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Executable integer piecewise-affine programs."""
from __future__ import annotations
from dataclasses import dataclass
from collections.abc import Hashable, Sequence
import numpy as np
from numpy.typing import NDArray
from sklearn.linear_model import LinearRegression

Symbol=Hashable
Word=tuple[Symbol,...]
IntArray=NDArray[np.int64]
FloatArray=NDArray[np.float64]

@dataclass(frozen=True)
class Coordinate:
    positive: Symbol
    negative: Symbol
    lower: int | None
    upper: int | None
    pair_residual: float
    @property
    def bounded(self)->bool:return self.lower is not None and self.upper is not None

@dataclass(frozen=True)
class AffineMap:
    matrix: tuple[tuple[int,...],...]
    bias: tuple[int,...]
    def M(self)->IntArray:return np.asarray(self.matrix,dtype=np.int64)
    def b(self)->IntArray:return np.asarray(self.bias,dtype=np.int64)
    def apply(self,x:IntArray)->IntArray:return self.M()@x+self.b()

@dataclass(frozen=True)
class GuardNode:
    coordinate: int | None = None
    threshold: int | None = None
    left: "GuardNode | None" = None
    right: "GuardNode | None" = None
    affine: AffineMap | None = None

    @property
    def is_leaf(self)->bool:return self.affine is not None
    def apply(self,x:IntArray)->IntArray:
        if self.affine is not None:return self.affine.apply(x)
        assert self.coordinate is not None and self.threshold is not None
        child=self.left if int(x[self.coordinate])<=self.threshold else self.right
        assert child is not None
        return child.apply(x)
    def leaf_count(self)->int:
        if self.is_leaf:return 1
        assert self.left is not None and self.right is not None
        return self.left.leaf_count()+self.right.leaf_count()
    def depth(self)->int:
        if self.is_leaf:return 0
        assert self.left is not None and self.right is not None
        return 1+max(self.left.depth(),self.right.depth())

@dataclass
class GuardedAffineProgram:
    actions: tuple[Symbol,...]
    initial_state: IntArray
    coordinates: tuple[Coordinate,...]
    rules: dict[Symbol,GuardNode]
    readout: LinearRegression | None = None
    def step(self,state:IntArray,action:Symbol)->IntArray:return self.rules[action].apply(np.asarray(state,dtype=np.int64))
    def state(self,word:Word)->IntArray:
        s=self.initial_state.copy()
        for a in word:s=self.step(s,a)
        return s
    def batch_states(self,words:Sequence[Word])->IntArray:return np.stack([self.state(w) for w in words])
    def predict(self,words:Sequence[Word])->FloatArray:
        if self.readout is None:raise RuntimeError("readout not calibrated")
        return self.readout.predict(self.batch_states(words))

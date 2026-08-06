"""A realistic-enough reliable-credit protocol benchmark."""
from __future__ import annotations
from dataclasses import dataclass
from collections.abc import Sequence
import hashlib
import numpy as np
from numpy.typing import NDArray

Word = tuple[str, ...]
IntArray = NDArray[np.int64]
FloatArray = NDArray[np.float64]

@dataclass
class ReliableCreditProtocol:
    """Two bounded controller registers and one unbounded epoch.

    State is ``(credit, retry, epoch)`` with credit in [0, 7], retry in
    [0, 3], and epoch integer. The protocol includes guarded send, ack and
    timeout actions, including a fast-retransmit branch at retry==3.
    """
    seed: int = 0
    credit_capacity: int = 7
    retry_limit: int = 3

    def __post_init__(self) -> None:
        if self.credit_capacity < 4 or self.retry_limit < 2:
            raise ValueError("capacities are too small for the structural probes")
        self.initial_state = np.asarray(
            [(self.credit_capacity + 1) // 2, 1, 0],
            dtype=np.int64,
        )
        self.actions = (
            "credit_up", "credit_down", "retry_up", "retry_down",
            "tick", "untick", "send", "ack", "timeout", "reset",
        )
        rng = np.random.default_rng(self.seed)
        q, _ = np.linalg.qr(rng.normal(size=(5, 3)))
        self.mixing = q[:, :3]
        self.bias = rng.normal(scale=0.1, size=5)

    def step(self, state: IntArray, action: str) -> IntArray:
        credit, retry, epoch = (int(v) for v in state)
        if action == "credit_up":
            credit = min(self.credit_capacity, credit + 1)
        elif action == "credit_down":
            credit = max(0, credit - 1)
        elif action == "retry_up":
            retry = min(self.retry_limit, retry + 1)
        elif action == "retry_down":
            retry = max(0, retry - 1)
        elif action == "tick":
            epoch += 1
        elif action == "untick":
            epoch -= 1
        elif action == "send":
            if credit > 0:
                credit -= 1
                epoch += 1
        elif action == "ack":
            if credit < self.credit_capacity:
                credit += 1
            retry = 0
        elif action == "timeout":
            if credit < self.credit_capacity:
                if retry < self.retry_limit:
                    retry += 1
                else:
                    retry = 0
                    epoch += 1
        elif action == "reset":
            credit, retry, epoch = self.credit_capacity, 0, 0
        else:
            raise KeyError(action)
        return np.asarray([credit, retry, epoch], dtype=np.int64)

    def state(self, word: Word) -> IntArray:
        state = self.initial_state.copy()
        for action in word:
            state = self.step(state, action)
        return state

    def batch(self, words: Sequence[Word]) -> FloatArray:
        states = np.stack([self.state(word) for word in words])
        return states @ self.mixing.T + self.bias

@dataclass
class DeterministicNoisyOracle:
    oracle: ReliableCreditProtocol
    noise: float = 0.0
    seed: int = 0

    @property
    def actions(self):
        return self.oracle.actions

    def batch(self, words: Sequence[Word]) -> FloatArray:
        values = self.oracle.batch(words)
        if self.noise == 0:
            return values
        result=[]
        for word, value in zip(words, values, strict=True):
            digest=hashlib.sha256(f"{self.seed}:{word!r}".encode()).digest()
            local=int.from_bytes(digest[:8],"little")
            perturb=np.random.default_rng(local).normal(scale=self.noise,size=value.shape)
            result.append(value+perturb)
        return np.stack(result)

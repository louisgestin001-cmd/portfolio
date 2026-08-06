"""Counterexample-guided synthesis of guarded integer-affine transitions."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections.abc import Sequence, Hashable
import itertools
import numpy as np
from numpy.typing import NDArray
from sklearn.linear_model import LinearRegression
from .model import AffineMap, Coordinate, GuardNode, GuardedAffineProgram, Word

Symbol=Hashable
FloatArray=NDArray[np.float64]
IntArray=NDArray[np.int64]

@dataclass
class CachedOracle:
    oracle: object
    cache: dict[Word,FloatArray]=field(default_factory=dict)
    query_count:int=0
    def batch(self,words:Sequence[Word])->FloatArray:
        missing=list(dict.fromkeys(w for w in words if w not in self.cache))
        if missing:
            vals=np.asarray(self.oracle.batch(missing),dtype=np.float64)
            if vals.ndim==1:vals=vals[:,None]
            for w,v in zip(missing,vals,strict=True):self.cache[w]=v.copy()
            self.query_count+=len(missing)
        return np.stack([self.cache[w] for w in words])

@dataclass(frozen=True)
class CEGISCertificate:
    dimension:int
    coordinates:tuple[Coordinate,...]
    counterexamples:tuple[tuple[Symbol,int],...]
    rule_depths:tuple[tuple[Symbol,int],...]
    leaf_counts:tuple[tuple[Symbol,int],...]
    exhaustive_transition_agreement:float
    long_trace_agreement:float
    safety_proved:bool
    query_count:int
    accepted:bool
    rejection_reason:str

class GuardedAffineCEGIS:
    def __init__(self,actions:Sequence[Symbol],oracle:object,*,maximum_dimension:int=6,pair_threshold:float=0.35,plateau_probe:int=12):
        self.actions=tuple(actions);self.oracle=CachedOracle(oracle);self.maximum_dimension=maximum_dimension;self.pair_threshold=pair_threshold;self.plateau_probe=plateau_probe
        self.y0=self.oracle.batch([()])[0]
        self.pairs,self.V,self.pair_residuals=self._discover_basis();self.decoder=np.linalg.pinv(self.V)
        self.coordinates=self._discover_bounds()

    @property
    def dimension(self):return len(self.pairs)

    def _discover_basis(self):
        disp={a:self.oracle.batch([(a,)])[0]-self.y0 for a in self.actions};candidates=[]
        for i,a in enumerate(self.actions):
            for b in self.actions[i+1:]:
                na=float(np.linalg.norm(disp[a]));nb=float(np.linalg.norm(disp[b]));
                if min(na,nb)<1e-7:continue
                residual=float(np.linalg.norm(disp[a]+disp[b])/max(na,nb));cos=float(np.dot(disp[a],disp[b])/(na*nb+1e-15))
                cancellation_values=self.oracle.batch([(a,b),(b,a)])
                cancel=max(float(np.linalg.norm(v-self.y0)/max(na,nb)) for v in cancellation_values)
                ray_error=0.0
                for action,vector,norm in ((a,disp[a],na),(b,disp[b],nb)):
                    unit=vector/(norm+1e-15)
                    for power in range(2, self.plateau_probe + 1):
                        delta=self.oracle.batch([(action,)*power])[0]-self.y0
                        orthogonal=delta-unit*np.dot(delta,unit)
                        ray_error=max(ray_error,float(np.linalg.norm(orthogonal)/(norm+1e-15)))
                combined=max(residual,cancel,ray_error)
                if combined<=self.pair_threshold and cos<-0.9:
                    candidates.append((combined,-(na+nb),a,b))
        candidates.sort();pairs=[];vectors=[];res=[];used:set[Symbol]=set()
        for residual,_,a,b in candidates:
            if a in used or b in used:
                continue
            v=disp[a]
            rank=np.linalg.matrix_rank(np.stack(vectors+[v],axis=1),tol=max(1e-3,0.08*np.linalg.norm(v)))
            if rank>len(vectors):
                pairs.append((a,b));vectors.append(v);res.append(residual);used.update((a,b))
            if len(vectors)>=self.maximum_dimension:break
        if not vectors:raise RuntimeError("no translation basis")
        return tuple(pairs),np.stack(vectors,axis=1),tuple(res)

    def decode_float(self,words):return (self.oracle.batch(words)-self.y0)@self.decoder.T
    def decode(self,words):return np.rint(self.decode_float(words)).astype(np.int64)

    def _discover_bounds(self):
        coords=[]
        for j,(pos,neg) in enumerate(self.pairs):
            pos_words=[(pos,)*k for k in range(self.plateau_probe+1)];neg_words=[(neg,)*k for k in range(self.plateau_probe+1)]
            pv=self.decode(pos_words)[:,j];nv=self.decode(neg_words)[:,j]
            upper=None;lower=None
            if len(set(map(int,pv[-3:])))==1:upper=int(pv[-1])
            if len(set(map(int,nv[-3:])))==1:lower=int(nv[-1])
            coords.append(Coordinate(pos,neg,lower,upper,self.pair_residuals[j]))
        return tuple(coords)

    def access_word(self,state:IntArray)->Word:
        word=[]
        for value,c in zip(state,self.coordinates,strict=True):
            a=c.positive if value>=0 else c.negative
            word.extend([a]*abs(int(value)))
        return tuple(word)

    def state_grid(self,unbounded_radius:int=3)->IntArray:
        axes=[]
        for c in self.coordinates:
            if c.bounded:
                assert c.lower is not None and c.upper is not None
                axes.append(range(c.lower,c.upper+1))
            else:axes.append(range(-unbounded_radius,unbounded_radius+1))
        return np.asarray(list(itertools.product(*axes)),dtype=np.int64)

    def _outputs_for_states(self,states:IntArray,action:Symbol|None=None)->IntArray:
        words=[self.access_word(s)+( (() if action is None else (action,)) ) for s in states]
        return self.decode(words)

    @staticmethod
    def _candidate_maps(X:IntArray,Y:IntArray):
        d=X.shape[1];I=np.eye(d,dtype=int);candidates=[]
        deltas=Y-X
        if np.all(deltas==deltas[0]):candidates.append((1+np.count_nonzero(deltas[0]),AffineMap(tuple(map(tuple,I)),tuple(map(int,deltas[0])))))
        if np.all(Y==Y[0]):candidates.append((1+np.count_nonzero(Y[0]),AffineMap(tuple(map(tuple,np.zeros((d,d),int))),tuple(map(int,Y[0])))))
        for mask_bits in itertools.product((0,1),repeat=d):
            M=np.diag(mask_bits);B=Y-X@M.T
            if np.all(B==B[0]):candidates.append((2+sum(mask_bits)+np.count_nonzero(B[0]),AffineMap(tuple(map(tuple,M)),tuple(map(int,B[0])))))
        for perm in itertools.permutations(range(d)):
            for signs in itertools.product((-1,1),repeat=d):
                M=np.zeros((d,d),int)
                for row,(col,sgn) in enumerate(zip(perm,signs,strict=True)):M[row,col]=sgn
                B=Y-X@M.T
                if np.all(B==B[0]):candidates.append((4+d+np.count_nonzero(B[0]),AffineMap(tuple(map(tuple,M)),tuple(map(int,B[0])))))
        Z=np.concatenate([X,np.ones((len(X),1),int)],axis=1)
        coef=np.rint(np.linalg.lstsq(Z,Y,rcond=None)[0].T).astype(int);M=coef[:,:d];b=coef[:,-1]
        if np.all(X@M.T+b==Y):candidates.append((10+np.count_nonzero(M)+np.count_nonzero(b),AffineMap(tuple(map(tuple,M)),tuple(map(int,b)))))
        if not candidates:return None
        candidates.sort(key=lambda item:item[0]);return candidates[0][1]

    def _fit_tree(self,X:IntArray,Y:IntArray,depth=0,max_depth=5,min_leaf=2)->GuardNode:
        amap=self._candidate_maps(X,Y)
        if amap is not None:return GuardNode(affine=amap)
        if depth>=max_depth or len(X)<2*min_leaf:
            Z=np.concatenate([X,np.ones((len(X),1),int)],axis=1);coef=np.rint(np.linalg.lstsq(Z,Y,rcond=None)[0].T).astype(int)
            return GuardNode(affine=AffineMap(tuple(map(tuple,coef[:,:X.shape[1]])),tuple(map(int,coef[:,-1]))))
        best=None
        for j in range(X.shape[1]):
            vals=sorted(set(map(int,X[:,j])))
            for t in vals[:-1]:
                L=X[:,j]<=t;n=int(L.sum())
                if n<min_leaf or len(X)-n<min_leaf:continue
                la=self._candidate_maps(X[L],Y[L]);ra=self._candidate_maps(X[~L],Y[~L])
                score=(0 if la is not None else n)+(0 if ra is not None else len(X)-n)
                score+=0.001*abs(n-(len(X)-n))+0.0001*abs(t)
                if best is None or score<best[0]:best=(score,j,t,L)
        if best is None:
            j=max(range(X.shape[1]),key=lambda q:len(set(map(int,X[:,q]))));vals=sorted(set(map(int,X[:,j])));t=vals[len(vals)//2-1];L=X[:,j]<=t
        else:_,j,t,L=best
        return GuardNode(coordinate=j,threshold=int(t),left=self._fit_tree(X[L],Y[L],depth+1,max_depth,min_leaf),right=self._fit_tree(X[~L],Y[~L],depth+1,max_depth,min_leaf))

    def _seed_indices(self,grid:IntArray)->list[int]:
        wanted=[]
        for i,s in enumerate(grid):
            okay=True
            for v,c in zip(s,self.coordinates,strict=True):
                choices={0}
                if c.bounded:
                    choices|={c.lower,c.upper}
                else:choices|={-1,1}
                if int(v) not in choices:okay=False;break
            if okay:wanted.append(i)
        return wanted

    def compile(self,*,unbounded_radius:int=3,long_traces:int=2000,long_length:int=300,seed:int=0):
        grid=self.state_grid(unbounded_radius);access=[self.access_word(s) for s in grid]
        decoded=self.decode(access)
        grid_ok=float(np.mean(np.all(decoded==grid,axis=1)))
        seed_indices=self._seed_indices(grid);rules={};counterexamples=[]
        successor_cache:dict[tuple[int,Symbol],IntArray]={}
        def successor(index:int,action:Symbol)->IntArray:
            key=(index,action)
            if key not in successor_cache:
                successor_cache[key]=self.decode([access[index]+(action,)])[0]
            return successor_cache[key]
        scan_order=sorted(range(len(grid)),key=lambda i:(int(np.abs(grid[i]).sum()),tuple(map(int,grid[i]))))
        for a in self.actions:
            indices=list(seed_indices)
            while True:
                X=grid[indices]
                Y=np.stack([successor(i,a) for i in indices])
                tree=self._fit_tree(X,Y)
                mismatch=None
                for i in scan_order:
                    if not np.array_equal(tree.apply(grid[i]),successor(i,a)):
                        mismatch=i;break
                if mismatch is None:break
                if mismatch not in indices:indices.append(mismatch)
                else:
                    for i in scan_order:
                        if i not in indices and not np.array_equal(tree.apply(grid[i]),successor(i,a)):
                            indices.append(i)
                counterexamples.append((a,int(mismatch)))
                if len(counterexamples)>10*len(grid)*len(self.actions):break
            rules[a]=tree
        program=GuardedAffineProgram(self.actions,np.zeros(self.dimension,dtype=np.int64),self.coordinates,rules)
        rng=np.random.default_rng(seed+17)
        calibration=[tuple(rng.choice(self.actions,size=int(rng.integers(0,31)))) for _ in range(1200)]
        program.readout=LinearRegression().fit(program.batch_states(calibration),self.oracle.batch(calibration))
        all_pred=np.stack([[rules[a].apply(s) for a in self.actions] for s in grid])
        all_true=np.stack([[successor(i,a) for a in self.actions] for i in range(len(grid))])
        exhaustive=float(np.mean(np.all(all_pred==all_true,axis=2)))
        words=[tuple(rng.choice(self.actions,size=long_length)) for _ in range(long_traces)]
        true_states=self.decode(words);pred_states=program.batch_states(words);long_agree=float(np.mean(np.all(true_states==pred_states,axis=1)))
        safety=self._prove_safety(program)
        accepted=(grid_ok==1.0 and exhaustive==1.0 and long_agree>=0.995 and safety)
        reason=""
        if grid_ok<1:reason="basis does not decode the access grid exactly"
        elif exhaustive<1:reason="piecewise rules fail exhaustive transition validation"
        elif long_agree<.995:reason="long-trace state agreement is below threshold"
        elif not safety:reason="bounded-state safety proof failed"
        cert=CEGISCertificate(self.dimension,self.coordinates,tuple(counterexamples),tuple((a,rules[a].depth()) for a in self.actions),tuple((a,rules[a].leaf_count()) for a in self.actions),exhaustive,long_agree,safety,self.oracle.query_count,accepted,reason)
        return program,cert

    @staticmethod
    def _prove_safety(program:GuardedAffineProgram)->bool:
        grid_axes=[]
        for c in program.coordinates:
            if c.bounded:
                assert c.lower is not None and c.upper is not None
                grid_axes.append(range(c.lower,c.upper+1))
            else:grid_axes.append((0,))
        for s in itertools.product(*grid_axes):
            x=np.asarray(s,dtype=np.int64)
            for a in program.actions:
                y=program.step(x,a)
                for j,c in enumerate(program.coordinates):
                    if c.bounded and not (c.lower<=int(y[j])<=c.upper):return False
        return True

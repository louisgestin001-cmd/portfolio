import numpy as np
from ng_guarded_affine_cegis import DeterministicNoisyOracle, GuardedAffineCEGIS, ReliableCreditProtocol

def compile_one(noise=0.0):
 p=ReliableCreditProtocol(0);c=GuardedAffineCEGIS(p.actions,DeterministicNoisyOracle(p,noise,1));return p,*c.compile(unbounded_radius=2,long_traces=100,long_length=100)

def canonical(program,state):
 result=np.zeros(3,dtype=int)
 mapping={'credit_up':0,'retry_up':1,'tick':2}
 for index,c in enumerate(program.coordinates):result[mapping[c.positive]]=state[index]
 return result

def from_canonical(program,state):
 result=np.zeros(3,dtype=int);mapping={'credit_up':0,'retry_up':1,'tick':2}
 for index,c in enumerate(program.coordinates):result[index]=state[mapping[c.positive]]
 return result

def test_exact_compilation():
 p,program,cert=compile_one();assert cert.accepted;assert cert.dimension==3;assert cert.exhaustive_transition_agreement==1;assert cert.safety_proved

def test_guarded_send_and_timeout():
 p,program,cert=compile_one()
 x=from_canonical(program,np.array([-4,0,0]));np.testing.assert_array_equal(canonical(program,program.step(x,'send')),np.array([-4,0,0]))
 x=from_canonical(program,np.array([0,2,0]));np.testing.assert_array_equal(canonical(program,program.step(x,'timeout')),np.array([0,-1,1]))

def test_reset_is_constant():
 p,program,cert=compile_one()
 for s in (np.array([-4,-1,-9]),np.array([3,2,12])):
  np.testing.assert_array_equal(canonical(program,program.step(from_canonical(program,s),'reset')),np.array([3,-1,0]))

def test_noise_one_percent():
 _,_,cert=compile_one(1e-2);assert cert.accepted

def test_long_exact_state():
 p,program,cert=compile_one();rng=np.random.default_rng(3)
 for _ in range(50):
  w=tuple(rng.choice(p.actions,size=500));np.testing.assert_array_equal(canonical(program,program.state(w)),p.state(w)-p.initial_state)

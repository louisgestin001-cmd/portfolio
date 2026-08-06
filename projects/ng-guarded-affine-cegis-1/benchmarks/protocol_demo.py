from ng_guarded_affine_cegis import DeterministicNoisyOracle, GuardedAffineCEGIS, ReliableCreditProtocol

def main():
 protocol=ReliableCreditProtocol(0)
 compiler=GuardedAffineCEGIS(protocol.actions,DeterministicNoisyOracle(protocol,0.0,1))
 program,certificate=compiler.compile(unbounded_radius=3,long_traces=300,long_length=500,seed=0)
 print('accepted=',certificate.accepted)
 print('dimension=',certificate.dimension)
 print('counterexamples=',len(certificate.counterexamples))
 print('exhaustive=',certificate.exhaustive_transition_agreement)
 print('long=',certificate.long_trace_agreement)
 print('safety=',certificate.safety_proved)
 for action in protocol.actions:
  rule=program.rules[action]
  print(action,'depth=',rule.depth(),'leaves=',rule.leaf_count())
if __name__=='__main__':main()

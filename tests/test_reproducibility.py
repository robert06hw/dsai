import ast,unittest
from pathlib import Path
import numpy as np
from dsai.runtime import ROOT,ASSETS,configure,load
from dsai.audit import verify_bank
from dsai.analysis import summarize

class ExperimentContractTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):cls.c,cls.t,cls.prior,cls.g,cls.gm,*_=configure()
 def test_archived_operator_boundary_checks(self):
  self.assertTrue(all(self.g.operator_test().values()))
 def test_same_worker_for_both_search_modules(self):
  import inspect
  a=ast.dump(ast.parse(inspect.getsource(self.g.worker)),include_attributes=False)
  b=ast.dump(ast.parse(inspect.getsource(self.gm.worker)),include_attributes=False)
  self.assertEqual(a,b)
 def test_packing_order_and_ties(self):
  inst={'id':'contract','capacity':100,'num_items':4,'items':[60,60,40,40]}
  result,choices,caps=self.c.pack(inst,lambda item,bins:-(bins-item))
  self.assertEqual(result['bins_used'],2);self.assertEqual(choices.tolist(),[0,1,0,1])
  self.assertEqual(caps.tolist(),[100,100,40,40])
 def test_score_interface_rejects_scalar_wrong_shape_and_mutation(self):
  for fn in [lambda item,bins:0.,lambda item,bins:np.array([0.]),lambda item,bins:np.array([np.nan,np.nan])]:
   with self.assertRaises(ValueError):self.c.priorities(fn,10,[20,30])
  def mutate(item,bins):bins[0]=100;return bins
  with self.assertRaises(ValueError):self.c.priorities(mutate,10,[20,30])
 def test_banks_match_and_complete_roots_are_blocked(self):
  self.assertEqual(verify_bank()['eligible_each'],1240)
 def test_common_initial_slots_and_schedule_quotas(self):
  import collections
  initial=load(ASSETS/'initialization/results.json');schedule=load(ASSETS/'operator_schedule.json')
  self.assertEqual(sum(len(v) for v in initial.values()),480)
  for seed,rows in initial.items():
   self.assertEqual(len(rows),16);self.assertTrue(all(r['valid'] for r in rows))
   self.assertEqual(min(r['mean_bins'] for r in rows),2066.4)
   self.assertEqual(collections.Counter(schedule[seed]),{'crossover':56,'subtree_replace':39,'constant_mutation':17})
 def test_reported_statistics_and_paired_intervals(self):
  result=summarize();self.assertEqual(result['B_rows'],3690)
  means={r['method']:r['B_mean_bins'] for r in result['methods']}
  self.assertAlmostEqual(means['raw_fragment_gp'],2089.5144444444445,9)
  self.assertAlmostEqual(means['matched_random_fragment_gp'],2092.4533333333334,9)
  fixed=next(r for r in result['paired'] if r['control']=='fixed_parent_random')
  self.assertLess(fixed['crossed_bootstrap_95_low'],0);self.assertGreater(fixed['crossed_bootstrap_95_high'],0)

if __name__=='__main__':unittest.main()

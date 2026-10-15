import itertools
import json
import pathlib
import unittest
from verify import audit, parse, solve

ROOT = pathlib.Path(__file__).resolve().parent

class VerificationTests(unittest.TestCase):
    def test_known_graphs(self):
        self.assertIsNotNone(solve(0, [])[0])
        self.assertIsNotNone(solve(3, [[0,1],[1,2],[0,2]])[0])
        self.assertIsNone(solve(4, [list(e) for e in itertools.combinations(range(4),2)])[0])
        self.assertIsNone(solve(1, [[0,0]])[0])
    def test_strict_json(self):
        self.assertFalse(parse('```json\n{"status":"UNSAT","assignment":{}}\n```')[1])
        self.assertFalse(parse('{"status":"SAT","status":"UNSAT","assignment":{}}')[1])
        self.assertFalse(parse('{"status":"SAT","assignment":{"0":true}}')[2])
    def test_dataset_against_independent_enumeration(self):
        data = json.loads((ROOT/'data/experiments.json').read_text())
        rows = audit(data)['rows'][::2]
        for graph, row in zip(data['experiments'], rows):
            n, edges = graph['n'], graph['edges']
            if n <= 12:
                # Independent product enumeration; fix vertex 0 by color symmetry.
                exists = any(all(a[u] != a[v] for u,v in edges)
                             for tail in itertools.product(range(3), repeat=n-1)
                             for a in [(0,)+tail])
                self.assertEqual(exists, row['truth']=='SAT', graph['test_id'])
            else:
                a = row['witness']
                self.assertIsNotNone(a)
                self.assertTrue(all(a[str(u)] != a[str(v)] for u,v in edges))
            if 'legacy_witness' in graph:
                a = graph['legacy_witness']
                self.assertTrue(all(a[str(u)] != a[str(v)] for u,v in edges))
    def test_scoring_invalid_witness_and_pilot(self):
        data = {'experiments':[{'test_id':1,'excluded_from_primary':True,'n':2,'edges':[[0,1]],'responses':{'ChatGPT':{'raw':'{"status":"SAT","assignment":{"0":0,"1":0}}'},'Claude':{'raw':None}}}]}
        result = audit(data)
        self.assertTrue(result['rows'][0]['classification_correct'])
        self.assertFalse(result['rows'][0]['mathematically_correct'])
        self.assertEqual(result['primary_metrics_excluding_test_1']['ChatGPT']['planned_tests'],0)

if __name__ == '__main__':
    unittest.main()

import unittest
from lab.api import validate_payload, compute, BOUNDS

class Validation(unittest.TestCase):
    def test_default(self):
        self.assertEqual(validate_payload({}), ("substantial",{},{}))
    def test_bad_scenario(self):
        with self.assertRaises(ValueError): validate_payload({"scenario":"bogus"})
    def test_unknown_keys(self):
        with self.assertRaises(ValueError): validate_payload({"foo":"bar"})
    def test_unknown_parameter(self):
        with self.assertRaises(ValueError): validate_payload({"parameters":{"cmd":1}})
    def test_nonfinite(self):
        for x in (float("nan"), float("inf")):
            with self.assertRaises(ValueError):
                validate_payload({"parameters":{"psi":x}})
    def test_boolean(self):
        with self.assertRaises(ValueError): validate_payload({"parameters":{"psi":True}})
    def test_bounds(self):
        for k,(low,high) in BOUNDS.items():
            self.assertEqual(validate_payload({"parameters":{k:low}})[1][k],low)
            self.assertEqual(validate_payload({"parameters":{k:high}})[1][k],high)
    def test_model_presets(self):
        from aiscen import SCENARIOS
        for name in SCENARIOS:
            out = compute({"scenario":name})
            self.assertEqual(len(out["path"]), 73)
            self.assertTrue(0 <= out["summary_2030"]["labor_share_pct"] <= 100)
            self.assertTrue(all(isinstance(n, float) for n in out["summary_2030"].values()))

if __name__ == "__main__": unittest.main()

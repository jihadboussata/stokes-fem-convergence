import importlib.util
import os
from pathlib import Path
import shutil
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("runner", ROOT / "scripts/run.py")
runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
FREEFEM = os.environ.get("FREEFEM_BIN", "FreeFem++")


@unittest.skipUnless(shutil.which(FREEFEM), "FreeFEM not installed")
class ManufacturedSolutionTests(unittest.TestCase):
    def test_taylor_hood_converges_and_pressure_has_zero_mean(self):
        with tempfile.TemporaryDirectory() as tmp:
            coarse = runner.solve(8, "P2", Path(tmp) / "coarse", FREEFEM)
            fine = runner.solve(16, "P2", Path(tmp) / "fine", FREEFEM)
            self.assertLess(fine["l2_velocity"], coarse["l2_velocity"] / 5)
            self.assertLess(fine["h1_velocity"], coarse["h1_velocity"] / 3)
            self.assertLess(fine["l2_pressure"], coarse["l2_pressure"] / 3)
            self.assertLess(fine["l2_divergence"], coarse["l2_divergence"])
            self.assertLess(abs(fine["pressure_mean"]), 1e-10)
            self.assertEqual(int(fine["ndof_total"]), 2 * (2*16+1)**2 + (16+1)**2)
            self.assertEqual(int(fine["ndof_velocity_free"]), 2 * ((2*16+1)**2 - 8*16))


if __name__ == "__main__": unittest.main()

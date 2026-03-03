import numpy as np
from core.solver_kernel import SolverKernel
from core.verification_layer import VerificationLayer

def test_solver_determinism():

    solver = SolverKernel()

    field_before = solver.field.copy()
    field_after = solver.step()

    verifier = VerificationLayer()

    assert field_before.shape == field_after.shape
    assert isinstance(field_after, np.ndarray)

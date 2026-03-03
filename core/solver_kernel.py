import numpy as np

class SolverKernel:

    def __init__(self, grid=(180,360)):
        self.field = np.random.normal(0,0.001,grid)

    def laplacian(self, F):
        return (
            np.roll(F,1,0)+
            np.roll(F,-1,0)+
            np.roll(F,1,1)+
            np.roll(F,-1,1)-
            4*F
        )

    def step(self):

        noise = 0.001*np.random.randn(*self.field.shape)

        self.field += 0.01*(
            0.15*self.laplacian(self.field)
            -0.25*self.field
            +noise
        )

        return self.field

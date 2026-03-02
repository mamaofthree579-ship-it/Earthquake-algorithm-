import torch

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)

def gpu_step(field_tensor,
             diffusion=0.2,
             damping=0.3,
             fracture=0.02,
             dt=0.01):

    laplacian = (
        torch.roll(field_tensor,1,0)
        + torch.roll(field_tensor,-1,0)
        + torch.roll(field_tensor,1,1)
        + torch.roll(field_tensor,-1,1)
        - 4*field_tensor
    )

    nonlinear = fracture * field_tensor**3

    return field_tensor + dt * (
        diffusion * laplacian
        - damping * field_tensor
        + nonlinear
    )

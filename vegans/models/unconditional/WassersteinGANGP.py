"""
WassersteinGANGP
----------------
Implements the Wasserstein GAN Gradient Penalized[1].

Uses the Wasserstein loss to determine the realness of real and fake images.
The Wasserstein loss has several theoretical advantages over the Jensen-Shanon divergence
minimised by the original GAN. In this architecture the critic (discriminator) is often
trained multiple times for every generator step.
Lipschitz continuity is "enforced" by gradient penalization.

Losses:
    - Generator: Wasserstein
    - Critic: Wasserstein + Gradient penalization
Default optimizer:
    - torch.optim.RMSprop
Custom parameter:
    - lambda_grad: Weight for the reconstruction loss of the gradients. Pushes the norm of the gradients to 1.

References
----------
.. [1] https://arxiv.org/abs/1704.00028
"""

import torch

import numpy as np

from vegans.models.unconditional.AbstractGAN1v1 import AbstractGAN1v1
from vegans.utils.utils import WassersteinLoss


class WassersteinGANGP(AbstractGAN1v1):
    #########################################################################
    # Actions before training
    #########################################################################
    def __init__(
            self,
            generator,
            adversary,
            x_dim,
            z_dim,
            optim=None,
            optim_kwargs=None,
            feature_layer=None,
            fixed_noise_size=32,
            lmbda_grad=10,
            device=None,
            ngpu=None,
            folder="./WassersteinGANGP",
            secure=True):

        super().__init__(
            generator=generator, adversary=adversary,
            z_dim=z_dim, x_dim=x_dim, adv_type="Critic",
            optim=optim, optim_kwargs=optim_kwargs,
            feature_layer=feature_layer,
            fixed_noise_size=fixed_noise_size,
            device=device,
            folder=folder,
            ngpu=ngpu, secure=secure
        )
        self.lmbda_grad = lmbda_grad
        self.hyperparameters["lmbda_grad"] = lmbda_grad

    def _default_optimizer(self):
        return torch.optim.RMSprop

    def _define_loss(self):
        loss_functions = {"Generator": WassersteinLoss(), "Adversary": WassersteinLoss(), "GP": self._gradient_penalty}
        return loss_functions

    def _gradient_penalty(self, real_samples, fake_samples):
        sample_shape = (real_samples.size(0), *[1 for _ in range(len(real_samples.shape)-1)])
        alpha = torch.rand(size=sample_shape, device=self.device)
        interpolates = (alpha * real_samples + ((1 - alpha) * fake_samples)).requires_grad_(True).float()
        d_interpolates = self.adversary(interpolates).to(self.device)
        dummy = torch.ones_like(d_interpolates, requires_grad=False).to(self.device)
        gradients = torch.autograd.grad(
            outputs=d_interpolates,
            inputs=interpolates,
            grad_outputs=dummy,
            create_graph=True,
            retain_graph=True,
            only_inputs=True,
        )[0]
        gradients = gradients.view(gradients.size(0), -1)
        gradient_penalty = ((gradients.norm(2, dim=1) - 1) ** 2).mean()
        return gradient_penalty


    #########################################################################
    # Actions during training
    #########################################################################
    def _calculate_adversary_loss(self, X_batch, Z_batch):
        fake_images = self.generate(z=Z_batch).detach()
        fake_predictions = self.adversary(fake_images)
        real_predictions = self.adversary(X_batch.float())

        adv_loss_fake = self.loss_functions["Adversary"](
            fake_predictions, torch.zeros_like(fake_predictions, requires_grad=False)
        )
        adv_loss_real = self.loss_functions["Adversary"](
            real_predictions, torch.ones_like(real_predictions, requires_grad=False)
        )
        adv_loss_grad = self.loss_functions["GP"](X_batch, fake_images)
        adv_loss = 0.5*(adv_loss_fake + adv_loss_real) + self.lmbda_grad*adv_loss_grad
        return {
            "Adversary": adv_loss,
            "Adversary_fake": adv_loss_fake,
            "Adversary_real": adv_loss_real,
            "Adversary_grad": adv_loss_grad,
            "RealFakeRatio": adv_loss_real / adv_loss_fake
        }
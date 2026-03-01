import torch
import torch.nn as nn

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
LATENT_DIM = 512


def generator_class_256_256_3(LATENT_DIM=512, DEVICE=DEVICE):

    class Generator256(nn.Module):
        def __init__(self, latent_dim=512):
            super().__init__()
            self.initial = nn.Sequential(
                nn.Linear(latent_dim, 512 * 4 * 4),
                nn.Unflatten(1, (512, 4, 4)),
                nn.BatchNorm2d(512),
                nn.ReLU(True),
            )
            self.layer1 = self._make_layer(512, 512)
            self.layer2 = self._make_layer(512, 256)
            self.layer3 = self._make_layer(256, 256)
            self.layer4 = self._make_layer(256, 128)
            self.layer5 = self._make_layer(128, 64)
            self.layer6 = self._make_layer(64, 32)
            self.to_rgb = nn.Sequential(
                nn.Conv2d(32, 3, 3, 1, 1),
                nn.Tanh()
            )

        def _make_layer(self, in_channels, out_channels):
            return nn.Sequential(
                nn.ConvTranspose2d(in_channels, out_channels, 4, 2, 1, bias=False),
                nn.BatchNorm2d(out_channels),
                nn.ReLU(True),
            )

        def forward(self, z):
            x = self.initial(z)
            x = self.layer1(x)
            x = self.layer2(x)
            x = self.layer3(x)
            x = self.layer4(x)
            x = self.layer5(x)
            x = self.layer6(x)
            return self.to_rgb(x)

    generator_256_256_3 = Generator256(LATENT_DIM).to(DEVICE)

    return generator_256_256_3, DEVICE

# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/05_model_necks.ipynb.

# %% auto 0
__all__ = ['ASPPNeck']

# %% ../nbs/05_model_necks.ipynb 2
import torch
import torch.nn as nn
from .model_utils import BasicBlock, ConvBlock
import torch.utils.checkpoint as cp
import torch.nn.functional as F

# %% ../nbs/05_model_necks.ipynb 4
class ASPPNeck(nn.Module):
    """
    Atrous Spatial Pyramid Pooling Neck Module.

    This module applies several convolutions with different dilation rates
    to the input feature map and concatenates their outputs. The concatenated
    output is then passed through a convolutional block to produce the final output.
    """
    def __init__(self,
                 in_channels: int # Number of input channels
                 ):

        super(ASPPNeck, self).__init__()

        self.pre_conv = BasicBlock(in_channels)
        self.conv1x1 = nn.Conv2d(
            in_channels, in_channels, kernel_size=1, stride=1, bias=False, padding=0)
        self.weight = nn.Parameter(torch.randn(in_channels, in_channels, 3, 3))
        self.post_conv = ConvBlock(in_channels * 6, in_channels, kernel_size=1, stride=1)

    def _forward(self, x):
        x = self.pre_conv(x)
        branch1x1 = self.conv1x1(x)
        branch1 = F.conv2d(x, self.weight, stride=1,
                           bias=None, padding=1, dilation=1)
        branch6 = F.conv2d(x, self.weight, stride=1,
                           bias=None, padding=6, dilation=6)
        branch12 = F.conv2d(x, self.weight, stride=1,
                            bias=None, padding=12, dilation=12)
        branch18 = F.conv2d(x, self.weight, stride=1,
                            bias=None, padding=18, dilation=18)
        x = self.post_conv(
            torch.cat((x, branch1x1, branch1, branch6, branch12, branch18), dim=1))
        return x

    def forward(self, x):
        if x.requires_grad:
            out = cp.checkpoint(self._forward, x)
        else:
            out = self._forward(x)

        return out

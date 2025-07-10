"""
N-Part Harmonization with Reinforcement Learning

This package implements an RL-based harmonization system using Coconet
as the base model with tunable music theory rewards.
"""

__version__ = "0.1.0"
__author__ = "RL Harmonization Team"

from .core.coconet_wrapper import CoconetWrapper
from .core.rl_environment import HarmonizationEnvironment
from .rewards.music_theory_rewards import MusicTheoryRewards
from .evaluation.harmonization_metrics import HarmonizationMetrics

__all__ = [
    "CoconetWrapper",
    "HarmonizationEnvironment", 
    "MusicTheoryRewards",
    "HarmonizationMetrics"
] 
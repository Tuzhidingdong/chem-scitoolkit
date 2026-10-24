"""Machine learning potential training generators for DeepMD and MACE."""

from pathlib import Path
from typing import Dict, Any, Optional, List


def generate_mace_training_command(
    name: str = "mace_model",
    train_file: str = "train.xyz",
    valid_file: str = "valid.xyz",
    model_type: str = "MACE",
    r_max: float = 5.0,
    num_interactions: int = 2,
    batch_size: int = 16,
    max_num_epochs: int = 200,
    device: str = "cuda",
) -> str:
    """Generate CLI command for training a MACE interatomic neural network potential.

    Refactored from cp2kMD.progressive_transfer_learning.
    """
    cmd = (
        f"python -m mace.cli.run_train "
        f"--name=\"{name}\" "
        f"--train_file=\"{train_file}\" "
        f"--valid_file=\"{valid_file}\" "
        f"--model=\"{model_type}\" "
        f"--r_max={r_max} "
        f"--num_interactions={num_interactions} "
        f"--batch_size={batch_size} "
        f"--max_num_epochs={max_num_epochs} "
        f"--device={device} "
        f"--eval_interval=5 "
        f"--energy_weight=1.0 "
        f"--forces_weight=10.0"
    )
    return cmd


def generate_deepmd_input(
    type_map: List[str],
    rcut: float = 6.0,
    n_neurons: List[int] = (25, 50, 100),
    learning_rate_start: float = 0.001,
    learning_rate_stop: float = 3.5e-8,
) -> Dict[str, Any]:
    """Generate DeepMD-kit JSON parameter dict.

    Refactored from cp2kMD.DeepMD_train.
    
    Status: Pending/WIP - Ready for custom descriptor extension.
    """
    config = {
        "model": {
            "type_map": type_map,
            "descriptor": {
                "type": "se_e2_a",
                "sel": "auto",
                "rcut_smth": 0.5,
                "rcut": rcut,
                "neuron": list(n_neurons),
                "resnet_dt": False,
                "axis_neuron": 4,
                "seed": 1,
            },
            "fitting_net": {
                "neuron": [240, 240, 240],
                "resnet_dt": True,
                "seed": 1,
            },
        },
        "learning_rate": {
            "type": "exp",
            "decay_steps": 5000,
            "start_lr": learning_rate_start,
            "stop_lr": learning_rate_stop,
        },
        "loss": {
            "type": "ener",
            "start_pref_e": 0.02,
            "limit_pref_e": 1.0,
            "start_pref_f": 1000,
            "limit_pref_f": 1.0,
            "start_pref_v": 0.0,
            "limit_pref_v": 0.0,
        },
    }
    return config

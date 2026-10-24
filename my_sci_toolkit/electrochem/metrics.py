"""Electrochemical mass and molar metric transformations."""

def active_material_moles(
    mass_active_g: float,
    molecular_weight_g_mol: float,
) -> float:
    """Calculate moles of active electrode material (e.g. NCM cathode)."""
    if molecular_weight_g_mol <= 0:
        raise ValueError("Molecular weight must be positive.")
    return mass_active_g / molecular_weight_g_mol


def theoretical_specific_capacity(
    n_electrons: int,
    molecular_weight_g_mol: float,
) -> float:
    """Calculate theoretical specific capacity (mAh/g): Q_theo = (n * F) / (3.6 * Mw)."""
    faraday_const = 96485.332  # C / mol
    c_per_g = (n_electrons * faraday_const) / molecular_weight_g_mol
    return c_per_g / 3.6  # mAh / g

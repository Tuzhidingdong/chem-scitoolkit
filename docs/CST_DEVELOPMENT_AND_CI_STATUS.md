# CST development and CI validation status

**Base:** `main` at `87a061b309bbb9fdf4461d2d1d2873dbfd8681fb`  
**Development branch:** `dft-finite-cluster-production-interfaces`  
**Code-validation head:** `55ccd8acc734f9013b20cd7e91f4d1fe57629d0a`  
**Draft PR:** https://github.com/Tuzhidingdong/chem-scitoolkit/pull/1

## Feature mapping

| ID | Scope | Branch implementation |
|---|---|---|
| CST-1 | Finite-system CP2K builder | Additive `CP2KInputBuilder.build_finite_system`: explicit KIND-specific basis/potential, charge/multiplicity/parity, cell and Poisson periodicity, triclinic cell geometry, SCF method, optional smearing/mixing/dispersion/print sections. Legacy builder entry points remain unchanged. |
| CST-2 | Task-aware output validation | Checks normal termination, SCF convergence, energy, requested force evidence and GEO_OPT completion independently of scheduler state; adds an optional `cp2klint` input wrapper. |
| CST-3 | Bader versus Hirshfeld | New true-Bader result validation checks atom identity/order and population residual; calibrated Hirshfeld results have a distinct approximate API. The old function remains for compatibility with a deprecation warning. |
| CST-4 | PDOS normalization | Optional `cp2k-output-tools` adapter preserves projection/spin/source-hash metadata and energy-axis/alignment metadata; vacuum alignment fails closed without an explicit validated plateau. |
| CST-5 | Cube and vacuum analysis | Single-field cube reader; subtraction checks grid dimensions, origin, voxel vectors and atom mapping; vacuum plateau/reference checks require explicit potential quantity and reference zero. |
| CST-6 | Thermochemistry | Thin optional ASE HarmonicThermo wrapper requires explicit mode scope, temperature and imaginary-mode policy. |
| CST-7 | Figure profiles | Explicit profile API for typography, palette, dimensions, panel labels and raster/vector export; existing defaults are unchanged unless called. |

No project-specific chemical system or parameter set was added as a generic Skill default.

## Commits

- `fe03a6f5874292a897fd3064b236545e2e1e6c2b` — finite-system builder.
- `872c3b5726d554f61fb3512638cc663ca95fb4c6` — task-aware DFT post-processing adapters.
- `ff43092c51851e78d2e8f8d68d17871785680365` — charge, PDOS, cube, thermochemistry and figure profile exports.
- `4deb7ef439fbd0e1c0547dd041ca13d405b531bc` — explicit SCF subsection activation.
- `21a9270a332c64fc285d29a98075c0ad22986456` — synthetic tests and wrapper exports.
- `55ccd8acc734f9013b20cd7e91f4d1fe57629d0a` — triclinic cell geometry/centering validation and GEO_OPT gate refinement.

## Actions validation

Existing workflow: `.github/workflows/ci.yml`  
Command: `pip install -e ".[dev]"`, followed by `pytest tests/ -v`.

Draft PR validation run for code head `55ccd8acc734f9013b20cd7e91f4d1fe57629d0a`:
https://github.com/Tuzhidingdong/chem-scitoolkit/actions/runs/45924547038

| Runner | Result |
|---|---|
| Python 3.10 | Success — 25 passed, 1 skipped |
| Python 3.11 | Success — 25 passed, 1 skipped |
| Python 3.12 | Success — 25 passed, 1 skipped |

The skipped test covers the optional ASE runtime because ASE is not installed by the existing `.[dev]` CI extra. The tests for the explicit ASE scope validation and optional dependency handling passed; actual numerical ASE thermochemistry was not executed. Optional CP2K input/PDOS CLI tools were not installed in this CI run. No CP2K calculation was run.

## Remaining validation limits

- The optional `cp2klint`, `cp2k_pdos` and ASE integration paths need a separate opt-in integration environment and representative CP2K fixtures.
- No production CP2K calculation, external DFT program or Slurm job was launched.
- This Draft PR remains open and unmerged.

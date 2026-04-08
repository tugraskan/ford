# Fortran Documentation Campaign Style Guide

This guide defines the canonical documentation format for `.f90` updates done in batches.

## 1) PURPOSE block placement
Place the purpose block immediately below each routine declaration.

```fortran
subroutine routine_name(...)

!!    ~ ~ ~ PURPOSE ~ ~ ~
!!    one or more lines describing what the routine does,
!!    when it is called, and key assumptions/dependencies.
```

Do this for:
- `subroutine`
- `function`

## 2) Variable comment format
For declaration comments, use:

```fortran
real :: q_cell = 0.        !! [m3/day] groundwater flow rate between connected cells
integer :: end_yr = 0      !! [flag] end-of-year indicator (1=yes)
character(len=256) :: p    !! [path] resolved output directory path
```

Rules:
- Prefer `!! [units] description`.
- If unitless, use `[unitless]`.
- If not applicable/unknown, use `[n/a]`.
- Keep existing accurate descriptions; only rewrite if inaccurate or inconsistent.
- When declaration comments use single-bang style (`!`), convert them to documentation style (`!!`) in touched code.

## 2b) Type and derived-type member documentation
Yes—documenting derived types and their members is standard practice for this campaign.

Apply the same declaration comment format to:
- `type :: ...` / `type, extends(...) :: ...` definitions (type-level summary),
- member declarations inside `type` blocks.

Example:
```fortran
type :: groundwater_state
  !! [n/a] state variables for one groundwater cell
  real :: head = 0.      !! [m] current groundwater head
  real :: stor = 0.      !! [m3] available groundwater storage
end type groundwater_state
```

## 3) No-guessing rule
Do not invent meaning/units.
Derive from:
1. declaration context,
2. usage context in equations/calls,
3. output label/header text when available.

If uncertain, use conservative wording and `[n/a]` or `[unitless]`.

## 4) Change scope rules
- Documentation/comments only unless explicitly requested otherwise.
- No numerical/logic/control-flow changes.
- Keep whitespace churn minimal.

## 5) Commit discipline
- One batch per commit.
- Commit message format:
  - `docs(batch-XX): normalize purpose + variable docs for <family>`
- Include brief batch scope in commit body if needed.

## 6) Per-batch checklist
Before commit:
- PURPOSE block exists for touched routines and is in correct location.
- Variable comments in touched declarations follow canonical format.
- Single-bang declaration comments (`!`) are converted to `!!` in touched code.
- Type and derived-type members in touched code are documented using `!!` format.
- Legacy intro/purpose variants removed in touched files.
- No logic changes.


## 7) Batch construction policy
- Modules-first ordering: process module-anchored batches before fallback batches.
- Target at most 12 files per batch.
- Prefer one module anchor per batch chunk; include directly related users from `use <module>` where feasible.

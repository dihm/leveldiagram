Changelog
=========

v0.3.1
------

Improvements
++++++++++++

- Remove implicit assumption in `LD` that graph node keys must be integers or floats

v0.3.0
------

Improvements
++++++++++++

- Many improvements for releasing, docs, and linting workflows

v0.2.0
------

Improvements
++++++++++++

- All coupling types are now available in :class:`Coupling`
- Added option for circular coupling paths, set by a deflection parameter
- Added many options to :class:`LD` for working with graphs from other projects
  
  - Can now specify all leveldiagram control parameters under a single key `ld_kw`.
    This helps avoid key naming conflicts between projects.
  - Wavy and deflected couplings are enabled via `'wavy'` and `'deflect'` boolean control parameters
  - Individual couplings can be ignored by setting `'hidden'` to `True`
  - Start and stop anchors can be specified independently for couplings

Bug Fixes
+++++++++

- Fixed definition when using custom anchor positions

Deprecations
++++++++++++

- `WavyCoupling` is no longer used. Use :class:`Coupling` with `waveamp` and `halfperiod` parameters defined.


v0.1.1
------

Improvements
++++++++++++

- Add and about function for easy tracking of imrprovements in example notebooks

Bug Fixes
+++++++++

- Fixed issue where level labels near the axes edge would get clipped

Deprecations
++++++++++++

- Updated some default plotting values

v0.1.0
------

Initial release.

Includes the artist primitives `EnergyLevel`, `Coupling`, and `WavyCoupling`.
Also includes the base leveldiagram creation class `LD`.
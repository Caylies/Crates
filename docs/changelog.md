# Changelog

Crates changes will be documented on this page.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added

- Custom pools can now be created and existing pools are configurable.
- Added `Amount min` and `Amount max` fields to configure how many crates a pool can grant.
- Added a `Conditions` field for controlling who can claim from a pool, using an advanced condition builder.
- Added `Server`, `User`, `Ball completion percentage`, and `Ball count` condition rules for pools.
- Pool commands are now registered dynamically from each pool's `command_name` and `command_description` fields.
- Added the `reloadcrates` text command to re-sync pool commands after adding, renaming, or removing a pool.
- Added a view for claiming crates from a pool.
- Added documentation for how pools work.
- Added emoji support for crates.
- Added a `rarity` field to crates, used to weight which crate is granted when a pool has multiple.
- Added an `amount` parameter to `/crates admin give` for giving multiple crates at once.
- Added a background image to the Crates website homepage. 

### Changed

- Reorganized the crate admin form into sections.
- The `openable` field for crates can now be edited directly from the admin crate list.
- Revamped the Crates website colors.
- Slightly modified Crates' logo colors.
- Improved changelog formatting.
- Improved documentation.

### Fixed

- Fixed light mode website colors.

### Removed

- Removed the `claim message` setting.

---

## [0.1.1] <small>- 2026-09-12</small>

### Added

- Added an `openable` field to crates, allowing crates to be configured as openable or non-openable.

### Changed

- Improved README file layout.

### Fixed

- Fixed crate open validation.

---

## [0.1.0] <small>- 2026-09-07</small>

- Initial Crates release.


[Unreleased]: https://github.com/Caylies/Crates/compare/0.1.1...HEAD
[0.1.1]: https://github.com/Caylies/Crates/compare/0.1.0...0.1.1
[0.1.0]: https://github.com/Caylies/Crates/releases/tag/0.1.0

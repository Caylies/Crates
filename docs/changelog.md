# Changelog

Crates changes will be documented on this page.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **Custom pool instances:**
    - Added `Amount min` and `Amount max` fields to configure the number of crates a pool can grant.
    - Added a `Conditions` field for controlling which players can claim from a pool using an advanced builder widget.
    - Added `Server`, `User`, `Ball completion percentage`, and `Ball count` rules for pool conditions.
    - Pool commands are now registered dynamically using the `command_name` and `command_description` fields.
    - Added the `reloadcrates` text command for synchronizing pool commands.
- Added a new pool claiming view rather than using a claim message.
- Added documentation for pools.

### Removed

- Removed the `claim message` setting.

## [0.1.1] - 2026-09-12

### Added

- Added an `openable` field to crates, allowing crates to be configured as openable or non-openable.

### Fixed

- Fixed crate open validation.

### Changed

- Improved README file layout.

## [0.1.0] - 2026-09-07

- Initial Crates release.

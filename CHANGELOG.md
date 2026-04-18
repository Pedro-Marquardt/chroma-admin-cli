# Changelog

All notable changes to this project will be documented in this file.

## [0.2.1] - 2026-04-18
### Fixed
- Unicode normalization in metadata filtering: filtering by metadata values now works regardless of composed/decomposed accents (e.g., "lógica" vs "lógica").

## [0.2.0] - 2026-04-18
### Added
- New `filter-chunks` command: interactively filter and navigate chunks of a collection by metadata key/value, with support for tenant and database selection.

### Fixed
- Unicode normalization in metadata filtering: now you can filter by metadata values regardless of composed/decomposed accents (e.g., "lógica" vs "lógica").

### Changed
- All CLI messages, help, and documentation are now in English.

## [0.1.2] - 2026-03-10
### Added
- Initial public release.

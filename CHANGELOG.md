# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),

## [unreleased]

### Added
- Add an optional full index (all files in all commits in all branches).
- Add globbing to the sparse mode configuration.
- Add numerous libraries.

### Changed
- Database schema: rename and reorder columns.
- The sparse index now considers all branches, not just HEAD.
- The GitHub workflow now generates both the sparse and the full index.
- Update metric.py to decrease the bias for old files.

### Deprecated

### Removed
- Remove .xz from GitHub workflow to save space.

### Fixed

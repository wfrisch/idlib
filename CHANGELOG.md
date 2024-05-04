# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),

## [unreleased]

### Added
- Full index (all files in all commits in all branches).

### Changed
- Database schema: columns renamed and reordered.
- The sparse index now considers all branches, not just HEAD.
- The GitHub workflow now generates both the sparse and the full index.

### Deprecated

### Removed
- Remove .xz from GitHub workflow to save space.

### Fixed

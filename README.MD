# KubeChaos

[![CI](https://github.com/shrutistyanlik/kubechaos/actions/workflows/ci.yml/badge.svg)](https://github.com/shrutistyanlik/kubechaos/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A CLI chaos engineering toolkit for Kubernetes. Inject controlled failures into your cluster to test resilience, validate self-healing, and build confidence in your infrastructure.

## Why Chaos Engineering?

Production systems fail in unexpected ways. Chaos engineering helps you discover weaknesses **before** they become incidents. KubeChaos lets you:

- Verify pods restart after being killed
- Test service discovery when labels change
- Validate monitoring and alerting catches failures
- Build runbooks based on real failure scenarios

## Features

- **Pod Kill** — Delete random or specific pods to test self-healing
- **Label Scramble** — Modify pod labels to test service discovery and selectors
- **Health Snapshots** — Capture namespace state before and after experiments
- **Safety First** — Protected namespace blocking, dry-run mode, and force override
- **Rich CLI Output** — Color-coded terminal output for clear experiment feedback

## Installation

```bash
pip install -e .
```

For development:

```bash
pip install -e ".[dev]"
```

## Quick Start

```bash
# Check namespace health
kubechaos health -n my-app

# Preview a pod kill (dry run)
kubechaos kill -n my-app --dry-run

# Kill a random pod
kubechaos kill -n my-app

# Kill a specific pod
kubechaos kill -n my-app --pod my-pod-abc123

# Scramble pod labels (dry run)
kubechaos scramble -n my-app --dry-run

# Override namespace protection (use with caution)
kubechaos kill -n kube-system --force
```

## Safety

KubeChaos is built with safety as a core principle:

| Feature | Description |
|---------|-------------|
| **Protected Namespaces** | `kube-system`, `kube-public`, and `default` are blocked by default |
| **Dry Run** | Preview any experiment with `--dry-run` before executing |
| **Force Override** | Use `--force` to override protection (requires explicit intent) |
| **Health Snapshots** | Capture pod state before chaos to compare after |

## Architecture

```
kubechaos/
├── cli.py        # Click-based CLI — entry point and command definitions
├── chaos.py      # Core chaos experiments — pod kill, label scramble
├── safety.py     # Safety layer — namespace protection, health snapshots
└── __init__.py
```

**Design principle:** Every chaos function calls `pre_chaos_check()` before executing. Safety is not optional — it's built into the call chain.

## Development

```bash
# Install dev dependencies
make install

# Format code
make format

# Run linter
make lint

# Run tests
make test

# Run all checks (same as CI)
make check
```

## Tech Stack

- **Python 3.10+** — CLI and core logic
- **Kubernetes Python Client** — Cluster API interaction
- **Click** — CLI framework
- **Rich** — Terminal formatting
- **pytest** — Testing with mocked K8s API
- **GitHub Actions** — CI pipeline (lint, format, test on Python 3.10 + 3.12)

## Roadmap

- [ ] Network delay simulation (pod network chaos)
- [ ] Resource stress testing (CPU/memory limits)
- [ ] Experiment reports (before/after comparison)
- [ ] YAML-based experiment definitions
- [ ] Helm chart for running as a CronJob in-cluster

## License

MIT

## Overview

This repository powers a modular homelab environment built around multi-node Docker orchestration. It supports both standalone container management and Docker Swarm deployments, with a focus on clarity, control, and operational hygiene.

The tooling here enables:

- Per-node container lifecycle management
- Swarm-aware orchestration and role assignment
- VLAN-mapped networking and IP discipline
- Environment-driven configuration and audit tagging

At the heart of this system is the **LuxForge** interface—a branded CLI toolkit that provides expressive menu-driven control, lore-aligned automation, and artifact-grade logging. While currently embedded in this repo, LuxForge may evolve into its own standalone module as its scope expands.

This project is designed for homelab operators who value modular clarity, signature-grade interfaces, and disciplined infrastructure workflows.

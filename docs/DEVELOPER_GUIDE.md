# VESPERA OS Developer Guide

This guide describes how to extend VESPERA OS capabilities by developing custom skills.

## Adding a Custom Skill

1. Skills are placed in the `packages/umbracore/skills/` directory.
2. Each skill must be a standalone python function decorated with the skills registry.
3. Test your skills using `npm run dev:electron` locally in the workspace.

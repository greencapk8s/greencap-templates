# greencap-templates

Official catalog of Templates consumed by the **Templates Catalog** view in [GreenCap K8s](https://github.com/greencapk8s/greencap-k8s). A Template is a complete study application (Kubernetes resources, and optionally source code to be built) that GreenCap can deploy into a Cluster in one click.

This repo is fetched by GreenCap over plain HTTP (`raw.githubusercontent.com`) — every referenced file must be reachable as raw content on the default branch. See `README.md` for the repository layout, `catalog.json`/`template.yaml` formats, and conventions for adding new Templates.

## Agent skills

### Issue tracker

Issues live as GitHub issues in `greencapk8s/greencap-templates` (via the `gh` CLI). See `docs/agents/issue-tracker.md`.

### Triage labels

Canonical default labels from mattpocock/skills. See `docs/agents/triage-labels.md`.

### Domain docs

Single-context: `CONTEXT.md` at the root + `docs/adr/` (created lazily by `/grill-with-docs`). See `docs/agents/domain.md`.

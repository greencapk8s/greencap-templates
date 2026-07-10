# greencap-templates

Official catalog of Templates consumed by the Samples Catalog view in [GreenCap K8s](https://github.com/greencapk8s/greencap-k8s), under Developer Experience. A Template is a complete study application (Kubernetes resources, and optionally source code to be built) that GreenCap can deploy into a Cluster in one click.

This repository is fetched by GreenCap over plain HTTP (`raw.githubusercontent.com`) — there is no Git client involved on the GreenCap side, so every file referenced below must be reachable as raw content on the default branch.

## Repository layout

```
catalog.json                  # index of every Template (read by the Samples Catalog list view)
<template-id>/
  template.yaml                # manifest for this Template (read when a user opens/deploys it)
  <resource files>.yaml         # Kubernetes resources, applied in the order listed in template.yaml
  <build context dir>/          # source + Dockerfile, only if the Template declares a "builds" entry
```

## `catalog.json`

A JSON array. Each entry:

| Field | Description |
|---|---|
| `id` | Unique identifier, matches the Template's directory name |
| `title` | Card title in the Samples Catalog |
| `description` | Card description |
| `technologies` | List of technology badges shown on the card |
| `path` | Directory (relative to the repository root) containing `template.yaml` |
| `namespace` | Fixed name of the Namespace this Template creates — used by GreenCap to detect whether the Template is already Installed in a Cluster |

## `template.yaml`

```yaml
resources:
  - namespace.yaml
  - postgres.yaml
  - backend.yaml
  - ingress.yaml
builds:
  - name: backend
    contextPath: app
    dockerfilePath: Dockerfile
    image: crud-flask-postgres/backend
```

- `resources`: files applied in order, relative to the Template's directory. One of them must define the Namespace named in `catalog.json`, and it must come first — everything else in the Template lives inside it.
- `builds` (optional): components without a ready-made public image. GreenCap builds each one via Kaniko, using this repository as Git context, and pushes to the target Cluster's internal Registry — never to an external registry. `contextPath` is relative to the Template's directory; `dockerfilePath` is relative to `contextPath` itself (Kaniko resolves the Dockerfile from the build context, not from the repository root) — leave it as just `Dockerfile` unless the file lives in a subdirectory of the build context. In the resource file that uses the built image, set the container's `image` field to the sentinel `__BUILD__<name>` (matching the `name` in this list); GreenCap substitutes it with the real pushed reference before applying that file.

See ADR 0015 in `greencap-k8s` (`docs/adr/0015-sample-catalog-templates-via-indice-raw-http.md`) for the reasoning behind this format.

## Conventions for new Templates

- Keep every resource inside the Template's own Namespace — GreenCap deploys Templates without touching the user's active Namespace.
- Prefer public, pinned images (`postgres:16-alpine`, not `postgres:latest`) for components that don't need a `builds` entry.
- If the app is reachable over HTTP, include an Ingress with a fixed host `<template-id>.greencap.local`, so a successful deploy is immediately visible in a browser.
- A deploy aborts on the first conflict (a resource that already exists) with no automatic rollback — design resource names so a second deploy attempt fails clearly rather than partially overwriting the first.

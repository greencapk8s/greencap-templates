---
name: create-template
description: Guides the user through authoring a new Template for this catalog — from sharpening the idea with grill-with-docs, through scaffolding the directory, template.yaml, Kubernetes Resources and optional build context, to registering it in catalog.json. Use when the user wants to create, add, or scaffold a new Template (study application) in this repo.
---

# create-template

Author a new **Template** for the GreenCap Templates Catalog. A Template is a complete study application that GreenCap deploys into a Cluster in one click. Every Template is self-contained, lives in its own top-level directory, and confines all its Resources to a single Namespace.

Read `CONTEXT.md` for the vocabulary (Template, Catalog, Manifest, Resource, Build, Image sentinel, …) and `README.md` for the authoritative file formats before starting. Use existing Templates (`crud-flask-postgres`, `crud-flask-mongodb`, `cache-aside-flask-postgres-redis`) as reference implementations — mirror their structure rather than inventing a new one.

This is a prompt-driven skill, not a script. Grill first, confirm, then write.

## Step 1 — Sharpen the idea with grill-with-docs

A Template exists to **teach one thing** (a pattern, a component relationship, a datastore). Before writing any file, run the **`grill-with-docs`** skill to pin down:

- **What it teaches** — the single pedagogical goal, in one sentence. If it overlaps an existing Template, what's the meaningful difference?
- **Components** — which stateless/stateful pieces it needs, and whether each has a pinned public image or must be built from source.
- **Naming** — resolve any new domain vocabulary against `CONTEXT.md`. If the Template introduces a term the glossary doesn't have (e.g. a new pattern name), grill-with-docs updates `CONTEXT.md` inline. Don't drift to synonyms the glossary lists under `_Avoid_`.

Carry the resolved decisions into the next steps. Don't scaffold until the goal and components are settled.

## Step 2 — Fix the identity

Decide and confirm with the user:

- **`id`** — kebab-case, unique. It is used verbatim three times: the directory name, the `id` in `catalog.json`, and the Namespace name. These three MUST match.
- **`title`** — the card title (e.g. "Cache-aside in Python (Flask) + PostgreSQL + Redis").
- **`description`** — one card paragraph: what it is and what it's a good starting point to study.
- **`technologies`** — badge strings shown on the card (e.g. `["Python", "Flask", "PostgreSQL"]`). Display only.

## Step 3 — Plan the Resources

List the Resource files in apply order. Rules (see `README.md`):

- Resource files live under the Template's **`infra/` directory**, referenced from `resources` as `infra/<file>.yaml`.
- The **Namespace Resource comes first** — everything else lives inside it. Its `name` equals the `id`.
- Every other Resource sets `namespace: <id>` and never touches the user's active Namespace.
- Prefer **public, pinned images** (`postgres:16-alpine`, not `postgres:latest`) for anything that doesn't need a Build.
- If the app is reachable over HTTP, include an **Ingress** with a fixed host `<id>.greencap.local`.
- Design Resource names so a second Deploy attempt fails clearly on conflict rather than partially overwriting — a Deploy aborts on the first existing Resource with no rollback.
- Label every Resource for Topology grouping in GreenCap:
  ```yaml
  labels:
    app.kubernetes.io/part-of: <id>
    app.kubernetes.io/component: <component>   # e.g. backend, postgres, redis
  ```
  On Deployments, also put these labels on the pod template, alongside the existing `app: <component>` selector label.

## Step 4 — Plan Builds (only if a component has no public image)

For each component built from source, add a `builds` entry to `template.yaml`:

```yaml
builds:
  - name: backend
    contextPath: app          # dir relative to the Template's directory
    dockerfilePath: Dockerfile # relative to contextPath itself, not the repo root
    image: <id>/backend
```

Then:

- Put the source + `Dockerfile` under `contextPath` (conventionally `app/`).
- In the Resource that runs it, set the container `image` to the **Image sentinel** `__BUILD__<name>`, matching the Build's `name` exactly (e.g. `__BUILD__backend`). GreenCap builds it with Kaniko and substitutes the real pushed reference before applying.

Leave `dockerfilePath` as bare `Dockerfile` unless it lives in a subdirectory of the build context.

## Step 5 — Write the files

Create `<id>/` and, inside it:

1. `template.yaml` — `resources` in apply order (Namespace first, each path as `infra/<file>.yaml`) and optional `builds`.
2. `infra/` holding each Resource `.yaml` file.
3. The build context directory (source + `Dockerfile`) for any Build.

Then add the Template's entry to the `catalog.json` array at the repo root:

```json
{
  "id": "<id>",
  "title": "...",
  "description": "...",
  "technologies": ["..."],
  "path": "<id>",
  "namespace": "<id>"
}
```

## Step 6 — Validate before finishing

Check every invariant:

- [ ] `id` == directory name == `catalog.json` `id`/`path`/`namespace` == Namespace Resource `name`.
- [ ] The Namespace Resource is listed **first** in `template.yaml` `resources`.
- [ ] Every non-Namespace Resource sets `namespace: <id>`.
- [ ] Every file under `resources` and every `contextPath`/`dockerfilePath` actually exists.
- [ ] Each `__BUILD__<name>` sentinel matches a `builds[].name`; each `builds[].name` is referenced by a sentinel.
- [ ] Ingress host is `<id>.greencap.local` (if the app is HTTP-reachable).
- [ ] Every Resource carries the `app.kubernetes.io/part-of` and `app.kubernetes.io/component` labels.
- [ ] `catalog.json` is still valid JSON.

Because GreenCap fetches this repo as raw HTTP on the default branch, remind the user that the Template only becomes deployable once these files are committed and pushed.

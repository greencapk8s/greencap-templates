# greencap-templates

The official catalog of Templates that GreenCap K8s can deploy into a Cluster in one click. This repo holds no application runtime of its own — it is a set of manifests and build contexts fetched by GreenCap over raw HTTP (`raw.githubusercontent.com`), so every referenced file must be reachable as raw content on the default branch.

## Language

### Catalog structure

**Template**:
A complete study application that GreenCap can deploy into a Cluster in one click. Lives in its own top-level directory (named after its `id`) and is fully self-contained: a `template.yaml` manifest plus the Kubernetes Resources it applies, and optionally source to be built. Every Template creates and stays inside a single Namespace.
_Avoid_: Sample, example, app, chart, project

**Catalog**:
The `catalog.json` index at the repo root — a JSON array with one entry per Template, read by the Templates Catalog list view to render cards. The entry carries `id`, `title`, `description`, `technologies`, `path`, and `namespace`. The `id` matches the Template's directory name; the `namespace` matches the Namespace the Template creates.
_Avoid_: Index, registry, list, manifest

**Manifest**:
A Template's `template.yaml` — read when a user opens or deploys the Template. Declares `resources` (the ordered list of Resource files) and optionally `builds`. Distinct from a Kubernetes manifest, which is any individual Resource file.
_Avoid_: Config, spec, descriptor

**Resource**:
A single Kubernetes object file listed under `resources` in the Manifest, applied in the order given. Resources live under the Template's `infra/` directory, and paths are relative to the Template's directory (e.g. `infra/namespace.yaml`). Exactly one Resource must define the Template's Namespace, and it must come first — everything else lives inside it.
_Avoid_: Object, asset, file

**Namespace**:
The single Kubernetes Namespace a Template creates and confines all its Resources to. Its fixed name is declared in both the Catalog entry (`namespace`) and the Template's first Resource. GreenCap uses this name to detect whether a Template is already Installed in a Cluster, and never touches the user's active Namespace when deploying.
_Avoid_: Environment, project, scope

**Technology**:
A badge string in the Catalog entry's `technologies` array (e.g. `Python`, `Flask`, `PostgreSQL`), shown on the Template's card. Display metadata only — it does not affect deployment.
_Avoid_: Tag, stack, label

### Building & deployment

**Build**:
An entry under `builds` in the Manifest, declaring a component that has no ready-made public image and must be built from source. Each Build names a `contextPath`, a `dockerfilePath`, and a logical `name`. Templates without a Build use only public, pinned images.
_Avoid_: Compile, package, bake

**Build context**:
The directory a Build is built from, given by `contextPath` relative to the Template's directory. `dockerfilePath` is resolved relative to the Build context itself (not the repo root) — left as bare `Dockerfile` unless the Dockerfile sits in a subdirectory of the context.
_Avoid_: Source dir, workdir, root

**Kaniko**:
The in-cluster tool GreenCap uses to build each Build, using this repository as Git context. It pushes the resulting image to the target Cluster's internal Registry — never to an external registry.
_Avoid_: Docker build, builder

**Registry**:
The target Cluster's internal image Registry, the only place built images are pushed. External registries are never a push target for a Build.
_Avoid_: Repository, image store, hub

**Image sentinel**:
The placeholder `__BUILD__<name>` written into a Resource's container `image` field, matching a Build's `name`. GreenCap substitutes it with the real pushed image reference before applying that Resource.
_Avoid_: Placeholder tag, image ref, template variable

**Deploy**:
The one-click action, initiated from GreenCap, that applies a Template's Resources in order into a fresh Namespace. A Deploy aborts on the first conflict (a Resource that already exists) with no automatic rollback — Resource names are chosen so a second attempt fails clearly rather than partially overwriting the first.
_Avoid_: Install (as a verb), apply, provision, launch

**Installed**:
The state of a Template whose Namespace already exists in a Cluster. GreenCap derives this by checking for the Template's declared `namespace`, and uses it to distinguish Templates already present from those still deployable.
_Avoid_: Deployed, running, active

**Templates Catalog**:
The consuming view inside GreenCap K8s (under Developer Experience) that lists Templates from the Catalog and deploys them. This repo is its data source; it is not part of this repo.
_Avoid_: Samples Catalog, Sample Catalog, marketplace, store

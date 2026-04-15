# internal-service — Helm-based GitOps-Friendly Deployment

> **Recruitment task for NXLog.**
> The application is deployed and publicly available at:
> - **dev:** https://dev-nxlog.darekjatkowski.com
> - **prod:** https://prod-nxlog.darekjatkowski.com

A containerized Python web application with a Helm chart designed for internal services.
The chart abstracts Kubernetes complexity and supports GitOps workflows with clear `dev` / `prod` separation.

## Repository structure

```
.
├── app/
│   ├── main.py          # Python HTTP server (stdlib only)
│   └── Dockerfile
├── charts/
│   └── internal-service/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
├── gitops/
│   ├── base/
│   │   ├── kustomization.yaml
│   │   └── manifests.yaml   # rendered Helm output (committed to git)
│   └── overlays/
│       ├── dev/
│       │   ├── kustomization.yaml
│       │   └── patch-env.yaml   # sets PROD=false
│       └── prod/
│           ├── kustomization.yaml
│           └── patch-env.yaml   # sets PROD=true
└── scripts/
    └── render.sh        # regenerates gitops/base/manifests.yaml
```

## Application

The app serves on port **8080** and exposes all environment variables as JSON.

| Endpoint       | Description                          |
|----------------|--------------------------------------|
| `GET /`        | All environment variables as JSON    |
| `GET /healthz` | Health check — returns `ok`          |

### Docker image

The image is publicly available on GitHub Container Registry:

```
docker pull ghcr.io/djatkowski/nxlog-demo:latest
```

Run locally:

```bash
docker run --rm -p 8080:8080 ghcr.io/djatkowski/nxlog-demo:latest
curl http://localhost:8080/
```

---

## Prerequisites

| Tool | Version |
|------|---------|
| [kind](https://kind.sigs.k8s.io/) | v0.20+ |
| [kubectl](https://kubernetes.io/docs/tasks/tools/) | v1.28+ |
| [helm](https://helm.sh/docs/intro/install/) | v3.14+ |
| [kustomize](https://kubectl.docs.kubernetes.io/installation/kustomize/) | v5+ (or `kubectl apply -k`) |

---

## Quick start — kind

### 1. Create a local cluster

```bash
kind create cluster --name internal-service
```

### 2. (Optional) Build and load the image without a registry

```bash
docker build -t ghcr.io/djatkowski/nxlog-demo:latest app/
kind load docker-image ghcr.io/djatkowski/nxlog-demo:latest --name internal-service
```

### 3a. Deploy with Helm directly

**dev** (PROD=false):

```bash
kubectl create namespace dev
helm upgrade --install internal-service charts/internal-service \
  --namespace dev \
  --set prod=false
```

**prod** (PROD=true):

```bash
kubectl create namespace prod
helm upgrade --install internal-service charts/internal-service \
  --namespace prod \
  --set prod=true
```

### 3b. Deploy with Kustomize (GitOps)

**dev**:

```bash
kubectl create namespace dev
kubectl apply -k gitops/overlays/dev
```

**prod**:

```bash
kubectl create namespace prod
kubectl apply -k gitops/overlays/prod
```

### 4. Verify

```bash
kubectl -n dev get pods
kubectl -n dev port-forward svc/internal-service 8080:8080
curl http://localhost:8080/
```

---

## Helm chart values

| Key | Default | Description |
|-----|---------|-------------|
| `hub` | `ghcr.io` | Registry hostname |
| `image` | `djatkowski/nxlog-demo` | Image name |
| `tag` | `latest` | Image tag |
| `prod` | `false` | Sets the `PROD` env var inside the container (`true` / `false`) |
| `env` | `{}` | Additional environment variables |
| `resources.requests.cpu` | `100m` | CPU request |
| `resources.requests.memory` | `64Mi` | Memory request |
| `resources.limits.cpu` | `500m` | CPU limit |
| `resources.limits.memory` | `128Mi` | Memory limit |
| `autoscaling.minReplicas` | `3` | Minimum number of pods |
| `autoscaling.maxReplicas` | `10` | Maximum number of pods |

Example with extra env vars:

```bash
helm upgrade --install internal-service charts/internal-service \
  --namespace dev \
  --set prod=false \
  --set env.LOG_LEVEL=debug \
  --set env.FEATURE_X=enabled
```

---

## GitOps workflow — re-rendering manifests

When the chart or values change, regenerate the base manifests and commit them:

```bash
./scripts/render.sh --set tag=1.2.3
git add gitops/base/manifests.yaml
git commit -m "chore: update rendered manifests to 1.2.3"
```

The overlays (`dev` / `prod`) patch only the `PROD` environment variable on top of the shared base.

---

## Security defaults

The following are hardcoded in the chart templates and cannot be weakened via values:

- `runAsNonRoot: true` — container runs as UID 65534
- `readOnlyRootFilesystem: true` — no writes to the container filesystem
- `allowPrivilegeEscalation: false`
- `capabilities.drop: [ALL]`
- `seccompProfile: RuntimeDefault`
- `automountServiceAccountToken: false`

---

## Clean up

```bash
kind delete cluster --name internal-service
```

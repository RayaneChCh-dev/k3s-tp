# devops-tp-rayane

TP DevOps — application full stack conteneurisée, orchestrée avec Docker Compose,
déployée sur un cluster Kubernetes (k3s) sur une VM Azure via un pipeline CI/CD
GitHub Actions.

## Stack technique

| Couche | Techno |
|---|---|
| Frontend | Nginx (HTML + JS vanille) servi en static + reverse proxy `/api` |
| Backend | Python 3.11 / Flask (API REST) |
| Base de données | PostgreSQL 15 (image Alpine) |
| Conteneurisation | Docker (multi-stage builds) |
| Orchestration locale | Docker Compose v2 |
| Orchestration cloud | Kubernetes via k3s (NodePort) |
| Cloud | Microsoft Azure (VM Ubuntu 22.04) |
| CI/CD | GitHub Actions |
| Registry | Docker Hub (`saphir10036/devops-tp-rayane-*`) |

## Architecture

```
                 ┌──────────────────────────────────────┐
 navigateur ───▶ │ VM Azure (74.161.44.42)              │
                 │                                      │
                 │  k3s cluster                         │
                 │  ┌────────────────────────────────┐  │
                 │  │ namespace: devops-tp-rayane    │  │
                 │  │                                │  │
                 │  │  frontend (NodePort 30080) ──▶ backend :5000 ──▶ db :5432
                 │  │                                │  │
                 │  │  Secret db-secret              │  │
                 │  └────────────────────────────────┘  │
                 └──────────────────────────────────────┘
```

## Endpoints exposés

| URL | Description |
|---|---|
| `GET /` | Page HTML (dashboard health + users) |
| `GET /api/health` | Liveness simple, `{"status":"ok"}` |
| `GET /api/ready` | Readiness (teste la connexion DB) |
| `GET /api/users` | Liste des utilisateurs en base |
| `GET /api/users/count` | Compteur d'utilisateurs |

En local :
- Frontend : http://localhost:8080
- Backend direct : http://localhost:5000/health

## Lancer en local (Docker Compose)

```bash
cp .env.example .env
docker compose up --build
```

Arrêter :

```bash
docker compose down -v
```

Lancer les tests (sans Docker) :

```bash
cd backend
pip install -r requirements.txt
pytest test_app.py -v
```

## Pipeline CI/CD

```
git push main
     │
     ▼
┌───────────────────────┐
│ 1. test               │ pytest du backend (3 tests) — échec = pipeline rouge
└──────────┬────────────┘
           ▼
┌───────────────────────┐
│ 2. build-and-push     │ docker buildx pour backend + frontend
│                       │ push sur Docker Hub (tags: :latest + :<sha>)
└──────────┬────────────┘
           ▼
┌───────────────────────┐
│ 3. deploy             │ SSH vers la VM Azure
│                       │ git pull + kubectl apply + kubectl set image
│                       │ kubectl rollout status (timeout 120s)
└───────────────────────┘
```

Contraintes respectées :
- Pipeline déclenché **automatiquement** à chaque push sur `main`
- Les tests **bloquent** le pipeline en cas d'échec (`needs: test`)
- Le déploiement est **entièrement automatique** (SSH + kubectl)
- Aucun secret n'est écrit dans le code (voir section Secrets)

## Variables d'environnement & secrets

### Local (Docker Compose)
`.env` (non commité, basé sur `.env.example`) :
```
DB_NAME=appdb
DB_USER=appuser
DB_PASSWORD=apppassword
```

### Kubernetes
Les credentials PostgreSQL sont injectés dans les pods via un `Secret`
(`k8s/secret.yml`) référencé avec `secretKeyRef`.

### GitHub Actions
Secrets à créer dans **Settings → Secrets → Actions** :

| Secret | Valeur |
|---|---|
| `DOCKER_USERNAME` | `saphir10036` |
| `DOCKER_PASSWORD` | Token Docker Hub |
| `VM_HOST` | `74.161.44.42` |
| `VM_USER` | `azureuser` |
| `VM_PASSWORD` | Mot de passe SSH de la VM |

## Déploiement Kubernetes (manuel, première fois sur la VM)

```bash
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/secret.yml
kubectl apply -f k8s/db-deployment.yml
kubectl apply -f k8s/backend-deployment.yml
kubectl apply -f k8s/frontend-deployment.yml
```

Application accessible sur `http://74.161.44.42:30080`.

Guide détaillé de la VM (install Docker + k3s) : [`docs/VM_SETUP.md`](docs/VM_SETUP.md)

## Structure du repo

```
.
├── backend/                   # API Flask + tests + Dockerfile multi-stage
│   ├── app.py
│   ├── init.sql
│   ├── requirements.txt
│   ├── test_app.py
│   ├── Dockerfile
│   └── .dockerignore
├── frontend/                  # Nginx + HTML + Dockerfile multi-stage
│   ├── index.html
│   ├── nginx.conf
│   └── Dockerfile
├── k8s/                       # Manifests Kubernetes
│   ├── namespace.yml
│   ├── secret.yml
│   ├── db-deployment.yml
│   ├── backend-deployment.yml
│   └── frontend-deployment.yml
├── .github/workflows/
│   └── ci-cd.yml              # Pipeline test → build → push → deploy
├── docs/
│   └── VM_SETUP.md
├── docker-compose.yml
├── .env.example
├── RAPPORT.md                 # Rapport de projet (trame pour Word + screenshots)
└── README.md
```

## Difficultés rencontrées

- **Accès NodePort avec Minikube** : Minikube n'expose pas directement le NodePort
  sur l'IP de la VM, ce qui forçait à utiliser `minikube tunnel` ou `socat`.
  **Résolu** en passant à **k3s**, qui expose les NodePorts nativement sur l'IP
  de l'hôte.
- **Ordre de démarrage DB → backend** : le backend tombait au démarrage car
  PostgreSQL n'était pas encore prêt. **Résolu** en Docker Compose avec
  `depends_on.condition: service_healthy`, et en Kubernetes via la
  `readinessProbe` du backend (pod non-ready tant que `/health` ne répond pas).
- **Gestion des secrets** : les credentials DB apparaissaient en dur dans les
  manifests. **Résolu** avec un `Secret` K8s + `secretKeyRef` côté pods, et une
  variable `DB_PASSWORD` jamais exposée dans le code Git.
- **Rolling update sans downtime** : avec 2 replicas backend, `RollingUpdate`
  garantit qu'une instance est toujours Ready. `kubectl rollout status` fait
  échouer le job CI si le rollout dépasse 120 s.

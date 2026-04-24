# Rapport de projet — TP DevOps

> **Ce fichier est la trame du rapport à rendre en Word (ou PDF).**
> Chaque `[📸 Screenshot N — description]` indique où coller la capture correspondante.
> La liste complète des 11 screenshots est en bas du document.

---

## 1. Contexte

Une entreprise souhaite automatiser le déploiement de son application web afin
de gagner du temps et d'éviter les erreurs humaines. L'objectif du TP est de
conteneuriser une application full stack, de l'orchestrer avec Docker Compose,
de la déployer sur un cluster Kubernetes installé sur une VM cloud, puis
d'automatiser le tout via un pipeline CI/CD.

**Application choisie :** mini dashboard de users en base, composé de :
- un **frontend** Nginx servant une page HTML statique (dashboard des endpoints),
- un **backend** Flask exposant 5 endpoints REST (`/health`, `/api/ready`,
  `/api/users`, `/api/users/count`),
- une base **PostgreSQL 15** avec une table `users` initialisée via un script
  `init.sql`.

Les trois services communiquent entre eux (frontend → backend via reverse
proxy Nginx, backend → db via le réseau interne).

---

## 2. Étape 1 — Conteneurisation avec Docker

### 2.1 Dockerfile backend (multi-stage)

Voir `backend/Dockerfile`. Stage builder = installation des deps pip dans
`/root/.local`, stage runtime = copie de ces deps + `app.py`, exposition du
port 5000, `HEALTHCHECK` intégré.

### 2.2 Dockerfile frontend (multi-stage)

Voir `frontend/Dockerfile`. Stage builder = préparation de l'index HTML,
stage runtime = `nginx:alpine` qui sert le HTML et fait le reverse proxy vers
le service backend.

### 2.3 Orchestration Docker Compose

Voir `docker-compose.yml`. Trois services (`db`, `backend`, `frontend`) sur un
réseau bridge `appnet`. La DB a un `healthcheck` et le backend dépend de
`db.condition: service_healthy`.

### 2.4 Lancement local

```bash
cp .env.example .env
docker compose up --build
```

**[📸 Screenshot A — `docker compose ps` montrant les 3 conteneurs en `healthy`]**

**[📸 Screenshot B — Navigateur sur `http://localhost:8080` affichant le dashboard avec health + users]**

**[📸 Screenshot C — `curl http://localhost:5000/api/users` dans le terminal, réponse JSON avec les 4 users]**

---

## 3. Étape 2 — Tests automatisés

Le backend dispose de 3 tests pytest (`backend/test_app.py`) qui vérifient :
- que `/health` renvoie `200` + `{"status":"ok"}`,
- que le content-type est bien `application/json`,
- qu'une route inconnue renvoie bien `404`.

**[📸 Screenshot D — sortie de `pytest test_app.py -v` (3 passed)]**

---

## 4. Étape 3 — Machine virtuelle sur Azure

### 4.1 Création de la VM

VM `Standard_B2s` sous Ubuntu 22.04, avec IP publique statique
`74.161.44.42`, accessible en SSH via la clé `~/.ssh/id_rsa`.

**[📸 Screenshot 1 — Vue d'ensemble de la VM dans le portail Azure]**

### 4.2 Installation de Docker + Docker Compose

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo apt install -y docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

**[📸 Screenshot 2 — `docker --version` et `docker compose version` sur la VM]**

### 4.3 Installation de k3s (à la place de Minikube)

Justification du choix de k3s : exposition native des NodePorts sur l'IP
publique de la VM, là où Minikube aurait nécessité un tunnel.

```bash
curl -sfL https://get.k3s.io | sh -
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config
```

**[📸 Screenshot 3 — `kubectl get nodes` (node Ready) et `kubectl get pods -A`]**

### 4.4 Ouverture du port 30080 (NSG Azure)

**[📸 Screenshot 4 — Règle NSG dans le portail Azure, port 30080 autorisé]**

---

## 5. Étape 4 — Déploiement Kubernetes

### 5.1 Structure des manifests

- `namespace.yml` : namespace `devops-tp-rayane`
- `secret.yml` : Secret Opaque avec `DB_NAME`, `DB_USER`, `DB_PASSWORD`
- `db-deployment.yml` : Deployment PostgreSQL + Service ClusterIP
- `backend-deployment.yml` : Deployment Flask (2 replicas, rolling update) +
  `livenessProbe` + `readinessProbe` + Service ClusterIP
- `frontend-deployment.yml` : Deployment Nginx + Service **NodePort 30080**

### 5.2 Déploiement manuel (première fois)

```bash
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/secret.yml
kubectl apply -f k8s/db-deployment.yml
kubectl apply -f k8s/backend-deployment.yml
kubectl apply -f k8s/frontend-deployment.yml
```

**[📸 Screenshot 5 — `ls -la` du repo cloné sur la VM]**

**[📸 Screenshot 6 — `kubectl get pods -n devops-tp-rayane` avec tous les pods `Running`]**

**[📸 Screenshot 7 — `kubectl get svc -n devops-tp-rayane` montrant le frontend en `NodePort 30080`]**

### 5.3 Test d'accès depuis l'extérieur

**[📸 Screenshot 8 — Navigateur sur `http://74.161.44.42:30080` (page frontend + status ok + liste des users)]**

**[📸 Screenshot 9 — `curl http://74.161.44.42:30080/api/health` depuis le poste local, réponse `{"status":"ok"}`]**

---

## 6. Étape 5 — Pipeline CI/CD GitHub Actions

### 6.1 Structure du workflow

Le workflow `.github/workflows/ci-cd.yml` est composé de 3 jobs chaînés :

| Job | Contenu | Échec bloque ? |
|---|---|---|
| `test` | `pip install -r requirements.txt` + `pytest` | Oui — stoppe le pipeline |
| `build-and-push` | Build multi-arch avec Buildx, push sur Docker Hub | Oui — pas de deploy si échec |
| `deploy` | SSH vers la VM, `git pull`, `kubectl set image`, `kubectl rollout status` | Oui |

### 6.2 Secrets configurés dans GitHub

| Secret | Rôle |
|---|---|
| `DOCKER_USERNAME` | Push images sur Docker Hub |
| `DOCKER_PASSWORD` | Token Docker Hub |
| `VM_HOST` | IP publique VM |
| `VM_USER` | User SSH (`azureuser`) |
| `VM_SSH_KEY` | Clé privée SSH dédiée au CI |

**[📸 Screenshot 10 — Page Actions de GitHub avec le dernier run vert (3 jobs passés)]**

### 6.3 Vérification du rollout après push

**[📸 Screenshot 11 — Sortie de `kubectl rollout history deployment/backend -n devops-tp-rayane` montrant plusieurs révisions après un second push]**

---

## 7. Gestion des variables d'environnement et secrets

Aucun secret n'est écrit en dur dans le code. Les mécanismes utilisés :

| Niveau | Mécanisme | Où |
|---|---|---|
| Local | Fichier `.env` (gitignoré) | `docker-compose.yml` avec `${DB_PASSWORD}` |
| Kubernetes | Objet `Secret` + `secretKeyRef` | `k8s/secret.yml` + `backend-deployment.yml` |
| CI/CD | Secrets GitHub Actions | `${{ secrets.DOCKER_PASSWORD }}`, etc. |

Le fichier `.env.example` documente les variables sans contenir de valeurs
sensibles et est commité ; `.env` est listé dans `.gitignore`.

---

## 8. Bonus réalisés

- ✅ **Multi-stage build** sur les deux Dockerfiles (backend et frontend)
- ✅ **Liveness + readiness probes** sur le backend K8s
- ✅ **Rolling update** sans downtime (2 replicas backend)
- ✅ **Resource requests/limits** sur tous les pods
- ✅ **k3s** à la place de Minikube (choix technique justifié)

---

## 9. Difficultés rencontrées

### Difficulté 1 — Accès NodePort avec Minikube
**Problème** : Minikube crée un réseau isolé, le NodePort n'était pas
directement joignable depuis l'IP publique de la VM.
**Tentatives** : `minikube tunnel`, redirection via `socat`.
**Solution retenue** : remplacement par k3s, qui expose les NodePorts
nativement sur l'IP de l'hôte.

### Difficulté 2 — Ordre de démarrage DB → backend
**Problème** : le backend tombait avec `connection refused` car PostgreSQL
n'était pas prêt au démarrage.
**Solution** : `depends_on.condition: service_healthy` en Compose, et
`readinessProbe` HTTP sur `/health` en Kubernetes.

### Difficulté 3 — Accès non-root à kubectl côté k3s
**Problème** : le kubeconfig de k3s (`/etc/rancher/k3s/k3s.yaml`) n'est
lisible qu'en root ; le job SSH du CI tournait donc en erreur.
**Solution** : copie de `k3s.yaml` dans `~/.kube/config` du user
`azureuser` et `export KUBECONFIG` dans `.bashrc`.

---

## 10. Récap des 11 screenshots pour le Word

| # | Section | Description |
|---|---------|-------------|
| 1 | 4.1 | VM Azure dans le portail |
| 2 | 4.2 | `docker --version` + `docker compose version` |
| 3 | 4.3 | `kubectl get nodes` + `kubectl get pods -A` |
| 4 | 4.4 | Règle NSG port 30080 ouverte |
| 5 | 5.2 | `ls -la` du repo cloné sur la VM |
| 6 | 5.2 | `kubectl get pods -n devops-tp-rayane` (tous Running) |
| 7 | 5.2 | `kubectl get svc -n devops-tp-rayane` (NodePort 30080) |
| 8 | 5.3 | Page frontend accessible via `http://<IP>:30080` |
| 9 | 5.3 | `curl /api/health` depuis poste local |
| 10 | 6.2 | Pipeline GitHub Actions vert (3 jobs OK) |
| 11 | 6.3 | `kubectl rollout history` après 2 push |

Screenshots locaux bonus (optionnels, pour l'étape Docker Compose) :

| # | Description |
|---|-------------|
| A | `docker compose ps` en local (3 conteneurs healthy) |
| B | Navigateur sur `localhost:8080` |
| C | `curl localhost:5000/api/users` |
| D | `pytest -v` (3 tests passent) |

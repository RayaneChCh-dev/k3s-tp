# Setup de la VM Azure — Docker + k3s

Ce document décrit l'installation pas à pas sur la VM Ubuntu 22.04 déployée sur Azure.

## Prérequis

- Une VM Azure Ubuntu 22.04 (ex. `Standard_B2s`), accessible en SSH
- Un groupe de sécurité réseau (NSG) permettant :
  - **22** (SSH) entrant depuis ton IP
  - **30080** (NodePort frontend) entrant depuis ton IP ou `0.0.0.0/0`

## 1. Docker + Docker Compose

```bash
sudo apt update && sudo apt upgrade -y

curl -fsSL https://get.docker.com | sudo sh
sudo apt install -y docker-compose-plugin

sudo usermod -aG docker $USER
newgrp docker

docker --version
docker compose version
```

## 2. Kubernetes local avec k3s

k3s a été choisi à la place de Minikube car il expose nativement les NodePorts
sur l'IP de l'hôte (pas besoin de `minikube tunnel` ou `socat`).

```bash
# Installation one-liner
curl -sfL https://get.k3s.io | sh -

# Rendre kubectl utilisable sans sudo
mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $USER:$USER ~/.kube/config
echo 'export KUBECONFIG=$HOME/.kube/config' >> ~/.bashrc
export KUBECONFIG=$HOME/.kube/config

# Vérification
kubectl get nodes
kubectl get pods -A
```

## 3. Cloner le projet sur la VM

```bash
cd ~
git clone https://github.com/RayaneChCh-dev/devops-tp-rayane.git
cd devops-tp-rayane
```

## 4. Déployer manuellement (première fois)

```bash
kubectl apply -f k8s/namespace.yml
kubectl apply -f k8s/secret.yml
kubectl apply -f k8s/db-deployment.yml
kubectl apply -f k8s/backend-deployment.yml
kubectl apply -f k8s/frontend-deployment.yml

kubectl get pods -n devops-tp-rayane -w
```

## 5. Tester l'accès

Depuis ton poste local :

```bash
curl http://<IP_PUBLIQUE_VM>:30080/
curl http://<IP_PUBLIQUE_VM>:30080/api/health
curl http://<IP_PUBLIQUE_VM>:30080/api/users
```

Dans un navigateur : `http://<IP_PUBLIQUE_VM>:30080`

## 6. Préparer le CI/CD (côté VM)

Le job `deploy` de GitHub Actions se connecte en SSH (authentification par
mot de passe) et exécute `git pull` + `kubectl set image`. Il faut donc :

1. Que le password SSH de la VM soit stocké dans le secret GitHub
   `VM_PASSWORD`.
2. Que le repo soit déjà cloné sur la VM dans `~/devops-tp-rayane` (le job
   `git fetch && git reset --hard origin/main`).

> **Note sécurité** : en production on utiliserait une clé SSH dédiée plutôt
> qu'un mot de passe. Pour ce TP l'authentification par password est
> acceptée car la VM est éphémère et le password protégé par les secrets
> GitHub.

## Récap des secrets GitHub Actions à créer

| Secret          | Valeur |
|-----------------|--------|
| `DOCKER_USERNAME` | `saphir10036` |
| `DOCKER_PASSWORD` | Token Docker Hub (pas le mot de passe du compte) |
| `VM_HOST`         | IP publique de la VM (`74.161.44.42`) |
| `VM_USER`         | `azureuser` (ou le user SSH de la VM) |
| `VM_PASSWORD`     | Mot de passe SSH de la VM |

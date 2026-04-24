"""Génère le rapport PDF du TP DevOps avec les captures d'écran fournies."""
from fpdf import FPDF
from PIL import Image
import os

SCREENSHOT_DIR = "/home/saphirdev/Images/Captures d’écran"

SCREENSHOTS = {
    "docker":       f"{SCREENSHOT_DIR}/Capture d’écran du 2026-04-24 10-42-15.png",
    "nodes":        f"{SCREENSHOT_DIR}/Capture d’écran du 2026-04-24 10-43-46.png",
    "pods_system":  f"{SCREENSHOT_DIR}/Capture d’écran du 2026-04-24 10-44-11.png",
    "nsg":          f"{SCREENSHOT_DIR}/Capture d’écran du 2026-04-24 10-47-38.png",
    "repo_ls":      f"{SCREENSHOT_DIR}/Capture d’écran du 2026-04-24 10-54-08.png",
    "pods_app":     f"{SCREENSHOT_DIR}/Capture d’écran du 2026-04-24 11-20-51.png",
    "svc":          f"{SCREENSHOT_DIR}/Capture d’écran du 2026-04-24 11-22-00.png",
    "browser":      f"{SCREENSHOT_DIR}/Capture d’écran du 2026-04-24 11-23-09.png",
    "curl":         f"{SCREENSHOT_DIR}/Capture d’écran du 2026-04-24 11-23-48.png",
    "pipeline":     f"{SCREENSHOT_DIR}/Capture d’écran du 2026-04-24 11-37-07.png",
}

TITLE = "Projet Intégration et Déploiement Continus"
AUTHOR = "Rayane Achouchi"
DATE = "24 avril 2026"


class Report(FPDF):
    def header(self):
        if self.page_no() == 1:
            return
        self.set_font("DejaVu", "I", 9)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, f"{TITLE} — {AUTHOR}", align="L")
        self.ln(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("DejaVu", "I", 9)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, f"Page {self.page_no()}", align="C")

    def h1(self, text):
        self.set_font("DejaVu", "B", 16)
        self.set_text_color(20, 20, 20)
        self.ln(3)
        self.multi_cell(0, 8, text)
        self.set_draw_color(180, 180, 180)
        self.set_line_width(0.3)
        self.line(self.l_margin, self.get_y() + 1, self.w - self.r_margin, self.get_y() + 1)
        self.ln(4)

    def h2(self, text):
        self.set_font("DejaVu", "B", 12)
        self.set_text_color(40, 40, 40)
        self.ln(2)
        self.multi_cell(0, 7, text)
        self.ln(1)

    def para(self, text):
        self.set_font("DejaVu", "", 10.5)
        self.set_text_color(20, 20, 20)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text):
        self.set_font("DejaVu", "", 10.5)
        self.set_text_color(20, 20, 20)
        # indentation + puce + texte
        self.set_x(self.l_margin + 5)
        self.cell(4, 5.5, "•")
        self.multi_cell(0, 5.5, text)

    def code(self, text):
        self.set_font("DejaVuMono", "", 9.5)
        self.set_fill_color(245, 245, 247)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5, text, fill=True, border=0)
        self.ln(2)

    def screenshot(self, path, caption, max_width=170, max_height=110):
        """Insère une capture en conservant son ratio, avec une légende en italique."""
        with Image.open(path) as im:
            w_px, h_px = im.size
        # convertir px -> mm (96 dpi standard = 25.4/96 mm/px)
        w_mm = w_px * 25.4 / 96
        h_mm = h_px * 25.4 / 96
        # redimensionner si trop large/haut
        scale = min(max_width / w_mm, max_height / h_mm, 1.0)
        final_w = w_mm * scale
        final_h = h_mm * scale

        # vérifier qu'on a la place sur la page
        remaining = self.h - self.b_margin - self.get_y()
        if remaining < final_h + 10:
            self.add_page()

        # centrer horizontalement
        x = (self.w - final_w) / 2
        self.image(path, x=x, w=final_w, h=final_h)
        self.ln(2)
        self.set_font("DejaVu", "I", 9)
        self.set_text_color(100, 100, 100)
        self.multi_cell(0, 4.5, caption, align="C")
        self.ln(3)


pdf = Report(format="A4")
pdf.set_margins(20, 20, 20)
pdf.set_auto_page_break(auto=True, margin=18)

# Polices Unicode (supportent les caractères français, tirets longs, etc.)
FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdf.add_font("DejaVu", "",  f"{FONT_DIR}/DejaVuSans.ttf")
pdf.add_font("DejaVu", "B", f"{FONT_DIR}/DejaVuSans-Bold.ttf")
pdf.add_font("DejaVu", "I", f"{FONT_DIR}/DejaVuSans-Oblique.ttf")
pdf.add_font("DejaVuMono", "",  f"{FONT_DIR}/DejaVuSansMono.ttf")

pdf.add_page()

# ---------- COVER ----------
pdf.set_y(70)
pdf.set_font("DejaVu", "B", 24)
pdf.set_text_color(20, 20, 20)
pdf.multi_cell(0, 12, TITLE, align="C")
pdf.ln(4)
pdf.set_font("DejaVu", "", 14)
pdf.set_text_color(90, 90, 90)
pdf.multi_cell(0, 7, "TP DevOps — Docker, Kubernetes, CI/CD", align="C")
pdf.ln(40)

pdf.set_font("DejaVu", "B", 16)
pdf.set_text_color(20, 20, 20)
pdf.cell(0, 10, AUTHOR, align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("DejaVu", "", 12)
pdf.set_text_color(70, 70, 70)
pdf.cell(0, 7, DATE, align="C", new_x="LMARGIN", new_y="NEXT")
pdf.ln(4)
pdf.set_font("DejaVu", "", 10)
pdf.set_text_color(40, 80, 180)
pdf.cell(0, 6, "github.com/RayaneChCh-dev/k3s-tp", align="C", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)

pdf.ln(30)
pdf.set_font("DejaVu", "I", 10)
pdf.set_text_color(110, 110, 110)
pdf.multi_cell(
    0, 5,
    "Application full stack (Frontend Nginx + Backend Flask + PostgreSQL)\n"
    "Orchestration locale Docker Compose, déploiement Kubernetes via k3s\n"
    "sur une VM Azure, automatisé par un pipeline GitHub Actions.",
    align="C",
)

# ---------- 1. CONTEXTE ----------
pdf.add_page()
pdf.h1("1. Contexte et objectifs")
pdf.para(
    "Une entreprise souhaite automatiser le déploiement de son application web "
    "afin de gagner du temps et d'éviter les erreurs humaines. L'objectif du TP "
    "est de mettre en place une chaîne complète : conteneurisation d'une "
    "application, orchestration locale, déploiement Kubernetes sur une "
    "machine virtuelle dans le cloud, et pipeline CI/CD qui relie le tout."
)
pdf.para(
    "L'application retenue est un mini-dashboard composé de trois services "
    "distincts qui communiquent entre eux :"
)
pdf.bullet("un frontend Nginx servant une page HTML avec dashboard des endpoints ;")
pdf.bullet("un backend Python (Flask) exposant 5 endpoints REST ;")
pdf.bullet("une base PostgreSQL 15 initialisée par un script SQL.")

pdf.h2("Stack technique retenue")
pdf.code(
    " Frontend         Nginx + HTML + JavaScript vanille\n"
    " Backend          Python 3.11 / Flask\n"
    " Base de données  PostgreSQL 15 (image Alpine)\n"
    " Conteneurisation Docker (multi-stage builds)\n"
    " Orchestration    Docker Compose v2 (local) / k3s (cloud)\n"
    " Cloud            Microsoft Azure (VM Ubuntu 22.04)\n"
    " CI/CD            GitHub Actions\n"
    " Registry         Docker Hub (saphir10036/*)"
)

pdf.h2("Architecture cible")
pdf.code(
    " Navigateur --> VM Azure (74.161.44.42)\n"
    "                  |\n"
    "                  +--> k3s cluster\n"
    "                         namespace: devops-tp-rayane\n"
    "                           frontend (NodePort 30080)\n"
    "                              |\n"
    "                              v\n"
    "                           backend (ClusterIP :5000)\n"
    "                              |\n"
    "                              v\n"
    "                           db (ClusterIP :5432) -- Secret db-secret"
)

# ---------- 2. CONTENEURISATION ----------
pdf.add_page()
pdf.h1("2. Conteneurisation avec Docker")

pdf.h2("2.1 Dockerfile backend (multi-stage)")
pdf.para(
    "Le backend utilise un build en deux étapes. La première (builder) installe "
    "les dépendances Python avec pip dans /root/.local ; la seconde (runtime) "
    "récupère uniquement ces artefacts et la source, ce qui réduit la taille "
    "finale de l'image et évite d'embarquer la toolchain de build."
)
pdf.code(
    "FROM python:3.11-slim AS builder\n"
    "WORKDIR /app\n"
    "COPY requirements.txt .\n"
    "RUN pip install --user --no-cache-dir -r requirements.txt\n"
    "\n"
    "FROM python:3.11-slim\n"
    "WORKDIR /app\n"
    "COPY --from=builder /root/.local /root/.local\n"
    "COPY app.py ./\n"
    "ENV PATH=/root/.local/bin:$PATH\n"
    "EXPOSE 5000\n"
    "HEALTHCHECK --interval=30s CMD curl -fsS http://localhost:5000/health || exit 1\n"
    "CMD [\"python\", \"app.py\"]"
)

pdf.h2("2.2 Dockerfile frontend (multi-stage)")
pdf.para(
    "Le frontend suit le même principe : un stage builder prépare les assets "
    "statiques, le stage runtime nginx:alpine sert les fichiers et fait le "
    "reverse proxy vers le backend via /api."
)

pdf.h2("2.3 Orchestration Docker Compose")
pdf.para(
    "Le fichier docker-compose.yml définit trois services (db, backend, "
    "frontend) sur un réseau bridge dédié (appnet). La DB possède un "
    "healthcheck pg_isready et le backend déclare depends_on avec la "
    "condition service_healthy afin de ne démarrer qu'une fois la base prête."
)
pdf.code(
    "services:\n"
    "  db:\n"
    "    image: postgres:15-alpine\n"
    "    healthcheck:\n"
    "      test: [\"CMD-SHELL\", \"pg_isready -U appuser -d appdb\"]\n"
    "  backend:\n"
    "    build: ./backend\n"
    "    ports: [\"5000:5000\"]\n"
    "    depends_on: { db: { condition: service_healthy } }\n"
    "  frontend:\n"
    "    build: ./frontend\n"
    "    ports: [\"8080:80\"]\n"
    "    depends_on: [backend]"
)

pdf.h2("2.4 Lancement local")
pdf.code(
    "$ cp .env.example .env\n"
    "$ docker compose up --build\n"
    "$ curl http://localhost:5000/health\n"
    "{\"service\":\"backend\",\"status\":\"ok\"}"
)

# ---------- 3. TESTS ----------
pdf.add_page()
pdf.h1("3. Tests automatisés")
pdf.para(
    "Le backend embarque 3 tests pytest qui vérifient le comportement de "
    "l'endpoint /health, son content-type et le fait qu'une route inconnue "
    "renvoie bien un 404. Ces tests sont exécutés automatiquement au premier "
    "job du pipeline CI/CD et bloquent l'ensemble de la chaîne en cas d'échec."
)
pdf.code(
    "def test_health_returns_ok(client):\n"
    "    res = client.get('/health')\n"
    "    assert res.status_code == 200\n"
    "    assert res.get_json()['status'] == 'ok'"
)

# ---------- 4. VM AZURE ----------
pdf.add_page()
pdf.h1("4. Machine virtuelle Azure et installation")

pdf.h2("4.1 Création de la VM")
pdf.para(
    "Une VM Ubuntu 22.04 (taille Standard_B2s) a été provisionnée sur Azure "
    "avec une IP publique statique 74.161.44.42. La connexion s'effectue en "
    "SSH avec authentification par mot de passe."
)

pdf.h2("4.2 Installation de Docker et Docker Compose")
pdf.code(
    "$ curl -fsSL https://get.docker.com | sudo sh\n"
    "$ sudo apt install -y docker-compose-plugin\n"
    "$ sudo usermod -aG docker $USER && newgrp docker"
)
pdf.screenshot(
    SCREENSHOTS["docker"],
    "Figure 1 — Vérification des versions de Docker et Docker Compose installés sur la VM.",
)

pdf.h2("4.3 Installation de Kubernetes via k3s")
pdf.para(
    "k3s a été retenu à la place de Minikube car il expose nativement les "
    "services de type NodePort sur l'IP de l'hôte — là où Minikube aurait "
    "nécessité un tunnel ou un reverse-proxy supplémentaire pour exposer "
    "l'application depuis l'extérieur."
)
pdf.code(
    "$ curl -sfL https://get.k3s.io | sh -\n"
    "$ sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config\n"
    "$ sudo chown $USER:$USER ~/.kube/config\n"
    "$ export KUBECONFIG=~/.kube/config"
)
pdf.screenshot(
    SCREENSHOTS["nodes"],
    "Figure 2 — Le node k3s (rayane-machine) est bien en état Ready.",
)
pdf.screenshot(
    SCREENSHOTS["pods_system"],
    "Figure 3 — Les pods système k3s (coredns, traefik, metrics-server…) tournent.",
)

pdf.h2("4.4 Ouverture du port 30080 dans le NSG Azure")
pdf.para(
    "Pour rendre l'application accessible depuis l'extérieur, une règle de "
    "sécurité entrante a été ajoutée au NSG de la VM pour autoriser le port "
    "TCP 30080 (celui exposé par le service Kubernetes frontend)."
)
pdf.screenshot(
    SCREENSHOTS["nsg"],
    "Figure 4 — Règles NSG de la VM : SSH (port 22) et NodePort frontend (port 30080) autorisés.",
)

# ---------- 5. DEPLOIEMENT K8S ----------
pdf.add_page()
pdf.h1("5. Déploiement Kubernetes")

pdf.h2("5.1 Manifests utilisés")
pdf.bullet("namespace.yml — crée le namespace applicatif.")
pdf.bullet("secret.yml — stocke les credentials PostgreSQL (type Opaque).")
pdf.bullet("db-deployment.yml — Deployment + Service ClusterIP pour PostgreSQL.")
pdf.bullet(
    "backend-deployment.yml — Deployment (2 replicas, RollingUpdate) avec "
    "livenessProbe et readinessProbe HTTP, resources requests/limits, et un "
    "Service ClusterIP."
)
pdf.bullet(
    "frontend-deployment.yml — Deployment Nginx et Service de type NodePort "
    "exposant le port 30080 sur l'IP de la VM."
)

pdf.h2("5.2 Application des manifests")
pdf.code(
    "$ kubectl apply -f k8s/namespace.yml\n"
    "$ kubectl apply -f k8s/secret.yml\n"
    "$ kubectl apply -f k8s/db-deployment.yml\n"
    "$ kubectl apply -f k8s/backend-deployment.yml\n"
    "$ kubectl apply -f k8s/frontend-deployment.yml"
)
pdf.screenshot(
    SCREENSHOTS["repo_ls"],
    "Figure 5 — Le repo k3s-tp cloné sur la VM contient tous les fichiers du projet.",
)
pdf.screenshot(
    SCREENSHOTS["pods_app"],
    "Figure 6 — Tous les pods applicatifs (db, backend x2, frontend) sont en état Running.",
)
pdf.screenshot(
    SCREENSHOTS["svc"],
    "Figure 7 — Services Kubernetes : le frontend est exposé en NodePort 80:30080/TCP.",
)

# ---------- 6. TEST ACCES EXTERIEUR ----------
pdf.add_page()
pdf.h1("6. Validation de l'accès externe")
pdf.para(
    "Depuis le poste local, l'application est accessible sur "
    "http://74.161.44.42:30080. Le frontend affiche le statut du backend, "
    "et une requête directe sur l'API confirme le bon fonctionnement du "
    "reverse proxy Nginx vers le service backend Kubernetes."
)
pdf.screenshot(
    SCREENSHOTS["browser"],
    "Figure 8 — Accès à l'application depuis un navigateur (IP publique de la VM, port 30080).",
)
pdf.screenshot(
    SCREENSHOTS["curl"],
    "Figure 9 — curl sur /api/health via le reverse proxy Nginx retourne la réponse du backend.",
)

# ---------- 7. CI/CD ----------
pdf.add_page()
pdf.h1("7. Pipeline CI/CD avec GitHub Actions")

pdf.h2("7.1 Structure du workflow")
pdf.para(
    "Le workflow .github/workflows/ci-cd.yml est composé de 3 jobs chaînés. "
    "Un échec dans un job précédent bloque le suivant grâce à la directive "
    "needs, ce qui garantit qu'aucune image cassée n'est poussée sur le "
    "registry et qu'aucun déploiement n'est tenté si les tests échouent."
)
pdf.code(
    " Job             Rôle                                               Bloquant\n"
    " ---             ----                                               --------\n"
    " test            pytest du backend                                  Oui\n"
    " build-and-push  Build multi-arch Buildx + push Docker Hub          Oui\n"
    " deploy          SSH vers la VM, kubectl set image, rollout status  Oui"
)

pdf.h2("7.2 Séquence d'exécution")
pdf.code(
    " git push main\n"
    "      |\n"
    "      v\n"
    " [test] -- pytest test_app.py -v (3 tests)\n"
    "      |  ok\n"
    "      v\n"
    " [build-and-push] -- docker buildx backend + frontend\n"
    "                  -- push saphir10036/devops-tp-rayane-*:{latest,<sha>}\n"
    "      |  ok\n"
    "      v\n"
    " [deploy] -- ssh azureuser@74.161.44.42\n"
    "          -- git reset --hard origin/main\n"
    "          -- kubectl apply -f k8s/\n"
    "          -- kubectl set image deployment/backend ... :<sha>\n"
    "          -- kubectl set image deployment/frontend ... :<sha>\n"
    "          -- kubectl rollout status (timeout 120s)"
)
pdf.screenshot(
    SCREENSHOTS["pipeline"],
    "Figure 10 — Exécution du pipeline CI/CD sur GitHub Actions : les 3 jobs passent "
    "en 1m13s après le push du commit ci: trigger first pipeline run.",
)

# ---------- 8. SECRETS ----------
pdf.add_page()
pdf.h1("8. Gestion des variables d'environnement et secrets")
pdf.para(
    "Aucune valeur sensible n'est écrite en dur dans le code versionné. "
    "Trois mécanismes complémentaires sont utilisés selon le contexte :"
)
pdf.bullet(
    "En local : fichier .env (git-ignoré), basé sur un .env.example fourni. "
    "Les variables sont interpolées dans le docker-compose.yml."
)
pdf.bullet(
    "Dans Kubernetes : objet Secret de type Opaque (k8s/secret.yml) et "
    "référence via secretKeyRef depuis les Deployments."
)
pdf.bullet(
    "Dans GitHub Actions : secrets de repository référencés via "
    "${{ secrets.NOM_DU_SECRET }} dans le workflow."
)

pdf.h2("Secrets configurés dans GitHub Actions")
pdf.code(
    " DOCKER_USERNAME   saphir10036\n"
    " DOCKER_PASSWORD   token Docker Hub (jamais le mot de passe du compte)\n"
    " VM_HOST           74.161.44.42\n"
    " VM_USER           azureuser\n"
    " VM_PASSWORD       mot de passe SSH de la VM"
)

# ---------- 9. BONUS ----------
pdf.h1("9. Bonus réalisés")
pdf.bullet("Multi-stage build sur les deux Dockerfiles (backend et frontend).")
pdf.bullet("Liveness + readiness probes HTTP sur le backend Kubernetes.")
pdf.bullet("Rolling update sans downtime (2 replicas backend, maxUnavailable=0).")
pdf.bullet("Resource requests/limits explicites sur tous les pods.")
pdf.bullet("k3s à la place de Minikube (choix justifié pour l'exposition NodePort).")
pdf.bullet("Tag d'image par SHA de commit en plus de latest, pour garantir une traçabilité stricte.")

# ---------- 10. DIFFICULTES ----------
pdf.add_page()
pdf.h1("10. Difficultés rencontrées")

pdf.h2("10.1 Exposition du NodePort avec Minikube")
pdf.para(
    "Problème initial : Minikube crée un réseau isolé et le NodePort n'est "
    "pas joignable directement depuis l'IP publique de la VM. Les tentatives "
    "minikube tunnel et socat ont toutes deux fonctionné mais introduisent "
    "un point de défaillance supplémentaire."
)
pdf.para(
    "Solution retenue : remplacement de Minikube par k3s, qui expose "
    "nativement les NodePorts sur l'IP de l'hôte. L'énoncé autorisait "
    "explicitement les deux."
)

pdf.h2("10.2 Ordre de démarrage DB puis backend")
pdf.para(
    "Problème : le backend tombait en connection refused au démarrage, "
    "PostgreSQL n'étant pas encore prêt à accepter les connexions."
)
pdf.para(
    "Solution : en Docker Compose, depends_on.condition: service_healthy "
    "couplé à un healthcheck pg_isready. En Kubernetes, readinessProbe HTTP "
    "sur /health côté backend qui retarde l'entrée du pod dans le Service "
    "tant que la DB n'est pas atteignable."
)

pdf.h2("10.3 Conflit de NodePort lors du redéploiement")
pdf.para(
    "Problème : lors du passage d'une première version (namespace "
    "devops-tp) au stack définitif (namespace devops-tp-rayane), "
    "l'application du manifest frontend a échoué avec "
    "« provided port is already allocated » car l'ancien Service n'avait "
    "pas encore été supprimé."
)
pdf.para(
    "Solution : suppression explicite de l'ancien namespace avec "
    "kubectl delete namespace devops-tp avant ré-application, ce qui "
    "garbage-collecte les Services qui y étaient rattachés."
)

pdf.h2("10.4 Accès non-root à kubectl sur k3s")
pdf.para(
    "Problème : le fichier kubeconfig de k3s (/etc/rancher/k3s/k3s.yaml) "
    "n'est lisible qu'en root par défaut, ce qui faisait échouer les "
    "commandes kubectl lancées par le job SSH du CI."
)
pdf.para(
    "Solution : copie de k3s.yaml dans ~/.kube/config du user azureuser, "
    "chown, et export KUBECONFIG dans ~/.bashrc."
)

# ---------- 11. CONCLUSION ----------
pdf.h1("11. Conclusion")
pdf.para(
    "L'ensemble des objectifs du TP a été atteint : l'application full "
    "stack est conteneurisée (multi-stage builds), orchestrée localement "
    "avec Docker Compose, déployée sur un cluster Kubernetes (k3s) "
    "installé sur une VM Azure, et toute la chaîne est automatisée par un "
    "pipeline GitHub Actions à trois étapes (test, build & push, deploy). "
    "Les secrets sont gérés de bout en bout sans apparaître dans le code "
    "versionné. Le pipeline s'est exécuté avec succès en 1 minute 13 "
    "(figure 10) et l'application est accessible sur "
    "http://74.161.44.42:30080."
)

out_path = "/home/saphirdev/devops-tp-rayane/rapport.pdf"
pdf.output(out_path)
print(f"PDF généré : {out_path}")

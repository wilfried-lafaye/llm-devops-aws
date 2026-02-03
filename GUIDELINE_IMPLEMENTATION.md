# 📋 Guideline d'Implémentation
## Dashboard Qualité Air France (Version sans LLM)

**Équipe:** Clem & Willou  
**Cours:** DevOps for SWE - Badr TAJINI - ESIEE Paris  
**Deadline:** 01/02/2026

---

## 🎯 Vue d'ensemble

Ce document détaille les étapes d'implémentation du Dashboard Qualité Air France. Cette version **sans composant LLM** se concentre sur :

1. ✅ **Dashboard interactif** avec visualisations
2. ✅ **API REST** complète avec FastAPI
3. ✅ **Pipeline CI/CD** automatisé
4. ✅ **Déploiement Kubernetes** production-ready

---

## 📅 Planning par Phases

### 🟢 Phase 1 : Backend API (Semaine 1)

#### 1.1 Structure du projet
```bash
mkdir -p backend/{app/routers,tests}
touch backend/app/{__init__.py,main.py,models.py,schemas.py,crud.py,database.py}
touch backend/app/routers/{__init__.py,air_quality.py,stats.py}
touch backend/{requirements.txt,Dockerfile}
```

#### 1.2 Dépendances (`requirements.txt`)
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
pydantic==2.5.3
python-dotenv==1.0.0
pytest==7.4.4
httpx==0.26.0
```

#### 1.3 Modèle de données (`app/models.py`)
```python
from sqlalchemy import Column, Integer, String, Float, Index
from app.database import Base

class AirQualityRecord(Base):
    __tablename__ = "air_quality"
    
    id = Column(Integer, primary_key=True, index=True)
    commune = Column(String, index=True)
    region = Column(String, index=True)
    annee = Column(Integer, index=True)
    no2 = Column(Float)        # Dioxyde d'azote (µg/m³)
    pm10 = Column(Float)       # Particules PM10 (µg/m³)
    pm25 = Column(Float)       # Particules PM2.5 (µg/m³)
    o3 = Column(Float)         # Ozone (µg/m³)
    somo35 = Column(Float)     # SOMO35 (µg/m³.jour)
    aot40 = Column(Float)      # AOT40 (µg/m³.heure)
    latitude = Column(Float)
    longitude = Column(Float)
    
    # Index composites pour optimisation
    __table_args__ = (
        Index('ix_commune_annee', 'commune', 'annee'),
        Index('ix_region_annee', 'region', 'annee'),
    )
```

#### 1.4 Endpoints à implémenter

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/api/v1/records` | Liste avec filtres |
| GET | `/api/v1/records/{id}` | Record par ID |
| POST | `/api/v1/records` | Créer un record |
| PUT | `/api/v1/records/{id}` | Modifier un record |
| DELETE | `/api/v1/records/{id}` | Supprimer un record |
| GET | `/api/v1/regions` | Liste des régions |
| GET | `/api/v1/communes` | Liste des communes |
| GET | `/api/v1/years` | Années disponibles |
| GET | `/api/v1/stats/region/{region}` | Stats par région |
| GET | `/api/v1/stats/commune/{commune}` | Stats par commune |
| GET | `/api/v1/trends/{pollutant}` | Tendances |

#### 1.5 Tests à écrire
- [ ] Test health check
- [ ] Tests CRUD complets
- [ ] Tests filtrage et pagination
- [ ] Tests endpoints stats
- [ ] Test gestion des erreurs

---

### 🔵 Phase 2 : Frontend HTML (Semaine 1-2)

#### 2.1 Structure des fichiers
```
frontend/
├── index.html          # Page principale
├── css/
│   └── style.css       # Styles dark theme
├── js/
│   ├── api.js          # Client API
│   ├── app.js          # Application principale
│   └── charts.js       # Graphiques Chart.js
├── nginx.conf          # Config Nginx
└── Dockerfile
```

#### 2.2 Sections du Dashboard

**Navigation (Sidebar)**
- Dashboard (vue d'ensemble)
- Carte (visualisation géographique)
- Données (tableau CRUD)
- Tendances (analyse temporelle)

**Dashboard principal**
```html
<section id="dashboard">
  <!-- Cartes statistiques -->
  <div class="stats-grid">
    <div class="stat-card">NO2 moyen</div>
    <div class="stat-card">PM10 moyen</div>
    <div class="stat-card">PM2.5 moyen</div>
    <div class="stat-card">O3 moyen</div>
  </div>
  
  <!-- Graphiques -->
  <div class="charts-grid">
    <canvas id="evolutionChart"></canvas>
    <canvas id="regionsChart"></canvas>
  </div>
</section>
```

#### 2.3 Carte Interactive (Leaflet.js)
```javascript
// Initialisation de la carte
const map = L.map('map').setView([46.603354, 1.888334], 6);

// Couche OpenStreetMap
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Marqueurs colorés selon pollution
function getColor(value, pollutant) {
  const thresholds = {
    no2: { low: 20, high: 40 },
    pm10: { low: 20, high: 40 },
    pm25: { low: 10, high: 25 },
    o3: { low: 100, high: 180 }
  };
  
  if (value < thresholds[pollutant].low) return '#3fb950';  // Vert
  if (value < thresholds[pollutant].high) return '#d29922'; // Orange
  return '#f85149';  // Rouge
}
```

#### 2.4 Graphiques (Chart.js)
```javascript
// Graphique d'évolution temporelle
const evolutionChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels: years,
    datasets: [{
      label: 'NO2',
      data: no2Values,
      borderColor: '#f85149'
    }]
  },
  options: {
    responsive: true,
    plugins: {
      legend: { position: 'top' }
    }
  }
});
```

---

### 🟠 Phase 3 : CI/CD Pipeline (Semaine 2-3)

#### 3.1 GitHub Actions Workflow

```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install & Test
        run: |
          cd backend
          pip install -r requirements.txt
          pytest tests/ -v --cov=app

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4
      - uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_HUB_USERNAME }}
          password: ${{ secrets.DOCKER_HUB_TOKEN }}
      - uses: docker/build-push-action@v5
        with:
          context: ./backend
          push: true
          tags: user/backend:${{ github.sha }}

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - uses: azure/setup-kubectl@v4
      - run: kubectl apply -f k8s/
```

#### 3.2 Secrets à configurer

| Secret | Description | Comment l'obtenir |
|--------|-------------|-------------------|
| `DOCKER_HUB_USERNAME` | Nom d'utilisateur | [Docker Hub](https://hub.docker.com/) |
| `DOCKER_HUB_TOKEN` | Token d'accès | Settings > Security > New Access Token |
| `KUBE_CONFIG` | Kubeconfig base64 | `cat ~/.kube/config | base64` |

---

### 🟣 Phase 4 : Kubernetes (Semaine 3)

#### 4.1 Manifestes à créer

```
k8s/
├── namespace.yaml
├── postgres/
│   ├── secret.yaml       # Credentials DB
│   ├── pvc.yaml          # Volume persistant
│   ├── deployment.yaml
│   └── service.yaml
├── backend/
│   ├── configmap.yaml    # Variables env
│   ├── deployment.yaml   # 2 replicas
│   └── service.yaml      # ClusterIP
└── frontend/
    ├── deployment.yaml   # 2 replicas
    └── service.yaml      # LoadBalancer
```

#### 4.2 Deployment Backend
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: air-quality
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    spec:
      containers:
      - name: backend
        image: user/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: url
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
```

#### 4.3 Commandes de déploiement
```bash
# Minikube
minikube start --driver=docker --memory=4096
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/postgres/
kubectl apply -f k8s/backend/
kubectl apply -f k8s/frontend/

# Vérifier le déploiement
kubectl get pods -n air-quality
kubectl get services -n air-quality

# Accéder au frontend
minikube service frontend -n air-quality
```

---

### 🟦 Phase 5 : Finalisation (Semaine 3-4)

#### 5.1 Checklist pré-rendu

**Backend**
- [ ] Tous les endpoints fonctionnels
- [ ] Tests avec >80% couverture
- [ ] Documentation Swagger/OpenAPI
- [ ] Gestion des erreurs

**Frontend**
- [ ] Dashboard responsive
- [ ] Carte interactive fonctionnelle
- [ ] Graphiques dynamiques
- [ ] Filtres opérationnels

**CI/CD**
- [ ] Pipeline passant
- [ ] Images Docker publiées
- [ ] Déploiement automatique

**Kubernetes**
- [ ] Pods en running
- [ ] Services accessibles
- [ ] Health checks OK
- [ ] Logs consultables

**Documentation**
- [ ] README complet
- [ ] Vidéo démo (2-3 min)
- [ ] Architecture documentée

#### 5.2 Vidéo démo (structure suggérée)

| Durée | Contenu |
|-------|---------|
| 0:00-0:15 | Introduction projet |
| 0:15-0:45 | Navigation Dashboard |
| 0:45-1:15 | Carte interactive |
| 1:15-1:45 | API et Swagger UI |
| 1:45-2:15 | Pipeline CI/CD |
| 2:15-2:45 | Déploiement K8s |
| 2:45-3:00 | Conclusion |

---

## 🔧 Outils Recommandés

| Outil | Usage |
|-------|-------|
| **VS Code** | IDE avec extensions Python, Docker |
| **Postman** | Test des endpoints API |
| **DBeaver** | Client PostgreSQL |
| **Lens** | Dashboard Kubernetes |
| **Git** | Gestion de versions |

---

## 📚 Ressources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/)
- [Chart.js](https://www.chartjs.org/docs/)
- [Leaflet.js](https://leafletjs.com/reference.html)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [GitHub Actions](https://docs.github.com/en/actions)

---

## ❓ FAQ

**Q: Pourquoi pas de LLM dans cette version ?**  
A: Cette version simplifiée permet de se concentrer sur les fondamentaux DevOps (CI/CD, K8s) sans la complexité d'intégration d'un modèle de langage.

**Q: Peut-on utiliser SQLite en local ?**  
A: Oui, le backend détecte automatiquement si PostgreSQL n'est pas disponible et bascule sur SQLite.

**Q: Comment débugger en local ?**  
A: Utilisez `uvicorn app.main:app --reload` pour le hot-reload et consultez les logs Docker avec `docker-compose logs -f`.

---

*Bonne implémentation ! 🚀*

# Examen du cours Prometheus & Grafana.

### Structure du repo :

```
├── deployment
│   ├── prometheus/
│   │   └── prometheus.yml
├── src/
│   ├── api/
│   │   ├── Dockerfile
│   │   ├── main.py
│   │   └── requirements.txt
│   ├── evaluation/
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── run_evaluation.py
├── docker-compose.yml
└── Makefile
```

#### Contexte de l'Examen

Vous êtes chargé(e) de mettre en place une solution de monitoring complète pour un modèle de prédiction du nombre de vélos partagés (`cnt`) basé sur le dataset "Bike Sharing UCI". L'objectif est de garantir que les performances du modèle et les dérives des données sont constamment surveillées, visualisées et alertables, avec un accent particulier sur l'automatisation de la création des dashboards Grafana.

Vous partirez du dépôt Git suivant :

```
https://github.com/DataScientest/PromGraf-MLOps-Exam-Student
```

Celui-ci qui contient une structure de base vide pour l'API et les configurations.

**Variables clés du dataset :**
*   **Variable cible (`target`) :** `cnt`
*   **Variables numériques :** `temp`, `atemp`, `hum`, `windspeed`, `mnth`, `hr`, `weekday`
*   **Variables catégorielles :** `season`, `holiday`, `workingday`, `weathersit`

#### Consignes Générales

1.  **Qualité du Code et de la Configuration :** Le code doit être propre, commenté et les configurations claires et bien structurées.
2.  **Reproductibilité :** Le projet doit pouvoir être lancé et fonctionnel sur une autre machine en exécutant une simple commande `make`.
3.  **Automatisation :** Privilégiez l'automatisation chaque fois que possible, notamment pour la mise en place des dashboards Grafana.
4.  **Versionnement :** Assurez-vous que tous les fichiers nécessaires (code, configurations, dashboards JSON) sont inclus dans votre rendu.

#### Tâches Spécifiques

Pour réussir cet examen, vous devrez implémenter les points suivants :

**I. Préparation de l'Environnement et de l'API :**

*   **Construction de l'API :**
    *   Vous devrez **construire l'API FastAPI** (`src/api/main.py`) pour un modèle de régression prédisant le nombre de vélos (`cnt`).
    *   **Intégrez les fonctions de chargement et de préparation des données** (`_fetch_data`, `_process_data`) ainsi que **d'entraînement du `RandomForestRegressor`** (`_train_and_predict_reference_model`) sur les données de janvier 2011. Le modèle doit être entraîné une seule fois (par exemple, au démarrage du conteneur API ou via une cible `make train` dédiée) et chargé pour l'inférence.
    *   Votre API devra exposer un endpoint `/predict` qui accepte les features du `Bike Sharing` dataset (la class `BikeSharingInput` fournie) et retourne une prédiction.
    *   Assurez-vous que le `Dockerfile` et le `requirements.txt` de votre API sont corrects (incluant toutes les dépendances nécessaires).
*   Configurez le `docker-compose.yml` pour lancer :
    *   Votre API (que vous nommerez `bike-api`, sur le port 8080).
    *   Prometheus (sur le port 9090).
    *   Grafana (sur le port 3000).
    *   `node-exporter` (sur le port 9100) pour le monitoring de l'infrastructure hôte.

**II. Instrumentation de l'API et Collecte de Métriques dans Prometheus :**

*   Dans le fichier `api/main.py` :
    *   Définissez et incrémentez les métriques suivantes (utilisant `prometheus_client` et votre `CollectorRegistry`) :
        *   `api_requests_total` (Counter, avec labels `endpoint`, `method`, `status_code`).
        *   `api_request_duration_seconds` (Histogram, avec labels `endpoint`, `method`, `status_code`).
        *   `model_rmse_score` (Gauge, pour le Root Mean Squared Error du modèle de régression, mise à jour via l'endpoint `/evaluate`).
        *   `model_mae_score` (Gauge, pour le Root Mean Squared Error du modèle de régression, mise à jour via l'endpoint `/evaluate`).
        *   `model_r2_score` (Gauge, pour le Root Mean Squared Error du modèle de régression, mise à jour via l'endpoint `/evaluate`).
        *   **Une métrique de votre choix :** Implémentez **une métrique supplémentaire jugée pertinente** pour le monitoring de ce modèle de régression et des dérives (par exemple, `model_mape_score`, `evidently_data_drift_detected_status` (Gauge), ou le score de dérive pour une feature spécifique). Justifiez brièvement (dans les commentaires du code ou un `README` rapide) pourquoi cette métrique est pertinente.
    *   Implémentez l'endpoint `/evaluate` :
        *   Il acceptera des données "courantes" pour une période (ex: une semaine de février).
        *   Il utilisera le modèle entraîné pour faire des prédictions sur ces données.
        *   Il exécutera un **rapport Evidently** (`RegressionPreset` ou `DataDriftPreset`) en utilisant les données de janvier (référence) et les données "courantes" fournies.
        *   **Il extraira le `RMSE`, `MAE`, `R2Score` et votre métrique de choix** des résultats du rapport Evidently (utilisez la documentation d'Evidently ou la structure des objets `Report` / `Snapshot` / `Metric` pour cela) et mettra à jour les `Gauge` ou `Counter` Prometheus correspondants.
        *   la class `EvaluationReportOutput` vous donne un exemple de format de sortie attendu.
    *   Exposez toutes ces métriques via l'endpoint `/metrics`.
*   Configurez `deployment/prometheus/prometheus.yml` pour :
    *   Scraper votre API `bike-api`.
    *   Scraper `node-exporter`.
*   Créez un fichier `deployment/prometheus/rules/alert_rules.yml` et configurez au moins une règle d'alerte Prometheus (par exemple, si l'API est `down`).

**III. Visualisation Automatisée avec Grafana :**

*   Configurez Grafana pour qu'il soit lancé avec Docker Compose.
*   **Implémentez le "Dashboards as Code" :**
    *   Créez un dossier `deployment/grafana/dashboards/` et placez-y des fichiers JSON de dashboards préalablement crées (par vous même via l'interface, récupérés sur le Hub Grafana, etc.).
    *   Configurez le provisioning de Grafana via un fichier YAML (par exemple, `deployment/grafana/provisioning/dashboards.yaml`) pour qu'il charge automatiquement ces dashboards au démarrage.
*   **Créez trois dashboards distinct :**
    *   **Dashboard "API Performance" :** Doit inclure des panels pour le taux de requêtes, la latence (P95), et le taux d'erreur de votre API.
    *   **Dashboard "Model Performance & Drift" :** Doit inclure des panels pour les scores du modèle (`model_rmse_score`, `model_mae_score`, `model_r2_score`, etc.) et la métrique personnalisée que vous avez choisie (ex: score de dérive de données).
    *   **Dashboard "Infrastructure Overview" :** Doit inclure des panels pour l'utilisation CPU, RAM, et l'espace disque (via `node-exporter`).

    > Vous êtes libres d'ajouter des panels pour chacun de dashboards, si les metrics qu'ils suivent sont pertinentes pour le dashboard en question.

**IV. Alerting (Prometheus et Grafana) :**

*   Vous devez avoir une alerte configurée dans Prometheus, comme demandé plus haut.
*   **Configurez au moins une alerte directement dans l'interface de Grafana.** Cette alerte doit être basée sur une métrique ML (ex: si le RMSE du modèle dépasse un seuil, ou si votre métrique de dérive choisie indique un problème).

**V. Simulation de Trafic et Évaluation :**

*   Le script Python `run_evaluation.py` vous sera **fourni**. Ce script permettra de charger un echantillon de données du dataset "Bike Sharing" pour des périodes spécifiques (ex: semaines de février) et d'envoyer ces données à l'endpoint `/evaluate` de votre API. Vous devrez vous assurer que votre endpoint `/evaluate` accepte le format de données envoyé par ce script.
*   Fournissez un script simple (ou une commande `curl` répétée dans un script shell) pour générer du trafic sur l'endpoint `/predict` afin de simuler l'utilisation réelle de l'API.

**VI. Livrables :**

*   Rendez une **archive `.tar` ou `.zip`** de l'ensemble de votre projet.
*   L'archive doit contenir tous les fichiers nécessaires (votre `docker-compose.yml`, votre dossier `src`, votre dossier `deployment`, votre `makefile`, etc.).
*   Le projet doit contenir un **`Makefile` à la racine** avec les cibles suivantes :
    *   `all` : Pour démarrer tous les services (API, Prometheus, Grafana, Node Exporter).
    *   `stop` : Pour arrêter tous les services.
    *   `evaluation` : Pour exécuter le script `run_evaluation.py`, qui mettra à jour les métriques dans Prometheus.
    *   `fire-alert` : Pour déclencher intentionnellement une des alertes que vous avez configurées (ex: un endpoint `/trigger-drift` dans votre API qui simule une dérive en retournant des valeurs extrêmes à Evidently, ou en forçant le RMSE à être très élevé pour un petit lot de données). Vous devrez justifier quelle alerte est testée.

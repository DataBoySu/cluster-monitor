<!-- HTML_BLOCK:1... -->
<div align="center">
  <a href="../README.md">🇺🇸 Anglais</a> |
  <a href="../locales/README.de.md">🇩🇪 Allemand</a> |
  <a href="../locales/README.ru.md">🇷🇺 Russe</a> |
  <a href="../locales/README.fr.md">🇫🇷 Français</a> |
  <a href="../locales/README.es.md">🇪🇸 Espagnol</a> |
  <a href="../locales/README.ja.md">🇯🇵 Japonais</a> |
  <a href="../locales/README.zh.md">🇨🇳 Chinois</a> |
  <a href="../locales/README.pt.md">🇵🇹 Portugais</a> |
  <a href="../locales/README.ko.md">🇰🇷 Coréen</a> |
  <a href="../locales/README.hi.md">🇮🇳 Hindi</a>
</div>
<!-- HTML_BLOCK:2... -->
<div style="text-align:center; margin:18px 0;">
  <img src="../monitor/api/static/logo.png" alt="MyGPU logo"/>
</div>
<!-- HTML_BLOCK:... -->

> *MyGPU : Outil de gestion GPU léger : un wrapper compact pour `nvidia-smi` avec un tableau de bord web élégant.*

<!-- HTML_BLOCK: no change to url; output entire as it is... -->
![Licence](https://img.shields.io/badge/licence-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Version](https://img.shields.io/badge/version-1.2.3-blue)
![Plateforme](https://img.shields.io/badge/plateforme-Windows-lightgrey)
![cuda 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## Galerie

<details>

  <summary>
  Tableau de bord web
  </summary>

  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- Utilisez le rapport d'aspect 1624/675 pour la première image afin de créer un cadre de diapositive; les images s'ajustent automatiquement avec `object-fit:contain` -->
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/web1.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/web2.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/web3.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/web4.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
  </div>

</details>
<details>
  <summary>CLI</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/cli1.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/cli2.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/cli3.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/cli4.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
    <div style="flex:0 0 100%; scroll-snap-align:center; aspect-ratio:1624/675; display:flex; align-items:center; justify-content:center;">
      <img src="../monitor/api/static/cli5.png" style="width:100%; height:100%; object-fit:contain;" />
    </div>
  </div>
</details>

### Pourquoi l'utiliser ?

- **Léger** : empreinte ressource minimale.
- **Polyvalent** : disponible en version CLI, ou avec un tableau de bord web complet.
- **Administratif** : inclut des fonctionnalités comme **la limitation de VRAM** (arrêt automatique des processus dépassant les limites) et les **listes de surveillance**.
- **Amical pour le développeur** : intégration de tests de performance et de simulation physique (GEMM, physique des particules) pour valider la stabilité du système.

---

## Fonctionnalités

- **Surveillance en temps réel** :
  - Métriques détaillées sur les GPU (Utilisation, VRAM, Température).
  - Métriques système (CPU, RAM, etc.).

- **Administration et application de règles** :
  - **Limites de VRAM** : définissez des limites de VRAM par GPU.
  - **Arrêt automatique** : arrêtez automatiquement les processus qui violent les règles de politique VRAM (administrateur uniquement).
  - **Listes de surveillance** : surveillez des PIDs ou des noms de processus spécifiques.

- **Tests et simulation** :
  - **Tests de stress** : configurez des charges de travail GEMM pour tester la thermolage et la stabilité.
  - **Simulation physique** : visualisez la charge GPU avec une simulation physique interactive de particules.

---

## Roadmap et travaux futurs

Les contributions sont les bienvenues ! Les points principaux à couvrir seraient :

- **Prise en charge multi-GPU** : gestion améliorée des configurations multi-cartes et des topologies NVLink.
- **Conteneurisation** : prise en charge officielle de Docker pour un déploiement facile dans des environnements conteneurisés.
- **Accès à distance** : intégration du tunnel SSH et de la gestion à distance sécurisée.
- **Prise en charge multiplateforme** :
  - [ ] Linux (focalisation sur Ubuntu/Debian).
  - [ ] macOS (surveillance de la thermolage Apple Silicon).
- **Indépendance matérielle** :
  - [ ] Prise en charge d'AMD ROCm.
  - [ ] Prise en charge d'Intel Arc.
- ~~**Documentation multilingue** : prise en charge des langues les plus populaires sur GitHub.~~

Consultez [CONTRIBUTING.md](../CONTRIBUTING.md) pour savoir comment participer.

---

## Exigences

- **OS** : Windows 10/11
- **Python** : 3.10+
- **Matériel** : GPU NVIDIA avec pilotes installés.
- **CUDA** : Version 12.x (strictement requise pour les tests de performance/simulation).
  - *Note : Si CUDA 12.x n'est pas détecté, les fonctionnalités de test et de simulation seront désactivées.*

---

## Installation

L'outil offre plusieurs options d'installation :

### 1. Installation minimale (CLI uniquement)

Idéale pour les serveurs sans tête ou la surveillance en arrière-plan.

- Interface en ligne de commande.
- Surveillance de base du système et des GPU.

### 2. Installation standard (CLI + Tableau de bord web)

Idéale pour la plupart des utilisateurs.

- Inclut le tableau de bord web.
- Endpoints API REST.
- Graphiques en temps réel.
- Mais sans simulation ni tests de performance.

### 3. Installation complète (Standard + Visualisation)

Idéale pour le développement et les tests de performance.

- Inclut la simulation.
- Dépendances PyTorch/CuPy pour les tests de performance.

### Démarrage rapide

1. **Téléchargez** la dernière version ou clonez le dépôt.
2. **Installation** :

  ```powershell
  .\setup.ps1
  ```

3. **Lancement** :

```powershell
# Démarrage du tableau de bord web (Standard/Complete)
python health_monitor.py web

# Démarrage de l'interface CLI
python health_monitor.py cli
```
<!-- HTML_BLOCK:1... -->

<div align="center">
  <a href="../README.md">🇺🇸 English</a> |
  <a href="../locales/README.de.md">🇩🇪 Deutsch</a> |
  <a href="../locales/README.ru.md">🇷🇺 Русский</a> |
  <a href="../locales/README.fr.md">🇫🇷 Français</a> |
  <a href="../locales/README.es.md">🇪🇸 Español</a> |
  <a href="../locales/README.ja.md">🇯🇵 日本語</a> |
  <a href="../locales/README.zh.md">🇨🇳 中文</a> |
  <a href="../locales/README.pt.md">🇵🇹 Português</a> |
  <a href="../locales/README.ko.md">🇰🇷 한국어</a> |
  <a href="../locales/README.hi.md">🇮🇳 हिंदी</a>
</div>

<!-- HTML_BLOCK:2... -->

<div style="text-align:center; margin:18px 0;">
  <img src="../monitor/api/static/logo.png" alt="MyGPU logo"/>
</div>

<!-- HTML_BLOCK:... -->

> *MyGPU : Utilitaire de gestion de GPU léger : un wrapper compact pour `nvidia-smi` avec un tableau de bord web élégant.*

<!-- HTML_BLOCK: no change to url; output entire as it is... -->
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-pink)
![Version](https://img.shields.io/badge/version-1.4.0-green)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-blue)
![cuda 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## Galerie

<details>

  <summary>
    Tableau de bord web
  </summary>

  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- Utiliser le premier rapport d'aspect de l'image 1624x675 pour le cadre de diapositive; les images s'adaptent à l'intérieur avec object-fit:contain -->
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
  <summary>
  CLI
  </summary>
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
</details>

### Pourquoi l'utiliser ?

- **Légèreté** : Empreinte minimale en ressources.
- **Polyvalente** : Fonctionne en tant qu'outil en ligne de commande (CLI) ou sous forme de tableau de bord Web complet.
- **Centrée administration** : Inclut des fonctionnalités telles que **l'application de la VRAM** (arrêt automatique des processus dépassant les limites) et **les listes de surveillance**.
- **Amicale pour les développeurs** : Outils intégrés de test et de stress (GEMM, physique des particules) pour valider la stabilité du système.

## Fonctionnalités

- **Surveillance en temps réel** :
  - Métriques GPU détaillées (Utilisation, VRAM, Puissance, Température).
  - Métriques système (CPU, RAM, etc.).

- **Administration et contrôle** :
  - **Limites VRAM** : Définir des limites strictes sur l'utilisation de la VRAM par GPU.
  - **Arrêt automatique** : Arrêter automatiquement les processus qui violent les politiques VRAM (réservé aux administrateurs).
  - **Listes de surveillance** : Surveiller des PIDs ou des noms de processus spécifiques.

- **Benchmarking et simulation** :
  - **Tests de stress** : Chargements de travail GEMM configurables pour tester la throttling thermique et la stabilité.
  - **Simulation visuelle** : Simulation interactive de physique de particules 3D pour visualiser la charge sur le GPU.

## Roadmap et travaux futurs

Les contributions sont les bienvenues ! Les principaux points futurs à aborder sont :

- **Prise en charge multi-GPU** : Amélioration de la gestion des configurations multi-cartes et des topologies NVLink.
- **Conteneurisation** : Prise en charge officielle de Docker pour un déploiement facile dans des environnements conteneurisés.
- **Accès à distance** : Intégration du tunnel SSH et gestion à distance sécurisée.
- **Cross-Platform** :
  - [x] Support Linux (Ubuntu/Debian à l'accent).
  - [x] Support macOS (surveillance Apple Silicon).
- **Indépendant du matériel** :
  - [ ] Support AMD ROCm.
  - [ ] Support Intel Arc.
- ~~**Documentation multi-langues** : Prise en charge des langages GitHub les plus populaires.~~

Consultez [CONTRIBUTING.md](../CONTRIBUTING.md) pour savoir comment participer.

## Exigences

- **Système d'exploitation** : Windows 10/11, Linux, macOS
- **Python** : 3.10+
- **Matériel** : GPU NVIDIA (tous les systèmes), Apple Silicon (macOS), ou uniquement CPU.
- **CUDA** : Toolkit 12.x (Recommandé pour le benchmark/la simulation sur NVIDIA).
  - *Note : Si CUDA/MPS n'est pas détecté, certaines fonctionnalités de benchmark pourraient être désactivées.*

## Installation

L'outil prend en charge une installation modulaire pour s'adapter à vos besoins :

### 1. Minimal (Interface en ligne de commande uniquement)

Idéal pour les serveurs sans interface utilisateur ou la surveillance en arrière-plan.

- Interface en ligne de commande.
- Métriques de base système/GPU.

### 2. Standard (CLI + Interface Web)

Convient à la plupart des utilisateurs.

- Inclut le Tableau de bord Web.
- Points de terminaison API REST.
- Graphiques en temps réel.
- Mais sans Simulation ni benchmark.

### 3. Complet (Standard + Visualisation)

Idéal pour le développement et les tests de stress.

- Inclut la Simulation.
- Dépendances PyTorch/CuPy pour le benchmark.

### Démarrage Rapide

1. **Télécharger** ou cloner le dépôt.
2. **Exécuter l'installation**:

   **Windows**:

```powershell
   .\setup.ps1
   ```

**Linux/macOS** :

```bash
   chmod +x setup.sh
   ./setup.sh
```

3. **Lancement** :

```bash
# Démarrer le tableau de bord web (Standard/Complet)
python health_monitor.py web

# Démarrer l'interface CLI
python health_monitor.py cli
```

## Licence

Consultez [LICENSE](../LICENSE) pour plus de détails.


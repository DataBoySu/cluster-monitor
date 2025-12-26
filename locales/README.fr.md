# MyGPU: Outil de gestion de GPU léger

*MyGPU : Un utilitaire de gestion de GPU léger, un wrapper compact pour `nvidia-smi` avec un tableau de bord web élégant.*

<!-- Ne pas traduire la section des badges.io, conserver comme elle est -->
![Licence](https://img.shields.io/badge/licence-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Version](https://img.shields.io/badge/version-1.2.3-blue)
![Plateforme](https://img.shields.io/badge/plateforme-Windows-lightgrey)
![CUDA 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## Galerie

<details>
  <summary>Tableau de bord web</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- Utiliser la première image pour le cadre de diaporama avec un rapport de 1624x675; les autres images s'ajustent automatiquement -->
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
  <summary>Interface en ligne de commande (CLI)</summary>
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

### Pourquoi utiliser MyGPU ?

- **Légèreté** : Empreinte ressource minimale.
- **Flexibilité** : Disponible en outil CLI ou tableau de bord web.
- **Administration centrée** : Inclut des fonctionnalités telles que **l'enforcement de la mémoire VRAM** (arrêt automatique des processus dépassant les limites) et les **listes de surveillance**.
- **Amical pour les développeurs** : Outils intégrés de test de stabilité et de stress (GEMM, physique des particules) pour valider la stabilité du système.

---

## Fonctionnalités

- **Surveillance en temps réel** :
  - Métriques détaillées sur les GPU (Utilisation, VRAM, Puissance, Température).
  - Métriques système (CPU, RAM, etc.).

- **Administration et application de règles** :
  - **Limites de VRAM** : Définir des limites strictes sur l'utilisation de la VRAM par GPU.
  - **Arrêt automatique** : Arrêter automatiquement les processus qui violent les règles de VRAM (uniquement pour les administrateurs).
  - **Listes de surveillance** : Surveiller des PIDs ou des noms de processus spécifiques.

- **Benchmarking et simulation** :
  - **Tests de stress** : Configurer des charges de travail GEMM pour tester la throttling thermique et la stabilité.
  - **Simulation visuelle** : Simulation interactive de physique des particules pour visualiser la charge GPU.

---

## Roadmap et travaux futurs

Les contributions sont les bienvenues ! Les points principaux à couvrir seraient :

- **Support multi-GPU** : Gestion améliorée des configurations multi-cartes et des topologies NVLink.
- **Conteneurisation** : Support officiel pour Docker pour un déploiement facile dans des environnements conteneurisés.
- **Accès à distance** : Intégration du tunnel SSH et gestion à distance sécurisée.
- **Compatibilité multiplateforme** :
  - [ ] Support Ubuntu/Debian pour Linux.
  - [ ] Support Apple Silicon pour la surveillance.
- **Indépendance matérielle** :
  - [ ] Support AMD ROCm.
  - [ ] Support Intel Arc.
- ~~**Documentation multilingue** : Prise en charge des principales langues GitHub.~~

Voir [CONTRIBUTING.md](../CONTRIBUTING.md) pour savoir comment contribuer.

---

## Exigences

- **Système d'exploitation** : Windows 10/11
- **Python** : 3.10+
- **Matériel** : GPU NVIDIA avec pilotes installés.
- **CUDA** : Version 12.x (strictement requise pour les fonctionnalités de benchmarking/simulation).
  - *Note : Si CUDA 12.x n'est pas détecté, les fonctionnalités de benchmarking seront désactivées.*

---

## Installation

L'outil offre plusieurs options d'installation pour répondre à vos besoins :

### 1. Installation minimale (CLI uniquement)

Idéale pour les serveurs sans tête ou la surveillance en arrière-plan.

- Interface en ligne de commande.
- Surveillance de base du système et des GPU.

### 2. Installation standard (CLI + Tableau de bord web)

Idéale pour la plupart des utilisateurs.

- Inclut le tableau de bord web.
- Endpoints API REST.
- Graphiques en temps réel.
- Mais sans simulation ou benchmarking.

### 3. Installation complète (Standard + Visualisation)

Idéale pour le développement et les tests de stress.

- Inclut la simulation.
- Dépendances PyTorch/CuPy pour le benchmarking.

### Démarrage rapide

1. **Télécharger** la dernière version ou cloner le dépôt.
2. **Exécuter l'installation** :

  ```powershell
  .\setup.ps1
  ```

3. **Lancer** :

```powershell
# Démarrer le tableau de bord web (Standard/Complete)
python health_monitor.py web

# Démarrer l'interface en ligne de commande
python health_monitor.py cli
```
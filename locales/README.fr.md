<!-- HTML_BLOCK:1... -->
<div align="center">
  <a href="../README.md">🇺🇸 Anglais</a> |
  <a href="../locales/README.de.md">🇩🇪 Allemand</a> |
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

> *MyGPU : Un utilitaire de gestion GPU léger : un enveloppe compacte pour `nvidia-smi` avec un tableau de bord web élégant.*

<!-- HTML_BLOCK: no change to url; output entire as it is... -->
![Licence](https://img.shields.io/badge/licence-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Version](https://img.shields.io/badge/version-1.2.3-blue)
![Plateforme](https://img.shields.io/badge/plateforme-Windows-lightgrey)
![cuda 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## Galerie

<details>
  <summary>Tableau de bord web</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- Utilisez le rapport d'aspect 1624/675 pour la diapositive du cadre; les images s'adaptent à l'aide de object-fit:contain -->
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
    <!-- Mettez en place la même logique que pour le tableau de bord web -->

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

- **Léger** : Empreinte ressource minimale.
- **Polyvalent** : Fonctionne en tant qu'outil CLI, ou avec un tableau de bord web complet.
- **Administratif** : Inclut des fonctionnalités telles que **limites VRAM** (auto-arrêt des processus dépassant les limites) et **listes de surveillance**.
- **Amical pour les développeurs** : Intégré avec des outils de test et de simulation (GEMM, physique des particules) pour valider la stabilité du système.

---

## Fonctionnalités

- **Surveillance en temps réel** :
  - Métriques détaillées GPU (Utilisation, VRAM, Température).
  - Métriques système (CPU, RAM, etc.).

- **Administration et application de règles** :
  - **Limites VRAM** : Définir des limites dures sur l'utilisation de la VRAM par GPU.
  - **Arrêt automatique** : Arrêter automatiquement les processus qui violent les politiques VRAM (accès administrateur uniquement).
  - **Listes de surveillance** : Surveiller des PIDs ou des noms de processus spécifiques.

- **Benchmarking et simulation** :
  - **Tests de stress** : Utiliser des charges de travail GEMM configurables pour tester la thermo-throttling et la stabilité.
  - **Simulation physique** : Visualiser la charge GPU avec une simulation interactive de physique des particules 3D.

---

## Roadmap et travaux futurs

Les contributions sont les bienvenues ! Les principaux points à couvrir seraient :

- **Support multi-GPU** : Gestion améliorée des configurations multi-cartes et topologies NVLink.
- **Conteneurisation** : Support officiel Docker pour un déploiement facile dans des environnements conteneurisés.
- **Accès distant** : Intégration du tunnel SSH et gestion sécurisée de l'accès à distance.
- **Support multiplateforme** :
  - [ ] Linux (focussé sur Ubuntu/Debian).
  - [ ] macOS (support Apple Silicon pour la surveillance).
- **Support matériel non NVIDIA** :
  - [ ] Support AMD ROCm.
  - [ ] Support Intel Arc.
- ~~**Documentation multilingue** : Prendre en charge les langues les plus populaires sur GitHub.~~

Consultez [CONTRIBUTING.md](../CONTRIBUTING.md) pour savoir comment contribuer.

---

## Exigences

- **Système d'exploitation** : Windows 10/11
- **Python** : 3.10+
- **Matériel** : GPU NVIDIA avec pilotes installés.
- **CUDA** : Version 12.x (strictement requise pour les fonctionnalités de simulation et de test).
  - *Note : Si CUDA 12.x n'est pas détecté, les fonctionnalités de test et de simulation seront désactivées.*

---

## Installation

L'outil prend en charge une installation modulaire pour répondre à vos besoins :

### 1. Installation minimale (CLI uniquement)

Idéal pour les serveurs sans tête ou la surveillance en arrière-plan.

- Interface en ligne de commande.
- Métriques système et GPU de base.

### 2. Installation standard (CLI + Tableau de bord web)

Idéal pour la plupart des utilisateurs.

- Inclut le tableau de bord web.
- API REST pour les interactions.
- Graphiques en temps réel.
- Mais sans simulation ou fonctionnalités de test.

### 3. Installation complète (Standard + Visualisation)

Idéal pour le développement et les tests :

- Inclut la simulation.
- Dépendances PyTorch/CuPy pour les tests de performance.

---

## Instructions d'installation

> 1. **Télécharger** la dernière version ou cloner le dépôt.
> 2. **Lancer l'installation** :

```powershell
.\setup.ps1
```

> 3. **Lancer** :

```powershell
# Lancer le tableau de bord web (Standard/Complete)
python health_monitor.py web

# Lancer l'interface CLI
python health_monitor.py cli
```
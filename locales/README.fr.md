<div align="center">
  <a href="../README.md">🇺🇸 Anglais</a> |
  <a href="../README.de.md">🇩🇪 Allemand</a> |
  <a href="../README.fr.md">🇫🇷 Français</a> |
  <a href="../README.es.md">🇪🇸 Espagnol</a> |
  <a href="../README.ja.md">🇯🇵 Japonais</a> |
  <a href="../README.zh.md">🇨🇳 Chinois</a> |
  <a href="../README.pt.md">🇵🇹 Portugais</a> |
  <a href="../README.ko.md">🇰🇷 Coréen</a> |
  <a href="../README.hi.md">🇮🇳 Hindi</a>
</div>

<div style="text-align:center; margin:18px 0;">
  <img src="../monitor/api/static/logo.png" alt="MyGPU logo"/>
</div>

> *MyGPU : Outil de gestion de GPU léger : un wrapper compact pour `nvidia-smi` avec un tableau de bord web propre.*

![Licence](https://img.shields.io/badge/licence-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Version](https://img.shields.io/badge/version-1.2.3-blue)
![Plateforme](https://img.shields.io/badge/plateforme-Windows-lightgrey)
![cuda 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## Galerie

<details>
  <summary>Tableau de bord web</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- Utilisez la première image pour le cadre de diapositive avec un rapport d'aspect 1624/675; les autres images s'ajustent automatiquement -->
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
    <!-- Ajoutez d'autres images CLI ici -->
  </div>
</details>

### Pourquoi l'utiliser ?

- **Léger** : empreinte ressource minimale.
- **Polyvalent** : fonctionne comme outil en ligne de commande, service en arrière-plan ou tableau de bord web complet.
- **Orienté administration** : inclut des fonctionnalités telles que l'**application de politiques VRAM** (arrêt automatique des processus dépassant les limites) et les **listes de surveillance**.
- **Amical pour les développeurs** : outils intégrés de test de stabilité et de simulation (GEMM, physique des particules) pour valider la stabilité du système.

---

### Fonctionnalités

- **Surveillance en temps réel** :
  - Métriques détaillées sur les GPU (Utilisation, VRAM, Puissance, Température).
  - Métriques système (CPU, RAM, etc.).

- **Administration et application de politiques** :
  - **Limites VRAM** : définissez des limites dures sur l'utilisation de la VRAM par GPU.
  - **Arrêt automatique** : arrêtez automatiquement les processus qui violent les politiques VRAM (uniquement pour les administrateurs).
  - **Listes de surveillance** : surveillez des PIDs ou des noms de processus spécifiques.

- **Benchmarking et simulation** :
  - **Tests de stress** : configurez des charges de travail GEMM pour tester le throtting thermique et la stabilité.
  - **Simulation visuelle** : simulation interactive de physique des particules pour visualiser la charge de travail du GPU.

---

### Roadmap et travaux futurs

Les contributions sont les bienvenues ! Les points principaux à couvrir seraient :

- **Prise en charge multi-GPU** : gestion améliorée des configurations multi-cartes et des topologies NVLink.
- **Conteneurisation** : support officiel pour Docker pour un déploiement facile dans des environnements conteneurisés.
- **Accès à distance** : intégration du tunnel SSH et gestion à distance sécurisée.
- **Prise en charge multiplateforme** :
  - [ ] Linux (Ubuntu/Debian à l'accent).
  - [ ] macOS (surveillance Apple Silicon).
- **Indépendance matérielle** :
  - [ ] Prise en charge d'AMD ROCm.
  - [ ] Prise en charge d'Intel Arc.
- ~~**Documentation multilingue** : prise en charge des principales langues GitHub.~~

Consultez [CONTRIBUTING.md](../CONTRIBUTING.md) pour savoir comment participer.

---

### Exigences

- **Système d'exploitation** : Windows 10/11
- **Python** : 3.10+
- **Matériel** : GPU NVIDIA avec pilotes installés.
- **CUDA** : Version 12.x (strictement requise pour les fonctionnalités de benchmarking/simulation).
  - *Remarque : Si CUDA 12.x n'est pas détecté, les fonctionnalités de benchmarking seront désactivées.*

---

### Installation

L'outil prend en charge une installation modulaire pour répondre à vos besoins :

### 1. Installation minimale (CLI uniquement)

Idéale pour les serveurs sans tête ou la surveillance en arrière-plan.

- Interface en ligne de commande.
- Métriques système et GPU de base.

### 2. Installation standard (CLI + Tableau de bord web)

Idéale pour la plupart des utilisateurs.

- Inclut le tableau de bord web.
- Points de terminaison API REST.
- Graphiques en temps réel.

### 3. Installation complète (Standard + Simulation)

Idéale pour le développement et les tests de charge :

- Inclut la simulation de physique des particules.
- Dépendances PyTorch/CuPy pour le benchmarking.

### Démarrage rapide

1. **Téléchargez** la dernière version ou clonez le dépôt.
2. **Exécutez l'installation** :

  ```powershell
  .\setup.ps1
  ```

3. **Lancez** :

```powershell
# Démarrez le tableau de bord web (Standard/Complete)
python health_monitor.py web

# Lancez l'interface en ligne de commande
python health_monitor.py cli
```
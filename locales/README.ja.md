<div align="center">
  <a href="../README.md">🇺🇸 English</a> |
  <a href="../README.de.md">🇩🇪 Deutsch</a> |
  <a href="../README.fr.md">🇫🇷 Français</a> |
  <a href="../README.es.md">🇪🇸 Español</a> |
  <a href="../README.ja.md">🇯🇵 日本語</a> |
  <a href="../README.zh.md">🇨🇳 中文</a> |
  <a href="../README.pt.md">🇵🇹 Português</a> |
  <a href="../README.ko.md">🇰🇷 한국어</a> |
  <a href="../README.hi.md">🇮🇳 Hindi</a>
</div>

<div style="text-align:center; margin:18px 0;">
  <img src="../monitor/api/static/logo.png" alt="MyGPU logo"/>
</div>

> *マイGPU: 軽量GPU管理ユーティリティ: コンパクトな`nvidia-smi`ラッパーに洗練されたウェブダッシュボードを備えたものです。*

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Version](https://img.shields.io/badge/version-1.2.3-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![cuda 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## Gallery

<details>
  <summary>Web Dashboard</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- Use first image aspect ratio 1624x675 for slide frame; images fit inside using object-fit:contain -->
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

</details>

### このツールを使う理由

- **軽量**: 最小限のリソース消費。
- **柔軟**: CLIツールとして実行するか、完全なウェブダッシュボードとして実行可能。
- **管理者向け**: VRAM強制（制限を超えるプロセスを自動的に終了）やウォッチリストなどの機能が含まれています。
- **開発者向け**: システムの安定性を検証するための組み込みベンチマークとストレステストツール（GEMM、粒子物理学）を備えています。

---

## 特徴

- **リアルタイム監視**:
  - GPUメトリック（利用率、VRAM、電力、温度）。
  - システムメトリック（CPU、RAMなど）。

- **管理者および強制**:
  - **VRAMキャップ**: 各GPUに対してVRAM使用量の上限を設定。
  - **自動終了**: 管理者のみ、VRAMポリシーに違反するプロセスを自動的に終了（管理者のみ）。
  - **ウォッチリスト**: 特定のPIDやプロセス名を監視。

- **ベンチマークとシミュレーション**:
  - **ストレステスト**: 熱的スローイングと安定性をテストするための構成可能なGEMMワークロード。
  - **視覚シミュレーション**: インタラクティブな3D粒子物理学シミュレーションでGPU負荷を視覚化。

---

## ロードマップと将来の作業

貢献は歓迎します！主な今後のポイントは次のとおりです。

- **マルチGPUサポート**: マルチカードセットアップとNVLinkトポロジの処理を強化。
- **コンテナ化**: Docker公式サポートで、コンテナ環境への簡単なデプロイを実現。
- **リモートアクセス**: SSHトンネル統合とセキュアなリモート管理。
- **クロスプラットフォーム**:
  - [ ] Linuxサポート（Ubuntu/Debianに焦点を当てて）。
  - [ ] macOSサポート（Apple Siliconの監視）。
- **ハードウェア非依存**:
  - [ ] AMD ROCmサポート。
  - [ ] Intel Arcサポート。
- ~~**マルチ言語ドキュメント**: GitHubで最も人気のある言語でドキュメントをサポート。~~

[CONTRIBUTING.md](../CONTRIBUTING.md)を参照して、どのように貢献できるかを見てください。

---

## 要件

- **OS**: Windows 10/11
- **Python**: 3.10+
- **ハードウェア**: NVIDIA GPUにインストールされたドライバー。
- **CUDA**: 12.xツールキット（ベンチマーク/シミュレーション機能を有効にするには厳密に必要）。
  - *注: CUDA 12.xが検出されない場合は、GPU固有のベンチマーク機能が無効になります。*

---

## インストール

このツールは、ニーズに合わせてモジュール形式でインストールできます。

### 1. 最小（CLIのみ）

ヘッドレスサーバーやバックグラウンド監視に最適です。

- コマンドラインインターフェイス。
- 基本的なシステム/GPUメトリック。

### 2. 標準（CLI + Web UI）

ほとんどのユーザーに最適です。

- Webダッシュボードが含まれています。
- REST APIエンドポイント。
- リアルタイムチャート。

### 3. フル（標準 + 視覚化）

開発とストレステストに最適です。

- 粒子シミュレーションが含まれています。
- ベンチマークにはPyTorch/CuPy依存関係が必要です。

### クイックスタート

1. **ダウンロード** 最新リリースまたはリポジトリをクローンします。
2. **セットアップ実行**:

  ```powershell
  .\setup.ps1
  ```

3. **起動**:

```powershell
# Webダッシュボード（標準/フル）を起動
python health_monitor.py web

# CLIを起動
python health_monitor.py cli
```

---

## ライセンス

MITライセンス。[LICENSE](../LICENSE)で詳細をご確認ください。
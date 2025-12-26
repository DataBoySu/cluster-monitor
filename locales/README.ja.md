<div align="center">
  <a href="../README.md">🇺🇸 English</a> |
  <a href="README.de.md">🇩🇪 Deutsch</a> |
  <a href="README.fr.md">🇫🇷 Français</a> |
  <a href="README.es.md">🇪🇸 Español</a> |
  <a href="README.ja.md">🇯🇵 日本語</a> |
  <a href="README.zh.md">🇨🇳 中文</a> |
  <a href="README.pt.md">🇵🇹 Português</a> |
  <a href="README.ko.md">🇰🇷 한국어</a>
</div>

<div style="text-align:center; margin:18px 0;">
  <img src="../monitor/api/static/logo.png" alt="MyGPU ロゴ"/>
</div>

> *MyGPU: GPU 管理ユーティリティの軽量版: nvidia-smi のコンパクトラッパーにエレガントなウェブダッシュボードを組み込んだものです。*

![ライセンス](https://img.shields.io/badge/ライセンス-MIT-青.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![バージョン](https://img.shields.io/badge/バージョン-1.2.3-青)
![プラットフォーム](https://img.shields.io/badge/プラットフォーム-Windows-軽灰)
![cuda 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## ギャラリー

<details>
  <summary>ウェブダッシュボード</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x 必須; -webkit-overflow-scrolling:touch;">
    <!-- 最初の画像のアスペクト比を 1624x675 に設定し、他の画像は `object-fit: contain` を使用してフィット -->
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
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x 必須; -webkit-overflow-scrolling:touch;">
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

### 利用理由

- **軽量性**: リソース消費量が最小限に抑えられています。
- **柔軟性**: CLIツールとして、または完全なウェブダッシュボードとして利用可能です。
- **管理者向け機能**: VRAM制限（超過したプロセスを自動的に終了）やウォッチリストなどの機能を備えています。
- **開発者向け機能**: GEMMや粒子物理学シミュレーションなどのベンチマークツールを内蔵し、システムの安定性を視覚的に確認できます。

---

## 機能

- **リアルタイム監視**:
  - GPUメトリクス（利用率、VRAM、電力、温度）。
  - システムメトリクス（CPU、RAMなど）。
- **管理者向け機能**:
  - **VRAM制限**: 各GPUのVRAM使用量に上限を設定します。
  - **自動終了**: VRAMポリシーに違反するプロセスを自動的に終了（管理者のみ）。
  - **ウォッチリスト**: 特定のPIDやプロセス名を監視します。
- **ベンチマークとシミュレーション**:
  - **ストレステスト**: 構成可能なGEMMワークロードで、熱的スローや安定性をテストします。
  - **視覚シミュレーション**: インタラクティブな3D粒子物理学シミュレーションでGPU負荷を視覚化します。

---

## 今後の開発

貢献は歓迎します！今後の主な開発ポイントは以下の通りです。

- **マルチGPUサポート**: マルチカードセットアップやNVLinkトポロジーの処理を強化。
- **コンテナ化**: Docker公式サポートで、コンテナ環境での簡単なデプロイを実現。
- **リモートアクセス**: SSHトンネル統合とセキュアなリモート管理。
- **クロスプラットフォーム**:
  - [ ] Linuxサポート（Ubuntu/Debianに焦点を当てて）。
  - [ ] macOSサポート（Apple Siliconの監視）。
- **ハードウェア非依存**:
  - [ ] AMD ROCmサポート。
  - [ ] Intel Arcサポート。
- [ ] **マルチ言語ドキュメント**: GitHubで人気のある言語のドキュメントをサポート。

[CONTRIBUTING.md](../CONTRIBUTING.md) を参照して、どのように貢献できるか確認してください。

---

## 要件

- **OS**: Windows 10/11
- **Python**: 3.10+
- **ハードウェア**: NVIDIA GPU
- **CUDA**: 12.x (ベンチマーク/シミュレーション機能を使用する場合は必須)。
  - *注: CUDA 12.xが検出されない場合は、ベンチマーク機能が非対応になります。*

---

## インストール

ツールには、ニーズに合わせて複数のインストール方法があります。

### 1. 最小（CLIのみ）

ヘッドレスサーバーやバックグラウンド監視に最適です。

- コマンドラインインターフェースのみ。
- 基本的なシステム/GPUメトリクス。

### 2. 標準（CLI + ウェブUI）

ほとんどのユーザーに適しています。

- ウェブダッシュボードが含まれています。
- REST APIエンドポイント。
- リアルタイムチャート。

### 3. フル（標準 + 視覚化）

開発やストレステストに最適です。

- 粒子シミュレーションが含まれています。
- PyTorch/CuPy依存関係でベンチマーク機能を提供。

### クイックスタート

1. **最新版をダウンロードまたはリポジトリをクローンします。**
2. **セットアップスクリプトを実行します。**

  ```powershell
  .\setup.ps1
  ```

3. **起動します。**

```powershell
# ウェブダッシュボードを起動（標準/フル）
python health_monitor.py web

# CLIを起動
python health_monitor.py cli
```
# MyGPU: 軽量GPU管理ユーティリティ - 美しいウェブダッシュボード付きNVIDIA `nvidia-smi`ラッパー

> *MyGPU: 軽量GPU管理ユーティリティ - コンパクトな`nvidia-smi`ラッパーにエレガントなウェブダッシュボードを組み込んだものです。*

## ギャラリー

<details>
  <summary>ウェブダッシュボード</summary>
  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- 最初の画像を1624x675のアスペクト比で設定し、`object-fit: contain`を使用してスライドフレーム内に収まるようにします -->
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

### 利用理由

- **軽量**: リソース消費量が少ない。
- **柔軟性**: CLIツールとして、または完全なウェブダッシュボードとして利用可能。
- **管理者向け**: VRAM制限（超過プロセス自動終了）やウォッチリストなどの機能を備えている。
- **開発者向け**: 負荷テストやシミュレーション（GEMM、粒子物理学）のための組み込みツールを提供。

---

## 機能

- **リアルタイム監視**:
  - GPUメトリクス（利用率、VRAM、電力、温度）。
  - システムメトリクス（CPU、メモリなど）。

- **管理者向け機能**:
  - **VRAM制限**: 各GPUのVRAM使用量に上限を設定。
  - **自動終了**: VRAMポリシーを違反するプロセスを自動的に終了（管理者のみ）。
  - **ウォッチリスト**: 特定のPIDやプロセス名を監視。

- **ベンチマークとシミュレーション**:
  - **負荷テスト**: 構成可能なGEMMワークロードで熱的スローや安定性をテスト。
  - **視覚化シミュレーション**: インタラクティブな3D粒子物理学シミュレーションでGPU負荷を視覚化。

---

## 今後の開発

貢献は歓迎します！主な今後の開発ポイントは以下の通りです。

- **マルチGPUサポート**: マルチカードセットアップやNVLinkトポロジーの処理強化。
- **コンテナ化**: Docker公式サポートで環境構築を簡素化。
- **リモートアクセス**: SSHトンネル統合とセキュアなリモート管理。
- **クロスプラットフォーム**:
  - [ ] Linuxサポート（Ubuntu/Debianに焦点を当てて）。
  - [ ] macOSサポート（Apple Siliconの監視）。
- **ハードウェア非依存**:
  - [ ] AMD ROCmサポート。
  - [ ] Intel Arcサポート。
- [ ] マルチ言語ドキュメント（GitHubで人気のある言語をサポート）。

[CONTRIBUTING.md](../CONTRIBUTING.md) を参照して、どのように貢献できるか確認してください。

---

## 要件

- **OS**: Windows 10/11
- **Python**: 3.10+
- **ハードウェア**: NVIDIA GPU
- **CUDA**: 12.xツールキット（ベンチマーク/シミュレーション機能を使用する場合に必須）。
  - *注: CUDA 12.xが検出されない場合、GPU関連のベンチマーク機能が無効になります。*

---

## インストール

ツールには、ニーズに合わせて複数のインストール方法があります。

### 1. 最小（CLIのみ）

サーバーやバックグラウンド監視に最適です。

- コマンドラインインターフェースのみ。
- 基本的なシステム/GPUメトリクス。

### 2. 標準（CLI + ウェブUI）

ほとんどのユーザーに最適です。

- ウェブダッシュボードが含まれています。
- REST APIエンドポイント。
- リアルタイムチャート。
- シミュレーションやベンチマークは含まれません。

### 3. フル（標準 + 視覚化）

開発やストレステストに最適です。

- 視覚化機能が含まれています。
- PyTorch/CuPy依存関係でベンチマーク機能が利用可能。

### クイックスタート

1. **ダウンロード** またはリポジトリをクローンします。
2. **セットアップスクリプトを実行**:

  ```powershell
  .\setup.ps1
  ```

3. **起動**:

```powershell
# ウェブダッシュボードを起動（標準/フル）
python health_monitor.py web

# CLIを起動
python health_monitor.py cli
```
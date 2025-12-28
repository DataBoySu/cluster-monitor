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

> *MyGPU: 軽量GPU管理ユーティリティ: 洗練されたウェブダッシュボードを備えたコンパクトな`nvidia-smi`ラッパーです。*~nyan!

<!-- HTML_BLOCK: no change to url; output entire as it is... -->
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-pink)
![Version](https://img.shields.io/badge/version-1.2.3-green)
![Platform](https://img.shields.io/badge/platform-Windows10/11-blue)
![cuda 12.x](https://img.shields.io/badge/CUDA-12.x-0f9d58?logo=nvidia)

## ギャラリー

<details>

  <summary>
    ウェブダッシュボード
  </summary>

  <div style="display:flex; overflow-x:auto; gap:10px; padding:12px 0; scroll-snap-type:x mandatory; -webkit-overflow-scrolling:touch;">
    <!-- 最初の画像を1624x675のアスペクト比で利用し、スライドフレームに適合させます。画像はobject-fit:containで内側に収まります -->
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

~nyan!

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

### なぜこれを使うの？

- **軽量**: リソースの足場が最小限。
- **柔軟**: コマンドライン（CLI）ツールとして、または機能豊富なウェブダッシュボードとして実行可能。
- **管理者向け**: VRAM強制（制限を超えるプロセスを自動的に終了）やウォッチリストなどの機能が含まれています。
- **開発者向け**: 組み込みベンチマークとストレステストツール（GEMM、粒子物理学）でシステムの安定性を検証。~nyan!

## 機能

- **リアルタイム監視**
  - GPUの詳細なメトリクス（利用率、VRAM、電力、温度）
  - システムメトリクス（CPU、RAMなど）

- **管理および執行**
  - **VRAMキャップ**：GPUごとにVRAM使用量の上限を設定
  - **自動終了**：VRAMポリシーに違反するプロセスを自動的に終了（管理者のみ）
  - **ウォッチリスト**：特定のPIDまたはプロセス名を監視

- **ベンチマークおよびシミュレーション**
  - **ストレステスト**：GEMMワークロードを設定して、熱的スロットリングと安定性をテスト
  - **視覚シミュレーション**：インタラクティブな3D粒子物理シミュレーションでGPUの負荷を可視化

## ロードマップと将来の取り組み

貢献をお待ちしています！今後の主な取り組みポイントは次のとおりです。

- **マルチGPUサポート**: マルチカードセットアップとNVLinkトポロジの強化処理。
- **コンテナ化**: Docker公式サポートで、コンテナ環境での簡単なデプロイを実現。
- **リモートアクセス**: SSHトンネル統合とセキュアなリモート管理。
- **クロスプラットフォーム**:
  - [ ] Linuxサポート（Ubuntu/Debianに焦点を当てて）。
  - [ ] macOSサポート（Apple Siliconの監視）。
- **ハードウェアに依存しない**:
  - [ ] AMD ROCmサポート。
  - [ ] Intel Arcサポート。
- **~~マルチ言語ドキュメント**: GitHubで最も人気のある言語のサポート。~~

[CONTRIBUTING.md](../CONTRIBUTING.md)をご覧ください。参加方法はこちらです。~nyan!~

## 要件

- **OS**: Windows 10/11
- **Python**: 3.10以上
- **ハードウェア**: NVIDIA GPUおよびインストール済みドライバー
- **CUDA**: 12.xツールキット（ベンチマーク/シミュレーション機能を使用するには必須です）

- *注意: CUDA 12.xが検出されない場合は、GPU固有のベンチマーク機能が無効になります。*

## インストール

このツールは、ニーズに合わせてモジュール形式でインストールできます。~nyan!

### 1. 最小限（CLIのみ）

ヘッドレスサーバーやバックグラウンドモニタリングに最適です。

- コマンドラインインターフェース。
- 基本的なシステム/GPUメトリクス。~nyan!

### 2. 標準（CLI + Web UI）

ほとんどのユーザーに最適です。

- Webダッシュボードが含まれています。
- REST APIエンドポイント
- リアルタイムチャート
- シミュレーションやベンチマークは含まれていません。~nyan!

### 3. フル（標準＋可視化）

開発やストレステストに最適です。

- シミュレーション機能が含まれています。
- PyTorch/CuPyの依存関係がベンチマークのために用意されています。~nyan!

### クイックスタート

1. **ダウンロード** 最新バージョンまたはリポジトリをクローンしてください。
2. **セットアップを実行**してにゃん！

```powershell
  .\setup.ps1
  ```

3. **起動**:

```powershell
# ウェブダッシュボード（標準/フル）を起動
python health_monitor.py web

# CLIを起動
python health_monitor.py cli
```

~nyan!

---

## License

<summary>詳細については[LICENSE](../LICENSE)をご覧ください。</summary>~nyan!


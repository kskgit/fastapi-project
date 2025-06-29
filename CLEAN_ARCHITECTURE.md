# Clean Architecture - Layer Dependencies

このプロジェクトはClean Architectureを採用し、各技術レイヤー毎に`pyproject.toml`を配置して依存関係を制御しています。

## 📁 ディレクトリ構造

```
app/clean/
├── domain/              # ドメイン層（最内側）
│   ├── pyproject.toml   # 依存関係: なし
│   ├── entities/        # ドメインエンティティ
│   └── repositories/    # Repository Interface
├── infrastructure/      # インフラ層
│   ├── pyproject.toml   # 依存関係: domain, core
│   ├── database/        # データベース関連
│   └── repositories/    # Repository Implementation
├── services/           # サービス層
│   ├── pyproject.toml   # 依存関係: domain のみ
│   └── todo_service.py  # ビジネスロジック
├── api/                # API層（最外側）
│   ├── pyproject.toml   # 依存関係: domain, services
│   ├── dtos/           # API用DTO
│   └── endpoints/      # FastAPIエンドポイント
└── core/               # 共通層
    ├── pyproject.toml   # 依存関係: なし
    ├── config.py        # 設定
    └── database_clean.py # データベース設定
```

## 🔄 依存関係ルール

Clean Architectureの依存性逆転の原則に従い、以下の依存関係を強制しています：

### Domain層 (domain/)
- **依存先**: なし（純粋なビジネスロジック）
- **役割**: エンティティ、Repository Interface
- **制約**: 外部ライブラリ一切禁止

### Infrastructure層 (infrastructure/)
- **依存先**: Domain, Core
- **役割**: データベース、外部サービス、フレームワーク詳細
- **制約**: Domain Interface を実装

### Services層 (services/)
- **依存先**: Domain のみ
- **役割**: アプリケーションのビジネスロジック
- **制約**: Infrastructure層への直接依存禁止

### API層 (api/)
- **依存先**: Domain, Services
- **役割**: HTTP エンドポイント、DTO、Web フレームワーク
- **制約**: Infrastructure層への直接依存禁止

### Core層 (core/)
- **依存先**: なし
- **役割**: 共通設定、ユーティリティ
- **制約**: 他の内部レイヤーへの依存禁止

## 🔍 依存関係チェック

依存関係の違反を自動検出するスクリプトを提供しています：

```bash
python scripts/check_dependencies.py
```

### チェック内容
- 各層が許可された依存関係のみを持っているか
- Clean Architectureの依存性逆転の原則が守られているか
- 外向きの依存関係が存在しないか

## 🏗️ レイヤー別pyproject.toml

各レイヤーに独立した`pyproject.toml`を配置し、以下を管理：

### 1. 依存関係制御
```toml
dependencies = [
    "domain @ file://../../domain",  # 許可された依存のみ
]
```

### 2. 開発ツール設定
```toml
[tool.mypy]
disallow_any_unimported = true  # 不正なimportを禁止
```

### 3. レイヤー固有設定
各レイヤーの特性に応じたlint・type checkルール

## 🚀 利点

### 1. 強制的な依存関係制御
- コンパイル時に依存関係違反を検出
- Clean Architectureルールの自動強制

### 2. レイヤー独立性
- 各レイヤーが独立してテスト可能
- レイヤー毎の異なる開発制約

### 3. 保守性向上
- 技術詳細の変更が他レイヤーに影響しない
- ビジネスロジックがフレームワークから独立

### 4. チーム開発支援
- 新メンバーでも依存関係を間違えない
- コードレビューで構造違反を自動検出

## 📋 開発ガイドライン

### DO's ✅
- Domain Entity にビジネスルールを集約
- Services層で Repository Interface のみ使用
- Infrastructure層で外部ライブラリの詳細を隠蔽
- API層で HTTP 詳細とビジネスロジックを分離

### DON'Ts ❌
- Services層で SQLAlchemy を直接import
- Domain層で FastAPI を import
- API層で Infrastructure の実装詳細に依存
- Core層で他の内部レイヤーに依存

## 🔧 セットアップ

1. 依存関係インストール：
```bash
uv sync
```

2. 依存関係チェック：
```bash
python scripts/check_dependencies.py
```

3. テスト実行：
```bash
uv run pytest tests/unit/services/test_todo_service_clean.py -v
```

4. 静的解析：
```bash
uv run ruff check .
uv run mypy .
```

この構造により、Clean Architectureの原則を技術的に強制し、保守性の高いコードベースを実現しています。
# FastAPI プロジェクト概要

## プロジェクトの目的
FastAPIを使用したTodo管理システム。Clean Architectureパターンを採用し、レイヤー間の依存関係を厳密に管理している。

## 技術スタック
- **フレームワーク**: FastAPI
- **言語**: Python 3.12+
- **パッケージ管理**: uv
- **データベース**: PostgreSQL (SQLAlchemy ORM)
- **マイグレーション**: Alembic
- **コード品質**: ruff (linting & formatting), mypy (型チェック), import-linter
- **複雑度チェック**: lizard
- **テスト**: pytest
- **タスクランナー**: Task (Taskfile.yml)
- **Git hooks**: lefthook

## アーキテクチャ
Clean Architectureを採用し、以下のレイヤーに分離：
- **Controller**: API層、バリデーション、UseCase呼び出し
- **UseCase**: ビジネスロジック、Domain層とInfrastructure層の組み合わせ
- **Domain**: 純粋なビジネスロジック（外部依存なし）
- **Infrastructure**: 外部ストレージ、データベース操作
- **DI**: 依存性注入（Composition Root）

## 主要機能
- ユーザー管理（CRUD）
- Todo管理（CRUD）
- サブタスク管理
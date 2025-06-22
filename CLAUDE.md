# FastAPI Todo管理API - Repository Pattern 実装

## プロジェクト概要
FastAPI × SQLAlchemyを使用したTodo管理APIをRepository Patternで実装する。
Service層をデータベース詳細から完全に保護し、テスト容易性と保守性を向上させる。

## アーキテクチャ方針

### 層構造
```
API層 (FastAPI) → Service層 → Repository層 → SQLAlchemy ORM → Database
```

### 重要な原則
1. **Service層はSQLAlchemyを一切知らない** - Domain EntityとRepositoryインターフェースのみ使用
2. **Repository層がSQLAlchemyの詳細を隠蔽** - クエリ最適化、Lazy Loading対策を実施
3. **Domain Entityは純粋なビジネスロジック** - データベース実装に依存しない
4. **依存性注入でテスト容易性を確保** - Repositoryはインターフェースで抽象化

## ディレクトリ構造

```
app/
├── domain/                 # ドメイン層（ビジネスロジック）
│   ├── __init__.py
│   ├── entities/           # Domain Entity
│   │   ├── __init__.py
│   │   └── todo.py
│   └── repositories/       # Repository Interface
│       ├── __init__.py
│       └── todo_repository.py
├── infrastructure/         # インフラ層（技術詳細）
│   ├── __init__.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py   # DB接続設定
│   │   └── models.py       # SQLAlchemy Models
│   └── repositories/       # Repository Implementation
│       ├── __init__.py
│       └── sqlalchemy_todo_repository.py
├── services/               # Service層（ビジネスロジック）
│   ├── __init__.py
│   └── todo_service.py
├── api/                    # API層（インターフェース）
│   ├── __init__.py
│   ├── dtos/               # API用DTO
│   │   ├── __init__.py
│   │   └── todo_dto.py
│   └── endpoints/
│       ├── __init__.py
│       └── todos.py
├── tests/                  # テスト
│   ├── __init__.py
│   ├── unit/               # 単体テスト
│   │   ├── services/
│   │   └── repositories/
│   └── integration/        # 統合テスト
└── main.py                 # FastAPI app
```

## 実装要件

### 1. Domain Entity (domain/entities/todo.py)
- **純粋なビジネスロジック**のみ実装
- SQLAlchemy, FastAPI に一切依存しない
- dataclass または Pydantic BaseModel を使用
- ビジネスルール（バリデーション、状態変更）を含む

**必要なメソッド例:**
- `Todo.create(title, description)` - 新規Todo作成
- `todo.mark_completed()` - 完了状態に変更
- `todo.is_overdue()` - 期限切れチェック
- `todo.can_be_deleted()` - 削除可能チェック

### 2. Repository Interface (domain/repositories/todo_repository.py)
- **抽象基底クラス**でインターフェースを定義
- Service層が依存するのはこのインターフェースのみ
- Domain Entityのみを引数・戻り値に使用
- SQLAlchemyに関する情報は一切含まない

**必要なメソッド:**
- `save(todo: Todo) -> Todo`
- `find_by_id(todo_id: int) -> Optional[Todo]`
- `find_all_by_user_id(user_id: int) -> List[Todo]`
- `find_active_todos(user_id: int) -> List[Todo]`
- `delete(todo_id: int) -> bool`

### 3. SQLAlchemy Repository Implementation (infrastructure/repositories/sqlalchemy_todo_repository.py)
- Repository Interfaceの具体実装
- SQLAlchemyの詳細知識を要求
- **Lazy Loading対策**を実装（eager loadingなど）
- **クエリ最適化**を実装
- SQLAlchemy Model ↔ Domain Entity の変換を担当

**重要な実装ポイント:**
- N+1問題を回避するクエリ最適化
- トランザクション管理
- エラーハンドリング（SQLAlchemy例外 → ドメイン例外への変換）

### 4. Service Layer (services/todo_service.py)
- **ビジネスロジックのみ**実装
- Repository Interfaceに依存
- Domain Entityのみ使用
- 複数のRepositoryを組み合わせた複雑な処理

**実装すべきメソッド例:**
- `create_todo(user_id, title, description, due_date)`
- `complete_todo(user_id, todo_id)`
- `get_user_todo_summary(user_id)` - 統計情報
- `get_overdue_todos(user_id)`

### 5. API Layer (api/endpoints/todos.py)
- FastAPI エンドポイント実装
- API DTO ↔ Domain Entity の変換
- Service層の呼び出し
- HTTP ステータスコード、エラーハンドリング

### 6. Dependency Injection (main.py)
- FastAPIの依存性注入を使用
- Repository Interface → Implementation のバインド
- Database session の管理
- Service層への依存注入

## 実装順序

### Phase 1: Domain層の実装
1. Domain Entity (Todo) の実装
2. Repository Interface の定義
3. 基本的なビジネスルールの実装

### Phase 2: Infrastructure層の実装
1. SQLAlchemy Models の実装
2. Database connection の設定
3. Repository Implementation の実装
4. Domain Entity ↔ SQLAlchemy Model 変換の実装

### Phase 3: Service層の実装
1. 基本的なCRUD操作のService実装
2. 複雑なビジネスロジックの実装
3. 複数Repositoryを使用した処理の実装

### Phase 4: API層の実装
1. API DTO の定義
2. FastAPI エンドポイントの実装
3. 依存性注入の設定
4. エラーハンドリングの実装

### Phase 5: テストの実装
1. Repository の単体テスト（モック使用）
2. Service の単体テスト（Repository モック使用）
3. API の統合テスト

## 技術仕様

### 使用ライブラリ
- **FastAPI** - Web フレームワーク
- **SQLAlchemy** - ORM
- **Pydantic** - データバリデーション
- **pytest** - テストフレームワーク
- **pytest-mock** - モックライブラリ

### データベース
- **開発**: SQLite
- **本番**: PostgreSQL対応可能な設計

### エラーハンドリング戦略
- **Domain Exception**: ビジネスルール違反
- **Repository Exception**: データアクセスエラー
- **API Exception**: HTTP レスポンス用

## パフォーマンス考慮事項

### Repository層での最適化
1. **Eager Loading** - 関連データの事前取得
2. **Query Optimization** - 効率的なSQL生成
3. **Batch Operations** - 複数レコードの一括処理

### キャッシュ戦略
- Repository層でのクエリ結果キャッシュ（将来拡張）

## テスト戦略

### 単体テスト
- **Service層**: Repository をモックして純粋なビジネスロジックをテスト
- **Repository層**: インメモリDBまたはモックでデータアクセスをテスト

### 統合テスト
- **API層**: 実際のDBを使用してエンドツーエンドテスト

## セキュリティ考慮事項
- SQL Injection 対策（SQLAlchemy ORM使用）
- 認証・認可（JWT Token想定）
- データアクセス権限の制御

## コード品質基準
- **型ヒント**: 全メソッドに必須
- **docstring**: public メソッドに必須
- **テストカバレッジ**: 80%以上
- **Linting**: flake8, black使用

## 実装時の注意点

### Domain層
- SQLAlchemy import を絶対に行わない
- 外部ライブラリへの依存を最小化
- ビジネスルールは Domain Entity に集約

### Repository層
- lazy loading を意識したクエリ実装
- SQLAlchemy 例外をドメイン例外に変換
- トランザクション境界を適切に設定

### Service層
- Repository Interface のみに依存
- 複雑なビジネスロジックはここに実装
- ドメイン例外のハンドリング

### API層
- HTTP詳細はこの層でのみ扱う
- 適切なステータスコードの返却
- API DTOとDomain Entityの変換

## 将来の拡張性
- 複数データソース対応（MongoDB, Redis等）
- マイクロサービス分割時の容易性
- CI/CDパイプラインでのテスト実行

## 参考実装例
各層の具体的な実装例は、実装時に段階的に提供します。

このアーキテクチャにより、保守性が高く、テストしやすく、技術変更に強いTodo管理APIを構築できます。
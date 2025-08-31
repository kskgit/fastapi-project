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

本プロジェクトでは、層別責任に基づく統一的なエラーハンドリング戦略を採用し、保守性と一貫性を確保する。

#### エラー種別と層別責任

**1. Domain Entity層 (domain/entities/)**
- **ValueError**: ビジネスルール違反時に発生
- 例: 完了済みTodoの再完了、キャンセル済みTodoの進行中変更
- 純粋なビジネスロジック検証のみを実装

**2. Service層 (services/)**
- **ValueError**: ドメインレベルのビジネスエラー
  - 例: `Todo with id {id} not found` (リソース未発見)
  - 例: ページネーション制限違反
- **RuntimeError**: 想定外のシステムエラー
  - 例: `Failed to create todo: {reason}` (作成処理失敗)
  - Repository層からの例外をラップして発生

**3. Repository層 (infrastructure/repositories/)**
- SQLAlchemy例外を適切にハンドリング
- Service層へは統一された例外で伝播
- データベース固有のエラーを隠蔽

**4. API層 (api/endpoints/)**
- FastAPI Exception Handlerで統一的に処理
- ドメイン例外を適切なHTTPステータスコードに変換
- エンドポイント内でのtry-catchは不要

#### FastAPI Exception Handler実装

**main.py でのグローバル例外ハンドラー**

```python
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """ビジネスエラーのハンドリング
    
    - "not found" を含む場合: 404 NOT FOUND
    - その他: 400 BAD REQUEST
    """
    error_message = str(exc)
    if "not found" in error_message.lower():
        raise HTTPException(status_code=404, detail=error_message)
    raise HTTPException(status_code=400, detail=error_message)

@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    """システムエラーのハンドリング"""
    raise HTTPException(
        status_code=500, 
        detail=f"Internal server error: {str(exc)}"
    )
```

#### エラーハンドリングの利点

**1. コード重複の削除**
- エンドポイント毎のtry-catchブロックを排除
- エラーハンドリングロジックの一元化

**2. 一貫性の確保**
- 統一されたエラーレスポンス形式
- HTTPステータスコードの一貫した使用

**3. 保守性の向上**
- エラーハンドリング変更時の単一更新箇所
- 新しいエラー種別の追加が容易

**4. テストの簡素化**
- エンドポイントテストでエラーハンドリングロジックのテストが不要
- Exception Handlerの単体テストで十分

#### エラーメッセージ戦略

**Domain Entity**
```python
# ビジネスルール違反の明確な表現
raise ValueError("Todo is already completed")
raise ValueError("Cannot complete a canceled todo")
```

**Service層**
```python
# リソース特定とエラー理由の明確化
raise ValueError(f"Todo with id {todo_id} not found")
raise RuntimeError(f"Failed to create todo: {str(e)}")
```

**API層**
```python
# Exception Handlerが自動的に適切なHTTPレスポンスに変換
# エンドポイント内では例外処理を記述せず、ビジネスロジックに集中
```

この戦略により、各層の責任が明確化され、エラーハンドリング関連のコードが大幅に削減される。

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

---

## 実装進捗とメモリ (2025-01-05)

### 完了した作業

#### 1. Clean Architecture層構造の実装
- `app/clean/` 配下に5層構造を構築
- API、UseCases、Domain、Infrastructure、Services の分離完了

#### 2. Import制約の実装
- **import-linter** を導入して層間依存関係を制約
- `pyproject.toml` で各層の禁止importを設定
- ruffの層別設定は廃止し、import-linterで一元管理

#### 3. UseCaseパターンの導入
- `TodoService.create_todo` を `CreateTodoUseCase.execute` に分離
- 1クラス1メソッドの原則でUseCase実装
- `app/clean/usecases/create_todo_usecase.py` を作成

#### 4. マルチユーザー対応
- **User Entity** (`app/clean/domain/entities/user.py`) を作成
- **Todo Entity** にuser_idフィールドを追加
- **UserRepository Interface** を作成
- User-Todo関連付けでマルチユーザー管理を実現

#### 5. データベース層の更新  
- SQLAlchemy ModelsにUserModelを追加
- TodoModelにuser_id外部キーを追加
- User-Todo間の1対多リレーションシップを設定

#### 6. タスク管理コマンドの追加
- **Taskfile.yml** に `db-rest` コマンドを追加
- alembic downgrade base → revision → upgrade の自動化

### 現在の技術構成

#### 依存性管理
- **import-linter**: 層間依存関係の制約
- **ruff**: コードフォーマット・リント
- **mypy**: 型チェック（層別設定）
- **pytest**: テストフレームワーク

#### アーキテクチャパターン
- **Repository Pattern**: データアクセス抽象化
- **UseCase Pattern**: ビジネスロジック単一責任
- **Domain-Driven Design**: 純粋ドメインエンティティ
- **Dependency Injection**: FastAPIによる依存注入

### 未完了の作業

#### 1. Repository実装の更新
- [ ] **SQLAlchemyTodoRepository** のuser_id対応
- [ ] **SQLAlchemyUserRepository** の完全実装
- [ ] Domain Entity ↔ SQLAlchemy Model 変換の更新

#### 2. API層の更新
- [ ] API DTOのuser_id対応（TodoCreateDTO等）
- [ ] エンドポイントのマルチユーザー対応
- [ ] 認証・認可システムの実装

#### 3. その他の実装
- [ ] 他のUseCaseクラスの実装（UpdateTodo、DeleteTodo等）
- [ ] テストの更新（マルチユーザー対応）
- [ ] データベースマイグレーションの実行

### 実行予定のコマンド

```bash
# データベースリセット（次回セッション開始時に実行）
task db-rest

# または手動で
uv run alembic downgrade base
uv run alembic revision --autogenerate -m "Reset: User and Todo models"  
uv run alembic upgrade head
```

### 技術的注意点

#### Clean Architecture制約
- Domain層はSQLAlchemy/FastAPI禁止
- Services層はinfrastructure層直接アクセス禁止  
- API層はSQLAlchemy禁止
- UseCases層は独立性維持

#### マルチユーザー対応
- 全TodoはUser.idとの関連付け必須
- 認証後のuser_idをUseCase層で受け取り
- Todoアクセス時の所有権チェック実装

#### データベース管理
- alembicによるマイグレーション管理
- PostgreSQL本番対応済み設定
- 開発時はdb-restコマンドでリセット可能

### 次回開始時の優先タスク

1. **db-rest実行** でデータベース状態をクリーンアップ
2. **Repository実装の更新** でuser_id対応完了
3. **API層の更新** でエンドツーエンド動作確認
4. **認証システム追加** で実用性向上

このメモリを基に、次回セッションでは効率的に作業を継続できます。

---

## 重要な実装ルール

### Git操作に関する制約
- **NEVER run `git add` automatically** - ユーザーが明示的に指示した場合のみ実行
- **Git commit前の確認必須** - コミット前に必ずユーザーの承認を得る
- **Git操作は慎重に** - 自動的なステージング、コミット、プッシュを禁止

### 推奨ワークフロー
1. コード変更後、必ずユーザーに確認を求める
2. ユーザーが承認した場合のみ `git add` を実行
3. `git commit` 前に再度確認を求める
4. プッシュは明示的な指示がない限り実行しない

この制約により、ユーザーが意図しないGit操作を防ぎ、開発プロセスの安全性を確保する。
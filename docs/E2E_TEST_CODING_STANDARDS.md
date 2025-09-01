# E2E テスト コーディング規約

## 基本方針

### テスト設計の原則
E2Eテストは**レスポンスコード単位**で実装し、各HTTPステータスコードの代表的なケースを網羅する。
詳細なビジネスロジックのバリエーションは単体テストでカバーする。

### 責務分離
- **E2Eテスト**: HTTPインターフェース契約の検証
- **単体テスト**: ビジネスロジックの詳細検証

## テスト実装規約

### 1. テストクラス命名規則

```python
class Test{Entity}{Action}E2E:
    """E2E tests for {entity} {action} via HTTP API."""
    
# 例
class TestCreateTodoE2E:
    """E2E tests for todo creation via HTTP API."""
```

### 2. テストメソッド命名規則

```python
async def test_{action}_{entity}_{scenario}_{status_code}(self):
    """Test {action} {entity} {scenario description} → {status_code}"""

# 例
async def test_create_todo_success_201(self):
    """Test successful todo creation → 201"""
    
async def test_create_todo_validation_error_400(self):
    """Test todo creation with invalid data → 400"""
    
async def test_create_todo_user_not_found_404(self):
    """Test todo creation with non-existent user → 404"""
```

### 3. レスポンスコード別実装パターン

#### 2xx Success
```python
async def test_create_todo_success_201(self):
    """正常系の代表例（最もシンプルなケース）"""
    # 基本的な入力値で成功パターンを検証
    # レスポンス構造とステータスコードを確認
    # DB永続化を GET エンドポイントで検証
```

#### 4xx Client Error
```python
async def test_create_todo_validation_error_400(self):
    """バリデーションエラーの代表例"""
    # 明らかに不正な入力値
    # エラーレスポンス形式の確認
    # DB変更がないことを確認
    
async def test_create_todo_user_not_found_404(self):
    """リソース未発見エラー"""
    # 存在しないリソースへのアクセス
    # 適切なエラーメッセージの確認
```

#### 5xx Server Error
```python
async def test_create_todo_server_error_500(self):
    """サーバーエラーの代表例"""
    # DB接続エラーなどのシミュレーション
    # 適切なエラーハンドリングの確認
```

### 4. テスト構造規約

```python
async def test_method_name(self):
    """Test description."""
    # Arrange - テストデータ準備
    request_data = {
        "field": "value"
    }
    
    # Act - HTTP リクエスト実行
    response = await test_client.post("/endpoint", json=request_data)
    
    # Assert - レスポンス検証
    assert response.status_code == expected_status
    response_data = response.json()
    
    # Assert - レスポンス構造検証
    assert "required_field" in response_data
    
    # Assert - DB状態確認（必要に応じて）
    verification_response = await test_client.get(f"/endpoint/{id}")
    assert verification_response.status_code == 200
```

### 5. 検証項目

#### 必須検証項目
- **HTTPステータスコード**: 期待値との一致
- **レスポンス構造**: 必須フィールドの存在
- **データ型**: レスポンスフィールドの型確認

#### 推奨検証項目
- **DB永続化**: GETリクエストでの確認
- **エラーメッセージ**: 適切なエラー情報
- **副作用**: 他のリソースへの影響確認

### 6. データ準備規約

#### テストデータ原則
```python
# ✅ Good: シンプルで理解しやすい
todo_data = {
    "title": "Complete project documentation"
}

# ❌ Bad: 複雑すぎる
todo_data = {
    "title": "Complex title with unicode 🚀 and special chars",
    "description": "Very long description..." * 100,
    "due_date": datetime.now() + timedelta(days=random.randint(1, 365))
}
```

#### フィクスチャ活用
```python
# conftest.py で共通テストデータを定義
@pytest.fixture
async def test_user(test_db_session):
    """Standard test user for E2E tests."""
    # 標準的なテストユーザーを作成
```

## 対象外事項

### E2Eテストで実装しない項目
- **詳細なバリデーションパターン**: 単体テストで実装
- **ビジネスロジックの分岐**: 単体テストで実装
- **境界値テスト**: 単体テストで実装
- **パフォーマンステスト**: 専用のパフォーマンステストで実装

### 単体テストで実装する項目
```python
# Unit Test Examples
class TestCreateTodoUseCase:
    def test_create_todo_with_all_fields(self):
        """全フィールド指定パターン"""
        
    def test_create_todo_with_minimal_fields(self):
        """最小フィールドパターン"""
        
    def test_create_todo_with_past_due_date(self):
        """過去日付パターン"""
        
    def test_create_todo_title_boundary_values(self):
        """タイトル長の境界値テスト"""
```

## 実行・保守規約

### テスト実行
```bash
# E2Eテストのみ実行
task test-e2e

# 全テスト実行
task test-all
```

### パフォーマンス考慮
- **高速実行**: インメモリSQLite使用
- **並列実行**: 可能な限り独立したテストケース
- **最小セットアップ**: 必要最小限のデータ準備

### 保守性確保
- **明確な命名**: テスト意図が伝わる名前
- **適切なコメント**: 複雑なセットアップの説明
- **DRY原則**: 共通処理のフィクスチャ化

## 品質基準

### 必須要件
- すべてのエンドポイントで主要レスポンスコードをカバー
- エラーハンドリングの一貫性検証
- HTTPインターフェース契約の準拠

### 推奨要件
- OpenAPI仕様との整合性確認
- セキュリティテスト（認証・認可）
- CORS、Content-Type等のHTTPヘッダ検証

## 例外事項

### 複雑なE2Eテストが必要な場合
- **ユーザーフロー**: 複数APIの連携が必要
- **外部システム連携**: 実際の統合動作確認
- **トランザクション境界**: 複数処理の整合性確認

この場合は、別途 `integration` テストディレクトリで実装する。

---

この規約により、効率的で保守性の高いE2Eテスト実装を実現する。
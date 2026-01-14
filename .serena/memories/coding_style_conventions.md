# コーディング規約とスタイル

## コードスタイル
- **フォーマッター**: ruff format
- **行長**: 88文字
- **クォート**: ダブルクォート
- **インデント**: スペース4つ
- **型ヒント**: 必須（mypy使用）

## 命名規則
- **クラス**: PascalCase (例: UserRepository)
- **関数・変数**: snake_case (例: get_user_by_id)
- **定数**: UPPER_SNAKE_CASE (例: MAX_RETRY_COUNT)
- **プライベート**: アンダースコア接頭辞 (例: _private_method)

## Clean Architecture規則
### レイヤー間依存関係
```
Controller → UseCase → Domain
UseCase → Infrastructure
DI → 全レイヤー（Composition Root）
```

### 禁止事項
- **Domain層**: 外部ライブラリ依存禁止（FastAPI, SQLAlchemy等）
- **UseCase層**: Infrastructure層直接参照禁止（インターフェース経由）
- **Infrastructure層**: Controller層参照禁止
- **各層**: 上位レイヤー参照禁止

## ドキュメント
- **docstring**: 必須（特にpublicメソッド）
- **型ヒント**: 全関数・メソッドに必須
- **コメント**: 複雑なロジックには日本語コメント

## エラーハンドリング
- カスタム例外クラス使用
- 適切なHTTPステータスコード返却
- ログ出力の統一
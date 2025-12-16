# 例外設計ポリシー
FastAPI のグローバル例外ハンドラ（`app/core/middleware/exception_handlers.py`）は `BaseCustomException` を継承したユーザ定義例外を前提にログ・レスポンスを制御している。新しいドメイン/アプリケーションコードでは、基本的に次の2系統の例外を使い分ける。

- ビジネス系例外（`app/domain/exceptions/business.py`）
  - `BusinessRuleException` 派生クラスを利用する。
  - ユーザ入力の誤りやドメイン制約違反など、利用者が対処可能な事象を表す。
  - ログレベルは WARNING、HTTP レスポンスは 4xx 系を返す。
  - `user_message` プロパティで利用者向けメッセージを明示し、内部情報は出さない。
- システム系例外（`app/domain/exceptions/system.py`）
  - `SystemException` 派生クラスを利用する。
  - 永続化層の障害や外部サービス連携の失敗など、利用者側で対処できない事象を表す。
  - ログレベルは ERROR（クリティカル系は `include_exc_info=True` でスタックトレースを出力）、HTTP レスポンスは 5xx 系を返す。
  - `DataOperationException` のように `operation_context` を渡すと、ハンドラでログに操作名が出力されトラブルシュートしやすくなる。

いずれの系統でも、設計方針は「例外クラス側でログレベル・レスポンス情報を決める」「ハンドラは `BaseCustomException` を受け取って一貫した処理を行う」というもの。ドメインコードで標準例外のみを送出するとグローバルハンドラの `Exception` キャッチに流れ、HTTP 500 として返却されるため、意図的なビジネス判定には必ずユーザ定義例外を使う。

新しい例外を追加する際は、上記どちらの系統かを判断し、`log_level` / `user_message` / `http_status_code` プロパティを適切に実装する。また、例外の `details` には復旧に役立つ情報（フィールド名・制約名など）だけを含め、機密情報やスタックトレースは入れない。

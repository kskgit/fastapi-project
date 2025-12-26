# テスト戦略

このプロジェクトでは、テストを読みやすく、意図が伝わりやすい形で保守するために以下の指針を採用します。

# テストを書くタイミング
- パブリックメソッドに対して全てテストを記述する

# 命名規約
- 特に失敗時のテストにおいては接続後を利用しない（by,with,when,doe_toなどばらつきが出ることを防ぐため）

# ファイル作成単位
- コンテキストを最小限にするために、基本的にはテスト対象に対して1テストファイルとする

# Arrange-Act-Assert (AAA) パターン
- すべてのテストを Arrange（準備）→ Act（実行）→ Assert（検証）の3段階で記述する。
- フェーズの境界が分かるように、 `# Arrange` ・`# Act`・`# Assert`コメントを各フェーズ毎の先頭に記述する。

## Arrange
必要なモックの設定やテスト対象（System Under Test）の初期化を行う。

## Act
検証したい操作を1回だけ呼び出すことを意識する。

## Assert
戻り値や副作用を明確に検証する。

# 非同期処理のテスト
非同期のリポジトリやサービスをMockする場合は以下の点を留意する
- モック化する際は、`AsyncMock` もしくは `return_value` に await 可能なオブジェクトを設定する。
- 呼び出し回数の確認は`assert_awaited_XX`シリーズ（`assert_awaited_once_with`など）を利用する。これにより、実装でawaitの記述漏れがあった場合にテストが失敗するため、非同期処理の実装ミスを防げる。

# 例外処理のテスト
- 例外を意図的にハンドリングしていない場合のテストは行わない
- 例外をハンドリングしていない箇所にて、発生した例外がそのままthrowされることの振る舞いはe2eテストの500系のパターンで担保する
  - 記述の簡潔さを優先し各層ではテストを記載しない

# レイヤ別ガイド
レイヤ固有のテスト観点・命名規約は以下のファイルに分割しました。必要なレイヤのドキュメントを参照してください。

- [Controller](./test_strategy_controller.md)
- [Usecase](./test_strategy_usecase.md)
- [Domain](./test_strategy_domain.md)
- [Domain Service](./test_strategy_domain_service.md)
- [Repository](./test_strategy_repository.md)
- [E2Eテスト](./test_strategy_e2e.md)

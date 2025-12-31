# Controller
## バリデーション設計
- リクエスト構造・型・必須項目など「入力の形」をここで保証する。`field_validator` などを利用し、422 を返せる形で早期に弾く。
- 単純なフォーマットやトリミング、Null 可否、桁数チェックは DTO 側で処理し、ユースケースへ渡るデータの素性を揃える。
- DTO で `ValidationException` を送出する場合は、API レスポンス仕様（422 か 400 か）との整合を確認する。

### レスポンスDTO
- Usecase から返るドメインエンティティを DTO へ写経する際、`id` や `created_at` / `updated_at` など「永続化済みであることを示す最低限のフィールド」が None だった場合は `ValidationException` を送出して早期検知する。
- それ以外のフィールドはドメイン層でのバリデーション済みと捉え、Controller 側では変換に徹する。

### リクエストDTO
- DTO/Schema で `Field` 設定を付与する場合は `Annotated` を用い、型アノテーション内へメタ情報を記述する（例: `user_id: Annotated[int, Field(description="...", frozen=True, strict=True)]`）。
    - `Annotated` を使えば `Field(..., ...)` の `...`（省略値）を避けられ、静的型チェッカーとの相性が良くなるため。
- 基本は `Field` に `frozen=True`（読み取り専用）と `strict=True`（暗黙の型変換を避ける）を付け、Controller 層で受けた値をそのまま Usecase へ伝播させる方針とする。緩和が必要な場合のみ理由をコメント等で残して例外的に許容する。
- デフォルト値が必要な場合も `Field(default=..., ...)` を `Annotated` のメタデータとして渡せる。必要に応じて `default_factory` なども利用し、代入構文への後退は基本的に不要。
- 具体例は下記サンプルと `docs/test/unit/controller.md` のユニットテスト例を参照し、DTO とテストで同じ契約を保つ。

#### リクエストDTOサンプル
```python
from typing import Annotated

from pydantic import BaseModel, Field, field_validator

from app.domain.exceptions import ValidationException


class CreateSubTaskDTO(BaseModel):
    """サブタスク作成時の入力を正規化する DTO。"""

    user_id: Annotated[
        int,
        Field(
            description="Todo owner user ID",
            frozen=True,
            strict=True,
        ),
    ]
    title: Annotated[
        str,
        Field(
            min_length=3,
            max_length=100,
            description="Todo title",
            frozen=True,
            strict=True,
        ),
    ]

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized) < 3:
            raise ValidationException("Title must be at least 3 characters")
        return normalized
```

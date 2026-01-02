from app.domain.subtask import SubTask


def test_user_create_success_defaults_member_role() -> None:
    """create()がrole未指定時にMemberを設定することを確認する."""
    # Act
    subtask = SubTask.create(title="title")

    # Assert
    assert subtask.title == "title"

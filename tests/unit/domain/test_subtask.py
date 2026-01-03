from app.domain.subtask import SubTask


def test_user_create_success_defaults_member_role() -> None:
    """create()がrole未指定時にMemberを設定することを確認する."""
    # Act
    subtask = SubTask.create(
        user_id=1,
        todo_id=2,
        title="title",
    )

    # Assert
    assert subtask.user_id == 1
    assert subtask.todo_id == 2
    assert subtask.title == "title"
    assert not subtask.is_compleated

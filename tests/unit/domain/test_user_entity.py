"""Unit tests for app.domain.entities.user.User."""

from app.domain.entities import User, UserRole


def test_user_create_success_defaults_member_role() -> None:
    """create()がrole未指定時にMemberを設定することを確認する."""
    # Act
    user = User.create(username="alice", email="alice@example.com")

    # Assert
    assert user.username == "alice"
    assert user.email == "alice@example.com"
    assert user.full_name is None
    assert user.role == UserRole.MEMBER


def test_user_create_success_keep_specified_role() -> None:
    """create()が指定されたroleを保持することを確認する."""
    # Act
    user = User.create(
        username="viewer_user",
        email="viewer@example.com",
        full_name="Viewer",
        role=UserRole.VIEWER,
    )

    # Assert
    assert user.role == UserRole.VIEWER
    assert user.full_name == "Viewer"
    assert user.created_at is None

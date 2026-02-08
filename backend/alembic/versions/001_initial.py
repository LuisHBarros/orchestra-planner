"""initial migration

Revision ID: 001
Revises:
Create Date: 2026-02-08 00:00:00.000000
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. USERS
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("magic_link_token_hash", sa.String(64), nullable=True),
        sa.Column("token_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # 2. PROJECTS
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("manager_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default="", nullable=False),
        sa.Column("llm_provider", sa.String(100), nullable=True),
        sa.Column("llm_api_key_encrypted", sa.Text(), nullable=True),
        sa.Column("expected_end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_foreign_key(
        "fk_projects_manager_id_users",
        "projects",
        "users",
        ["manager_id"],
        ["id"],
    )
    op.create_index("ix_projects_manager_id", "projects", ["manager_id"])
    op.create_index("ix_projects_expected_end_date", "projects", ["expected_end_date"])

    # 3. ROLES
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "name", name="uq_roles_project_id_name"),
    )
    op.create_foreign_key(
        "fk_roles_project_id_projects",
        "roles",
        "projects",
        ["project_id"],
        ["id"],
    )
    op.create_index("ix_roles_project_id", "roles", ["project_id"])

    # 4. PROJECT_CALENDARS
    op.create_table(
        "project_calendars",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "timezone",
            sa.String(64),
            server_default="UTC",
            nullable=False,
        ),
        sa.Column(
            "exclusion_dates",
            postgresql.ARRAY(sa.Date()),  # ← Mudado para ARRAY de DATE
            server_default=sa.text("'{}'::date[]"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", name="uq_project_calendars_project_id"),
    )
    op.create_foreign_key(
        "fk_project_calendars_project_id_projects",
        "project_calendars",
        "projects",
        ["project_id"],
        ["id"],
    )
    op.create_index(
        "ix_project_calendars_project_id",
        "project_calendars",
        ["project_id"],
    )

    # 5. PROJECT_MEMBERS
    op.create_table(
        "project_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "seniority_level",
            sa.Enum(
                "Junior",
                "Mid",
                "Senior",
                "Specialist",
                "Lead",
                name="seniority_level",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "project_id",
            "user_id",
            name="uq_project_members_project_id_user_id",
        ),
    )
    op.create_foreign_key(
        "fk_project_members_project_id_projects",
        "project_members",
        "projects",
        ["project_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_project_members_user_id_users",
        "project_members",
        "users",
        ["user_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_project_members_role_id_roles",
        "project_members",
        "roles",
        ["role_id"],
        ["id"],
    )
    op.create_index(
        "ix_project_members_project_id",
        "project_members",
        ["project_id"],
    )
    op.create_index(
        "ix_project_members_user_id",
        "project_members",
        ["user_id"],
    )
    op.create_index(
        "ix_project_members_role_id",
        "project_members",
        ["role_id"],
    )

    # 6. PROJECT_INVITES
    op.create_table(
        "project_invites",
        sa.Column("token", sa.String(255), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "status",
            sa.Enum(
                "Pending",
                "Accepted",
                "Expired",
                name="invite_status",
                native_enum=False,
            ),
            server_default="Pending",
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("token"),
    )
    op.create_foreign_key(
        "fk_project_invites_project_id_projects",
        "project_invites",
        "projects",
        ["project_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_project_invites_role_id_roles",
        "project_invites",
        "roles",
        ["role_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_project_invites_created_by_users",
        "project_invites",
        "users",
        ["created_by"],
        ["id"],
    )
    op.create_index(
        "ix_project_invites_project_id",
        "project_invites",
        ["project_id"],
    )
    op.create_index(
        "ix_project_invites_role_id",
        "project_invites",
        ["role_id"],
    )
    op.create_index(
        "ix_project_invites_created_by",
        "project_invites",
        ["created_by"],
    )
    op.create_index(
        "ix_project_invites_expires_at",
        "project_invites",
        ["expires_at"],
    )
    op.create_index(
        "ix_project_invites_status",
        "project_invites",
        ["status"],  # ← Adicionado para queries por status
    )

    # 7. TASKS
    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), server_default="", nullable=False),
        sa.Column("difficulty_points", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "Todo",
                "Doing",
                "Blocked",
                "Done",
                "Cancelled",
                name="task_status",
                native_enum=False,
            ),
            server_default="Todo",
            nullable=False,
        ),
        sa.Column("assignee_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("required_role_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("progress_percent", sa.Integer(), server_default="0", nullable=False),
        sa.Column("expected_start_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("expected_end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            onupdate=sa.text("now()"),  # ← Corrigido: adicionado onupdate
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_foreign_key(
        "fk_tasks_project_id_projects",
        "tasks",
        "projects",
        ["project_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_tasks_assignee_id_project_members",
        "tasks",
        "project_members",
        ["assignee_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_tasks_required_role_id_roles",
        "tasks",
        "roles",
        ["required_role_id"],
        ["id"],
    )
    op.create_index("ix_tasks_project_id", "tasks", ["project_id"])
    op.create_index("ix_tasks_assignee_id", "tasks", ["assignee_id"])
    op.create_index("ix_tasks_required_role_id", "tasks", ["required_role_id"])
    op.create_index("ix_tasks_expected_end_date", "tasks", ["expected_end_date"])
    op.create_index("ix_tasks_status", "tasks", ["status"])  # ← Adicionado
    op.create_index(
        "ix_tasks_difficulty_points", "tasks", ["difficulty_points"]
    )  # ← Adicionado

    # 8. TASK_DEPENDENCIES
    op.create_table(
        "task_dependencies",
        sa.Column("blocking_task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("blocked_task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("blocking_task_id", "blocked_task_id"),
    )
    op.create_foreign_key(
        "fk_task_dependencies_blocking_task_id_tasks",
        "task_dependencies",
        "tasks",
        ["blocking_task_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_task_dependencies_blocked_task_id_tasks",
        "task_dependencies",
        "tasks",
        ["blocked_task_id"],
        ["id"],
    )
    op.create_index(
        "ix_task_dependencies_blocking_task_id",
        "task_dependencies",
        ["blocking_task_id"],
    )
    op.create_index(
        "ix_task_dependencies_blocked_task_id",
        "task_dependencies",
        ["blocked_task_id"],
    )

    # 9. TASK_LOGS
    op.create_table(
        "task_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "log_type",
            sa.Enum(
                "ASSIGN",
                "UNASSIGN",
                "REPORT",
                "ABANDON",
                "STATUS_CHANGE",
                name="task_log_type",
                native_enum=False,
            ),
            nullable=False,
        ),
        sa.Column("content", sa.Text(), server_default="", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_foreign_key(
        "fk_task_logs_task_id_tasks",
        "task_logs",
        "tasks",
        ["task_id"],
        ["id"],
    )
    op.create_foreign_key(
        "fk_task_logs_author_id_project_members",
        "task_logs",
        "project_members",
        ["author_id"],
        ["id"],
    )
    op.create_index("ix_task_logs_task_id", "task_logs", ["task_id"])
    op.create_index("ix_task_logs_author_id", "task_logs", ["author_id"])


def downgrade() -> None:
    # Drop dependent tables first (ordem inversa do upgrade)
    op.drop_table("task_logs")
    op.drop_table("task_dependencies")
    op.drop_table("tasks")
    op.drop_table("project_invites")
    op.drop_table("project_members")
    op.drop_table("project_calendars")
    op.drop_table("roles")
    op.drop_table("projects")
    op.drop_table("users")

    # Drop enums (qualquer ordem após dropar tabelas)
    op.execute("DROP TYPE IF EXISTS task_log_type")
    op.execute("DROP TYPE IF EXISTS task_status")
    op.execute("DROP TYPE IF EXISTS invite_status")
    op.execute("DROP TYPE IF EXISTS seniority_level")

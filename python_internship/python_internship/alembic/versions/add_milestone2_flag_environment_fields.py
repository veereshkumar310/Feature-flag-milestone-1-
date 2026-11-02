"""Add Milestone 2 feature flag and environment fields."""

from alembic import op
import sqlalchemy as sa


revision = "b71c4d9e2f60"
down_revision = "669d9922c0ed"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add environment timestamp.
    op.add_column(
        "environments",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
    )

    # Add new feature flag fields.
    op.add_column(
        "feature_flags",
        sa.Column(
            "type",
            sa.String(),
            server_default="boolean",
            nullable=False,
        ),
    )
    op.add_column(
        "feature_flags",
        sa.Column("default_value", sa.JSON(), nullable=True),
    )
    op.add_column(
        "feature_flags",
        sa.Column("description", sa.String(), nullable=True),
    )
    op.add_column(
        "feature_flags",
        sa.Column("environment_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_feature_flags_environment_id",
        "feature_flags",
        "environments",
        ["environment_id"],
        ["id"],
    )
    op.add_column(
        "feature_flags",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
    )
    op.add_column(
        "feature_flags",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("feature_flags", "updated_at")
    op.drop_column("feature_flags", "created_at")
    op.drop_constraint(
        "fk_feature_flags_environment_id",
        "feature_flags",
        type_="foreignkey",
    )
    op.drop_column("feature_flags", "environment_id")
    op.drop_column("feature_flags", "description")
    op.drop_column("feature_flags", "default_value")
    op.drop_column("feature_flags", "type")
    op.drop_column("environments", "created_at")
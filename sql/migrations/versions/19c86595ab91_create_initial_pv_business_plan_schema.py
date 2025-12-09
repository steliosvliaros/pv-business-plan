"""create initial PV business plan schema

Revision ID: xxxxxxxxxxxx
Revises:
Create Date: 2024-12-09 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "xxxxxxxxxxxx"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create projects table
    op.create_table(
        "projects",
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("project_name", sa.String(255), nullable=False),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("latitude", sa.Numeric(10, 8)),
        sa.Column("longitude", sa.Numeric(11, 8)),
        sa.Column("project_type", sa.String(50)),
        sa.Column("status", sa.String(50), server_default="planning"),
        sa.Column(
            "created_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.Column(
            "updated_at", sa.TIMESTAMP(), server_default=sa.text("CURRENT_TIMESTAMP")
        ),
        sa.PrimaryKeyConstraint("project_id"),
    )

    # Add unique constraint
    op.create_unique_constraint(
        "uq_projects_project_name", "projects", ["project_name"]
    )

    # Add indexes
    op.create_index("idx_projects_status", "projects", ["status"])
    op.create_index("idx_projects_location", "projects", ["location"])


def downgrade() -> None:
    op.drop_index("idx_projects_location", "projects")
    op.drop_index("idx_projects_status", "projects")
    op.drop_table("projects")

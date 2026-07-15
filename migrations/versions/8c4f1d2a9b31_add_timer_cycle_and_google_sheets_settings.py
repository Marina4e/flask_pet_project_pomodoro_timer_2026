"""Add timer cycle settings columns

Revision ID: 8c4f1d2a9b31
Revises: 271cd7d32627
Create Date: 2026-07-14 11:30:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8c4f1d2a9b31"
down_revision = "271cd7d32627"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user_settings", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "cycles_before_long_break",
                sa.Integer(),
                nullable=False,
                server_default="4",
            )
        )
        batch_op.add_column(
            sa.Column(
                "auto_start_next_session",
                sa.Boolean(),
                nullable=False,
                server_default=sa.true(),
            )
        )


def downgrade():
    with op.batch_alter_table("user_settings", schema=None) as batch_op:
        batch_op.drop_column("auto_start_next_session")
        batch_op.drop_column("cycles_before_long_break")

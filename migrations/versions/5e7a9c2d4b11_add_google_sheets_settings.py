"""Add Google Sheets settings

Revision ID: 5e7a9c2d4b11
Revises: 1b2d7a4c9f10
Create Date: 2026-07-15 12:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5e7a9c2d4b11"
down_revision = "1b2d7a4c9f10"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("user_settings", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("google_sheets_enabled", sa.Boolean(), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "google_sheets_spreadsheet_id",
                sa.String(length=255),
                nullable=True,
            )
        )


def downgrade():
    with op.batch_alter_table("user_settings", schema=None) as batch_op:
        batch_op.drop_column("google_sheets_spreadsheet_id")
        batch_op.drop_column("google_sheets_enabled")

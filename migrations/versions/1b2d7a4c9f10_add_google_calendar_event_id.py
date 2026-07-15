"""Add Google Calendar event id to work sessions

Revision ID: 1b2d7a4c9f10
Revises: 8c4f1d2a9b31
Create Date: 2026-07-14 18:15:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1b2d7a4c9f10"
down_revision = "8c4f1d2a9b31"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("work_sessions", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("google_calendar_event_id", sa.String(length=255), nullable=True)
        )
        batch_op.create_unique_constraint(
            "uq_work_sessions_google_calendar_event_id",
            ["google_calendar_event_id"],
        )


def downgrade():
    with op.batch_alter_table("work_sessions", schema=None) as batch_op:
        batch_op.drop_constraint(
            "uq_work_sessions_google_calendar_event_id",
            type_="unique",
        )
        batch_op.drop_column("google_calendar_event_id")

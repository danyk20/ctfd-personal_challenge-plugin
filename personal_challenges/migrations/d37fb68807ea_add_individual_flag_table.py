"""Add individual flag table.

Revision ID: d37fb68807ea
Revises:
Create Date: 2021-02-24 12:21:39.373983

"""
# revision identifiers, used by Alembic.

import sqlalchemy as sa
from alembic import op

revision = "d37fb68807ea"
down_revision = None
branch_labels = None
depends_on = None

def upgrade(op=None):
    op.create_table(
        "individual_flag",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["id"], ["flags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade(op=None):
    op.drop_table("individual_flag")

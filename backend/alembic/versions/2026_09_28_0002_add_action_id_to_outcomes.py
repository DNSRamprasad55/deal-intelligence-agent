"""add action_id to deal_outcomes

Revision ID: 2026_09_28_0002
Revises: 2026_09_28_0001
Create Date: 2026-09-28 21:27:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2026_09_28_0002'
down_revision = '2026_09_28_0001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('deal_outcomes', sa.Column('action_id', sa.String(length=36), nullable=True))
    op.create_foreign_key(
        'fk_deal_outcomes_action_id_deal_actions',
        'deal_outcomes',
        'deal_actions',
        ['action_id'],
        ['id'],
        ondelete='SET NULL'
    )


def downgrade() -> None:
    op.drop_constraint('fk_deal_outcomes_action_id_deal_actions', 'deal_outcomes', type_='foreignkey')
    op.drop_column('deal_outcomes', 'action_id')

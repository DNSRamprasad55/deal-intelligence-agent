"""initial schema

Revision ID: 2026_09_28_0001
Revises: 
Create Date: 2026-09-28 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2026_09_28_0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('sales_rep', 'manager', 'admin', name='userrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_created_at'), 'users', ['created_at'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)

    # Companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('industry', sa.String(length=255), nullable=True),
        sa.Column('size', sa.String(length=100), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_companies_created_at'), 'companies', ['created_at'], unique=False)
    op.create_index(op.f('ix_companies_name'), 'companies', ['name'], unique=False)

    # Contacts table
    op.create_table(
        'contacts',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('company_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('job_title', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('role_in_deal', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_contacts_company_id'), 'contacts', ['company_id'], unique=False)
    op.create_index(op.f('ix_contacts_created_at'), 'contacts', ['created_at'], unique=False)

    # Deals table
    op.create_table(
        'deals',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('company_id', sa.String(length=36), nullable=False),
        sa.Column('owner_id', sa.String(length=36), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('stage', sa.Enum('DISCOVERY', 'QUALIFICATION', 'TECHNICAL_EVALUATION', 'PROPOSAL', 'NEGOTIATION', 'CLOSED_WON', 'CLOSED_LOST', name='dealstage'), nullable=False),
        sa.Column('value', sa.Numeric(precision=14, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False),
        sa.Column('probability', sa.Float(), nullable=False),
        sa.Column('expected_close_date', sa.Date(), nullable=True),
        sa.Column('status', sa.Enum('OPEN', 'WON', 'LOST', name='dealstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deals_company_id'), 'deals', ['company_id'], unique=False)
    op.create_index(op.f('ix_deals_created_at'), 'deals', ['created_at'], unique=False)
    op.create_index(op.f('ix_deals_owner_id'), 'deals', ['owner_id'], unique=False)
    op.create_index(op.f('ix_deals_stage'), 'deals', ['stage'], unique=False)
    op.create_index(op.f('ix_deals_status'), 'deals', ['status'], unique=False)

    # Interactions table
    op.create_table(
        'interactions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('deal_id', sa.String(length=36), nullable=False),
        sa.Column('contact_id', sa.String(length=36), nullable=True),
        sa.Column('type', sa.Enum('CALL', 'MEETING', 'EMAIL', 'NOTE', 'DEMO', 'TECHNICAL_REVIEW', name='interactiontype'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('occurred_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.String(length=36), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['deal_id'], ['deals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_interactions_contact_id'), 'interactions', ['contact_id'], unique=False)
    op.create_index(op.f('ix_interactions_created_at'), 'interactions', ['created_at'], unique=False)
    op.create_index(op.f('ix_interactions_deal_id'), 'interactions', ['deal_id'], unique=False)
    op.create_index(op.f('ix_interactions_occurred_at'), 'interactions', ['occurred_at'], unique=False)

    # Recommendations table
    op.create_table(
        'recommendations',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('deal_id', sa.String(length=36), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('reasoning', sa.Text(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'ACCEPTED', 'REJECTED', 'COMPLETED', name='recommendationstatus'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['deal_id'], ['deals.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_recommendations_created_at'), 'recommendations', ['created_at'], unique=False)
    op.create_index(op.f('ix_recommendations_deal_id'), 'recommendations', ['deal_id'], unique=False)
    op.create_index(op.f('ix_recommendations_status'), 'recommendations', ['status'], unique=False)

    # Deal Actions table
    op.create_table(
        'deal_actions',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('deal_id', sa.String(length=36), nullable=False),
        sa.Column('recommendation_id', sa.String(length=36), nullable=True),
        sa.Column('action_type', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['deal_id'], ['deals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recommendation_id'], ['recommendations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deal_actions_created_at'), 'deal_actions', ['created_at'], unique=False)
    op.create_index(op.f('ix_deal_actions_deal_id'), 'deal_actions', ['deal_id'], unique=False)

    # Deal Outcomes table
    op.create_table(
        'deal_outcomes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('deal_id', sa.String(length=36), nullable=False),
        sa.Column('recommendation_id', sa.String(length=36), nullable=True),
        sa.Column('outcome_type', sa.Enum('POSITIVE', 'NEGATIVE', 'NEUTRAL', 'UNKNOWN', name='outcometype'), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('impact', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['deal_id'], ['deals.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['recommendation_id'], ['recommendations.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_deal_outcomes_created_at'), 'deal_outcomes', ['created_at'], unique=False)
    op.create_index(op.f('ix_deal_outcomes_deal_id'), 'deal_outcomes', ['deal_id'], unique=False)


def downgrade() -> None:
    op.drop_table('deal_outcomes')
    op.drop_table('deal_actions')
    op.drop_table('recommendations')
    op.drop_table('interactions')
    op.drop_table('deals')
    op.drop_table('contacts')
    op.drop_table('companies')
    op.drop_table('users')

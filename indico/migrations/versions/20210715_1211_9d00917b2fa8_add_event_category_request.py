"""Add event category request

Revision ID: 9d00917b2fa8
Revises: 1cec32e42f65
Create Date: 2021-07-15 12:11:28.157824
"""

import sqlalchemy as sa
from alembic import op

from indico.core.db.sqlalchemy import PyIntEnum, UTCDateTime
# revision identifiers, used by Alembic.
from indico.modules.categories.models.event_move_request import MoveRequestState


revision = '9d00917b2fa8'
down_revision = '1cec32e42f65'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('event_move_requests',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('event_id', sa.Integer(), nullable=False),
                    sa.Column('category_id', sa.Integer(), nullable=True),
                    sa.Column('submitter_id', sa.Integer(), nullable=True),
                    sa.Column('state', PyIntEnum(MoveRequestState), nullable=False),
                    sa.Column('moderator_id', sa.Integer(), nullable=True),
                    sa.Column('submitted_dt', UTCDateTime, nullable=False),
                    sa.CheckConstraint('state in (1, 2) AND moderator_id IS NOT NULL OR moderator_id IS NULL',
                                       name=op.f('ck_event_move_requests_moderator_state')),
                    sa.ForeignKeyConstraint(['category_id'], ['categories.categories.id'],
                                            name=op.f('fk_event_move_requests_category_id_categories')),
                    sa.ForeignKeyConstraint(['event_id'], ['events.events.id'],
                                            name=op.f('fk_event_move_requests_event_id_events')),
                    sa.ForeignKeyConstraint(['moderator_id'], ['users.users.id'],
                                            name=op.f('fk_event_move_requests_moderator_id_users')),
                    sa.ForeignKeyConstraint(['submitter_id'], ['users.users.id'],
                                            name=op.f('fk_event_move_requests_submitter_id_users')),
                    sa.PrimaryKeyConstraint('id', name=op.f('pk_event_move_requests')),
                    schema='categories'
                    )
    op.create_index(op.f('ix_event_move_requests_category_id'), 'event_move_requests', ['category_id'], unique=False,
                    schema='categories')
    op.create_index(op.f('ix_event_move_requests_event_id'), 'event_move_requests', ['event_id'], unique=False,
                    schema='categories')
    op.create_index(op.f('ix_event_move_requests_submitter_id'), 'event_move_requests', ['submitter_id'], unique=False,
                    schema='categories')
    op.create_index(op.f('ix_uq_event_move_requests_event_id'), 'event_move_requests', ['event_id'], unique=True,
                    schema='categories', postgresql_where=sa.text('state = 0'))
    op.add_column('categories',
                  sa.Column('event_requires_approval', sa.Boolean(), nullable=False, server_default='false'),
                  schema='categories')


def downgrade():
    op.drop_column('categories', 'event_requires_approval', schema='categories')
    op.drop_index(op.f('ix_uq_event_move_requests_event_id'), table_name='event_move_requests', schema='categories',
                  postgresql_where=sa.text('state = 0'))
    op.drop_index(op.f('ix_event_move_requests_submitter_id'), table_name='event_move_requests', schema='categories')
    op.drop_index(op.f('ix_event_move_requests_event_id'), table_name='event_move_requests', schema='categories')
    op.drop_index(op.f('ix_event_move_requests_category_id'), table_name='event_move_requests', schema='categories')
    op.drop_table('event_move_requests', schema='categories')

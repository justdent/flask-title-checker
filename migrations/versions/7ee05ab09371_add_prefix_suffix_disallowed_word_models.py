"""Add prefix, suffix, disallowed word models

Revision ID: 7ee05ab09371
Revises: d50794f66e8e
Create Date: 2025-05-16 11:35:49.648417

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ee05ab09371'
down_revision = 'd50794f66e8e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('disallowed_word',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('word', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('word')
    )
    op.create_table('prefix',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('value')
    )
    op.create_table('suffix',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('value', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('value')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('suffix')
    op.drop_table('prefix')
    op.drop_table('disallowed_word')
    # ### end Alembic commands ###

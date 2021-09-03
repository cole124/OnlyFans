"""Add Liked Columns

Revision ID: d77eb4427129
Revises: 5493253cc03c
Create Date: 2021-09-01 12:29:37.923127

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd77eb4427129'
down_revision = '5493253cc03c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('liked', sa.Boolean(), nullable=True))
    op.add_column('medias', sa.Column('liked', sa.Boolean(), nullable=True))
    op.add_column('messages', sa.Column('liked', sa.Boolean(), nullable=True))
    op.add_column('stories', sa.Column('liked', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('posts','liked')
    op.drop_column('medias','liked')
    op.drop_column('messages','liked')
    op.drop_column('stories','liked')

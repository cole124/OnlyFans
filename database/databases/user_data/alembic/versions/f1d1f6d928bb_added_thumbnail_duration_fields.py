"""Added thumbnail & duration fields

Revision ID: f1d1f6d928bb
Revises: d77eb4427129
Create Date: 2021-10-01 16:43:30.273258

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f1d1f6d928bb'
down_revision = 'd77eb4427129'
branch_labels = None
depends_on = None


def upgrade():
    pass
    # op.add_column('medias', sa.Column('thumbnail', sa.String(), nullable=True))
    # op.add_column('medias', sa.Column(
    #     'duration', sa.Integer(), nullable=True, default=0))


def downgrade():
    op.drop_column('medias', 'duration')
    op.drop_column('medias', 'thumbnail')

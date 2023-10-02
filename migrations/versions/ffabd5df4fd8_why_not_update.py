"""why not update

Revision ID: ffabd5df4fd8
Revises: 
Create Date: 2021-05-17 19:20:45.198349

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ffabd5df4fd8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('candidates')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('candidates',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('img', sa.VARCHAR(), nullable=True),
    sa.Column('win', sa.INTEGER(), nullable=True),
    sa.Column('loss', sa.INTEGER(), nullable=True),
    sa.Column('score', sa.FLOAT(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###

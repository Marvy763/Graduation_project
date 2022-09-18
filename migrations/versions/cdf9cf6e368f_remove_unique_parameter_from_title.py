"""remove unique parameter from title

Revision ID: cdf9cf6e368f
Revises: 087d5afed2bb
Create Date: 2022-07-16 13:50:18.921071

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cdf9cf6e368f'
down_revision = '087d5afed2bb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('title', table_name='posts')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('title', 'posts', ['title'], unique=True)
    # ### end Alembic commands ###
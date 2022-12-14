"""modify comment model

Revision ID: 087d5afed2bb
Revises: 66fe9dcc8df6
Create Date: 2022-07-15 16:54:23.571880

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '087d5afed2bb'
down_revision = '66fe9dcc8df6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'comment_count')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('comment_count', mysql.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###

"""empty message

Revision ID: 088949707ae7
Revises: 89880274c0bd
Create Date: 2020-11-30 13:27:01.120828

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '088949707ae7'
down_revision = '89880274c0bd'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('about_me', sa.String(length=140), nullable=True))
    op.add_column('user', sa.Column('last_seen', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'last_seen')
    op.drop_column('user', 'about_me')
    # ### end Alembic commands ###

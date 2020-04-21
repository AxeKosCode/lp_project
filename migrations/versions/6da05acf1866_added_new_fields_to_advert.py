"""added new fields to advert

Revision ID: 6da05acf1866
Revises: cc1db3610e97
Create Date: 2020-04-21 19:57:23.450217

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6da05acf1866'
down_revision = 'cc1db3610e97'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('advert', sa.Column('adress', sa.Text(), nullable=True))
    op.add_column('advert', sa.Column('phone', sa.Text(), nullable=True))
    op.add_column('advert', sa.Column('seller', sa.String(), nullable=True))
    op.add_column('advert', sa.Column('theme', sa.String(), nullable=True))
    op.add_column('advert', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_advert_user_id'), 'advert', ['user_id'], unique=False)
    op.create_foreign_key(None, 'advert', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'comment', 'user', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'comment', type_='foreignkey')
    op.drop_constraint(None, 'advert', type_='foreignkey')
    op.drop_index(op.f('ix_advert_user_id'), table_name='advert')
    op.drop_column('advert', 'user_id')
    op.drop_column('advert', 'theme')
    op.drop_column('advert', 'seller')
    op.drop_column('advert', 'phone')
    op.drop_column('advert', 'adress')
    # ### end Alembic commands ###
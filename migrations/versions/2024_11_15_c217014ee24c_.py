"""empty message

Revision ID: c217014ee24c
Revises: 806ab5b6c1ac
Create Date: 2024-11-14 20:53:45.591554

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c217014ee24c'
down_revision: Union[str, None] = '806ab5b6c1ac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('order_customer_id_fkey', 'order', type_='foreignkey')
    op.create_foreign_key(None, 'order', 'user', ['customer_id'], ['id'], ondelete='CASCADE')
    op.drop_constraint('order_detail_good_id_fkey', 'order_detail', type_='foreignkey')
    op.drop_constraint('order_detail_order_id_fkey', 'order_detail', type_='foreignkey')
    op.create_foreign_key(None, 'order_detail', 'good', ['good_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'order_detail', 'order', ['order_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'order_detail', type_='foreignkey')
    op.drop_constraint(None, 'order_detail', type_='foreignkey')
    op.create_foreign_key('order_detail_order_id_fkey', 'order_detail', 'order', ['order_id'], ['id'])
    op.create_foreign_key('order_detail_good_id_fkey', 'order_detail', 'good', ['good_id'], ['id'])
    op.drop_constraint(None, 'order', type_='foreignkey')
    op.create_foreign_key('order_customer_id_fkey', 'order', 'user', ['customer_id'], ['id'])
    # ### end Alembic commands ###

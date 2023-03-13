"""Initial migration.

Revision ID: 73f295badce8
Revises: 882465a4da72
Create Date: 2023-03-11 14:33:20.572417

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '73f295badce8'
down_revision = '882465a4da72'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('result_info', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id_req', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('res_link', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('res_text', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('result_info', schema=None) as batch_op:
        batch_op.drop_column('res_text')
        batch_op.drop_column('res_link')
        batch_op.drop_column('id_req')

    # ### end Alembic commands ###
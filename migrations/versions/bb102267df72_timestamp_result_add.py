"""timestamp result add

Revision ID: bb102267df72
Revises: 107ce2a0455e
Create Date: 2023-03-24 19:47:30.635829

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "bb102267df72"
down_revision = "107ce2a0455e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("result_info", schema=None) as batch_op:
        batch_op.add_column(sa.Column("timestamp", sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("result_info", schema=None) as batch_op:
        batch_op.drop_column("timestamp")

    # ### end Alembic commands ###

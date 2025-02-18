"""empty message

Revision ID: 7894397aa1f3
Revises: 2a81454fb84c
Create Date: 2021-09-22 20:53:38.886897

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7894397aa1f3'
down_revision = '2a81454fb84c'
branch_labels = None
depends_on = None


def upgrade(engine_name):
    globals()["upgrade_%s" % engine_name]()


def downgrade(engine_name):
    globals()["downgrade_%s" % engine_name]()


def upgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('workers')
    op.create_table('workers',
        sa.Column('hostname', sa.String(length=255), nullable=False),
        sa.Column('port', sa.Integer, nullable=False),
        sa.Column('blockchain', sa.String(length=64), nullable=False),
        sa.Column('displayname', sa.String(length=255), nullable=True),
        sa.Column('mode', sa.String(length=64), nullable=False),
        sa.Column('blockchain', sa.String(length=255), nullable=True),
        sa.Column('services', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('config', sa.String(), nullable=False),
        sa.Column('latest_ping_result', sa.String(), nullable=True),
        sa.Column('ping_success_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('hostname','port')
    )
    # ### end Alembic commands ###


def downgrade_():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('workers')
    op.create_table('workers',
        sa.Column('hostname', sa.String(length=255), nullable=False),
        sa.Column('port', sa.Integer, nullable=True),
        sa.Column('displayname', sa.String(length=255), nullable=True),
        sa.Column('mode', sa.String(length=64), nullable=False),
        sa.Column('services', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('config', sa.String(), nullable=False),
        sa.Column('latest_ping_result', sa.String(), nullable=True),
        sa.Column('ping_success_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('hostname')
    )
    # ### end Alembic commands ###


def upgrade_stats():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade_stats():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


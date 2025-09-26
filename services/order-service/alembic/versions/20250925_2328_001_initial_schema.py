"""Initial schema - orders, order_items, shipping_addresses, order_modifications

Revision ID: 001
Revises:
Create Date: 2025-09-25 23:28:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('order_number', sa.String(length=50), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED', name='orderstatus'), nullable=False),
        sa.Column('subtotal', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('tax_rate', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('tax_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('shipping_cost', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, default='USD'),
        sa.Column('modification_count', sa.Integer(), nullable=False, default=0),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_orders_id'), 'orders', ['id'], unique=False)
    op.create_index(op.f('ix_orders_order_number'), 'orders', ['order_number'], unique=True)
    op.create_index(op.f('ix_orders_status'), 'orders', ['status'], unique=False)
    op.create_index(op.f('ix_orders_user_id'), 'orders', ['user_id'], unique=False)

    # Create order_items table
    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('product_name', sa.String(length=200), nullable=False),
        sa.Column('product_sku', sa.String(length=100), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('total_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('weight', sa.Numeric(precision=8, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_items_id'), 'order_items', ['id'], unique=False)
    op.create_index(op.f('ix_order_items_order_id'), 'order_items', ['order_id'], unique=False)
    op.create_index(op.f('ix_order_items_product_id'), 'order_items', ['product_id'], unique=False)

    # Create shipping_addresses table
    op.create_table(
        'shipping_addresses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('recipient_name', sa.String(length=100), nullable=False),
        sa.Column('company', sa.String(length=100), nullable=True),
        sa.Column('address_line_1', sa.String(length=200), nullable=False),
        sa.Column('address_line_2', sa.String(length=200), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state_province', sa.String(length=100), nullable=False),
        sa.Column('postal_code', sa.String(length=20), nullable=False),
        sa.Column('country', sa.String(length=2), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('delivery_instructions', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_shipping_addresses_id'), 'shipping_addresses', ['id'], unique=False)
    op.create_index(op.f('ix_shipping_addresses_order_id'), 'shipping_addresses', ['order_id'], unique=True)

    # Create order_modifications table
    op.create_table(
        'order_modifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('user_email', sa.String(length=255), nullable=True),
        sa.Column('modification_type', sa.Enum('STATUS_CHANGE', 'ITEM_ADDED', 'ITEM_REMOVED', 'QUANTITY_CHANGED', 'ADDRESS_UPDATED', 'CANCELLATION', 'NOTES_UPDATED', 'SHIPPING_COST_UPDATED', name='modificationtype'), nullable=False),
        sa.Column('old_value', sa.JSON(), nullable=True),
        sa.Column('new_value', sa.JSON(), nullable=True),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_order_modifications_created_at'), 'order_modifications', ['created_at'], unique=False)
    op.create_index(op.f('ix_order_modifications_id'), 'order_modifications', ['id'], unique=False)
    op.create_index(op.f('ix_order_modifications_modification_type'), 'order_modifications', ['modification_type'], unique=False)
    op.create_index(op.f('ix_order_modifications_order_id'), 'order_modifications', ['order_id'], unique=False)
    op.create_index(op.f('ix_order_modifications_user_id'), 'order_modifications', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_order_modifications_user_id'), table_name='order_modifications')
    op.drop_index(op.f('ix_order_modifications_order_id'), table_name='order_modifications')
    op.drop_index(op.f('ix_order_modifications_modification_type'), table_name='order_modifications')
    op.drop_index(op.f('ix_order_modifications_id'), table_name='order_modifications')
    op.drop_index(op.f('ix_order_modifications_created_at'), table_name='order_modifications')
    op.drop_table('order_modifications')

    op.drop_index(op.f('ix_shipping_addresses_order_id'), table_name='shipping_addresses')
    op.drop_index(op.f('ix_shipping_addresses_id'), table_name='shipping_addresses')
    op.drop_table('shipping_addresses')

    op.drop_index(op.f('ix_order_items_product_id'), table_name='order_items')
    op.drop_index(op.f('ix_order_items_order_id'), table_name='order_items')
    op.drop_index(op.f('ix_order_items_id'), table_name='order_items')
    op.drop_table('order_items')

    op.drop_index(op.f('ix_orders_user_id'), table_name='orders')
    op.drop_index(op.f('ix_orders_status'), table_name='orders')
    op.drop_index(op.f('ix_orders_order_number'), table_name='orders')
    op.drop_index(op.f('ix_orders_id'), table_name='orders')
    op.drop_table('orders')

    # Drop enums
    sa.Enum(name='orderstatus').drop(op.get_bind())
    sa.Enum(name='modificationtype').drop(op.get_bind())
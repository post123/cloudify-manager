"""4.0

Revision ID: 333998bc1627
Revises:
Create Date: 2017-04-26 12:42:40.587570

"""
from alembic import op
import sqlalchemy as sa
import manager_rest     # Adding this manually


# revision identifiers, used by Alembic.
revision = '333998bc1627'
down_revision = None
branch_labels = None
depends_on = None

snapshot_status = sa.Enum(
    'created',
    'failed',
    'creating',
    'uploaded',
    name='snapshot_status',
)
deployment_modification_status = sa.Enum(
    'started',
    'finished',
    'rolledback',
    name='deployment_modification_status',
)
execution_status = sa.Enum(
    'terminated',
    'failed',
    'cancelled',
    'pending',
    'started',
    'cancelling',
    'force_cancelling',
    name='execution_status',
)
action_type = sa.Enum(
    'add',
    'remove',
    'modify',
    name='action_type',
)
entity_type = sa.Enum(
    'node',
    'relationship',
    'property',
    'operation',
    'workflow',
    'output',
    'description',
    'group',
    'policy_type',
    'policy_trigger',
    'plugin',
    name='entity_type',
)


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'groups',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('ldap_dn', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_groups_ldap_dn'),
        'groups',
        ['ldap_dn'],
        unique=True,
    )
    op.create_index(op.f('ix_groups_name'), 'groups', ['name'], unique=True)
    op.create_table(
        'provider_context',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('context', sa.PickleType(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tenants_name'), 'tenants', ['name'], unique=True)
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.Column(
            'created_at',
            manager_rest.storage.models_base.UTCDateTime(),
            nullable=True,
        ),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column(
            'last_login_at',
            manager_rest.storage.models_base.UTCDateTime(),
            nullable=True,
        ),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('password', sa.String(length=255), nullable=True),
        sa.Column('api_token_key', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(
        op.f('ix_users_username'),
        'users',
        ['username'],
        unique=True,
    )
    op.create_table(
        'blueprints',
        sa.Column('_storage_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            manager_rest.storage.models_base.UTCDateTime(),
            nullable=False,
        ),
        sa.Column('main_file_name', sa.Text(), nullable=False),
        sa.Column('plan', sa.PickleType(), nullable=False),
        sa.Column(
            'updated_at',
            manager_rest.storage.models_base.UTCDateTime(),
            nullable=True,
        ),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('_tenant_id', sa.Integer(), nullable=False),
        sa.Column('_creator_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['_creator_id'],
            [u'users.id'],
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['_tenant_id'],
            [u'tenants.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('_storage_id')
    )
    op.create_index(
        op.f('ix_blueprints_created_at'),
        'blueprints',
        ['created_at'],
        unique=False,
    )
    op.create_index(
        op.f('ix_blueprints_id'),
        'blueprints',
        ['id'],
        unique=False,
    )
    op.create_table(
        'groups_tenants',
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], )
    )
    op.create_table(
        'plugins',
        sa.Column('_storage_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Text(), nullable=True),
        sa.Column('archive_name', sa.Text(), nullable=False),
        sa.Column('distribution', sa.Text(), nullable=True),
        sa.Column('distribution_release', sa.Text(), nullable=True),
        sa.Column('distribution_version', sa.Text(), nullable=True),
        sa.Column('excluded_wheels', sa.PickleType(), nullable=True),
        sa.Column('package_name', sa.Text(), nullable=False),
        sa.Column('package_source', sa.Text(), nullable=True),
        sa.Column('package_version', sa.Text(), nullable=True),
        sa.Column('supported_platform', sa.PickleType(), nullable=True),
        sa.Column('supported_py_versions', sa.PickleType(), nullable=True),
        sa.Column(
            'uploaded_at',
            manager_rest.storage.models_base.UTCDateTime(),
            nullable=False,
        ),
        sa.Column('wheels', sa.PickleType(), nullable=False),
        sa.Column('_tenant_id', sa.Integer(), nullable=False),
        sa.Column('_creator_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['_creator_id'],
            [u'users.id'],
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['_tenant_id'],
            [u'tenants.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('_storage_id')
    )
    op.create_index(
        op.f('ix_plugins_archive_name'),
        'plugins',
        ['archive_name'],
        unique=False,
    )
    op.create_index(op.f('ix_plugins_id'), 'plugins', ['id'], unique=False)
    op.create_index(
        op.f('ix_plugins_package_name'),
        'plugins',
        ['package_name'],
        unique=False,
    )
    op.create_index(
        op.f('ix_plugins_uploaded_at'),
        'plugins',
        ['uploaded_at'],
        unique=False,
    )
    op.create_table(
        'secrets',
        sa.Column('_storage_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Text(), nullable=True),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            manager_rest.storage.models_base.UTCDateTime(),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            manager_rest.storage.models_base.UTCDateTime(),
            nullable=True,
        ),
        sa.Column('_tenant_id', sa.Integer(), nullable=False),
        sa.Column('_creator_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['_creator_id'],
            [u'users.id'],
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['_tenant_id'],
            [u'tenants.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('_storage_id')
    )
    op.create_index(
        op.f('ix_secrets_created_at'),
        'secrets',
        ['created_at'],
        unique=False,
    )
    op.create_index(
        op.f('ix_secrets_id'),
        'secrets',
        ['id'],
        unique=False,
    )
    op.create_table(
        'snapshots',
        sa.Column('_storage_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            manager_rest.storage.models_base.UTCDateTime(),
            nullable=False,
        ),
        sa.Column('status', snapshot_status, nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('_tenant_id', sa.Integer(), nullable=False),
        sa.Column('_creator_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['_creator_id'],
            [u'users.id'],
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['_tenant_id'],
            [u'tenants.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('_storage_id')
    )
    op.create_index(op.f(
        'ix_snapshots_created_at'),
        'snapshots',
        ['created_at'],
        unique=False,
    )
    op.create_index(op.f('ix_snapshots_id'), 'snapshots', ['id'], unique=False)
    op.create_table(
        'users_groups',
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('group_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_table(
        'users_roles',
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('role_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_table(
        'users_tenants',
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_table(
        'deployments',
        sa.Column('_storage_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            manager_rest.storage.models_base.UTCDateTime(),
            nullable=False,
        ),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('inputs', sa.PickleType(), nullable=True),
        sa.Column('groups', sa.PickleType(), nullable=True),
        sa.Column('permalink', sa.Text(), nullable=True),
        sa.Column('policy_triggers', sa.PickleType(), nullable=True),
        sa.Column('policy_types', sa.PickleType(), nullable=True),
        sa.Column('outputs', sa.PickleType(), nullable=True),
        sa.Column('scaling_groups', sa.PickleType(), nullable=True),
        sa.Column(
            'updated_at',
            manager_rest.storage.models_base.UTCDateTime(),
            nullable=True,
        ),
        sa.Column('workflows', sa.PickleType(), nullable=True),
        sa.Column('_blueprint_fk', sa.Integer(), nullable=False),
        sa.Column('_creator_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['_blueprint_fk'],
            [u'blueprints._storage_id'],
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['_creator_id'],
            [u'users.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('_storage_id')
    )
    op.create_index(
        op.f('ix_deployments_created_at'),
        'deployments',
        ['created_at'],
        unique=False,
    )
    op.create_index(
        op.f('ix_deployments_id'),
        'deployments',
        ['id'],
        unique=False,
    )
    op.create_table(
        'owners_blueprints_users',
        sa.Column('blueprint_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['blueprint_id'],
            ['blueprints._storage_id'],
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_table(
        'owners_plugins_users',
        sa.Column('plugin_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['plugin_id'], ['plugins._storage_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_table(
        'owners_secrets_users',
        sa.Column('secret_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['secret_id'], ['secrets._storage_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_table(
        'owners_snapshots_users',
        sa.Column('snapshot_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['snapshot_id'], ['snapshots._storage_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_table(
        'viewers_blueprints_users',
        sa.Column('blueprint_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['blueprint_id'],
            ['blueprints._storage_id'],
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_table(
        'viewers_plugins_users',
        sa.Column('plugin_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['plugin_id'], ['plugins._storage_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_table(
        'viewers_secrets_users',
        sa.Column('secret_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['secret_id'], ['secrets._storage_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_table(
        'viewers_snapshots_users',
        sa.Column('snapshot_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['snapshot_id'], ['snapshots._storage_id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_table(
        'deployment_modifications',
        sa.Column('_storage_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Text(), nullable=True),
        sa.Column('context', sa.PickleType(), nullable=True),
        sa.Column(
            'created_at',
            manager_rest.storage.models_base.UTCDateTime(),
            nullable=False,
        ),
        sa.Column(
            'ended_at',
            manager_rest.storage.models_base.UTCDateTime(),
            nullable=True,
        ),
        sa.Column('modified_nodes', sa.PickleType(), nullable=True),
        sa.Column('node_instances', sa.PickleType(), nullable=True),
        sa.Column('status', deployment_modification_status, nullable=True),
        sa.Column('_deployment_fk', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['_deployment_fk'],
            [u'deployments._storage_id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('_storage_id')
    )
    op.create_index(
        op.f('ix_deployment_modifications_created_at'),
        'deployment_modifications',
        ['created_at'],
        unique=False,
    )
    op.create_index(
        op.f('ix_deployment_modifications_ended_at'),
        'deployment_modifications',
        ['ended_at'],
        unique=False,
    )
    op.create_index(
        op.f('ix_deployment_modifications_id'),
        'deployment_modifications',
        ['id'],
        unique=False,
    )
    op.create_table(
        'executions',
        sa.Column('_storage_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            manager_rest.storage.models_base.UTCDateTime(),
            nullable=False,
        ),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('is_system_workflow', sa.Boolean(), nullable=False),
        sa.Column('parameters', sa.PickleType(), nullable=True),
        sa.Column('status', execution_status, nullable=True),
        sa.Column('workflow_id', sa.Text(), nullable=False),
        sa.Column('_deployment_fk', sa.Integer(), nullable=True),
        sa.Column('_tenant_id', sa.Integer(), nullable=False),
        sa.Column('_creator_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['_creator_id'],
            [u'users.id'],
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['_deployment_fk'],
            [u'deployments._storage_id'],
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['_tenant_id'],
            [u'tenants.id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('_storage_id')
    )
    op.create_index(
        op.f('ix_executions_created_at'),
        'executions',
        ['created_at'],
        unique=False,
    )
    op.create_index(
        op.f('ix_executions_id'),
        'executions',
        ['id'],
        unique=False,
    )
    op.create_table(
        'nodes',
        sa.Column('_storage_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Text(), nullable=True),
        sa.Column('deploy_number_of_instances', sa.Integer(), nullable=False),
        sa.Column('host_id', sa.Text(), nullable=True),
        sa.Column('max_number_of_instances', sa.Integer(), nullable=False),
        sa.Column('min_number_of_instances', sa.Integer(), nullable=False),
        sa.Column('number_of_instances', sa.Integer(), nullable=False),
        sa.Column('planned_number_of_instances', sa.Integer(), nullable=False),
        sa.Column('plugins', sa.PickleType(), nullable=True),
        sa.Column('plugins_to_install', sa.PickleType(), nullable=True),
        sa.Column('properties', sa.PickleType(), nullable=True),
        sa.Column('relationships', sa.PickleType(), nullable=True),
        sa.Column('operations', sa.PickleType(), nullable=True),
        sa.Column('type', sa.Text(), nullable=False),
        sa.Column('type_hierarchy', sa.PickleType(), nullable=True),
        sa.Column('_deployment_fk', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['_deployment_fk'],
            [u'deployments._storage_id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('_storage_id')
    )
    op.create_index(op.f('ix_nodes_id'), 'nodes', ['id'], unique=False)
    op.create_index(op.f('ix_nodes_type'), 'nodes', ['type'], unique=False)
    op.create_table(
        'owners_deployments_users',
        sa.Column('deployment_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['deployment_id'],
            ['deployments._storage_id'],
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_table(
        'viewers_deployments_users',
        sa.Column('deployment_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['deployment_id'],
            ['deployments._storage_id'],
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_table(
        'deployment_updates',
        sa.Column('_storage_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Text(), nullable=True),
        sa.Column(
            'created_at',
            manager_rest.storage.models_base.UTCDateTime(),
            nullable=False,
        ),
        sa.Column('deployment_plan', sa.PickleType(), nullable=True),
        sa.Column(
            'deployment_update_node_instances',
            sa.PickleType(),
            nullable=True,
        ),
        sa.Column(
            'deployment_update_deployment',
            sa.PickleType(),
            nullable=True,
        ),
        sa.Column('deployment_update_nodes', sa.PickleType(), nullable=True),
        sa.Column('modified_entity_ids', sa.PickleType(), nullable=True),
        sa.Column('state', sa.Text(), nullable=True),
        sa.Column('_execution_fk', sa.Integer(), nullable=True),
        sa.Column('_deployment_fk', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['_deployment_fk'],
            [u'deployments._storage_id'],
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['_execution_fk'],
            [u'executions._storage_id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('_storage_id')
    )
    op.create_index(
        op.f('ix_deployment_updates_created_at'),
        'deployment_updates',
        ['created_at'],
        unique=False,
    )
    op.create_index(
        op.f('ix_deployment_updates_id'),
        'deployment_updates',
        ['id'],
        unique=False,
    )
    op.create_table(
        'events',
        sa.Column('_storage_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Text(), nullable=True),
        sa.Column(
            'timestamp',
            manager_rest.storage.models_base.UTCDateTime(),
            nullable=False,
        ),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('message_code', sa.Text(), nullable=True),
        sa.Column('event_type', sa.Text(), nullable=True),
        sa.Column('operation', sa.Text(), nullable=True),
        sa.Column('node_id', sa.Text(), nullable=True),
        sa.Column('_execution_fk', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['_execution_fk'],
            [u'executions._storage_id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('_storage_id')
    )
    op.create_index(op.f('ix_events_id'), 'events', ['id'], unique=False)
    op.create_index(
        op.f('ix_events_timestamp'),
        'events',
        ['timestamp'],
        unique=False,
    )
    op.create_table(
        'logs',
        sa.Column('_storage_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Text(), nullable=True),
        sa.Column(
            'timestamp',
            manager_rest.storage.models_base.UTCDateTime(),
            nullable=False,
        ),
        sa.Column('message', sa.Text(), nullable=True),
        sa.Column('message_code', sa.Text(), nullable=True),
        sa.Column('logger', sa.Text(), nullable=True),
        sa.Column('level', sa.Text(), nullable=True),
        sa.Column('operation', sa.Text(), nullable=True),
        sa.Column('node_id', sa.Text(), nullable=True),
        sa.Column('_execution_fk', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['_execution_fk'],
            [u'executions._storage_id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('_storage_id')
    )
    op.create_index(op.f('ix_logs_id'), 'logs', ['id'], unique=False)
    op.create_index(
        op.f('ix_logs_timestamp'),
        'logs',
        ['timestamp'],
        unique=False,
    )
    op.create_table(
        'node_instances',
        sa.Column('_storage_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Text(), nullable=True),
        sa.Column('host_id', sa.Text(), nullable=True),
        sa.Column('relationships', sa.PickleType(), nullable=True),
        sa.Column('runtime_properties', sa.PickleType(), nullable=True),
        sa.Column('scaling_groups', sa.PickleType(), nullable=True),
        sa.Column('state', sa.Text(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=True),
        sa.Column('_node_fk', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['_node_fk'],
            [u'nodes._storage_id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('_storage_id')
    )
    op.create_index(
        op.f('ix_node_instances_id'),
        'node_instances',
        ['id'],
        unique=False,
    )
    op.create_table(
        'owners_executions_users',
        sa.Column('execution_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['execution_id'],
            ['executions._storage_id'],
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_table(
        'viewers_executions_users',
        sa.Column('execution_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ['execution_id'],
            ['executions._storage_id'],
        ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], )
    )
    op.create_table(
        'deployment_update_steps',
        sa.Column('_storage_id', sa.Integer(), nullable=False),
        sa.Column('id', sa.Text(), nullable=True),
        sa.Column('action', action_type, nullable=True),
        sa.Column('entity_id', sa.Text(), nullable=False),
        sa.Column('entity_type', entity_type, nullable=True),
        sa.Column('_deployment_update_fk', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['_deployment_update_fk'],
            [u'deployment_updates._storage_id'],
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('_storage_id')
    )
    op.create_index(
        op.f('ix_deployment_update_steps_id'),
        'deployment_update_steps',
        ['id'],
        unique=False,
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f('ix_deployment_update_steps_id'),
        table_name='deployment_update_steps',
    )
    op.drop_table('deployment_update_steps')
    entity_type.drop(op.get_bind())
    action_type.drop(op.get_bind())
    op.drop_table('viewers_executions_users')
    op.drop_table('owners_executions_users')
    op.drop_index(op.f('ix_node_instances_id'), table_name='node_instances')
    op.drop_table('node_instances')
    op.drop_index(op.f('ix_logs_timestamp'), table_name='logs')
    op.drop_index(op.f('ix_logs_id'), table_name='logs')
    op.drop_table('logs')
    op.drop_index(op.f('ix_events_timestamp'), table_name='events')
    op.drop_index(op.f('ix_events_id'), table_name='events')
    op.drop_table('events')
    op.drop_index(
        op.f('ix_deployment_updates_id'),
        table_name='deployment_updates',
    )
    op.drop_index(
        op.f('ix_deployment_updates_created_at'),
        table_name='deployment_updates',
    )
    op.drop_table('deployment_updates')
    op.drop_table('viewers_deployments_users')
    op.drop_table('owners_deployments_users')
    op.drop_index(op.f('ix_nodes_type'), table_name='nodes')
    op.drop_index(op.f('ix_nodes_id'), table_name='nodes')
    op.drop_table('nodes')
    op.drop_index(op.f('ix_executions_id'), table_name='executions')
    op.drop_index(op.f('ix_executions_created_at'), table_name='executions')
    op.drop_table('executions')
    execution_status.drop(op.get_bind())
    op.drop_index(
        op.f('ix_deployment_modifications_id'),
        table_name='deployment_modifications',
    )
    op.drop_index(
        op.f('ix_deployment_modifications_ended_at'),
        table_name='deployment_modifications',
    )
    op.drop_index(
        op.f('ix_deployment_modifications_created_at'),
        table_name='deployment_modifications',
    )
    op.drop_table('deployment_modifications')
    deployment_modification_status.drop(op.get_bind())
    op.drop_table('viewers_snapshots_users')
    op.drop_table('viewers_secrets_users')
    op.drop_table('viewers_plugins_users')
    op.drop_table('viewers_blueprints_users')
    op.drop_table('owners_snapshots_users')
    op.drop_table('owners_secrets_users')
    op.drop_table('owners_plugins_users')
    op.drop_table('owners_blueprints_users')
    op.drop_index(op.f('ix_deployments_id'), table_name='deployments')
    op.drop_index(op.f('ix_deployments_created_at'), table_name='deployments')
    op.drop_table('deployments')
    op.drop_table('users_tenants')
    op.drop_table('users_roles')
    op.drop_table('users_groups')
    op.drop_index(op.f('ix_snapshots_id'), table_name='snapshots')
    op.drop_index(op.f('ix_snapshots_created_at'), table_name='snapshots')
    op.drop_table('snapshots')
    snapshot_status.drop(op.get_bind())
    op.drop_index(op.f('ix_secrets_id'), table_name='secrets')
    op.drop_index(op.f('ix_secrets_created_at'), table_name='secrets')
    op.drop_table('secrets')
    op.drop_index(op.f('ix_plugins_uploaded_at'), table_name='plugins')
    op.drop_index(op.f('ix_plugins_package_name'), table_name='plugins')
    op.drop_index(op.f('ix_plugins_id'), table_name='plugins')
    op.drop_index(op.f('ix_plugins_archive_name'), table_name='plugins')
    op.drop_table('plugins')
    op.drop_table('groups_tenants')
    op.drop_index(op.f('ix_blueprints_id'), table_name='blueprints')
    op.drop_index(op.f('ix_blueprints_created_at'), table_name='blueprints')
    op.drop_table('blueprints')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_tenants_name'), table_name='tenants')
    op.drop_table('tenants')
    op.drop_index(op.f('ix_roles_name'), table_name='roles')
    op.drop_table('roles')
    op.drop_table('provider_context')
    op.drop_index(op.f('ix_groups_name'), table_name='groups')
    op.drop_index(op.f('ix_groups_ldap_dn'), table_name='groups')
    op.drop_table('groups')
    # ### end Alembic commands ###

########
# Copyright (c) 2019 Cloudify Platform Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
############

import os
import json
import logging
import argparse

from cloudify import broker_config, dispatch
from cloudify.logs import setup_agent_logger
from cloudify.utils import get_admin_api_token
from cloudify.constants import MGMTWORKER_QUEUE
from cloudify.manager import get_rest_client
from cloudify.amqp_client import (
    AMQPConnection, TaskConsumer
)
from cloudify.error_handling import serialize_known_exception


DEFAULT_MAX_WORKERS = 10
logger = logging.getLogger('mgmtworker')


class CloudifyWorkflowConsumer(TaskConsumer):
    routing_key = 'workflow'
    handler = dispatch.WorkflowHandler
    late_ack = 'never'

    def _print_task(self, ctx, action, status=None):
        if ctx['type'] in ['workflow', 'hook']:
            prefix = '{0} {1}'.format(action, ctx['type'])
            suffix = ''
        else:
            prefix = '{0} operation'.format(action)
            suffix = '\n\tNode ID: {0}'.format(ctx.get('node_id'))

        if status:
            suffix += '\n\tStatus: {0}'.format(status)

        tenant_name = ctx.get('tenant', {}).get('name')
        logger.info(
            '\n\t{prefix} on queue `{queue}` on tenant `{tenant}`:\n'
            '\tTask name: {name}\n'
            '\tExecution ID: {execution_id}\n'
            '\tWorkflow ID: {workflow_id}{suffix}\n'.format(
                tenant=tenant_name,
                prefix=prefix,
                name=ctx['task_name'],
                queue=ctx.get('task_target'),
                execution_id=ctx.get('execution_id'),
                workflow_id=ctx.get('workflow_id'),
                suffix=suffix))

    def handle_task(self, full_task):
        task = full_task['cloudify_task']
        ctx = task['kwargs'].pop('__cloudify_context')

        self._print_task(ctx, 'Started handling')
        handler = self.handler(cloudify_context=ctx,
                               args=task.get('args', []),
                               kwargs=task['kwargs'])
        try:
            rv = handler.handle_or_dispatch_to_subprocess_if_remote()
            result = {'ok': True, 'result': rv}
            status = 'SUCCESS - result: {0}'.format(result)
        except Exception as e:
            error = serialize_known_exception(e)
            result = {'ok': False, 'error': error}
            status = 'ERROR - result: {0}'.format(result)
            logger.error(
                'ERROR - caught: {0}\n{1}'.format(
                    repr(e), error['traceback']))
        self._print_task(ctx, 'Finished handling', status)
        return result


def make_amqp_worker(args):
    handlers = [
        CloudifyWorkflowConsumer(args.queue, args.max_workers),
    ]
    return AMQPConnection(handlers=handlers, connect_timeout=None)


def prepare_broker_config():
    client = get_rest_client(
        tenant='default_tenant', api_token=get_admin_api_token())
    brokers = client.manager.get_brokers().items
    config_path = broker_config.get_config_path()
    cert_path = os.path.join(os.path.dirname(config_path), 'broker_cert.pem')
    with open(cert_path, 'w') as f:
        f.write('\n'.join(broker.ca_cert_content for broker in brokers
                if broker.ca_cert_content))
    broker_addrs = [broker.networks.get('default') for broker in brokers
                    if broker.networks.get('default')]
    config = {
        'broker_ssl_enabled': True,
        'broker_cert_path': cert_path,
        'broker_username': brokers[0].username,
        'broker_password': brokers[0].password,
        'broker_vhost': '/',
        'broker_management_hostname': brokers[0].management_host,
        'broker_hostname': broker_addrs
    }
    with open(config_path, 'w') as f:
        json.dump(config, f)
    broker_config.load_broker_config()


def main():
    os.environ.update({
        'REST_HOST': '127.0.0.1',
        'REST_PORT': '53333',
        'LOCAL_REST_CERT_FILE': '/etc/cloudify/ssl/cloudify_internal_ca_cert.pem',  # NOQA
        'AGENT_WORK_DIR': '/opt/mgmtworker/work'
    })
    parser = argparse.ArgumentParser()
    parser.add_argument('--queue', default=MGMTWORKER_QUEUE)
    parser.add_argument('--max-workers', default=DEFAULT_MAX_WORKERS, type=int)
    parser.add_argument('--name')
    parser.add_argument('--hooks-queue')
    parser.add_argument('--cluster-service-queue')
    args = parser.parse_args()

    setup_agent_logger('mgmtworker')

    prepare_broker_config()
    worker = make_amqp_worker(args)
    worker.consume()


if __name__ == '__main__':
    main()

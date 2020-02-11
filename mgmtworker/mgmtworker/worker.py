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

import logging
import argparse

from cloudify import broker_config, dispatch
from cloudify.logs import setup_agent_logger
from cloudify.constants import MGMTWORKER_QUEUE
from cloudify.amqp_client import (
    AMQPConnection, TaskConsumer
)
from cloudify.error_handling import serialize_known_exception


DEFAULT_MAX_WORKERS = 10
logger = logging.getLogger('mgmtworker')


class CloudifyWorkflowConsumer(TaskConsumer):
    routing_key = 'workflow'
    handler = dispatch.WorkflowHandler
    late_ack = True

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
    broker_config.load_broker_config()


def main():
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

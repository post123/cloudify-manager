import os
import aiohttp
import logging
import asyncio
import aio_pika
import json

from cloudify import utils
from mgmtworker.workflows import workflow_context

logger = logging.getLogger()


def get_conn_kwargs(vhost='/'):
    with open('/opt/mgmtworker/work/broker_config.json') as f:
        broker_config = json.load(f)
    return {
        'host': broker_config['broker_hostname'][0],
        'port': 5671,
        'ssl': True,
        'ssl_options': {
            'ca_certs': broker_config['broker_cert_path']
        },
        'login': broker_config['broker_username'],
        'password': broker_config['broker_password'],
        'virtualhost': vhost
    }


class Worker:
    def __init__(self, loop):
        self._loop = loop
        self._session = None
        self._events_exchange = None
        self.channel = None
        self._connections = {}
        self._channels = {}

    async def get_channel(self, vhost):
        if vhost in self._channels:
            return self._channels[vhost]
        kwargs = get_conn_kwargs(vhost)
        logger.info('conn kwargs for %s: %s', vhost, kwargs)
        connection = await aio_pika.connect_robust(
            loop=self._loop,
            **kwargs
        )
        channel = await connection.channel()
        self._connections[vhost] = connection
        self._channels[vhost] = channel
        return channel

    async def handle_message(self, message):
        data = json.loads(message.body)
        task = data['cloudify_task']
        ctx = task['kwargs'].pop('__cloudify_context')
        args = task.get('args', [])
        kwargs = task['kwargs']
        ctx['worker'] = self
        wctx = workflow_context.CloudifyWorkflowContext(ctx)
        await wctx.prepare()
        func = utils.get_func(ctx['task_name'])
        await wctx.internal.send_workflow_event(
            event_type='workflow_started',
            message="Starting '{0}' workflow execution".format(
                wctx.workflow_id)
        )
        try:
            await func(wctx, **kwargs)
        except Exception as e:
            logger.exception('failed')
            await wctx.rest_client.request(
                'PATCH',
                f'executions/{wctx.execution_id}',
                json={'status': 'failed'}
            )
            await wctx.internal.send_workflow_event(
                event_type='workflow_failed',
                message="'{0}' workflow execution failed: {1}".format(
                    wctx.workflow_id, str(e))
            )
        else:
            await wctx.rest_client.request(
                'PATCH',
                f'executions/{wctx.execution_id}',
                json={'status': 'terminated'}
            )
            await wctx.internal.send_workflow_event(
                event_type='workflow_succeeded',
                message="'{0}' workflow execution succeeded".format(
                    wctx.workflow_id),
            )
        logging.info('wctx %s func %s', wctx, func)

    @property
    def rest_session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def main(self):
        finished = asyncio.Event()
        queue_name = "cloudify.management_workflow"

        channel = await self.get_channel('/')
        self.channel = channel
        queue = await channel.declare_queue(
            queue_name,
            durable=True
        )
        await channel.declare_exchange(
            name='cloudify.management',
            durable=True
        )
        self._events_exchange = await channel.declare_exchange(
            name='cloudify-events-topic',
            durable=True,
            type='topic'
        )
        self._events_exchange = await channel.declare_exchange(
            name='cloudify-events-topic',
            durable=True,
            type='topic'
        )
        await queue.bind('cloudify.management', routing_key='workflow')
        await queue.consume(self.handle_message, no_ack=True)
        await finished.wait()


if __name__ == "__main__":
    os.environ['AGENT_WORK_DIR'] = '/opt/mgmtworker/work'
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    worker = Worker(loop)
    loop.run_until_complete(worker.main())
    loop.close()

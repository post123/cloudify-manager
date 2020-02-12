import aiohttp
import logging
import asyncio
import aio_pika
import json

from cloudify import utils
from mgmtworker.workflows import workflow_context

logger = logging.getLogger()


def get_conn_kwargs():
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
    }


class Worker:
    def __init__(self, loop):
        self._loop = loop
        self._session = None

    async def handle_message(self, message):
        data = json.loads(message.body)
        logging.info('hello %s, %s', message, data)
        task = data['cloudify_task']
        ctx = task['kwargs'].pop('__cloudify_context')
        args = task.get('args', [])
        kwargs = task['kwargs']
        ctx['worker'] = self
        wctx = workflow_context.CloudifyWorkflowContext(ctx)
        await wctx.prepare()
        func = utils.get_func(ctx['task_name'])
        logging.info('wctx %s func %s', wctx, func)

    @property
    def rest_session(self):
        if self._session is None:
            self._session = aiohttp.ClientSession()
        return self._session

    async def main(self):
        finished = asyncio.Event()
        connection = await aio_pika.connect_robust(
            loop=self._loop,
            **get_conn_kwargs()
        )

        async with connection:
            queue_name = "cloudify.management_workflow"

            channel = await connection.channel()
            queue = await channel.declare_queue(
                queue_name,
                durable=True
            )
            await channel.declare_exchange(
                name='cloudify.management',
                durable=True
            )
            await queue.bind('cloudify.management', routing_key='workflow')
            await queue.consume(self.handle_message, no_ack=True)
            await finished.wait()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    worker = Worker(loop)
    loop.run_until_complete(worker.main())
    loop.close()

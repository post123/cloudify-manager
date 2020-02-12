import logging
import asyncio
import aio_pika
import json

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


async def handle_message(message):
    logging.info('hello %s', message)


async def main(loop):
    connection = await aio_pika.connect_robust(
        loop=loop,
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
        queue.consume(handle_message, no_ack=True)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
    loop.close()

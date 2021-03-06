########
# Copyright (c) 2016 GigaSpaces Technologies Ltd. All rights reserved
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

import json
import os
import sys
import threading

from pika.exceptions import ConnectionClosed

import cloudify.event
import cloudify.logs
from cloudify_cli.colorful_event import ColorfulEvent
from cloudify.constants import EVENTS_EXCHANGE_NAME, LOGS_EXCHANGE_NAME

from integration_tests.framework import utils

logger = utils.setup_logger('events_printer')


class EventsPrinter(threading.Thread):

    def __init__(self, container_ip):
        super(EventsPrinter, self).__init__()
        self.daemon = True
        self._container_ip = container_ip

    def run(self):
        """
        This function will consume logs and events directly from the
        cloudify-logs and cloudify-events-topic exchanges. (As opposed to the
        usual means of fetching events using the REST api).

        Note: This method is only used for events/logs printing.
        Tests that need to assert on event should use the REST client events
        module.
        """
        connection = utils.create_pika_connection(self._container_ip)
        channel = connection.channel()
        queues = []

        # Binding the logs queue
        self._bind_queue_to_exchange(channel,
                                     LOGS_EXCHANGE_NAME,
                                     'fanout',
                                     queues)

        # Binding the events queue
        self._bind_queue_to_exchange(channel,
                                     EVENTS_EXCHANGE_NAME,
                                     'topic',
                                     queues,
                                     routing_key='events.#')

        if not os.environ.get('CI'):
            cloudify.logs.EVENT_CLASS = ColorfulEvent
        cloudify.logs.EVENT_VERBOSITY_LEVEL = cloudify.event.MEDIUM_VERBOSE

        def callback(ch, method, properties, body):
            try:
                ev = json.loads(body)
                output = cloudify.logs.create_event_message_prefix(ev)
                if output:
                    sys.stdout.write('{0}\n'.format(output))
            except Exception:
                logger.error('event/log format error - output: {0}'
                             .format(body), exc_info=True)

        channel.basic_consume(callback, queue=queues[0], no_ack=True)
        channel.basic_consume(callback, queue=queues[1], no_ack=True)
        try:
            channel.start_consuming()
        except ConnectionClosed:
            pass

    def _bind_queue_to_exchange(self,
                                channel,
                                exchange_name,
                                exchange_type,
                                queues,
                                routing_key=None):
        channel.exchange_declare(exchange=exchange_name,
                                 exchange_type=exchange_type,
                                 auto_delete=False,
                                 durable=True)
        result = channel.queue_declare(exclusive=True)
        queue_name = result.method.queue
        queues.append(queue_name)
        channel.queue_bind(exchange=exchange_name,
                           queue=queue_name,
                           routing_key=routing_key)

#########
# Copyright (c) 2019 Cloudify Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  * See the License for the specific language governing permissions and
#  * limitations under the License.
#

from flask_restful.reqparse import Argument

from manager_rest.rest import resources_v2
from manager_rest.security import SecuredResource
from manager_rest.security.authorization import authorize
from manager_rest.resource_manager import get_resource_manager
from manager_rest.storage import (models,  get_storage_manager)
from manager_rest.rest.rest_utils import get_args_and_verify_arguments


class Executions(resources_v2.Executions):
    # @authorize('execution_delete')
    # TODO :: this should be added to authorization.conf at the very end.
    def delete(self):
        sm = get_storage_manager()
        args = get_args_and_verify_arguments(
            [Argument('keep_last', required=False),
             Argument('keep_days', required=False)]
        )
        # TODO ::
        #  filter by days, tenant, created_by, status
        #  only delete executions with status in EndStates
        #  make `keep_last` and `keep_days` mutually-exclusive

        executions = sm.list(models.Execution, all_tenants=True)
        if args['keep_last']:
            executions = executions[:int(args['keep_last'])]

        import pydevd
        pydevd.settrace('192.168.9.43', port=53100, stdoutToServer=True,
                        stderrToServer=True)
        return 'Done.', 200


class ExecutionsCheck(SecuredResource):
    @authorize('execution_should_start')
    def get(self, execution_id):
        """
        `should_start` - return True if this execution can currently start
        (no system exeuctions / executions under the same deployment are
        currently running)
        """

        sm = get_storage_manager()
        execution = sm.get(models.Execution, execution_id)
        deployment_id = execution.deployment.id
        rm = get_resource_manager()
        return not (rm.check_for_executions(deployment_id, force=False,
                                            queue=True, execution=execution))


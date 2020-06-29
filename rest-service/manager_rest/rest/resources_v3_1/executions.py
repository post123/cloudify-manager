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
from datetime import datetime, timedelta

from flask_restful.reqparse import Argument
from flask_restful.inputs import positive, date

from cloudify._compat import text_type
from cloudify.models_states import ExecutionState

from manager_rest.security import SecuredResource
from manager_rest.security.authorization import authorize
from manager_rest.rest import resources_v2, rest_decorators
from manager_rest.resource_manager import get_resource_manager
from manager_rest.rest.rest_utils import get_args_and_verify_arguments
from manager_rest.storage import models,  get_storage_manager


class Executions(resources_v2.Executions):
    # @authorize('execution_delete')
    # TODO :: this should be added to authorization.conf at the very end.
    @rest_decorators.marshal_with(models.Execution)
    def delete(self):
        sm = get_storage_manager()
        args = get_args_and_verify_arguments(
            [Argument('keep_last', type=positive, required=False),
             Argument('keep_days', type=positive, required=False),
             Argument('keep_since_date', type=date, required=False),
             Argument('created_by', type=text_type, required=False),
             Argument('tenant_name', type=text_type, required=False),
             Argument('status', type=text_type, required=False)]
        )

        filters = {}
        if args['created_by']:
            filters['created_by'] = args['created_by']
        if args['tenant_name']:
            filters['tenant_name'] = args['tenant_name']
        if args['status']:
            if args['status'] not in ExecutionState.END_STATES:
                raise ValueError(
                    'Can\'t filter by execution status `{0}`. '
                    'Allowed statuses are: {1}'.format(
                        args['status'], ExecutionState.END_STATES)
                )
            filters['status'] = args['status']
        else:
            filters['status'] = ExecutionState.END_STATES

        executions = sm.list(models.Execution,
                             filters=filters,
                             all_tenants=True)
        dep_creation_execs = {}
        for execution in executions:
            if execution.workflow_id == 'create_deployment_environment' and \
                    execution.status == 'terminated':
                dep_creation_execs[execution.deployment_id] = \
                    dep_creation_execs.get(execution.deployment_id, 0) + 1

        executions_to_delete = []

        if args['keep_days']:
            now_utc = datetime.utcnow()
            requested_time = (datetime(*now_utc.timetuple()[:3])
                              - timedelta(days=args['keep_days']-1))
            for execution in executions:
                creation_time = datetime.strptime(execution.created_at,
                                                  '%Y-%m-%dT%H:%M:%S.%fZ')
                if creation_time < requested_time and \
                        self._can_delete_execution(execution,
                                                   dep_creation_execs):
                    executions_to_delete.append(execution)
                    sm.delete(execution)
        elif args['keep_since_date']:  # UNIX date format: YYYY-(m)m-(d)d
            for execution in executions:
                creation_time = datetime.strptime(execution.created_at,
                                                  '%Y-%m-%dT%H:%M:%S.%fZ')
                if creation_time < args['keep_since_date'] and \
                        self._can_delete_execution(execution,
                                                   dep_creation_execs):
                    executions_to_delete.append(execution)
                    sm.delete(execution)
        elif args['keep_last']:
            num_to_delete = len(executions) - args['keep_last']
            for execution in executions:
                if self._can_delete_execution(execution, dep_creation_execs):
                    executions_to_delete.append(execution)
                    sm.delete(execution)
                    num_to_delete -= 1
                if num_to_delete == 0:
                    break

        return executions_to_delete

    @staticmethod
    def _can_delete_execution(execution, dep_creation_execs):
        if execution.workflow_id == \
                'create_deployment_environment':
            if dep_creation_execs[execution.deployment_id] <= 1:
                return False
            else:
                dep_creation_execs[execution.deployment_id] -= 1
        return True


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


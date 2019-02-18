#########
# Copyright (c) 2019 Cloudify Platform Ltd. All rights reserved
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

from datetime import datetime

from manager_rest.rest import rest_decorators, rest_utils
from manager_rest.security import SecuredResource
from manager_rest.security.authorization import authorize
from manager_rest.storage import get_storage_manager, models


class ManagerConfig(SecuredResource):
    @rest_decorators.exceptions_handled
    @authorize('manager_config_get')
    def get(self):
        """
        Get the Manager config
        """
        sm = get_storage_manager()
        return [m.to_dict() for m in sm.list(models.Config)]

    @rest_decorators.exceptions_handled
    @authorize('manager_config_get')
    def put(self):
        sm = get_storage_manager()
        data = rest_utils.get_json_and_verify_params({
            'name': {'type': 'unicode'},
            'value': {'type': 'unicode'},
        })
        name = data['name']
        value = data['value']
        try:
            inst = sm.list(models.Config, {'name': name})[0]
        except IndexError:
            inst = models.Config(name=name, value=value)
        sm.update(inst)
        inst.updated_at = datetime.now()
        return inst.to_dict()

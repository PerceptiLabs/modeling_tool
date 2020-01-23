'''
import pytest
from unittest.mock import MagicMock, call
from core_new.core2 import Core


def test_deploys_with_identifier():
    graph_builder = MagicMock()
    script_builder = MagicMock()
    deployment_pipe = MagicMock()
    command_queue = MagicMock()
    result_queue = MagicMock()
    data_policies = MagicMock()

    graph_spec = MagicMock()
    
    script_builder.build.return_value = ''
    deployment_pipe.is_active = False
    
    core = Core(graph_builder, script_builder, deployment_pipe,
                command_queue, result_queue, data_policies)
    core.run(graph_spec, session_id='123456')
    assert deployment_pipe.deploy.call_args == call('123456', '')
    


'''

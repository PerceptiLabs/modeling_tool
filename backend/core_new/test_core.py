import pytest
from unittest.mock import MagicMock, call
from core_new.core2 import Core


def test_deploys_with_identifier():
    script_builder = MagicMock()
    deployment_pipe = MagicMock()
    
    script_builder.build.return_value = ''
    deployment_pipe.is_active = False
    
    core = Core(script_builder, deployment_pipe)
    core.run(identifier='123456')
    assert deployment_pipe.deploy.call_args == call('123456', '')
    


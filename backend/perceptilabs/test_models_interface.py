import pytest
from unittest.mock import MagicMock

from perceptilabs.models_interface import ModelsInterface
from perceptilabs.utils import KernelError


def make_interface(task_executor=None, message_broker=None, event_tracker=None, dataset_access=None, model_access=None, model_archives_access=None, epochs_access=None, training_results_access=None, preprocessing_results_access=None, preview_cache=None):
    interface = ModelsInterface(
        task_executor=task_executor or MagicMock(),
        message_broker=message_broker or MagicMock(),
        event_tracker=event_tracker or MagicMock(),
        dataset_access=dataset_access or MagicMock(),
        model_access=model_access or MagicMock(),
        model_archives_access=model_archives_access or MagicMock(),
        epochs_access=epochs_access or MagicMock(),
        training_results_access=training_results_access or MagicMock(),
        preprocessing_results_access=preprocessing_results_access or MagicMock(),
        preview_cache=preview_cache or MagicMock(),
    )
    return interface


def test_export_archive_failure_raises_kernel_error(tmp_path):
    model_archives_access = MagicMock()
    model_archives_access.write.side_effect = ValueError("Crash!")
    interface = make_interface(model_archives_access=model_archives_access)

    with pytest.raises(KernelError):
        interface.export(
            model_id=MagicMock(),
            options={'Type': 'Archive', 'Location': tmp_path},
            dataset_settings_dict=MagicMock(),
            graph_spec_dict=MagicMock(),
            user_email=MagicMock(),
            training_settings_dict=MagicMock(),
            frontend_settings=MagicMock(),
            training_session_id=MagicMock(),            
        )

    
def test_export_archive_failure_raises_kernel_error(tmp_path):
    model_archives_access = MagicMock()
    model_archives_access.write.side_effect = ValueError("Crash!")
    interface = make_interface(model_archives_access=model_archives_access)

    with pytest.raises(KernelError):
        interface.export(
            model_id=MagicMock(),
            options={'Type': 'Archive', 'Location': tmp_path},
            dataset_settings_dict=MagicMock(),
            graph_spec_dict=MagicMock(),
            user_email=MagicMock(),
            training_settings_dict=MagicMock(),
            frontend_settings=MagicMock(),
            training_session_id=MagicMock(),            
        )

    
def test_export_normal_failure_raises_kernel_error(monkeypatch):
    epochs_access = MagicMock()
    epochs_access.has_checkpoint = True

    fn_export = MagicMock()
    fn_export.side_effect = ValueError("Crash!")

    from perceptilabs.sharing.exporter import Exporter
    monkeypatch.setattr(Exporter, "export", fn_export)  
    
    interface = make_interface(epochs_access=epochs_access)

    with pytest.raises(KernelError):
        interface.export(
            model_id=MagicMock(),
            options=MagicMock(),
            dataset_settings_dict=MagicMock(),
            graph_spec_dict=MagicMock(),
            user_email=MagicMock(),
            training_settings_dict=MagicMock(),
            frontend_settings=MagicMock(),
            training_session_id=MagicMock(),            
        )

    
    
        
    
    
        
    

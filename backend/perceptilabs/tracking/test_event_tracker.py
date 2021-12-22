import pytest
from unittest.mock import MagicMock

import perceptilabs.tracking.base
from perceptilabs.tracking.base import EventTracker


@pytest.fixture(scope='function', autouse=True)
def mixpanel_mock(monkeypatch):
    fn_track = MagicMock()
    fn_set_once = MagicMock()
    fn_set = MagicMock()    

    from mixpanel import Mixpanel
    monkeypatch.setattr(Mixpanel, 'track', fn_track, raising=True)
    monkeypatch.setattr(Mixpanel, 'people_set_once', fn_set_once, raising=True)
    monkeypatch.setattr(Mixpanel, 'people_set', fn_set, raising=True)        

    return Mixpanel


def test_event_fires_despite_some_properties_corrupt(mixpanel_mock):
    tracker = EventTracker()
    tracker.emit(
        'some-event',
        'a@b.com',
        properties={
            'something-that-can-be-serialized': 'abc',
            'something-that-cannot-be-serialized': EventTracker
        }
    )
    assert mixpanel_mock.track.call_args[1] == {
        'event_name': 'some-event',
        'distinct_id': 'a@b.com',
        'properties': {'something-that-can-be-serialized': 'abc'}
    }

    
def test_event_fires_despite_all_properties_corrupt(mixpanel_mock):
    tracker = EventTracker()
    tracker.emit(
        'some-event',
        'a@b.com',
        properties={
            'something-that-cannot-be-serialized-1': EventTracker,
            'something-that-cannot-be-serialized-2': EventTracker
        }
    )
    assert mixpanel_mock.track.call_args[1] == {
        'event_name': 'some-event',
        'distinct_id': 'a@b.com',
        'properties': {}
    }
        

@pytest.mark.parametrize("method", ['track', 'people_set', 'people_set_once'])
@pytest.mark.parametrize("raise_errors", [True, False])
def test_raises_errors(mixpanel_mock, method, raise_errors):
    method_mock = getattr(mixpanel_mock, method)
    method_mock.side_effect = ValueError(f"method '{method}' raised error")

    tracker = EventTracker(raise_errors=raise_errors)

    def closure():
        tracker.emit(
            'some-event',
            'a@b.com',
            properties={
                'something-that-can-be-serialized': 'abc',
            }
        )

    if raise_errors:
        with pytest.raises(ValueError):  # Asserts that the error is raised
            closure()
    else:
        closure() # If an error is raised the test fails with a ValueError

    
    
    
    

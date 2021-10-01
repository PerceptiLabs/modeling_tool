from concurrent.futures import ThreadPoolExecutor
from threading import Lock, Event
import logging
import requests

from perceptilabs.session.base import BaseExecutor
from perceptilabs.logconf import APPLICATION_LOGGER
from perceptilabs.utils import DummyExecutor
import perceptilabs.session.utils as session_utils

logger = logging.getLogger(APPLICATION_LOGGER)


class ThreadedSession:  
    def __init__(self, make_future):
        self._token = Event()
        self._future = make_future(self._token)
        self._meta = None

    def __del__(self):
        if self._token:
            self._token.set()
            self._token = None

        if self._future:
            ret = self._future.cancel()
            self._future = None

    def get_metadata(self):
        return self._meta

    def set_metadata(self, **kwargs):
        self._meta = kwargs

        
# Thread-interlocked cache of session-related metadata
class SessionCache:  
    def __init__(self):
        self._sessions = {}
        self._lock = Lock()

    def dispose(self):
        with self._lock:
            while self._sessions:
                first_key = list(self._sessions.keys())[0]
                del self._sessions[first_key]
        
    def add(self, id, make_future):
        # thread-unsafe pre-clear of the cache for perf
        if id in self._sessions:  # Delete existing
            with self._lock:
                del self._sessions[id]

        # thread-safe upsert of cache value for correctness
        with self._lock:
            if id in self._sessions:
                del self._sessions[id]
            self._sessions[id] = ThreadedSession(make_future)

    def set_metadata(self, id, **kwargs):
        with self._lock:
            self._sessions[id].set_metadata(**kwargs)

    def set_exception(self, id, exception):
        with self._lock:
            self._sessions[id].set_metadata(exception=exception)

    def set_complete(self, id):
        with self._lock:
            self._sessions[id] = None

    def cancel_session(self, id):
        with self._lock:
            session = self._sessions.get(id)
            if not session:
                return None

            del self._sessions[id]
            return session.get_metadata()

    def get(self, id):
        with self._lock:
            session = self._sessions.get(id)
            if not session:
                return None
            meta = session.get_metadata()

            if not meta:
                return None

            if "exception" in meta:
                raise meta["exception"]

            return meta

    def get_active(self):
        with self._lock:
            ret = {}

            for key, value in self._sessions.items():
                if value and value.get_metadata() is not None:
                    ret[key] = value.get_metadata().copy()
                    
            return ret

        
class ThreadedExecutor(BaseExecutor):
    def __init__(self, single_threaded=False, session_classes=None):
        self._session_classes = session_classes or {}        
        self._pool = DummyExecutor() if single_threaded else ThreadPoolExecutor()
        self._session_cache = SessionCache()
        self._id_counter = 0

    @property
    def session_classes(self):
        return self._session_classes.copy()

    def dispose(self):
        if self._pool and isinstance(self._pool, ThreadPoolExecutor):
            self._pool.shutdown(wait=False)
            self._pool = None

        if self._session_cache:
            self._session_cache.dispose()
            self._session_cache = None

    def start_session(self, session_type, payload):
        session_class = self.session_classes[session_type]

        session_id = self._id_counter
        self._id_counter += 1
        
        def on_session_started(start_payload, port):
            self._session_cache.set_metadata(
                session_id,
                port=port,
                hostname='localhost',
                payload=start_payload,
                type=session_type
            )

        def run_session(cancel_token):
            try:
                session = session_class()
                session.start(
                    payload,
                    on_task_started=on_session_started,
                    is_retry=False,
                    cancel_token=cancel_token
                )
                self._session_cache.set_complete(session_id)
            except Exception as e:
                #import traceback
                #tb = traceback.format_exc()
                #print('TRACEBACK', tb)
                
                self._session_cache.set_exception(session_id, e)
                logger.exception("Exception when starting session")

        run_with_token = lambda token: self._pool.submit(run_session, token)
        self._session_cache.add(session_id, run_with_token)
        return session_id

    def get_session_hostname(self, session_id):
        meta = self.get_session_meta(session_id)
        hostname = meta['hostname']
        return hostname

    def get_workers(self):
        return [{"host": "-"}]

    def cancel_session(self, session_id, payload=None):
        payload = payload or {}
        
        try:
            # try to send an initial stop request.
            self.send_request(session_id, payload)
        except:
            pass

        self._session_cache.cancel_session(session_id)

    def get_sessions(self, predicate=None):
        if predicate is None:
            predicate = lambda x, y: True  # Get all sessions
        
        sessions = {}
        for session_id, metadata in self._session_cache.get_active().items():
            if predicate(session_id, metadata):
                sessions[session_id] = metadata
                
        return sessions

    def get_session_meta(self, session_id):
        return self._session_cache.get(session_id)

    def is_available(self):
        return True

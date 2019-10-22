from unittest.mock import MagicMock
import pytest

from core_new.session import *

class TestLayerSession:

    def test_render_not_called(self):
        code = "print('Hello!')"
        
        on_render = MagicMock()
        session = LayerSession(123, code, on_render_callback=on_render)
        session.run()

        assert on_render.call_count == 0
        
    def test_render_called(self):
        code  = "print('Hello!')\n"
        code += "api.ui.render(dashboard='testing')\n"
        

        on_render = MagicMock()        
        session = LayerSession(123, code, on_render_callback=on_render)
        session.run()

        assert on_render.call_count == 1

    def test_pause(self):
        code  = "for i in range(2):\n"
        code += "    api.ui.render(dashboard='testing')\n"

        global was_paused
        was_paused = False
        
        global on_render_calls
        on_render_calls = 0

        def on_render(session, dashboard):
            global was_paused            
            if session.is_paused and not was_paused:
                was_paused = True

            global on_render_calls
            
            if on_render_calls == 0:
                session.pause()

            if on_render_calls == 3:
                session.unpause()

            on_render_calls += 1
        
        session = LayerSession(123, code, on_render_callback=on_render)
        session.run()
        assert was_paused

    def test_stop(self):
        code  = "import time\n"        
        code += "while True:\n"
        code += "    api.ui.render(dashboard='testing')\n"
        code += "    time.sleep(0.1)\n"        

        global on_render_calls
        on_render_calls = 0

        def on_render(session, dashboard):
            global on_render_calls            
            if on_render_calls > 10:
                session.stop()

            on_render_calls += 1
        
        session = LayerSession(123, code, on_render_callback=on_render)        

        with pytest.raises(LayerSessionStop):
            session.run()
            
        

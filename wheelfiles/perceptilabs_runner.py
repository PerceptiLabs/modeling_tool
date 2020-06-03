import os
import sys
import tempfile

# TODO: remove sleep. It's there to keep honcho running even after the kernel fails
# hard-coded Procfile
PROCFILE = """\
kernel: python -c "from perceptilabs.mainServer import main; main()" || sleep 10;
rygg: python -m django migrate --settings rygg.settings -v 0 && python -m django runserver --settings rygg.settings --noreload -v 0
frontend: python -m django runserver localhost:8080 --settings static_file_server.settings --noreload -v 0
frontend_launcher: python -c "from static_file_server import website_launcher; website_launcher.launchAndKeepAlive()"
"""

with tempfile.NamedTemporaryFile(mode="w") as tmp:
    tmp.writelines(PROCFILE)
    tmp.flush()
    sys.exit(os.system(f"honcho start --procfile {tmp.name}"))

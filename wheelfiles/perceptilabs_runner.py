import os
import sys
import tempfile

# TODO: remove sleep. It's there to keep honcho running even after the kernel fails
# hard-coded Procfile
PROCFILE = """\
kernel: python -c "from perceptilabs.mainServer import main; main()" || sleep 10;
rygg: python -m django migrate --settings rygg.settings -v 0 && python -m django runserver --settings rygg.settings --noreload -v 0
"""

with tempfile.NamedTemporaryFile(mode="w") as tmp:
    tmp.writelines(PROCFILE)
    tmp.flush()
    sys.exit(os.system(f"honcho start --procfile {tmp.name}"))

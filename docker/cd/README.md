# Tasks around releases, managing AWS machines, etc.

## Clean up machines:
1. In the percetilabs repo, `cd docker/cd`
2. Set up a virtual env. For example, with pyenv and venv:
    ```bash
    pyenv local 3.8.11
    pyenv exec python -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    ```
3. run `./list_ec2_groups` to see any machines that need cleaning, Note their instance IDs, which are formatted like "i-0396e6525fe30d8f4". You only need the hex part.
4. run `ansible-playbook -i inventory -l instance_id_i_<the hex part of the instance ID> deprovision.yaml`
   ... or for example to deprovision all of the "cd" machines: `ansible-playbook -i inventory -l subenv_cd deprovision.yaml`

## Start a stopped AWS machine
In pipelines, run "Start AWS Instance". Parameters:
- If you have the instance ID (e.g. i-0396e6525fe30d8f4), then select intance_id and enter that
- If you have a domain (e.g. "enthusiast-gpu" or "cd") select subdomain and enter that
- Minutes to stay running: whatever you need
- SSH key to add: <none>

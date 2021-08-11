# Tasks around releases, managing AWS machines, etc.


## Make a release
1. Install and test pl-nightly to make sure it's shippable
1. Do the same tests against cd.perceptilabshosting.com
1. In the perceptilabs repo:
    ```bash
    # Stash your stuff
    CUR_BRANCH=$(git branch --show-current)
    export STASH=1; git stash | grep -i saved || { export STASH=0; }

    # switch to master
    git checkout master
    git pull -r
    git log
    # Review the log to pick the git commit to ship. Usually it'll be the one that was built for pl-nightly or for cd, which will be tagged as "docker_xxxx"
    export COMMIT_TO_SHIP=<the commit from the last step>
    git co $COMMIT_TO_SHIP

    # make the release tags
    git checkout -b tmp
    export PL_VERSION=<new version>
    scripts/release_pip tmp $PL_VERSION origin
    git tag $PL_VERSION
    git push origin $PL_VERSION
    git tag enterprise_$PL_VERSION
    git push origin enterprise_$PL_VERSION

    # merge the tags into master
    git checkout master
    git merge tmp
    git push origin HEAD
    git branch -D tmp

    # switch back to your work
    git checkout $CUR_BRANCH
    [ $STASH -ne 1 ] || git stash pop
    ```
1. In pipelines
    1. Start "PerceptiLabs Docker" for $PL_VERSION tag. Note the build number from the URL of the build (a four-digit number currently starting with 7).
    1. Start "PerceptiLabs Pip" for $PL_VERSION tag
        1. Go to a previous release build
        1. Click "Run New"
        1. Select $PL_VERSION as the tag to build
1. When Perceptilabs Pip finishes, install the new perceptilabs from PyPI and do some sanity checks on it
1. When Perceptilabs Docker finishes, run the "Docker Release" pipeline
    - Use tag $PL_VERSION
    - Build ID to deploy: The build number from above
1. When Docker Release finishes, run "Docker CD":
    - Branch: master
    - Release Channel: prod
    - Requested version: $PL_VERSION
    - GPUs: 1
    - CPUs: 4
    - Release environment: releasetest
    - DNS Subdomain: releasetest
    - Minutes to stay running: 120
    - SSH Key Name: <none>
1. When Docker Release finishes, go to releasetest.perceptilabshosting.com and do some sanity checks

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

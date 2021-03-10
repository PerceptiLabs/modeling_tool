Role Name
=========

Install apt packages from a third party repository, complete with public
key checking.

Role Variables
--------------

* `apt_key_url` - where to get the public key of the repo
* `apt_repo` - the url of the repo
* `packages` - what packages to install from the repo
* `package_state` - what to install from the repo. Must be one of: ['build-dep', 'latest', 'present', 'fixed']. Default is 'latest'.

Example Playbook
----------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: servers
      roles:
         - role: third_party_apt
           apt_key_url: https://download.docker.com/linux/ubuntu/gpg
           apt_repo: "deb [arch=amd64] https://download.docker.com/linux/ubuntu {{ ansible_distribution_release }} stable"
           packages:
             - docker-ce
             - docker-ce-cli
             - containerd.io

License
-------

CC-BY-4.0

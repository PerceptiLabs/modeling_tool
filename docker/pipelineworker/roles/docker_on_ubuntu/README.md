Role Name
=========

docker_on_ubuntu

Role Variables
--------------

`apt_key_url` and `apt_repo` are changeable if you're not going to pull from docker.com's sources
`docker_compose_url` is for changing where you pull docker-compose from, including changing the version.

Dependencies
------------

none

Example Playbook
----------------

    - hosts: servers
      roles:
         - role: docker_on_ubuntu

License
-------

CC-BY-4.0

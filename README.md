# API Ubiquity UniFi Controller

A simple API abstraction for interacting with UniFi Controllers.

Example:


    #!python
    import json
    from unifi import controller

    uconn = controller.Controller(hostname, creds['port'])
    uconn.username = 'admin'
    uconn.password = 'password'

    users = uconn.get_users()
    clients = uconn.get_clients()

    print("Clients:")
    print(json.dumps(clients, indent=4, sort_keys=True))

    print("Users:")
    print(json.dumps(users, indent=4, sort_keys=True))


## Changes

1.0.5 - Joshua Schmidlkofer
  - Added loguru tracing support
  - Began work on unificli script

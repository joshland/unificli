# Ubiquity UniFi Cli tools

Simple tool(s) for manipulating the UniFi Controller from a command line.

Focussed on client management.

## Setup

In your controller create a user for the API.  Copy the `creds.json.example`
add your own host and credentials. Reference the host in `creds.json` to target your commands.

Currently, this requires valid SSL certificates.  For local controllers, see
[GlennR's Page](https://GlennR.nl) and get his [Unifi Update](https://get.glennr.nl/unifi/update/unifi-update.sh)
script.

### Listing Clients and Users

    $ unicli list ufu.ashbyte.com
    Hostname                  Mac                OUI       IP           Status
    ------------------------  -----------------  --------  -----------  ---------
    n/a                       58:cb:ff:f6:f1:af  Google    10.1.1.191
    n/a                       40:4e:ff:f3:f3:4f  Htc       10.1.1.99
    android-bf5e132e7e6ab1e1  c8:f3:ff:fe:f8:7f  LgElectr  n/a          [BLOCKED]
    android-faa4c5ad47bfe582  c8:f3:ff:fe:ff:f3  LgElectr  n/a          [BLOCKED]

### block named clients

    $ unicli block -y ufu.ashbyte.com bitumen compose
    Hostname    Mac                OUI       IP    Status
    ----------  -----------------  --------  ----  ---------
    compose     0c:8b:fd:9a:7c:25  IntelCor  n/a   [BLOCKED]
    bitumen     0c:8b:fd:99:a9:e9  IntelCor  n/a   [BLOCKED]


### rerun blocking operation

    $ unicli block ufu.ashbyte.com -y bitumen compose
    Hostname    Mac                OUI       IP    Status
    ----------  -----------------  --------  ----  ---------
    compose     0c:8b:fd:9a:7c:25  IntelCor  n/a   [BLOCKED]
    bitumen     0c:8b:fd:99:a9:e9  IntelCor  n/a   [BLOCKED]

    Clients already blocked.


### Unblock named clients

    $ unicli unblock ufu.ashbyte.com -y android
    Hostname                  Mac                OUI       IP           Status
    ------------------------  -----------------  --------  -----------  ---------
    n/a                       58:cb:ff:f6:f1:af  Google    10.1.1.191
    n/a                       40:4e:ff:f3:f3:4f  Htc       10.1.1.99
    android-bf5e132e7e6ab1e1  c8:f3:ff:fe:f8:7f  LgElectr  n/a          [BLOCKED]
    android-faa4c5ad47bfe582  c8:f3:ff:fe:ff:f3  LgElectr  n/a          [BLOCKED]


## Changes

1.0.0 - Joshua Schmidlkofer
  - initial

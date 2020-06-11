#!/usr/bin/env python3

import os, sys
import pprint
import json
import copy

import click
from loguru import logger
from unifi import controller

def fmt_clients(value):
    ''' format json list into a python list by client MAC '''
    retval = {}
    for client in value:
        retval[client['mac']] = client
        continue
    return retval


def loadcreds(credfile='creds.json'):
    retval = {}
    default_creds = {
        'user': 'xxxxxxxxxx',
        'password': 'yyyyyyyyyyyyyyyyy',
        'port': 8443,
    }
    logger.trace(f'Load Credentials {credfile}')
    for k, v in json.load(credfile).items():
        retval[k] = copy.copy(default_creds)
        retval[k].update(v)
        continue        
    return retval

def connect(hostname, creds):
    ''' return a connection to the host '''
    logger.debug(f'Open: {hostname}, host: {hostname}')
    unifi = controller.Controller(hostname, creds['port'])
    unifi.username = creds['user']
    unifi.password = creds['password']
    retval = unifi.connect()
    logger.trace(f'Connection Results: {retval}')
    return unifi

def logit(trace, debug):
    ''' initialize logging '''
    logger.remove()
    logger.add(sys.stderr, level='ERROR')

    if debug:
        logger.remove()
        logger.add(sys.stderr, level='DEBUG')
        pass

    if trace:
        logger.remove()        
        logger.add(sys.stderr, level='TRACE')
        pass

    pass

def integrate_clients_users(clients, users):
    ''' merge the clients and users into a single dict.'''
    client = {
        'hostname': 'n/a',
        'oui': 'n/a',
        'ip': 'n/a',
        'blocked': False,
    }
    retval = {}
    for c in clients:
        key = c['mac']
        retval[key] = copy.copy(client)
        retval[key].update(c)
        continue
    for u in users:
        key = u['mac']
        try:
            retval[key].update(u)
        except KeyError:
            retval[key] = copy.copy(client)
            retval[key].update(u)
        continue
    return retval

def client_check(search_args, record):
    ''' examine record field for items in search args '''
    if not search_args:
        return True

    fields = ['mac', 'hostname', 'oui', 'ip']
    for args in search_args:
        for f in fields:
            if str(record[f]).find(args) > -1:
                logger.trace(f"{record['hostname']} found {f} {args}")
                return True
            continue
        continue
    return False


@click.group()
@click.option('--trace', '-t', default=False, required=False, is_flag=True)
@click.option('--debug', '-d', default=False, required=False, is_flag=True)
def main(trace, debug):
    logit(trace, debug)
    pass

@main.command()
@click.option('--creds', '-c', default='creds.json', type=click.File('r'), required=False)
@click.option('--all', '-a', default=False, required=False, is_flag=True)
@click.argument('host', nargs=1)
@click.argument('client', nargs=-1, required=False)
def list(creds, all, host, client):
    from tabulate import tabulate

    creds = loadcreds(creds)
    local = creds[host]
    unifi = connect(host, local)
    uclients = unifi.get_clients()
    uusers = unifi.get_users()
    nodes = integrate_clients_users(uclients, uusers)

    results = []
    for k, v in nodes.items():
        if not client_check(client, v):
            logger.trace(f"skip non-matched {k}")
            continue

        if v['blocked']:
            logger.warning(f"{v['hostname']} [{k}]: ({v['oui']}) {v['ip']}  [BLOCKED]")
            results.append(
                (v['hostname'],k,v['oui'],v['ip'], '[BLOCKED]')
            )
        else:
            logger.info(f"{v['hostname']} [{k}]: ({v['oui']}) {v['ip']}  ")
            results.append(
                (v['hostname'],k,v['oui'],v['ip'])
            )
            pass
        continue
    print(tabulate(results, headers=['Hostname', 'Mac', 'OUI', 'IP', 'Status']))
    return 0

@main.command()
@click.option('--creds', '-c', default='creds.json', type=click.File('r'), required=False)
@click.option('--dry-run', '-d', default=False, required=False, is_flag=True)
@click.option('--yes', '-y', default=False, required=False, is_flag=True)
@click.argument('host', nargs=1)
@click.argument('client', nargs=-1, required=False)
def block(creds, dry_run, yes, host, client):
    from tabulate import tabulate
    from getkey import getkey, keys

    creds = loadcreds(creds)
    local = creds[host]
    unifi = connect(host, local)
    uclients = unifi.get_clients()
    uusers = unifi.get_users()
    nodes = integrate_clients_users(uclients, uusers)

    results = []
    blocked = []
    pending = []
    for k, v in nodes.items():
        if not client_check(client, v):
            logger.trace(f"skip non-matched {k}")
            continue

        if v['blocked']:
            logger.warning(f"{v['hostname']} [{k}]: ({v['oui']}) {v['ip']}  [BLOCKED]")
            results.append(
                (v['hostname'],k,v['oui'],v['ip'], '[BLOCKED]')
            )
            blocked.append(k)
        else:
            logger.info(f"{v['hostname']} [{k}]: ({v['oui']}) {v['ip']}  ")
            results.append(
                (v['hostname'],k,v['oui'],v['ip'])
            )
            pending.append(k)
            pass
        continue
    while 1:
        print(tabulate(results, headers=['Hostname', 'Mac', 'OUI', 'IP', 'Status']))
        print()
        if not len(pending):
            logger.trace("No pending blocks found.")
            if len(blocked):
                print('Clients already blocked.')
                break
            else:
                print('No clients found')
                break
            print("")
        if not yes:
            key = input("Block Clients? (y/N) ")
            print ()
        else:
            key = "y"
            pass

        if key in ('Y', 'y'):
            if dry_run:
                logger.trace(f"{key} receive, Dry-run.")
                print("Draino")
                "report block"
                break
            else:
                logger.trace(f"{key} receive, They're dead.")
                print("Draino")
                "do block"
                break
        elif key in ('N', 'n', '\n'):
            logger.trace(f"{key} receive, exiting.")
            print("Fine. Be that way.")
            break
        continue
       
    return 0

if __name__ == "__main__":
    __name__ = 'unificli'
    main(obj={})

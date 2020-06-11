#!/usr/bin/env python3

import os, sys
import pprint
import json
import copy
import atexit

import click
from loguru import logger
from .functions import ClientManagement

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
    # this api call seems not to work.
    #atexit.register(unifi.disconnect)
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

def blocking_search(searches, nodes):
    ''' search nodes for list for blocking or unblocking '''
    blocked = []
    unblocked = []
    for k, v in nodes.items():
        if not client_check(searches, v):
            logger.trace(f"skip non-matched {k}")
            continue

        if v['blocked']:
            logger.trace(f"{v['hostname']} [{k}]: ({v['oui']}) {v['ip']}  [BLOCKED]")
            blocked.append(k)
        else:
            logger.trace(f"{v['hostname']} [{k}]: ({v['oui']}) {v['ip']}  [OPEN]")
            unblocked.append(k)
            pass
        continue

    return blocked, unblocked

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
@click.argument('searches', nargs=-1, required=False)
def list(creds, all, host, searches):
    from tabulate import tabulate

    creds = loadcreds(creds)
    local = creds[host]
    unifi = ClientManagement(host, **local)
    unifi.filters = searches
    nodes = unifi.get_clients_and_users()

    results = []
    for k, v in nodes.items():
        if not client_check(searches, v):
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
@click.argument('searches', nargs=-1, required=False)
def block(creds, dry_run, yes, host, searches):
    from tabulate import tabulate
    from getkey import getkey, keys

    creds = loadcreds(creds)
    local = creds[host]
    local['filters'] = searches
    unifi = ClientManagement(host, **local)
    nodes = unifi.get_clients_and_users()

    results = []
    blocked = []
    pending = []

    blocked, pending = blocking_search(searches, nodes)

    for mac in blocked:
        v = nodes[mac]
        results.append((v['hostname'],mac,v['oui'],v['ip'], '[BLOCKED]'))
        continue

    for mac in pending:
        v = nodes[mac]
        results.append((v['hostname'],mac,v['oui'],v['ip'], '*PENDING*'))
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
                logger.trace(f"{key} - execute dry-run")
                for mac in pending:
                    logger.info(f"unifi.block_sta({mac})")
                    continue
                break
            else:
                logger.trace(f"{key} - execute blocks.")
                for mac in pending:
                    unifi.block_sta(mac)
                    print(f"{nodes[mac]['hostname']} *SUCCESS* ")
                    continue
                break
        elif key in ('N', 'n', '\n'):
            logger.trace(f"{key} receive, exiting.")
            print("quitting, no action taken.")
            break
        continue
    print()
    return 0
@main.command()
@click.option('--creds', '-c', default='creds.json', type=click.File('r'), required=False)
@click.option('--dry-run', '-d', default=False, required=False, is_flag=True)
@click.option('--yes', '-y', default=False, required=False, is_flag=True)
@click.argument('host', nargs=1)
@click.argument('searches', nargs=-1, required=False)
def unblock(creds, dry_run, yes, host, searches):
    from tabulate import tabulate
    from getkey import getkey, keys

    creds = loadcreds(creds)
    local = creds[host]
    local['filters'] = searches
    unifi = ClientManagement(host, **local)
    nodes = unifi.get_clients_and_users()

    results = []
    blocked = []
    pending = []

    pending, unblocked = blocking_search(searches, nodes)

    for mac in pending:
        v = nodes[mac]
        results.append((v['hostname'],mac,v['oui'],v['ip'], '*PENDING*'))
        continue

    for mac in unblocked:
        v = nodes[mac]
        results.append((v['hostname'],mac,v['oui'],v['ip'], '[OPEN]'))
        continue

    while 1:
        print(tabulate(results, headers=['Hostname', 'Mac', 'OUI', 'IP', 'Status']))
        print()
        if not len(pending):
            logger.trace("No pending unblocks found.")
            if len(unblocked):
                print('Clients are not blocked.')
                break
            else:
                print('No clients found')
                break
            print("")
        if not yes:
            key = input("Release Clients? (y/N) ")
            print ()
        else:
            key = "y"
            pass

        if key in ('Y', 'y'):
            if dry_run:
                logger.trace(f"{key} - execute dry-run")
                for mac in pending:
                    logger.info(f"unifi.unblock_sta({mac})")
                    logger.info(f"unifi.reconnect_sta({mac})")
                    continue
                break
            else:
                logger.trace(f"{key} - execute unblocks.")
                for mac in pending:
                    unifi.unblock_sta(mac)
                    print(f"{nodes[mac]['hostname']} *SUCCESS* ")
                    continue
                break
        elif key in ('N', 'n', '\n'):
            logger.trace(f"{key} receive, exiting.")
            print("quitting, no action taken.")
            break
        continue
    print()
    return 0

if __name__ == "__main__":
    __name__ = 'unificli'
    main(obj={})

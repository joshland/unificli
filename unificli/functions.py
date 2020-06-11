#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# client fuction manipulation.
#

from __future__ import print_function

from loguru import logger
from unifi import controller

import copy

class ClientManagement(controller.Controller):
    default_client = {
        'hostname': 'n/a',
        'oui': 'n/a',
        'ip': 'n/a',
        'blocked': False,
    }
    fields = ['mac', 'hostname', 'oui', 'ip']
    def __init__(self, host, port, user, password, filters = None, fields = None):
        '''
        Client Management Shortcuts
        host: Unifi hostname
        port: Unifi Port
        username: unifi username
        password: Unifi Password
        filters:  tuple of strings use to filter node list
        field:    fields to search when for filters.
        '''
        super().__init__(host, port)
        self.username = user
        self.password = password
        self.connect()
        if fields:
            self.fields = fields
            pass
        self.filters = filters
        self.users = {}
        self.clients = {}
        self.nodes = {}

    def flush(self):
        ''' flush the caches '''
        self.users = {}
        self.clients = {}
        self.nodes = {}
        
    def get_clients(self):
        ''' return the clients '''
        if len(self.clients):
            return self.clients
        clients = super().get_clients()
        retval = {}
        for c in clients:
            normal =  copy.copy(self.default_client)
            normal.update(c)
            if self.filters and not self.node_search(normal):
                continue
            key = normal['mac']
            retval[key] = normal
            continue
        return retval

    def get_users(self):
        ''' return the users '''
        if len(self.users):
            return self.users
        users = super().get_users()
        retval = {}
        for u in users:
            normal =  copy.copy(self.default_client)
            normal.update(u)
            if self.filters and not self.node_search(normal):
                continue
            key = normal['mac']
            retval[key] = normal
            continue
        return retval

    def get_clients_and_users(self):
        ''' return merged clients and users '''
        if len(self.nodes):
            return self.nodes
        retval = self.get_clients()
        for k, v in self.get_users().items():
            try:
                retval[k].update(v)
            except:
                retval[k] = copy.copy(self.default_client)
                retval[k].update(v)
                pass
            continue
        return retval

    def node_search(self, record):
        ''' examine record field for items in search args '''
        if not self.filters:
            return True

        for arg in self.filters:
            for f in self.fields:
                if str(record[f]).find(arg) > -1:
                    try:
                        logger.trace(f"{record['hostname']} found {f} {arg}")
                    except KeyError:
                        print(f'{record}')
                    return True
                continue
            continue
        return False

    def block(self, mac):
        ''' block and address '''
        self.flush()
        super().block_sta(mac)


    def unblock(self, mac):
        ''' block and address '''
        self.flush()
        super().unblock_sta(mac)


        
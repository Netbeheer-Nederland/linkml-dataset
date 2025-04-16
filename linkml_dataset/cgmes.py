# -*- coding: utf-8 -*-

from datetime import date
from uuid import uuid4
from json import dumps, load
from collections import namedtuple
from pprint import pprint

import logging
log = logging.getLogger(__name__)


class CGMES:
    def __init__(self, jsonfile):
        self._json = load(jsonfile)
        self._nodes = {}
        self._cnodes = {}
        for obj in self._json['@graph']:
            # Populate lookup table: mrid -> obj
            self._nodes[obj['@id']] = obj
            # Group cim:Terminal by cim:ConnectivityNode
            match obj['@type']:
                case 'cim:Terminal':
                    if 'cim:Terminal.ConnectivityNode' not in obj:
                        continue
                    cnode = obj['cim:Terminal.ConnectivityNode']['@id']
                    if cnode not in self._cnodes:
                        self._cnodes[cnode] = []
                    self._cnodes[cnode].append(obj)

    def resolve(self, terminal_id):
        """ """
        if terminal_id not in self._nodes:
            log.info(f'Terminal ID "{terminal_id}" not found')
            return []
        objects = []
        terminal = self._nodes[terminal_id]
        if 'cim:Terminal.ConnectivityNode' not in terminal:
            log.debug(f'Terminal "{terminal_id}" has no ConnectivityNode')
            return[]
        for t in self._cnodes[terminal['cim:Terminal.ConnectivityNode']['@id']]:
            if 'cim:Terminal.ConductingEquipment' not in t:
                log.info(f'Terminal "{terminal_id}" has no ConductingEquipment')
                continue
            c_eq = self._nodes[t['cim:Terminal.ConductingEquipment']['@id']]['@type']
            objects.append(c_eq)
        return objects

    def edges(self):
        Triple = namedtuple('Triple', ['subject', 'predicate', 'object',
                                       'terminal'])
        edges = set()
        for obj in self._json['@graph']:
            subject = obj['@type']
            if subject == 'cim:Terminal':
                # Terminals are handled seperately
                continue
            for k, v in obj.items():
                if isinstance(v, dict):
                    # Value is a dict, contains a reference by mrid
                    if '@id' not in v:
                        continue
                    log.debug(f'Processing node {k} with range {v["@id"]}')
                    if v['@id'] not in self._nodes:
                        # Not a valid reference to a node
                        log.debug(f'Node ID "{v["@id"]}" not found')
                        continue
                    predicate = k
                    # Get referring node
                    node = self._nodes[v['@id']]
                    match node['@type']:
                        case 'cim:Terminal':
                            for o in self.resolve(node['@id']):
                                edges.add(Triple(subject, predicate, o, True))
                        case _:
                            edges.add(Triple(subject, predicate, node['@type'],
                                             False))
                    continue
        return edges

    def __str__(self):
        return ''

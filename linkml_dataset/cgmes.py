# -*- coding: utf-8 -*-

from datetime import date
from uuid import uuid4
from json import dumps, load
from collections import namedtuple
from pprint import pprint
from rdflib import Graph, RDF

import logging
log = logging.getLogger(__name__)


class CGMES:
    def __init__(self, jsonfile):
        self.G = Graph()
        self.G.parse(file=jsonfile, format='json-ld')

    def edges(self):
        Triple = namedtuple('Triple', ['subject', 'predicate', 'object'])
        edges = set()
        typed_resources = set(s for s, p, o in self.G if p == RDF.type)
        for subj, pred, obj in self.G:
            if not subj in typed_resources or obj not in typed_resources:
                continue
            if self._is_filtered(subj) or self._is_filtered(obj):
                continue
            subj = str(self._get_rdf_type(subj))
            obj = str(self._get_rdf_type(obj))
            pred = str(self._get_rdf_type(pred))
            edges.add(Triple(subj, pred, obj))
        return edges

    def _get_rdf_type(self, resource):
        rdf_type = next(self.G.objects(resource, RDF.type), None)
        return rdf_type if rdf_type else resource

    def _is_filtered(self, resource):
        resource_type = self._get_rdf_type(resource)
        filter_types = {'Terminal', 'ConnectivityNode', 'IdentifiedObject',
                        'Name', 'NameType'}
        return resource_type and str(resource_type).split('#')[-1] in filter_types

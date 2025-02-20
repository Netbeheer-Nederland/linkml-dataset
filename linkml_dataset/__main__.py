# -*- coding: utf-8 -*-

from click import option, group, argument, File, echo, ClickException
from sys import stdin, stdout
from yaml import safe_load, dump, SafeDumper
from pprint import pprint
from uuid import uuid4
from datetime import date
from csv import DictReader

from .models import dp_netbewust_laden as nbl
# from .models.dp_netbewust_laden import *

import logging
log = logging.getLogger(__name__)

LOG_FORMAT = '[%(asctime)s] [%(levelname)s] %(message)s'


class IndentDumper(SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentDumper, self).increase_indent(flow, False)


def catch_exception(func=None, *, handle):
    if not func:
        return partial(catch_exception, handle=handle)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except handle as e:
            log.error(e)
            # raise ClickException(e)
    return wrapper


@group()
@option('--log', type=File(mode='a'), help='Filename for log file')
@option('--debug', is_flag=True, default=False, help='Enable debug mode')
def cli(log, debug):
    """ """
    # Setup logging
    if log:
        handler = logging.FileHandler(log.name)
    else:
        handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    # Add handler to the root log
    logging.root.addHandler(handler)
    # Set log level
    level = logging.DEBUG if debug else logging.INFO
    logging.root.setLevel(level)


@cli.command()
@option('--out', '-o', type=File('wt'), default=stdout,
        help='Output file.  Omit to print schema to stdout')
@option('--region', '-r', required=True, help='Region of DSO')
@option('--count', '-c', required=False, default=None, type=int,
        help='Number of rows to process')
@argument('csvfile', type=File('rt'), default=stdin)
def netbewust_laden(csvfile, out, region, count):
    """Process NBL Forecast"""
    # Mapping between CSV/YAML
    substations = {}
    mkt_c_nodes = {}
    t_nodes = {}
    market_participants = {}
    # Output YAML
    data = {'identifier': str(uuid4()),
            'conforms_to': 'http://data.netbeheernederland.nl/dp-nbl-forecast/version/1.0.0',
            'contact_point': 'ritger.teunissen@alliander.com',
            'release_date': date.today().strftime('%Y-%m-%d'),
            'version': '1.0.0',
            'ac_line_segments': [],
            'analogs': [],
            'coordinate_systems': [],
            'energy_consumers': [],
            'geographical_regions': [],
            'market_participants': [],
            'market_roles': [],
            'mkt_connectivity_nodes': [],
            'lines': [],
            'power_transformers': [],
            'registered_loads': [],
            'sub_geographical_regions': [],
            'substations': [],
            'terminals': [],
            'topological_nodes': [],
            'usage_points': []}
    forecast = nbl.ForecastDataSet(**data)
    # GeographicalRegion
    geo_region = nbl.GeographicalRegion(description='Netherlands',
                                        m_rid=str(uuid4()),
                                        regions=[str(uuid4())])
    forecast.geographical_regions.append(geo_region)
    # GeographicalRegion -> SubGeographicalRegion
    sub_geo_region = nbl.SubGeographicalRegion(description=f'{region}',
                                               m_rid=geo_region.regions[0],
                                               substations=[],
                                               lines=[])
    forecast.sub_geographical_regions.append(sub_geo_region)
    # Market Role
    forecast.market_roles.append(nbl.MarketRole(m_rid=str(uuid4()),
                                                type='Charge Point Operator'))
    # Process each row in the CSV
    reader = DictReader(csvfile)
    for c, row in enumerate(reader, start=1):
        if count is not None and c > count:
            break
        log.debug(f'Processing charge point: "{row["100_MarketEvaluationPoint.EAN"]}"')
        _nbl_charge_points(forecast,
                           row['1_Substation.Name'],
                           row['2_ConductingEquipment.Name'],
                           row['110_MarketParticipant.Name'],
                           row['120_StreetAddress.Postalcode'],
                           row['122_Streetdetail.Number'],
                           row['123_Towndetail.Name'],
                           row['125_Towndetail.stateOrProvince'],
                           row['100_MarketEvaluationPoint.EAN'])
    # Output dataset
    echo(dump(forecast.dict(exclude_none=True), Dumper=IndentDumper,
              sort_keys=False, allow_unicode=True), file=out)


def _nbl_assets(forecast):
    """Process assets."""
    return


def _nbl_charge_points(forecast, s_name, ce_name, mp_name, postal_code, number,
                      town_name, province, ean):
    """Process a single charge point."""
    def instance_exists(name, container):
        return next((i for i in container if i.description == name), None)

    sub_geo_region = forecast.sub_geographical_regions[0]
    # SubGeographicalRegion -> Substation
    substation = instance_exists(s_name, forecast.substations)
    if substation is None:
        log.info(f'Adding Substation "{s_name}"')
        substation = nbl.Substation(m_rid=str(uuid4()), description=s_name,
                                    equipments=[])
        sub_geo_region.substations.append(substation.m_rid)
        forecast.substations.append(substation)
    # Substation -> PowerTransformer
    pt = instance_exists(ce_name, forecast.power_transformers)
    if pt is None:
        log.info(f'Adding PowerTransformer "{ce_name}" to substation "{s_name}"')
        pte = nbl.PowerTransformerEnd(description=ce_name, m_rid=str(uuid4()),
                                      terminal=str(uuid4()))
        pt = nbl.PowerTransformer(description=ce_name, m_rid=str(uuid4()),
                                  power_transformer_end=[pte])
        substation.equipments.append(pt.m_rid)
        forecast.power_transformers.append(pt)
        # PowerTransformer -> Terminal
        terminal = nbl.Terminal(m_rid=pte.terminal,
                                topological_node=str(uuid4()))
        forecast.terminals.append(terminal)
        # Terminal -> TopologicalNode
        topological_node = nbl.TopologicalNode(description=ce_name,
                                               m_rid=terminal.topological_node,
                                               terminal=[])
        forecast.topological_nodes.append(topological_node)
    # TopologicalNode
    topological_node = instance_exists(ce_name, forecast.topological_nodes)
    if topological_node is None:
        raise ValueError(f'No TopologicalNode found for "{ce_name}"')
    # TopologicalNode -> Terminal
    terminal = nbl.Terminal(description=ce_name, m_rid=str(uuid4()),
                            conducting_equipment=str(uuid4()))
    topological_node.terminal.append(terminal.m_rid)
    forecast.terminals.append(terminal)
    # Terminal -> EnergyConsumer
    street_address = nbl.StreetAddress(postal_code=postal_code,
                                       street_detail=nbl.StreetDetail(number=number),
                                       town_detail=nbl.TownDetail(name=town_name,
                                                                  state_or_province=province))
    location = nbl.Location(m_rid=str(uuid4()), main_address=street_address)
    energy_consumer = nbl.EnergyConsumer(m_rid=terminal.conducting_equipment,
                                         location=location,
                                         usage_points=[str(uuid4())])
    forecast.energy_consumers.append(energy_consumer)
    # EnergyConsumer -> UsagePoint
    usage_point = nbl.UsagePoint(m_rid=energy_consumer.usage_points[0],
                                 european_article_number_ean=ean)
    forecast.usage_points.append(usage_point)
    # MktConnectivityNode
    mkt_c_node = instance_exists(mp_name, forecast.mkt_connectivity_nodes)
    if mkt_c_node is None:
        # TopologicalNode -> Terminal
        terminal = nbl.Terminal(description=ce_name, m_rid=str(uuid4()),
                                connectivity_node=str(uuid4()))
        topological_node.terminal.append(terminal.m_rid)
        forecast.terminals.append(terminal)
        # Terminal -> MktConnectivityNode
        mkt_c_node = nbl.MktConnectivityNode(description=mp_name,
                                             m_rid=terminal.connectivity_node,
                                             registered_resource=[])
        forecast.mkt_connectivity_nodes.append(mkt_c_node)
    # MarketParticipant
    mp = instance_exists(mp_name, forecast.market_participants)
    if mp is None:
        mp = nbl.MarketParticipant(description=mp_name, m_rid=str(uuid4()),
                                   market_role=[forecast.market_roles[0].m_rid])
        forecast.market_participants.append(mp)
    # MktConnectivityNode -> RegisteredLoad
    registered_load = nbl.RegisteredLoad(m_rid=str(uuid4()),
                                         market_participant=mp.m_rid)
    mkt_c_node.registered_resource.append(registered_load.m_rid)
    forecast.registered_loads.append(registered_load)

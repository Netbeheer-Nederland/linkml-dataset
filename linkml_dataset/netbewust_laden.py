# -*- coding: utf-8 -*-

from datetime import date
from uuid import uuid4
from yaml import safe_load, dump, SafeDumper

from .models import dp_netbewust_laden as nbl

import logging
log = logging.getLogger(__name__)


class IndentDumper(SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentDumper, self).increase_indent(flow, False)


class NetbewustLaden:
    def __init__(self, region):
        # Set up DataSet
        data = {'identifier': str(uuid4()),
                'conforms_to': 'http://data.netbeheernederland.nl/dp-nbl-forecast',
                'contact_point': 'ritger.teunissen@alliander.com',
                'release_date': date.today().strftime('%Y-%m-%d'),
                'version': '1.0.0',
                'ac_line_segments': [],
                'active_power_limits': [],
                'analogs': [],
                'coordinate_systems': [],
                'energy_consumers': [],
                'geographical_regions': [],
                'market_participants': [],
                'market_roles': [],
                'mkt_connectivity_nodes': [],
                'lines': [],
                'operational_limit_sets': [],
                'power_transformers': [],
                'registered_loads': [],
                'sub_geographical_regions': [],
                'substations': [],
                'terminals': [],
                'topological_nodes': [],
                'usage_points': []}
        self._fc = nbl.ForecastDataSet(**data)
        # GeographicalRegion
        geo_region = nbl.GeographicalRegion(description='Netherlands',
                                            m_rid=str(uuid4()),
                                            regions=[str(uuid4())])
        self._fc.geographical_regions.append(geo_region)
        # GeographicalRegion -> SubGeographicalRegion
        sub_geo_region = nbl.SubGeographicalRegion(description=f'{region}',
                                                   m_rid=geo_region.regions[0],
                                                   substations=[],
                                                   lines=[])
        self._fc.sub_geographical_regions.append(sub_geo_region)

    def __str__(self):
        """Dump ForecastDataSet to YAML."""
        return dump(self._fc.dict(exclude_none=True), Dumper=IndentDumper,
                    sort_keys=False, allow_unicode=True)

    def charge_points(self, s_name, ce_name, ean, mp_name, mp_role,
                      postal_code, number, town_name, town_section, province,
                      crs_urn, x_pos, y_pos):
        """Process a single charge point."""
        log.debug(f'Processing charge point: "{ean}"')
        # SubGeographicalRegion -> Substation
        substation = self._substation(self._fc.sub_geographical_regions[0],
                                      s_name)
        # Substation -> PowerTransformer
        pt = self._power_transformer(substation, ce_name)
        # TopologicalNode
        topological_node = self._instance_exists(ce_name,
                                                 self._fc.topological_nodes)
        if topological_node is None:
            raise ValueError(f'No TopologicalNode found for "{ce_name}"')
        # TopologicalNode -> UsagePoint
        usage_point = self._usage_point(topological_node, ean, postal_code,
                                        number, town_name, town_section,
                                        province, crs_urn, x_pos, y_pos)
        # TopologicalNode -> RegisteredLoad
        self._registered_load(topological_node, ce_name, mp_name, mp_role)

    def assets(self, s_name, ce_name, psr_type, postal_code, street_name,
               number, code, town_name, town_section, province, crs_urn, x_pos,
               y_pos, load, ol_01, ol_02):
        """Process assets."""
        # SubGeographicalRegion -> Substation
        substation = self._substation(self._fc.sub_geographical_regions[0],
                                      s_name)
        # Substation -> Location
        if substation.location is None:
            substation.location = self._location(postal_code, number,
                                                 town_name, town_section,
                                                 province, crs_urn, x_pos,
                                                 y_pos)
        # Substation -> PowerTransformer
        pt = self._power_transformer(substation, ce_name)
        # PowerTransformer -> PowerTransformerEnd
        terminal = self._power_transformer_end(pt)
        terminal.measurements = []
        # PowerTransformerEnd -> Analog
        self._analog(terminal, load)
        # PowerTransformerEnd -> OperationalLimitSet
        ols = nbl.OperationalLimitSet(m_rid=str(uuid4()),
                                      operational_limit_value=[])
        terminal.operational_limit_set = [ols.m_rid]
        self._fc.operational_limit_sets.append(ols)
        # OperationalLimitSet -> ActivePowerLimit (Capacity)
        apl = self._active_power_limit(ol_01[0], ol_01[3], ol_01[2], ol_01[1])
        ols.operational_limit_value.append(apl.m_rid)
        self._fc.active_power_limits.append(apl)
        # OperationalLimitSet -> ActivePowerLimit (NBL Limit)
        apl = self._active_power_limit(ol_02[0], ol_02[3], ol_02[2], ol_02[1])
        ols.operational_limit_value.append(apl.m_rid)
        self._fc.active_power_limits.append(apl)

    def _instance_exists(self, name, container):
        return next((i for i in container if i.description == name), None)

    def _active_power_limit(self, name, value, unit, multiplier):
        """cim:ActivePowerLimit"""
        ap = nbl.ActivePower(multiplier=multiplier, unit=unit, value=value)
        olt = nbl.OperationalLimitType(m_rid=str(uuid4()), description=name)
        return(nbl.ActivePowerLimit(m_rid=str(uuid4()), value=ap,
                                    operational_limit_type=olt))

    def _analog(self, terminal, load):
        """cim:Analog"""
        analog_value = nbl.AnalogValue(m_rid=str(uuid4()), value=load[4],
                                       time_stamp=load[5])
        analog = nbl.Analog(description=load[0], m_rid=str(uuid4()),
                            positive_flow_in=True, unit_multiplier=load[2],
                            unit_symbol=load[3], measurement_type=load[1],
                            analog_values=[analog_value])
        terminal.measurements.append(analog.m_rid)
        self._fc.analogs.append(analog)
        return analog

    def _substation(self, sub_geo_region, s_name):
        """cim:Substation"""
        substation = self._instance_exists(s_name, self._fc.substations)
        if substation is None:
            log.info(f'Adding Substation "{s_name}"')
            substation = nbl.Substation(m_rid=str(uuid4()), description=s_name,
                                        equipments=[])
            sub_geo_region.substations.append(substation.m_rid)
            self._fc.substations.append(substation)
        return substation

    def _power_transformer_end(self, power_transformer):
        """cim:PowerTransformerEnd. Returns the terminal."""
        pte = nbl.PowerTransformerEnd(m_rid=str(uuid4()),
                                      description=power_transformer.description,
                                      terminal=str(uuid4()))
        power_transformer.power_transformer_end.append(pte)
        # PowerTransformerEnd -> Terminal
        terminal = nbl.Terminal(m_rid=pte.terminal)
        self._fc.terminals.append(terminal)
        return terminal

    def _location(self, postal_code, number, town_name, town_section, province,
                  crs_urn, x_pos, y_pos):
        """cim:Location"""
        street_detail = nbl.StreetDetail(number=number, code=town_section)
        town_detail = nbl.TownDetail(name=town_name,
                                     state_or_province=province)
        street_address = nbl.StreetAddress(postal_code=postal_code,
                                           street_detail=street_detail,
                                           town_detail=town_detail)
        coordinate_system = self._instance_exists(crs_urn,
                                                  self._fc.coordinate_systems)
        if coordinate_system is None:
            coordinate_system = nbl.CoordinateSystem(description=crs_urn,
                                                     m_rid=str(uuid4()),
                                                     crs_urn=crs_urn)
            self._fc.coordinate_systems.append(coordinate_system)
        position_point = nbl.PositionPoint(x_position=x_pos, y_position=y_pos)
        location = nbl.Location(m_rid=str(uuid4()), main_address=street_address,
                                coordinate_system=coordinate_system.m_rid,
                                position_points=[position_point])
        return location

    def _power_transformer(self, substation, ce_name):
        """cim:PowerTransformer"""
        pt = self._instance_exists(ce_name, self._fc.power_transformers)
        if pt is None:
            log.info(f'Adding PowerTransformer "{ce_name}" to Substation "{substation.description}"')
            # PowerTransformer
            pt = nbl.PowerTransformer(description=ce_name, m_rid=str(uuid4()),
                                      power_transformer_end=[])
            substation.equipments.append(pt.m_rid)
            self._fc.power_transformers.append(pt)
            # PowerTransformerEnd
            terminal = self._power_transformer_end(pt)
            # Terminal -> TopologicalNode
            topological_node = nbl.TopologicalNode(description=ce_name,
                                                   m_rid=str(uuid4()),
                                                   terminal=[])
            terminal.topological_node = topological_node.m_rid
            self._fc.topological_nodes.append(topological_node)
        return pt

    def _usage_point(self, topological_node, ean, postal_code, number,
                     town_name, town_section, province, crs_urn, x_pos, y_pos):
        """cim:UsagePoint"""
        # TopologicalNode -> Terminal
        terminal = nbl.Terminal(description=topological_node.description,
                                m_rid=str(uuid4()),
                                conducting_equipment=str(uuid4()))
        topological_node.terminal.append(terminal.m_rid)
        self._fc.terminals.append(terminal)
        # Terminal -> EnergyConsumer
        location = self._location(postal_code, number, town_name,
                                  town_section, province, crs_urn, x_pos,
                                  y_pos)
        energy_consumer = nbl.EnergyConsumer(location=location,
                                             usage_points=[str(uuid4())],
                                             m_rid=terminal.conducting_equipment)
        self._fc.energy_consumers.append(energy_consumer)
        # EnergyConsumer -> UsagePoint
        usage_point = nbl.UsagePoint(m_rid=energy_consumer.usage_points[0],
                                     european_article_number_ean=ean)
        self._fc.usage_points.append(usage_point)
        return usage_point

    def _mkt_connectivity_node(self, topological_node, ce_mp_name):
        """cim:MktConnectivityNode"""
        mkt_c_node = self._instance_exists(ce_mp_name,
                                           self._fc.mkt_connectivity_nodes)
        if mkt_c_node is None:
            # TopologicalNode -> Terminal
            terminal = nbl.Terminal(description=ce_mp_name, m_rid=str(uuid4()),
                                    connectivity_node=str(uuid4()))
            topological_node.terminal.append(terminal.m_rid)
            self._fc.terminals.append(terminal)
            # Terminal -> MktConnectivityNode
            mkt_c_node = nbl.MktConnectivityNode(description=ce_mp_name,
                                                 m_rid=terminal.connectivity_node,
                                                 registered_resource=[])
            self._fc.mkt_connectivity_nodes.append(mkt_c_node)
        return mkt_c_node

    def _registered_load(self, topological_node, ce_name, mp_name, mp_role):
        """cim:RegisteredLoad"""
        ce_mp_name = f'{ce_name}|{mp_name}'
        # MktConnectivityNode
        mkt_c_node = self._mkt_connectivity_node(topological_node, ce_mp_name)
        # MarketRole
        market_role = self._instance_exists(mp_role, self._fc.market_roles)
        if market_role is None:
            market_role = nbl.MarketRole(m_rid=str(uuid4()), description=mp_role,
                                         type=mp_role)
            self._fc.market_roles.append(market_role)
        # MarketParticipant
        mp = self._instance_exists(mp_name, self._fc.market_participants)
        if mp is None:
            mp = nbl.MarketParticipant(description=mp_name, m_rid=str(uuid4()),
                                       market_role=[market_role.m_rid])
            self._fc.market_participants.append(mp)
        # MktConnectivityNode -> RegisteredLoad
        registered_load = nbl.RegisteredLoad(m_rid=str(uuid4()),
                                             market_participant=mp.m_rid)
        mkt_c_node.registered_resource.append(registered_load.m_rid)
        self._fc.registered_loads.append(registered_load)
        return registered_load

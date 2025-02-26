# -*- coding: utf-8 -*-

from click import option, group, argument, File, echo, ClickException
from sys import stdin, stdout
from pprint import pprint
from csv import DictReader

from .netbewust_laden import NetbewustLaden

import logging
log = logging.getLogger(__name__)

LOG_FORMAT = '[%(asctime)s] [%(levelname)s] %(message)s'


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
@option('--assets', type=File('rt'), required=True)
@option('--delimiter', '-d', default=',', help='Delimiter used in CSV file')
@option('--only-coord', is_flag=True, default=False,
        help='Reduce location information')
@option('--count', '-c', required=False, default=None, type=int,
        help='Number of rows to process')
@argument('charge_points', type=File('rt'), required=True)
def netbewust_laden(charge_points, assets, out, region, delimiter, only_coord,
                    count):
    """Process NBL Forecast"""
    nbl = NetbewustLaden(region, only_coord)
    # Process each row in the Charge Point CSV
    reader = DictReader(charge_points, delimiter=delimiter)
    for c, row in enumerate(reader, start=1):
        if count is not None and c > count:
            break
        try:
            if c % 1000 == 0:
                log.info(f'Processed {c} charge points')
            nbl.charge_points(row['1_Substation.Name'],
                              row['2_ConductingEquipment.Name'],
                              row['100_MarketEvaluationPoint.EAN'].strip("'"),
                              row['110_MarketParticipant.Name'],
                              # row['111_MarketRole.Name'],
                              'Charge Point Operator',
                              row['120_StreetAddress.Postalcode'],
                              row['122_StreetDetail.Number'].strip(' ELP'),
                              row['123_TownDetail.Name'],
                              row['124_TownDetail.Section'],
                              row['125_TownDetail.StateOrProvince'],
                              row['126_CoordinateSystem.Name'],
                              row['127_PositionPoint.Xposition'].strip("'"),
                              row['128_PositionPoint.Yposition'].strip("'"))
        except ValueError as e:
            # log.error(e)
            continue
    # Process each row in the Charge Point CSV
    reader = DictReader(assets, delimiter=delimiter)
    for c, row in enumerate(reader, start=1):
        if count is not None and c > count:
            break
        try:
            if c % 1000 == 0:
                log.info(f'Processed {c} assets')
            nbl.assets(row['1_Substation.Name'],
                       row['2_ConductingEquipment.Name'],
                       row['3_MktPSRType.PsrType'],
                       row['10_StreetAddress.Postalcode'],
                       row['11_StreetDetail.Name'],
                       row['12_StreetDetail.Number'],
                       row['13_StreetDetail.Code'],
                       row['14_TownDetail.Name'],
                       row['15_TownDetail.Section'],
                       row['16_TownDetail.StateOrProvince'],
                       row['17_CoordinateSystem.Name'],
                       row['18_PositionPoint.Xposition'].strip("'"),
                       row['19_PositionPoint.Yposition'].strip("'"),
                       (row['30_Analog.Name'],
                        row['31_Analog.MeasurementType'],
                        row['32_Analog.UnitMultiplier'],
                        row['33_Analog.UnitSymbol'],
                        float(row['34_AnalogValue.Value']),
                        row['35_AnalogValue.Timestamp']),
                       (row['40_OperationalLimitSet.Name'],
                        row['41_ActivePowerLimit.UnitMultiplier'],
                        row['42_ActivePowerLimit.UnitSymbol'],
                        float(row['43_ActivePowerLimit.Value'])),
                       (row['50_OperationalLimitSet.Name'],
                        row['51_ActivePowerLimit.UnitMultiplier'],
                        row['52_ActivePowerLimit.UnitSymbol'],
                        float(row['53_ActivePowerLimit.Value'])))
        except ValueError as e:
            # log.error(f'{row['2_ConductingEquipment.Name']}: {e}')
            continue
    # Output dataset
    echo(nbl, file=out)

from __future__ import annotations 

import re
import sys
from datetime import (
    date,
    datetime,
    time
)
from decimal import Decimal 
from enum import Enum 
from typing import (
    Any,
    ClassVar,
    Dict,
    List,
    Literal,
    Optional,
    Union
)

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    RootModel,
    field_validator
)


metamodel_version = "None"
version = "None"


class ConfiguredBaseModel(BaseModel):
    model_config = ConfigDict(
        validate_assignment = True,
        validate_default = True,
        extra = "forbid",
        arbitrary_types_allowed = True,
        use_enum_values = True,
        strict = False,
    )
    pass




class LinkMLMeta(RootModel):
    root: Dict[str, Any] = {}
    model_config = ConfigDict(frozen=True)

    def __getattr__(self, key:str):
        return getattr(self.root, key)

    def __getitem__(self, key:str):
        return self.root[key]

    def __setitem__(self, key:str, value):
        self.root[key] = value

    def __contains__(self, key:str) -> bool:
        return key in self.root


linkml_meta = None

class UnitMultiplier(str, Enum):
    """
    The unit multipliers defined for the CIM.  When applied to unit symbols, the unit symbol is treated as a derived unit. Regardless of the contents of the unit symbol text, the unit symbol shall be treated as if it were a single-character unit symbol. Unit symbols should not contain multipliers, and it should be left to the multiplier to define the multiple for an entire data type. 

For example, if a unit symbol is "m2Pers" and the multiplier is "k", then the value is k(m**2/s), and the multiplier applies to the entire final value, not to any individual part of the value. This can be conceptualized by substituting a derived unit symbol for the unit type. If one imagines that the symbol "Þ" represents the derived unit "m2Pers", then applying the multiplier "k" can be conceptualized simply as "kÞ".

For example, the SI unit for mass is "kg" and not "g".  If the unit symbol is defined as "kg", then the multiplier is applied to "kg" as a whole and does not replace the "k" in front of the "g". In this case, the multiplier of "m" would be used with the unit symbol of "kg" to represent one gram.  As a text string, this violates the instructions in IEC 80000-1. However, because the unit symbol in CIM is treated as a derived unit instead of as an SI unit, it makes more sense to conceptualize the "kg" as if it were replaced by one of the proposed replacements for the SI mass symbol. If one imagines that the "kg" were replaced by a symbol "Þ", then it is easier to conceptualize the multiplier "m" as creating the proper unit "mÞ", and not the forbidden unit "mkg".
    """
    a = "a"
    c = "c"
    d = "d"
    da = "da"
    E = "E"
    f = "f"
    G = "G"
    h = "h"
    k = "k"
    m = "m"
    M = "M"
    micro = "micro"
    n = "n"
    none = "none"
    p = "p"
    P = "P"
    T = "T"
    y = "y"
    Y = "Y"
    z = "z"
    Z = "Z"


class UnitSymbol(str, Enum):
    """
    The derived units defined for usage in the CIM. In some cases, the derived unit is equal to an SI unit. Whenever possible, the standard derived symbol is used instead of the formula for the derived unit. For example, the unit symbol Farad is defined as "F" instead of "CPerV". In cases where a standard symbol does not exist for a derived unit, the formula for the unit is used as the unit symbol. For example, density does not have a standard symbol and so it is represented as "kgPerm3". With the exception of the "kg", which is an SI unit, the unit symbols do not contain multipliers and therefore represent the base derived unit to which a multiplier can be applied as a whole. 
Every unit symbol is treated as an unparseable text as if it were a single-letter symbol. The meaning of each unit symbol is defined by the accompanying descriptive text and not by the text contents of the unit symbol.
To allow the widest possible range of serializations without requiring special character handling, several substitutions are made which deviate from the format described in IEC 80000-1. The division symbol "/" is replaced by the letters "Per". Exponents are written in plain text after the unit as "m3" instead of being formatted as "m" with a superscript of 3  or introducing a symbol as in "m^3". The degree symbol "°" is replaced with the letters "deg". Any clarification of the meaning for a substitution is included in the description for the unit symbol.
Non-SI units are included in list of unit symbols to allow sources of data to be correctly labelled with their non-SI units (for example, a GPS sensor that is reporting numbers that represent feet instead of meters). This allows software to use the unit symbol information correctly convert and scale the raw data of those sources into SI-based units. 
The integer values are used for harmonization with IEC 61850.
    """
    A = "A"
    A2 = "A2"
    A2h = "A2h"
    A2s = "A2s"
    Ah = "Ah"
    anglemin = "anglemin"
    anglesec = "anglesec"
    APerA = "APerA"
    APerm = "APerm"
    As = "As"
    bar = "bar"
    Bq = "Bq"
    Btu = "Btu"
    C = "C"
    cd = "cd"
    character = "character"
    charPers = "charPers"
    cosPhi = "cosPhi"
    count = "count"
    CPerkg = "CPerkg"
    CPerm2 = "CPerm2"
    CPerm3 = "CPerm3"
    d = "d"
    dB = "dB"
    dBm = "dBm"
    deg = "deg"
    degC = "degC"
    F = "F"
    FPerm = "FPerm"
    ft3 = "ft3"
    G = "G"
    gal = "gal"
    gPerg = "gPerg"
    Gy = "Gy"
    GyPers = "GyPers"
    H = "H"
    h = "h"
    ha = "ha"
    HPerm = "HPerm"
    Hz = "Hz"
    HzPerHz = "HzPerHz"
    HzPers = "HzPers"
    J = "J"
    JPerK = "JPerK"
    JPerkg = "JPerkg"
    JPerkgK = "JPerkgK"
    JPerm2 = "JPerm2"
    JPerm3 = "JPerm3"
    JPermol = "JPermol"
    JPermolK = "JPermolK"
    JPers = "JPers"
    K = "K"
    kat = "kat"
    katPerm3 = "katPerm3"
    kg = "kg"
    kgm = "kgm"
    kgm2 = "kgm2"
    kgPerJ = "kgPerJ"
    kgPerm3 = "kgPerm3"
    kn = "kn"
    KPers = "KPers"
    l = "l"
    lm = "lm"
    lPerh = "lPerh"
    lPerl = "lPerl"
    lPers = "lPers"
    lx = "lx"
    m = "m"
    M = "M"
    m2 = "m2"
    m2Pers = "m2Pers"
    m3 = "m3"
    m3Compensated = "m3Compensated"
    m3Perh = "m3Perh"
    m3Perkg = "m3Perkg"
    m3Pers = "m3Pers"
    m3Uncompensated = "m3Uncompensated"
    min = "min"
    mmHg = "mmHg"
    mol = "mol"
    molPerkg = "molPerkg"
    molPerm3 = "molPerm3"
    molPermol = "molPermol"
    mPerm3 = "mPerm3"
    mPers = "mPers"
    mPers2 = "mPers2"
    Mx = "Mx"
    N = "N"
    Nm = "Nm"
    none = "none"
    NPerm = "NPerm"
    Oe = "Oe"
    ohm = "ohm"
    ohmm = "ohmm"
    ohmPerm = "ohmPerm"
    onePerHz = "onePerHz"
    onePerm = "onePerm"
    Pa = "Pa"
    PaPers = "PaPers"
    Pas = "Pas"
    ppm = "ppm"
    Q = "Q"
    Qh = "Qh"
    rad = "rad"
    radPers = "radPers"
    radPers2 = "radPers2"
    rev = "rev"
    rotPers = "rotPers"
    s = "s"
    S = "S"
    SPerm = "SPerm"
    sPers = "sPers"
    sr = "sr"
    Sv = "Sv"
    T = "T"
    therm = "therm"
    tonne = "tonne"
    V = "V"
    V2 = "V2"
    V2h = "V2h"
    VA = "VA"
    VAh = "VAh"
    VAr = "VAr"
    VArh = "VArh"
    Vh = "Vh"
    VPerHz = "VPerHz"
    VPerm = "VPerm"
    VPerV = "VPerV"
    VPerVA = "VPerVA"
    VPerVAr = "VPerVAr"
    Vs = "Vs"
    W = "W"
    Wb = "Wb"
    Wh = "Wh"
    WPerA = "WPerA"
    WPerm2 = "WPerm2"
    WPerm2sr = "WPerm2sr"
    WPermK = "WPermK"
    WPers = "WPers"
    WPersr = "WPersr"
    WPerW = "WPerW"


class PhaseCode(str, Enum):
    """
    An unordered enumeration of phase identifiers.  Allows designation of phases for both transmission and distribution equipment, circuits and loads.   The enumeration, by itself, does not describe how the phases are connected together or connected to ground.  Ground is not explicitly denoted as a phase.
Residential and small commercial loads are often served from single-phase, or split-phase, secondary circuits. For the example of s12N, phases 1 and 2 refer to hot wires that are 180 degrees out of phase, while N refers to the neutral wire. Through single-phase transformer connections, these secondary circuits may be served from one or two of the primary phases A, B, and C. For three-phase loads, use the A, B, C phase codes instead of s12N.
The integer values are from IEC 61968-9 to support revenue metering applications.
    """
    A = "A"
    AB = "AB"
    ABC = "ABC"
    ABCN = "ABCN"
    ABN = "ABN"
    AC = "AC"
    ACN = "ACN"
    AN = "AN"
    B = "B"
    BC = "BC"
    BCN = "BCN"
    BN = "BN"
    C = "C"
    CN = "CN"
    N = "N"
    none = "none"
    s1 = "s1"
    s12 = "s12"
    s12N = "s12N"
    s1N = "s1N"
    s2 = "s2"
    s2N = "s2N"
    X = "X"
    XN = "XN"
    XY = "XY"
    XYN = "XYN"


class OperationalLimitDirectionKind(str, Enum):
    """
    The direction attribute describes the side of  a limit that is a violation.
    """
    absoluteValue = "absoluteValue"
    high = "high"
    low = "low"


class AmiBillingReadyKind(str, Enum):
    """
    Lifecycle states of the metering installation at a usage point with respect to readiness for billing via advanced metering infrastructure reads.

    """
    amiCapable = "amiCapable"
    amiDisabled = "amiDisabled"
    billingApproved = "billingApproved"
    enabled = "enabled"
    nonAmi = "nonAmi"
    nonMetered = "nonMetered"
    operable = "operable"


class UsagePointConnectedKind(str, Enum):
    """
    State of the usage point with respect to connection to the network.

    """
    connected = "connected"
    logicallyDisconnected = "logicallyDisconnected"
    physicallyDisconnected = "physicallyDisconnected"


class WindingConnection(str, Enum):
    """
    Winding connection type.

    """
    A = "A"
    D = "D"
    I = "I"
    Y = "Y"
    Yn = "Yn"
    Z = "Z"
    Zn = "Zn"


class YesNo(str, Enum):
    """
    Used as a flag set to Yes or No.
    """
    NO = "NO"
    YES = "YES"


class ResourceRegistrationStatus(str, Enum):
    """
    Types of resource registration status, for example:

Active
Mothballed
Planned
Decommissioned

    """
    Active = "Active"
    Decommissioned = "Decommissioned"
    Mothballed = "Mothballed"
    Planned = "Planned"


class PhaseShuntConnectionKind(str, Enum):
    """
    The configuration of phase connections for a single terminal device such as a load or capacitor.
    """
    D = "D"
    G = "G"
    I = "I"
    Y = "Y"
    Yn = "Yn"



class ForecastDataSet(ConfiguredBaseModel):
    """
    A single instance of a published dataset.
    """
    identifier: str = Field(default=...)
    conforms_to: str = Field(default=...)
    contact_point: str = Field(default=...)
    release_date: str = Field(default=...)
    version: str = Field(default=...)
    terminals: List[Terminal] = Field(default=..., description="""All instances of Terminals""")
    topological_nodes: List[TopologicalNode] = Field(default=..., description="""All instances of TopologicalNodes""")
    coordinate_systems: List[CoordinateSystem] = Field(default=..., description="""All instances of CoordinateSystems""")
    usage_points: List[UsagePoint] = Field(default=..., description="""All instances of UsagePoints""")
    substations: List[Substation] = Field(default=..., description="""All instances of Substations""")
    sub_geographical_regions: List[SubGeographicalRegion] = Field(default=..., description="""All instances of SubGeographicalRegions""")
    lines: List[Line] = Field(default=..., description="""All instances of Lines""")
    geographical_regions: List[GeographicalRegion] = Field(default=..., description="""All instances of GeographicalRegions""")
    power_transformers: List[PowerTransformer] = Field(default=..., description="""All instances of PowerTransformers""")
    ac_line_segments: List[ACLineSegment] = Field(default=..., description="""All instances of ACLineSegments""")
    analogs: List[Analog] = Field(default=..., description="""All instances of Analogs""")
    registered_loads: List[RegisteredLoad] = Field(default=..., description="""All instances of RegisteredLoads""")
    mkt_connectivity_nodes: List[MktConnectivityNode] = Field(default=..., description="""All instances of MktConnectivityNodes""")
    market_participants: List[MarketParticipant] = Field(default=..., description="""All instances of MarketParticipants""")
    market_roles: List[MarketRole] = Field(default=..., description="""All instances of MarketRoles""")
    energy_consumers: List[EnergyConsumer] = Field(default=..., description="""All instances of EnergyConsumers""")


class Name(ConfiguredBaseModel):
    """
    The Name class provides the means to define any number of human readable  names for an object. A name is <b>not</b> to be used for defining inter-object relationships. For inter-object relationships instead use the object identification 'mRID'.

    """
    name_type: NameType = Field(default=..., description="""Type of this name.""")


class NameType(ConfiguredBaseModel):
    """
    Type of name. Possible values for attribute 'name' are implementation dependent but standard profiles may specify types. An enterprise may have multiple IT systems each having its own local name for the same object, e.g. a planning system may have different names from an EMS. An object may also have different names within the same IT system, e.g. localName as defined in CIM version 14. The definition from CIM14 is:
    The localName is a human readable name of the object. It is a free text name local to a node in a naming hierarchy similar to a file directory structure. A power system related naming hierarchy may be: Substation, VoltageLevel, Equipment etc. Children of the same parent in such a hierarchy have names that typically are unique among them.

    """
    description: Optional[str] = Field(default=None, description="""Description of the name type.
""")
    name_type_authority: Optional[NameTypeAuthority] = Field(default=None, description="""Authority responsible for managing names of this type.""")


class NameTypeAuthority(ConfiguredBaseModel):
    """
    Authority responsible for creation and management of names of a given type; typically an organization or an enterprise system.

    """
    description: Optional[str] = Field(default=None, description="""Description of the name type authority.
""")


class IdentifiedObject(ConfiguredBaseModel):
    """
    This is a root class to provide common identification for all classes needing identification and naming attributes.
    """
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class ActivePower(ConfiguredBaseModel):
    """
    Product of RMS value of the voltage and the RMS value of the in-phase component of the current.
    """
    multiplier: UnitMultiplier = Field(default=...)
    unit: UnitSymbol = Field(default=...)
    value: float = Field(default=...)


class TopologicalNode(IdentifiedObject):
    """
    For a detailed substation model a topological node is a set of connectivity nodes that, in the current network state, are connected together through any type of closed switches, including  jumpers. Topological nodes change as the current network state changes (i.e., switches, breakers, etc. change state).
    For a planning model, switch statuses are not used to form topological nodes. Instead they are manually created or deleted in a model builder tool. Topological nodes maintained this way are also called \"busses\".
    """
    connectivity_nodes: Optional[List[str]] = Field(default=None, description="""The connectivity nodes combine together to form this topological node.  May depend on the current state of switches in the network.""")
    terminal: List[str] = Field(default=..., description="""The terminals associated with the topological node. This can be used as an alternative to the connectivity node path to terminal, thus making it unnecessary to model connectivity nodes in some cases. Note that if connectivity nodes are in the model, this association would probably not be used as an input specification.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class ConnectivityNode(IdentifiedObject):
    """
    Connectivity nodes are points where terminals of AC conducting equipment are connected together with zero impedance.
    """
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class TransformerEnd(IdentifiedObject):
    """
    A conducting connection point of a power transformer. It corresponds to a physical transformer winding terminal.  In earlier CIM versions, the TransformerWinding class served a similar purpose, but this class is more flexible because it associates to terminal but is not a specialization of ConductingEquipment.
    """
    terminal: str = Field(default=..., description="""Terminal of the power transformer to which this transformer end belongs.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class OperationalLimitSet(IdentifiedObject):
    """
    A set of limits associated with equipment.  Sets of limits might apply to a specific temperature, or season for example. A set of limits may contain different severities of limit levels that would apply to the same equipment. The set may contain limits of different types such as apparent power and current limits or high and low voltage limits  that are logically applied together as a set.

    """
    operational_limit_value: Optional[List[str]] = Field(default=None, description="""Values of equipment limits.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class ACDCTerminal(IdentifiedObject):
    """
    An electrical connection point (AC or DC) to a piece of conducting equipment. Terminals are connected at physical connection points called connectivity nodes.
    """
    operational_limit_set: Optional[List[str]] = Field(default=None, description="""The operational limit sets at the terminal.""")
    measurements: Optional[List[str]] = Field(default=None, description="""Measurements associated with this terminal defining  where the measurement is placed in the network topology.  It may be used, for instance, to capture the sensor position, such as a voltage transformer (PT) at a busbar or a current transformer (CT) at the bar between a breaker and an isolator.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class Terminal(ACDCTerminal):
    """
    An AC electrical connection point to a piece of conducting equipment. Terminals are connected at physical connection points called connectivity nodes.
    """
    topological_node: Optional[str] = Field(default=None, description="""The topological node associated with the terminal. This can be used as an alternative to the connectivity node path to topological node, thus making it unnecessary to model connectivity nodes in some cases. Note that the if connectivity nodes are in the model, this association would probably not be used as an input specification.""")
    connectivity_node: Optional[str] = Field(default=None, description="""The connectivity node to which this terminal connects with zero impedance.""")
    conducting_equipment: Optional[str] = Field(default=None, description="""The conducting equipment of the terminal. Conducting equipment have  terminals that may be connected to other conducting equipment terminals via connectivity nodes or topological nodes.""")
    operational_limit_set: Optional[List[str]] = Field(default=None, description="""The operational limit sets at the terminal.""")
    measurements: Optional[List[str]] = Field(default=None, description="""Measurements associated with this terminal defining  where the measurement is placed in the network topology.  It may be used, for instance, to capture the sensor position, such as a voltage transformer (PT) at a busbar or a current transformer (CT) at the bar between a breaker and an isolator.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class Measurement(IdentifiedObject):
    """
    A Measurement represents any measured, calculated or non-measured non-calculated quantity. Any piece of equipment may contain Measurements, e.g. a substation may have temperature measurements and door open indications, a transformer may have oil temperature and tank pressure measurements, a bay may contain a number of power flow measurements and a Breaker may contain a switch status measurement. 
    The PSR - Measurement association is intended to capture this use of Measurement and is included in the naming hierarchy based on EquipmentContainer. The naming hierarchy typically has Measurements as leaves, e.g. Substation-VoltageLevel-Bay-Switch-Measurement.
    Some Measurements represent quantities related to a particular sensor location in the network, e.g. a voltage transformer (VT) or potential transformer (PT) at a busbar or a current transformer (CT) at the bar between a breaker and an isolator. The sensing position is not captured in the PSR - Measurement association. Instead it is captured by the Measurement - Terminal association that is used to define the sensing location in the network topology. The location is defined by the connection of the Terminal to ConductingEquipment. 
    If both a Terminal and PSR are associated, and the PSR is of type ConductingEquipment, the associated Terminal should belong to that ConductingEquipment instance.
    When the sensor location is needed both Measurement-PSR and Measurement-Terminal are used.
    """
    measurement_type: Optional[str] = Field(default=None, description="""Specifies the type of measurement.  For example, this specifies if the measurement represents an indoor temperature, outdoor temperature, bus voltage, line flow, etc.
When the measurementType is set to \"Specialization\", the type of Measurement is defined in more detail by the specialized class which inherits from Measurement.

""")
    unit_multiplier: UnitMultiplier = Field(default=..., description="""The unit multiplier of the measured quantity.""")
    unit_symbol: UnitSymbol = Field(default=..., description="""The unit of measure of the measured quantity.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class PowerSystemResource(IdentifiedObject):
    """
    A power system resource (PSR) can be an item of equipment such as a switch, an equipment container containing many individual items of equipment such as a substation, or an organisational entity such as sub-control area. Power system resources can have measurements associated.
    """
    location: Optional[Location] = Field(default=None, description="""Location of this power system resource.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class ConnectivityNodeContainer(PowerSystemResource):
    """
    A base class for all objects that may contain connectivity nodes or topological nodes.

    """
    location: Optional[Location] = Field(default=None, description="""Location of this power system resource.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class Equipment(PowerSystemResource):
    """
    The parts of a power system that are physical devices, electronic or mechanical.
    """
    operational_limit_set: Optional[List[OperationalLimitSet]] = Field(default=None, description="""The operational limit sets associated with this equipment.""")
    usage_points: Optional[List[str]] = Field(default=None, description="""All usage points connected to the electrical grid through this equipment.""")
    location: Optional[Location] = Field(default=None, description="""Location of this power system resource.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class ConductingEquipment(Equipment):
    """
    The parts of the AC power system that are designed to carry current or that are conductively connected through terminals.
    """
    operational_limit_set: Optional[List[OperationalLimitSet]] = Field(default=None, description="""The operational limit sets associated with this equipment.""")
    usage_points: Optional[List[str]] = Field(default=None, description="""All usage points connected to the electrical grid through this equipment.""")
    location: Optional[Location] = Field(default=None, description="""Location of this power system resource.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class EnergyConnection(ConductingEquipment):
    """
    A connection of energy generation or consumption on the power system model.
    """
    operational_limit_set: Optional[List[OperationalLimitSet]] = Field(default=None, description="""The operational limit sets associated with this equipment.""")
    usage_points: Optional[List[str]] = Field(default=None, description="""All usage points connected to the electrical grid through this equipment.""")
    location: Optional[Location] = Field(default=None, description="""Location of this power system resource.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class Location(IdentifiedObject):
    """
    The place, scene, or point of something where someone or something has been, is, and/or will be at a given moment in time. It can be defined with one or more position points (coordinates) in a given coordinate system.

    """
    main_address: Optional[StreetAddress] = Field(default=None, description="""Main address of the location.""")
    coordinate_system: Optional[str] = Field(default=None, description="""Coordinate system used to describe position points of this location.""")
    position_points: Optional[List[PositionPoint]] = Field(default=None, description="""Sequence of position points describing this location, expressed in coordinate system 'Location.CoordinateSystem'.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class StreetAddress(ConfiguredBaseModel):
    """
    General purpose street and postal address information.
    """
    postal_code: str = Field(default=..., description="""Postal code for the address.""")
    street_detail: StreetDetail = Field(default=..., description="""Street detail.""")
    town_detail: Optional[TownDetail] = Field(default=None, description="""Town detail.""")


class StreetDetail(ConfiguredBaseModel):
    """
    Street details, in the context of address.

    """
    code: Optional[str] = Field(default=None, description="""(if applicable) Utilities often make use of external reference systems, such as those of the town-planner's department or surveyor general's mapping system, that allocate global reference codes to streets.""")
    number: str = Field(default=..., description="""Designator of the specific location on the street. Includes number suffix, i.e. '11 A'.""")


class TownDetail(ConfiguredBaseModel):
    """
    Town details, in the context of address.

    """
    name: Optional[str] = Field(default=None, description="""Town name.""")
    section: Optional[str] = Field(default=None, description="""Town section. For example, it is common for there to be 36 sections per township.""")
    state_or_province: str = Field(default=..., description="""Name of the state or province.""")


class CoordinateSystem(IdentifiedObject):
    """
    Coordinate reference system.

    """
    crs_urn: str = Field(default=..., description="""A Uniform Resource Name (URN) for the coordinate reference system (crs) used to define 'Location.PositionPoints'.
An example would be the European Petroleum Survey Group (EPSG) code for a coordinate reference system, defined in URN under the Open Geospatial Consortium (OGC) namespace as: urn:ogc:def:crs:EPSG::XXXX, where XXXX is an EPSG code (a full list of codes can be found at the EPSG Registry web site http://www.epsg-registry.org/). To define the coordinate system as being WGS84 (latitude, longitude) using an EPSG OGC, this attribute would be urn:ogc:def:crs:EPSG::4.3.2.6
A profile should limit this code to a set of allowed URNs agreed to by all sending and receiving parties.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class PositionPoint(ConfiguredBaseModel):
    """
    Set of spatial coordinates that determine a point, defined in the coordinate system specified in 'Location.CoordinateSystem'. Use a single position point instance to describe a point-oriented location. Use a sequence of position points to describe a line-oriented object (physical location of non-point oriented objects like cables or lines), or area of an object (like a substation or a geographical zone - in this case, have first and last position point with the same values).
    """
    group_number: Optional[int] = Field(default=None, description="""Zero-relative sequence number of this group within a series of points; used when there is a need to express disjoint groups of points that are considered to be part of a single location.""")
    sequence_number: Optional[int] = Field(default=None, description="""Zero-relative sequence number of this point within a series of points.""")
    x_position: str = Field(default=..., description="""X axis position.""")
    y_position: str = Field(default=..., description="""Y axis position.""")
    z_position: Optional[str] = Field(default=None, description="""(if applicable) Z axis position.""")


class OperationalLimit(IdentifiedObject):
    """
    A value and normal value associated with a specific kind of limit. 
    The sub class value and normalValue attributes vary inversely to the associated OperationalLimitType.acceptableDuration (acceptableDuration for short).  
    If a particular piece of equipment has multiple operational limits of the same kind (apparent power, current, etc.), the limit with the greatest acceptableDuration shall have the smallest limit value and the limit with the smallest acceptableDuration shall have the largest limit value.  Note: A large current can only be allowed to flow through a piece of equipment for a short duration without causing damage, but a lesser current can be allowed to flow for a longer duration. 
    """
    operational_limit_type: OperationalLimitType = Field(default=..., description="""The limit type associated with this limit.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class OperationalLimitType(IdentifiedObject):
    """
    The operational meaning of a category of limits.

    """
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class EquipmentContainer(ConnectivityNodeContainer):
    """
    A modelling construct to provide a root class for containing equipment. 
    """
    equipments: List[str] = Field(default=..., description="""Contained equipment.""")
    location: Optional[Location] = Field(default=None, description="""Location of this power system resource.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class UsagePoint(IdentifiedObject):
    """
    Logical or physical point in the network to which readings or events may be attributed. Used at the place where a physical or virtual meter may be located; however, it is not required that a meter be present.
    """
    european_article_number_ean: str = Field(default=..., description="""The attribute is used for an exchange of the EAN code (European Article Number). The length of the string is 18 characters as defined by the EAN code. For details on EAN scheme please refer to the [Codebesluit toekenning EAN-codes elektriciteit](https://www.acm.nl/nl/publicaties/codebesluit-toekenning-ean-codes-elektriciteit).""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class Substation(EquipmentContainer):
    """
    A collection of equipment for purposes other than generation or utilization, through which electric energy in bulk is passed for the purposes of switching or modifying its characteristics. 

    """
    equipments: List[str] = Field(default=..., description="""Contained equipment.""")
    location: Optional[Location] = Field(default=None, description="""Location of this power system resource.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class SubGeographicalRegion(IdentifiedObject):
    """
    A subset of a geographical region of a power system network model.

    """
    lines: List[str] = Field(default=..., description="""The lines within the sub-geographical region.""")
    substations: List[str] = Field(default=..., description="""The substations in this sub-geographical region.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class Line(EquipmentContainer):
    """
    Contains equipment beyond a substation belonging to a power transmission line. 
    """
    equipments: List[str] = Field(default=..., description="""Contained equipment.""")
    location: Optional[Location] = Field(default=None, description="""Location of this power system resource.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class GeographicalRegion(IdentifiedObject):
    """
    A geographical region of a power system network model.
    """
    regions: List[str] = Field(default=..., description="""All sub-geographical regions within this geographical region.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class PowerTransformer(ConductingEquipment):
    """
    An electrical device consisting of  two or more coupled windings, with or without a magnetic core, for introducing mutual coupling between electric circuits. Transformers can be used to control voltage and phase shift (active power flow).
    A power transformer may be composed of separate transformer tanks that need not be identical.
    A power transformer can be modelled with or without tanks and is intended for use in both balanced and unbalanced representations.   A power transformer typically has two terminals, but may have one (grounding), three or more terminals.
    The inherited association ConductingEquipment.BaseVoltage should not be used.  The association from TransformerEnd to BaseVoltage should be used instead.
    """
    power_transformer_end: List[PowerTransformerEnd] = Field(default=..., description="""The ends of this power transformer.""")
    operational_limit_set: Optional[List[OperationalLimitSet]] = Field(default=None, description="""The operational limit sets associated with this equipment.""")
    usage_points: Optional[List[str]] = Field(default=None, description="""All usage points connected to the electrical grid through this equipment.""")
    location: Optional[Location] = Field(default=None, description="""Location of this power system resource.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class PowerTransformerEnd(TransformerEnd):
    """
    A PowerTransformerEnd is associated with each Terminal of a PowerTransformer.
    The impedance values r, r0, x, and x0 of a PowerTransformerEnd represents a star equivalent as follows.
    1) for a two Terminal PowerTransformer the high voltage (TransformerEnd.endNumber=1) PowerTransformerEnd has non zero values on r, r0, x, and x0 while the low voltage (TransformerEnd.endNumber=2) PowerTransformerEnd has zero values for r, r0, x, and x0.  Parameters are always provided, even if the PowerTransformerEnds have the same rated voltage.  In this case, the parameters are provided at the PowerTransformerEnd which has TransformerEnd.endNumber equal to 1.
    2) for a three Terminal PowerTransformer the three PowerTransformerEnds represent a star equivalent with each leg in the star represented by r, r0, x, and x0 values.
    3) For a three Terminal transformer each PowerTransformerEnd shall have g, g0, b and b0 values corresponding to the no load losses distributed on the three PowerTransformerEnds. The total no load loss shunt impedances may also be placed at one of the PowerTransformerEnds, preferably the end numbered 1, having the shunt values on end 1.  This is the preferred way.
    4) for a PowerTransformer with more than three Terminals the PowerTransformerEnd impedance values cannot be used. Instead use the TransformerMeshImpedance or split the transformer into multiple PowerTransformers.
    Each PowerTransformerEnd must be contained by a PowerTransformer. Because a PowerTransformerEnd (or any other object) can not be contained by more than one parent, a PowerTransformerEnd can not have an association to an EquipmentContainer (Substation, VoltageLevel, etc).
    """
    terminal: str = Field(default=..., description="""Terminal of the power transformer to which this transformer end belongs.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class Conductor(ConductingEquipment):
    """
    Combination of conducting material with consistent electrical characteristics, building a single electrical system, used to carry current between points in the power system.  
    """
    operational_limit_set: Optional[List[OperationalLimitSet]] = Field(default=None, description="""The operational limit sets associated with this equipment.""")
    usage_points: Optional[List[str]] = Field(default=None, description="""All usage points connected to the electrical grid through this equipment.""")
    location: Optional[Location] = Field(default=None, description="""Location of this power system resource.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class ACLineSegment(Conductor):
    """
    A wire or combination of wires, with consistent electrical characteristics, building a single electrical system, used to carry alternating current between points in the power system.
    For symmetrical, transposed three phase lines, it is sufficient to use attributes of the line segment, which describe impedances and admittances for the entire length of the segment.  Additionally impedances can be computed by using length and associated per length impedances.
    The BaseVoltage at the two ends of ACLineSegments in a Line shall have the same BaseVoltage.nominalVoltage. However, boundary lines may have slightly different BaseVoltage.nominalVoltages and variation is allowed. Larger voltage difference in general requires use of an equivalent branch.
    """
    operational_limit_set: Optional[List[OperationalLimitSet]] = Field(default=None, description="""The operational limit sets associated with this equipment.""")
    usage_points: Optional[List[str]] = Field(default=None, description="""All usage points connected to the electrical grid through this equipment.""")
    location: Optional[Location] = Field(default=None, description="""Location of this power system resource.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class Analog(Measurement):
    """
    Analog represents an analog Measurement.

    """
    positive_flow_in: Optional[bool] = Field(default=None, description="""If true then this measurement is an active power, reactive power or current with the convention that a positive value measured at the Terminal means power is flowing into the related PowerSystemResource.""")
    analog_values: List[AnalogValue] = Field(default=..., description="""The values connected to this measurement.""")
    measurement_type: Optional[str] = Field(default=None, description="""Specifies the type of measurement.  For example, this specifies if the measurement represents an indoor temperature, outdoor temperature, bus voltage, line flow, etc.
When the measurementType is set to \"Specialization\", the type of Measurement is defined in more detail by the specialized class which inherits from Measurement.

""")
    unit_multiplier: UnitMultiplier = Field(default=..., description="""The unit multiplier of the measured quantity.""")
    unit_symbol: UnitSymbol = Field(default=..., description="""The unit of measure of the measured quantity.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class ActivePowerLimit(OperationalLimit):
    """
    Limit on active power flow.
    """
    value: ActivePower = Field(default=..., description="""Value of active power limit. The attribute shall be a positive value or zero.""")
    operational_limit_type: OperationalLimitType = Field(default=..., description="""The limit type associated with this limit.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class RegisteredResource(PowerSystemResource):
    """
    A resource that is registered through the market participant registration system. Examples include generating unit, load, and non-physical generator or load.
    """
    market_participant: str = Field(default=...)
    location: Optional[Location] = Field(default=None, description="""Location of this power system resource.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class RegisteredLoad(RegisteredResource):
    """
    Model of a load that is registered to participate in the market.

    RegisteredLoad is used to model any load that is served by the wholesale market directly. RegisteredLoads may be dispatchable or non-dispatchable and may or may not have bid curves. Examples of RegisteredLoads would include: distribution company load, energy retailer load, large bulk power system connected facility load.

    Loads that are served indirectly, for example - through an energy retailer or a vertical utility, should be modeled as RegisteredDistributedResources. Examples of RegisteredDistributedResources would include: distribution level storage, distribution level generation and distribution level demand response.
    """
    market_participant: str = Field(default=...)
    location: Optional[Location] = Field(default=None, description="""Location of this power system resource.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class MktConnectivityNode(ConnectivityNode):
    """
    Subclass of IEC61970:Topology:ConnectivityNode.
    """
    registered_resource: List[str] = Field(default=...)
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class Organisation(IdentifiedObject):
    """
    Organisation that might have roles as utility, contractor, supplier, manufacturer, customer, etc.
    """
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class MarketParticipant(Organisation):
    """
    An identification of a party acting in a electricity market business process. This class is used to identify organizations that can participate in market management and/or market operations.
    """
    market_role: List[str] = Field(default=...)
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class OrganisationRole(IdentifiedObject):
    """
    Identifies a way in which an organisation may participate in the utility enterprise (e.g., customer, manufacturer, etc).

    """
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class MarketRole(OrganisationRole):
    """
    The external intended behavior played by a party within the electricity market.
    """
    type: str = Field(default=..., description="""The kind of market roles that can be played by parties for given domains within the electricity market. Types are flexible using dataType of string for free-entry of role types.
""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class EnergyConsumer(EnergyConnection):
    """
    Generic user of energy - a  point of consumption on the power system model.
    EnergyConsumer.pfixed, .qfixed, .pfixedPct and .qfixedPct have meaning only if there is no LoadResponseCharacteristic associated with EnergyConsumer or if LoadResponseCharacteristic.exponentModel is set to False.
    """
    operational_limit_set: Optional[List[OperationalLimitSet]] = Field(default=None, description="""The operational limit sets associated with this equipment.""")
    usage_points: Optional[List[str]] = Field(default=None, description="""All usage points connected to the electrical grid through this equipment.""")
    location: Optional[Location] = Field(default=None, description="""Location of this power system resource.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class IOPoint(IdentifiedObject):
    """
    The class describe a measurement or control value. The purpose is to enable having attributes and associations common for measurement and control.
    """
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class MeasurementValue(IOPoint):
    """
    The current state for a measurement. A state value is an instance of a measurement from a specific source. Measurements can be associated with many state values, each representing a different source for the measurement.

    """
    time_stamp: datetime  = Field(default=..., description="""The time when the value was last updated.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


class AnalogValue(MeasurementValue):
    """
    AnalogValue represents an analog MeasurementValue.
    """
    value: float = Field(default=..., description="""The value to supervise.""")
    time_stamp: datetime  = Field(default=..., description="""The time when the value was last updated.""")
    description: Optional[str] = Field(default=None, description="""The description is a free human readable text describing or naming the object. It may be non unique and may not correlate to a naming hierarchy.""")
    m_rid: str = Field(default=..., description="""Master resource identifier issued by a model authority. The mRID is unique within an exchange context. Global uniqueness is easily achieved by using a UUID, as specified in RFC 4122, for the mRID. The use of UUID is strongly recommended.
For CIMXML data files in RDF syntax conforming to IEC 61970-552, the mRID is mapped to rdf:ID or rdf:about attributes that identify CIM object elements.""")


# Model rebuild
# see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
ForecastDataSet.model_rebuild()
Name.model_rebuild()
NameType.model_rebuild()
NameTypeAuthority.model_rebuild()
IdentifiedObject.model_rebuild()
ActivePower.model_rebuild()
TopologicalNode.model_rebuild()
ConnectivityNode.model_rebuild()
TransformerEnd.model_rebuild()
OperationalLimitSet.model_rebuild()
ACDCTerminal.model_rebuild()
Terminal.model_rebuild()
Measurement.model_rebuild()
PowerSystemResource.model_rebuild()
ConnectivityNodeContainer.model_rebuild()
Equipment.model_rebuild()
ConductingEquipment.model_rebuild()
EnergyConnection.model_rebuild()
Location.model_rebuild()
StreetAddress.model_rebuild()
StreetDetail.model_rebuild()
TownDetail.model_rebuild()
CoordinateSystem.model_rebuild()
PositionPoint.model_rebuild()
OperationalLimit.model_rebuild()
OperationalLimitType.model_rebuild()
EquipmentContainer.model_rebuild()
UsagePoint.model_rebuild()
Substation.model_rebuild()
SubGeographicalRegion.model_rebuild()
Line.model_rebuild()
GeographicalRegion.model_rebuild()
PowerTransformer.model_rebuild()
PowerTransformerEnd.model_rebuild()
Conductor.model_rebuild()
ACLineSegment.model_rebuild()
Analog.model_rebuild()
ActivePowerLimit.model_rebuild()
RegisteredResource.model_rebuild()
RegisteredLoad.model_rebuild()
MktConnectivityNode.model_rebuild()
Organisation.model_rebuild()
MarketParticipant.model_rebuild()
OrganisationRole.model_rebuild()
MarketRole.model_rebuild()
EnergyConsumer.model_rebuild()
IOPoint.model_rebuild()
MeasurementValue.model_rebuild()
AnalogValue.model_rebuild()


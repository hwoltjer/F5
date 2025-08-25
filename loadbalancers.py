from dataclasses import dataclass
from enum import Enum, auto


class Datacenter(Enum):
    ODC_z1 = auto()
    ODC_z2 = auto()


class HA_State(Enum):
    ACTIVE = auto()
    PASSIVE = auto()


@dataclass
class Loadbalancer():
    fqdn: str
    datacenter: Datacenter
    state: HA_State
    

class LB(Enum):
    
    f5bigip01 = Loadbalancer(
        fqdn        =   '10.32.6.34',
        datacenter  =   Datacenter.ODC_z1,
        state       =   HA_State.ACTIVE,
    )
    
    f5bigip02 = Loadbalancer(
        fqdn        =   '10.32.6.35',
        datacenter  =   Datacenter.ODC_z2,
        state       =   HA_State.PASSIVE,
    )
    
    #ACI block
    nlb013001_g2 = Loadbalancer(
        fqdn        =   'nlb013001-g2.mgmtdwr.rijksoverheid.nl',
        datacenter  =   Datacenter.ODC_z1,
        state       =   HA_State.ACTIVE,
    )
    
    nlb023002_g2 = Loadbalancer(
        fqdn        =   'nlb023002-g2.mgmtdwr.rijksoverheid.nl',
        datacenter  =   Datacenter.ODC_z2,
        state       =   HA_State.PASSIVE,
    )
    nlb013001_g3 = Loadbalancer(
        fqdn        =   'nlb013001-g3.mgmtdwr.rijksoverheid.nl',
        datacenter  =   Datacenter.ODC_z1,
        state       =   HA_State.ACTIVE,
    )
    
    nlb023002_g3 = Loadbalancer(
        fqdn        =   'nlb023002-g3.mgmtdwr.rijksoverheid.nl',
        datacenter  =   Datacenter.ODC_z2,
        state       =   HA_State.PASSIVE,
    )
    nlb013001_g4 = Loadbalancer(
        fqdn        =   'nlb013001-g4.mgmtdwr.rijksoverheid.nl',
        datacenter  =   Datacenter.ODC_z1,
        state       =   HA_State.ACTIVE,
    )
    nlb023002_g4 = Loadbalancer(
        fqdn        =   'nlb023002-g4.mgmtdwr.rijksoverheid.nl',
        datacenter  =   Datacenter.ODC_z2,
        state       =   HA_State.PASSIVE,
    )
    
    
    #Rijksweb block
    nlb014001_g4 = Loadbalancer(
        fqdn        =   'nlb014001-g4.mgmtdwr.rijksoverheid.nl',
        datacenter  =   Datacenter.ODC_z1,
        state       =   HA_State.ACTIVE,
    )
    
    nlb024002_g4 = Loadbalancer(
        fqdn        =   'nlb024002-g4.mgmtdwr.rijksoverheid.nl',
        datacenter  =   Datacenter.ODC_z2,
        state       =   HA_State.PASSIVE,
    )
    
    
     #Internet block
    nlb014001_g3 = Loadbalancer(
        fqdn        =   'nlb014001-g3.mgmtdwr.rijksoverheid.nl',
        datacenter  =   Datacenter.ODC_z1,
        state       =   HA_State.ACTIVE,
    )
    
    nlb024002_g3 = Loadbalancer(
        fqdn        =   'nlb024002-g3.mgmtdwr.rijksoverheid.nl',
        datacenter  =   Datacenter.ODC_z2,
        state       =   HA_State.PASSIVE,
    )
    
    #dclan block
    nlb013001_g1 = Loadbalancer(
        fqdn        =   'nlb013001-g1.mgmtdwr.rijksoverheid.nl',
        datacenter  =   Datacenter.ODC_z1,
        state       =   HA_State.ACTIVE,
    )
    
    nlb013002_g1 = Loadbalancer(
        fqdn        =   'nlb023002-g1.mgmtdwr.rijksoverheid.nl',
        datacenter  =   Datacenter.ODC_z2,
        state       =   HA_State.PASSIVE,
    )

class BuildingBlock(Enum):    
    hwlab        = [LB.f5bigip01, LB.f5bigip02]
    aci_prod     = [LB.nlb013001_g2, LB.nlb023002_g2]
    aci_acc      = [LB.nlb013001_g3, LB.nlb023002_g3]
    aci_test     = [LB.nlb013001_g4, LB.nlb023002_g4]
    rijksweb     = [LB.nlb014001_g4, LB.nlb024002_g4]
    shared       = [LB.nlb014001_g3, LB.nlb024002_g3] 
    dclan        = [LB.nlb013001_g1, LB.nlb013002_g1]
    
    
    

    
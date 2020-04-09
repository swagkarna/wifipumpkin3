from re import *
from netaddr import EUI
from wifipumpkin3.core.config.globalimport import *
from wifipumpkin3.core.common.uimodel import *
from wifipumpkin3.core.utility.component import ComponentBlueprint
from isc_dhcp_leases.iscdhcpleases import IscDhcpLeases
from wifipumpkin3.core.controls.threads import ProcessThread
from wifipumpkin3.exceptions.errors.dhcpException import DHCPServerSettingsError

# This file is part of the wifipumpkin3 Open Source Project.
# wifipumpkin3 is licensed under the Apache 2.0.

# Copyright 2020 P0cL4bs Team - Marcos Bomfim (mh4x0f)

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

class DHCPServers(QtCore.QObject,ComponentBlueprint):
    Name = "Generic"
    ID = "Generic"
    haspref = False
    ExecutableFile=""
    def __init__(self,parent=0):
        super(DHCPServers,self).__init__()
        self.parent = parent
        self.conf = SuperSettings.getInstance()

        self.DHCPConf = self.Settings.confingDHCP

    def prereq(self):
        dh, gateway = self.DHCPConf['router'], Linux.get_interfaces()['gateway']
        if gateway != None:
            if dh[:len(dh) - len(dh.split('.').pop())] == gateway[:len(gateway) - len(gateway.split('.').pop())]:
                raise DHCPServerSettingsError('DHCPServer', 'dhcp same ip range address ')


    def isChecked(self):
        return self.conf.get('accesspoint', self.ID, format=bool)

    def Stop(self):
        self.shutdown()
        self.reactor.stop()

    def Start(self):
        self.prereq()
        self.Initialize()
        self.boot()

    @property
    def Settings(self):
        return DHCPSettings.instances[0]

    @property
    def commandargs(self):
        pass

    def boot(self):
        print(self.command,self.commandargs)
        self.reactor = ProcessThread({self.command: self.commandargs})
        self.reactor._ProcssOutput.connect(self.LogOutput)
        self.reactor.setObjectName(self.Name)

    @property
    def command(self):
        cmdpath = os.popen('which {}'.format(self.ExecutableFile)).read().split('\n')[0]
        if cmdpath:
            return cmdpath
        else:
            return None

    def get_mac_vendor(self,mac):
        ''' discovery mac vendor by mac address '''
        try:
            d_vendor = EUI(mac)
            d_vendor = d_vendor.oui.registration().org
        except:
            d_vendor = 'unknown mac'
        return d_vendor

class DHCPSettings(CoreSettings):
    Name = "WP DHCP"
    ID = "DHCP"
    ConfigRoot = "dhcpdefault"
    Category = "DHCP"
    instances=[]
    confingDHCP={}

    def __init__(self,parent=0):
        super(DHCPSettings,self).__init__(parent)
        self.__class__.instances.append(weakref.proxy(self))

        self.title = self.__class__.__name__

        self.dhmode = [mod(parent) for mod in DHCPServers.__subclasses__()]
        self.updateconf()

    def updateconf(self):
        self.confingDHCP['leasetimeDef'] = self.conf.get(self.ConfigRoot,'leasetimeDef')
        self.confingDHCP['leasetimeMax'] = self.conf.get(self.ConfigRoot,'leasetimeMax')
        self.confingDHCP['subnet'] = self.conf.get(self.ConfigRoot,'subnet')  
        self.confingDHCP['router'] =  self.conf.get(self.ConfigRoot,'router')
        self.confingDHCP['netmask'] =  self.conf.get(self.ConfigRoot,'netmask')
        self.confingDHCP['broadcast'] = self.conf.get(self.ConfigRoot,'broadcast')
        self.confingDHCP['range'] = self.conf.get(self.ConfigRoot,'range')
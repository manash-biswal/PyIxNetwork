"""
@author yoram@ignissoft.com
"""

from os import path
from sys import platform

from trafficgenerator.tgn_tcl import TgnTclWrapper, get_args_pairs, tcl_file_name, tcl_str, tcl_list_2_py_list,\
    py_list_to_tcl_list

if platform == 'win32':
    pkgIndex_tail = 'TclScripts/lib/IxTclNetwork/pkgIndex.tcl'
else:
    pkgIndex_tail = 'lib/IxTclNetwork/pkgIndex.tcl'


class IxnTclWrapper(TgnTclWrapper):

    def __init__(self, logger, ixn_install_dir, tcl_interp=None):
        super(IxnTclWrapper, self).__init__(logger, tcl_interp)
        self.source(path.join(ixn_install_dir, pkgIndex_tail))
        self.eval('package require IxTclNetwork')

    def ixnCommand(self, command, *arguments):
        return self.eval('ixNet ' + command + ' ' + ' '.join(arguments))

    #
    # IxNetwork built in commands ordered alphabetically.
    #

    def commit(self):
        return self.ixnCommand('commit')

    def connect(self, ip, port):
        return self.ixnCommand('connect ' + ip + ' -port ' + str(port) + ' -version ' + self.getVersion())

    def execute(self, command, *arguments):
        return self.ixnCommand('exec ' + command, *arguments)

    def getList(self, objRef, childList):
        children_list = self.ixnCommand('getList', objRef, childList)
        return tcl_list_2_py_list(children_list)

    def getAttribute(self, objRef, attribute):
        """ Get current value of the requested attribute. """
        return self.ixnCommand('getAttribute', tcl_str(objRef), '-' + attribute)

    def getListAttribute(self, objRef, attribute):
        value = tcl_list_2_py_list(self.getAttribute(objRef, attribute))
        # Is there better way to determine that we have list of lists?
        return value if value[0][0] != '{' else [tcl_list_2_py_list(v[1:-1]) for v in value]

    def help(self, objRef):
        output = self.ixnCommand('help', objRef)
        children = None
        if 'Child Lists:' in output:
            children = output.split('Child Lists:')[1].split('Attributes:')[0].split('Execs:')[0]
            children_list = [c.strip().split()[0] for c in children.strip().split('\n')]
        attributes = None
        if 'Attributes:' in output:
            attributes = output.split('Attributes:')[1].split('Execs:')[0]
            attributes_list = [a.strip().split()[0][1:] for a in attributes.strip().split('\n')]
        execs = None
        if 'Execs:':
            execs = output.split('Execs:')[1]
            execs_list = [e.strip().split()[0] for e in execs.strip().split('\n')]
        return children_list, attributes_list, execs_list

    def getRoot(self):
        return self.ixnCommand('getRoot')

    def getVersion(self):
        return self.ixnCommand('getVersion')

    def loadConfig(self, configFileName):
        self.execute('loadConfig', self.ixnCommand('readFrom', tcl_file_name(configFileName)))

    def saveConfig(self, configFileName):
        self.execute('saveConfig', self.ixnCommand('writeTo', tcl_file_name(configFileName)))

    def newConfig(self):
        self.execute('newConfig')

    def setAttributes(self, objRef, **attributes):
        string_attributes = {}
        for attribute, value in attributes.items():
            string_attributes[attribute] = py_list_to_tcl_list(value) if type(value) is list else value
        self.ixnCommand('setMultiAttribute', tcl_str(objRef), get_args_pairs(string_attributes))

    def add(self, parent, obj_type, **attributes):
        """ IXN API add command

        @param parent: object parent - object will be created under this parent.
        @param object_type: object type.
        @param attributes: additional attributes.
        @return: IXN object reference.
        """
        return self.ixnCommand('add', parent.obj_ref(), obj_type, get_args_pairs(attributes))

    def remove(self, objRef):
        """ IXN API remove command

        @param objRef: object reference to remove.
        """
        self.ixnCommand('remove', objRef)

    def remapIds(self, objRef):
        return self.eval('lindex [ixNet remapIds ' + objRef + '] 0')

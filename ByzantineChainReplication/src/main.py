# -*- generated by 1.0.11 -*-
import da
_config_object = {}
import sys
import nacl.encoding
import nacl.hash
import nacl.signing
from nacl.bindings.utils import sodium_memcmp
from re import split
import time
import logging
Olympus = da.import_da('Olympus')
Parent = da.import_da('Parent')
Client = da.import_da('Client')
Replica = da.import_da('Replica')

class Node_(da.NodeProcess):

    def __init__(self, procimpl, props):
        super().__init__(procimpl, props)
        self._events.extend([])
    _config_object = {'channel': {'reliable', 'fifo'}}

    def run(self):
        config = dict()
        r = list()
        failure = dict()
        with open(sys.argv[(- 1)], 'r') as f:
            for line in f:
                if (not (line[0] == '#')):
                    (key, sep, val) = line.partition('=')
                    if (not (len(sep) == 0)):
                        val = val.strip()
                        config[key.strip()] = (int(val) if str.isdecimal(val) else val)
        logging.basicConfig(format='%(asctime)s : %(message)s', level=logging.INFO, filename=(sys.argv[(- 1)][0:(- 4)] + '_log.log'))
        num_replica = config['t']
        num_replica = ((num_replica * 2) + 1)
        num_client = config['num_client']
        c = list(self.new(Client.CL, num=num_client, at='ClientNode'))
        r1 = list(self.new(Replica.replica, num=2, at='ReplicaNode1'))
        r2 = list(self.new(Replica.replica, num=(num_replica - 2), at='ReplicaNode2'))
        r = (r1 + r2)
        olympus = list(self.new(Olympus.Olympus, num=1, at='OlympusNode'))
        parent = list(self.new(Parent.Parent, num=1))
        self._setup(olympus, (config, c, r, parent, olympus, num_replica))
        self._start(olympus)
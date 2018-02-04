# -*- generated by 1.0.11 -*-
import da
PatternExpr_241 = da.pat.TuplePattern([da.pat.ConstantPattern('finish'), da.pat.FreePattern('client_res')])
PatternExpr_248 = da.pat.FreePattern('client')
PatternExpr_300 = da.pat.TuplePattern([da.pat.ConstantPattern('parent-trans'), da.pat.FreePattern('encrypt_oper'), da.pat.FreePattern('encrypt_rid')])
PatternExpr_309 = da.pat.FreePattern('client')
_config_object = {}
import sys
import nacl.encoding
import nacl.hash
import nacl.signing
from nacl.bindings.utils import sodium_memcmp
from re import split
import time
import logging

class Parent(da.DistProcess):

    def __init__(self, procimpl, props):
        super().__init__(procimpl, props)
        self._events.extend([da.pat.EventPattern(da.pat.ReceivedEvent, '_ParentReceivedEvent_0', PatternExpr_241, sources=[PatternExpr_248], destinations=None, timestamps=None, record_history=None, handlers=[self._Parent_handler_240]), da.pat.EventPattern(da.pat.ReceivedEvent, '_ParentReceivedEvent_1', PatternExpr_300, sources=[PatternExpr_309], destinations=None, timestamps=None, record_history=None, handlers=[self._Parent_handler_299])])

    def setup(self, c, public_key_dict, pk, **rest_486):
        super().setup(c=c, public_key_dict=public_key_dict, pk=pk, **rest_486)
        self._state.c = c
        self._state.public_key_dict = public_key_dict
        self._state.pk = pk
        self._state.d = dict()
        self._state.result = dict()
        self._state.res = ''

    def run(self):
        logging.basicConfig(format='%(asctime)s : %(message)s', level=logging.INFO, filename=(sys.argv[(- 1)][0:(- 4)] + '_log.log'))
        self._state.res = ''
        super()._label('_st_label_236', block=False)
        _st_label_236 = 0
        while (_st_label_236 == 0):
            _st_label_236 += 1
            if False:
                _st_label_236 += 1
            else:
                super()._label('_st_label_236', block=True)
                _st_label_236 -= 1

    def _Parent_handler_240(self, client_res, client):
        if (not (self._state.result[client] == client_res)):
            self.output('result check failed')
            logging.error(((((('Parent Client : Final Results check failed for Client : ' + str(self._state.c.index(client))) + ' parent res ') + str(self._state.result[client])) + ' client res ') + str(client_res)))
        else:
            logging.info(('Parent Client : Final Results check passed for Client : ' + str(self._state.c.index(client))))
    _Parent_handler_240._labels = None
    _Parent_handler_240._notlabels = None

    def _Parent_handler_299(self, encrypt_oper, encrypt_rid, client):
        cl_parent_dkey = nacl.signing.VerifyKey(self._state.public_key_dict[client], encoder=nacl.encoding.HexEncoder)
        try:
            cl_parent_dkey.verify(encrypt_oper)
        except nacl.exceptions.BadSignatureError:
            self.output('fr-r decrypt fail')
        oper = encrypt_oper.message.decode()
        x = split("[,()']+", oper)
        if (x[0] == 'put'):
            self._state.d[x[1]] = x[2]
            self._state.res = 'ok'
        if (x[0] == 'get'):
            try:
                self._state.res = self._state.d[x[1]]
            except KeyError:
                self._state.res = ''
        if (x[0] == 'append'):
            try:
                self._state.d[x[1]] = (self._state.d[x[1]] + x[2])
                self._state.res = 'update ok'
            except KeyError:
                self._state.res = 'update failed'
        if (x[0] == 'slice'):
            x[2] = x[2].split(':')
            try:
                self._state.d[x[1]] = self._state.d[x[1]][int(x[2][0]):int(x[2][1])]
                self._state.res = 'slice ok'
            except KeyError:
                self._state.res = 'slice fail'
        try:
            self._state.result[client].append(self._state.res)
        except KeyError:
            self._state.result[client] = [self._state.res]
    _Parent_handler_299._labels = None
    _Parent_handler_299._notlabels = None
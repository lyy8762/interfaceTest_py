# -*- coding: utf-8 -*-

#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#

import sys, glob
from thrift.protocol.TMultiplexedProtocol import TMultiplexedProtocol
sys.path.append('gen-py')
# sys.path.insert(0, glob.glob('../../lib/py/build/lib.*')[0])

from cn.jsfund.trading.quotation.module.realtime import RealTimeQuotationService
from cn.jsfund.trading.quotation.module.realtime.ttypes import *
from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TCompactProtocol

transport = TSocket.TSocket('121.40.156.222', 9090)
transport = TTransport.TBufferedTransport(transport)
protocol = TCompactProtocol.TCompactProtocol(transport)
p = TMultiplexedProtocol(protocol, "RealTimeQuotationService")

  # Create a client to use the protocol encoder
client = RealTimeQuotationService.Client(p)

transport.open()
# quote = client.getSimpleQuotations('002441.SZ')
quote = client.getSimpleQuotations('018001.SH')

print quote
# print client.getSimpleQuotations('601918.SH')
print client.getSimpleQuotations('002131.SZ')

print client.getSimpleQuotations('601918.SH')
print client.getSimpleQuotations('600023.SH')

quote = client.getSimpleQuotations('399006.SZ')
print quote 
print client.getSimpleQuotations('000001.SH')


  # Close!
transport.close()
  
# except Thrift.TException, tx:
#   print '%s' % (tx.message)

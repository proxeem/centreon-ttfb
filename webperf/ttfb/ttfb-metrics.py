#!/usr/bin/env python

#
# Copyright 2020 Proxeem (https://www.proxeem.fr/)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import argparse
import subprocess
import shlex


#
# HTTP request with external CURL command
#
def requestByCommand():

    curlURL = args.proto + '://' + args.hostname + args.urlpath
    curlCommand = subprocess.Popen(shlex.split(
        'curl -so /dev/null -m ' + args.timeout + ' -w "%{http_code}|%{time_namelookup}|%{time_connect}|%{time_appconnect}|%{time_pretransfer}|%{time_starttransfer}|%{time_total}" ' + curlURL),
        stdout = subprocess.PIPE)
    curlOutput, curlError = curlCommand.communicate()

    if args.debug:
        print curlOutput

    curlValues = curlOutput.replace(',', '.').split('|')

    return {
        'http_code': int(curlValues[0]),
        'time_namelookup': int(round(float(curlValues[1]) * 1000)),
        'time_connect': int(round(float(curlValues[2]) * 1000)),
        'time_appconnect': int(round(float(curlValues[3]) * 1000)),
        'time_pretransfer': int(round(float(curlValues[4]) * 1000)),
        'time_starttransfer': int(round(float(curlValues[5]) * 1000)),
        'time_total': int(round(float(curlValues[6]) * 1000))
    }


# Parse command line
parser = argparse.ArgumentParser(description = 'TTFB Waterfall plugin for Centreon')
parser.add_argument('-d', '--debug', help = 'Output debug information (do not use with Centreon)', action = 'store_true')
parser.add_argument('--proto', help = 'Protocol', required=True)
parser.add_argument('--hostname', help = 'Hostname', required=True)
parser.add_argument('--urlpath', help = 'Relative URL', required=True)
parser.add_argument('--warning', help = 'Response time warning level (in ms)', default='600')
parser.add_argument('--critical', help = 'Response time critical level (in ms)', default='1200')
parser.add_argument('--timeout', help = 'Request timeout', default='30')
args = parser.parse_args()

if args.debug:
    print 'TTFB Waterfall plugin for Centreon'
    print 'Copyright 2020 Proxeem (https://www.proxeem.fr/)'
    print '---'
    print 'Analyzing ' + args.proto + '://' + args.hostname + args.urlpath
    print 'Timeout: ' + args.timeout + ', Warning: ' + args.warning + ', Critical: ' + args.critical
    print '---'

# Make HTTP Request
curlStats = requestByCommand()

if args.debug:
    # All values below are in ms
    # time_namelookup : The time it took from the start until the name resolving was completed
    # time_connect : The time it took from the start until the TCP connect to the remote host (or proxy) was completed
    # time_appconnect : The time it took from the start until the SSL/SSH/etc connect/handshake to the remote host was completed
    # time_pretransfer : The time it took from the start until the file transfer was just about to begin
    # time_starttransfer : The time it took from the start until the first byte was just about to be transferred
    # time_total : The total time that the full operation lasted
    print curlStats

# Compute waterfall values
if 200 <= curlStats['http_code'] < 300:
    # HTTP Response code OK (2xx)
    wfDNSLookup = curlStats['time_namelookup']
    wfTCPConnection = curlStats['time_connect'] - curlStats['time_namelookup']
    wfTLSHandshake = (curlStats['time_appconnect'] - curlStats['time_connect']) if (args.proto == 'https') else 0
    wfApplicationBackend = curlStats['time_starttransfer'] - curlStats['time_pretransfer']
    wfDataTransfert = curlStats['time_total'] - curlStats['time_starttransfer']

    # Centreon status & Performance datas
    if wfApplicationBackend < int(args.warning):
        centreonStatusMessage = 'OK'
        centreonStatusCode = 0

    elif wfApplicationBackend < int(args.critical):
        centreonStatusMessage = 'WARNING'
        centreonStatusCode = 1

    else:
        centreonStatusMessage = 'CRITICAL'
        centreonStatusCode = 2

    centreonStatusMessage += ': [' + str(curlStats['http_code']) + '] Response time: ' + str(wfApplicationBackend) + ' ms | '
    centreonStatusMessage += "'ttfb_dns'=" + str(wfDNSLookup) + 'ms '
    centreonStatusMessage += "'ttfb_tcp'=" + str(wfTCPConnection) + 'ms '
    centreonStatusMessage += "'ttfb_tls'=" + str(wfTLSHandshake) + 'ms '
    centreonStatusMessage += "'ttfb_backend'=" + str(wfApplicationBackend) + 'ms '
    centreonStatusMessage += "'ttfb_data'=" + str(wfDataTransfert) + 'ms'

else:
    # HTTP Response code KO (3xx, 4xx, 5xx or curl error)
    wfDNSLookup, wfTCPConnection, wfTLSHandshake, wfApplicationBackend, wfDataTransfert = 0, 0, 0, 0, 0
    centreonStatusMessage = 'UNKNOWN: [' + str(curlStats['http_code']) + '] Invalid response code'
    centreonStatusCode = 3

if args.debug:
    print '---'
    print 'DNS Lookup          : ' + str(wfDNSLookup) + ' ms'
    print 'TCP Connection      : ' + str(wfTCPConnection) + ' ms'
    print 'TLS Handshake       : ' + str(wfTLSHandshake) + ' ms'
    print 'Application Backend : ' + str(wfApplicationBackend) + ' ms'
    print 'Data Transfert      : ' + str(wfDataTransfert) + ' ms'
    print '---'

# Output Centreon datas
print centreonStatusMessage
exit(centreonStatusCode)
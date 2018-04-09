#!/usr/bin/python

# ver 0.0.0
# script to get a list of virtual IPs on a big-ip


from f5.bigip import ManagementRoot
import optparse
import sys
from pprint import pprint
import random
import time

# disable insuecure warnings
import requests
requests.packages.urllib3.disable_warnings()


parser = optparse.OptionParser()

parser.add_option(
    '-d',
    '--debug',
    dest="debug",
    default=False,
    action="store_true",
    help="Print out arg values given"
    )

parser.add_option(
    '-u',
    '--user',
    dest="remUser",
    default='admin',
    action="store",
    help="Remote user name"
    )

parser.add_option(
    '-p',
    '--pass',
    dest="remPass",
    default='admin',
    action="store",
    help="Remote user name"
    )

parser.add_option(
    '-a',
    '--address',
    dest="address",
    action="store",
    help="address of remote device"
    )

parser.add_option(
    '-n',
    '--name',
    dest="namePrefix",
    action="store",
    help="global name prefix for the opbject group being created"
    )

parser.add_option(
    '-t',
    '--target',
    dest="target",
    default="x.x.x.x",
    action="store",
    help="address that will be used in example if -e is used"
    )

parser.add_option(
    '-v',
    '--vs',
    dest="vsAddress",
    action="store",
    help="address that will be used for Virtual server destination"
    )


parser.add_option(
    '-r',
    '--remove',
    dest="removeAfterSeconds",
    action="store",
    help="Take arg of second and will remove objects created after sleeping for n seconds, if not present will not remove"
    )


#print(parser.parse_args())

options, remainder = parser.parse_args()

# check for needed opts
if not options.address: # if -a not give
    parser.error('IP address/host not given')

#if not options.namePrefix: # if -n not given
#    parser.error('-n is required')

#if not options.vsAddress: # is no virtual server dest given
#    parser.error('-v is required')


# Connect to the BIG-IP
mgmt = ManagementRoot(options.address, options.remUser, options.remPass)


virtualAddresses = mgmt.tm.ltm.virtual_address_s.get_collection()
#print type(virtualAddresses)
#print virtualAddresses
#pprint(dir(virtualAddresses[0]))
#print virtualAddresses[0].address

virt_list = []
for v in virtualAddresses:
    virt_list.append(v.address.encode('ascii'))

print virt_list




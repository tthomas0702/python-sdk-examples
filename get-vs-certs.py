#!/usr/bin/python


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



#print(parser.parse_args())

options, remainder = parser.parse_args()

# check for needed opts
if not options.address: # if -a not give
    parser.error('IP address/host not given')

#if not options.namePrefix: # if -n not given
#    parser.error('-n is required')

# Connect to the BIG-IP
mgmt = ManagementRoot(options.address, options.remUser, options.remPass)



### get list of virtuals ###
vsList = mgmt.tm.ltm.virtuals.get_collection()
#for v in vsList:
#    print v.name
print "There are ", len(vsList) , " Virtual Servers"


### get list of ssl keys ###
keys = mgmt.tm.sys.file.ssl_keys.get_collection()
#print(type(keys1))
#for key in keys:
#    print key.name
print "There are ", len(keys) , " SSL keys"

### get certs ###
certs = mgmt.tm.sys.file.ssl_certs.get_collection()
#for cert in certs:
#    print cert.name
print "There are ", len(certs) , " SSL certs"


#cert1 = mgmt.tm.sys.file.ssl_certs.ssl_cert.create(name= certName, partition='Common', sourcePath='file:/var/tmp/fake1_1.crt')


























#!/usr/bin/python

# make 1000 vs using list of IP fr pool members
# ver 0.0.1


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

if not options.namePrefix: # if -n not given
    parser.error('-n is required')

if not options.vsAddress: # is no virtual server dest given
    parser.error('-v is required')


# Connect to the BIG-IP
mgmt = ManagementRoot(options.address, options.remUser, options.remPass)


#create a pool

def makePool(poolName, port, mon, part, pm1, pm2):
    mgmt.tm.ltm.pools.pool.create(name = poolName, partition=part, monitor=mon)

    # Define a pool object and load an existing pool
    poolObj = mgmt.tm.ltm.pools.pool.load(partition=part, name= poolName )
    poolObj.description = "This is " + poolName
    poolObj.update()
    

    # Create members on poolObj
    members = poolObj.members_s
    member = poolObj.members_s.members

    m1 = poolObj.members_s.members.create(partition=part, name= pm1)
    m2 = poolObj.members_s.members.create(partition=part, name= pm2)


    return poolObj


# make list node for pool from test file tha contains list
nodes = open('data_webfarm/pool_member_ip_list', 'r').read()
nodeList = eval(nodes)

#### Make Pool ####
pname = 0
it = iter(nodeList)
for x in it:
    port = '80'
    pm1 = x + ':' + port
    pm2 = next(it) + ':' + port
    pname += 1
    #call makePool for port 80 pool
    poolName = "p_" + str(pname)
    mon = 'tcp'
    part = 'Common'
    poolObj80 = makePool(poolName, port, mon, part, pm1, pm2)


# This will makd bunch of pool
# next need to make VS that will use Pools



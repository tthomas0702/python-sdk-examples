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

if not options.namePrefix: # if -n not given
    parser.error('-n is required')

# Connect to the BIG-IP
mgmt = ManagementRoot(options.address, options.remUser, options.remPass)




#### make rules , lots of them ##

# make list of names
iruleName1 = options.namePrefix + "_irule"
ruleNameList = []    # This will be used to delete as well
# set number of rules to make
for i in range(1,50):
    ruleNameList.append(iruleName1 + str(i))
# open on test file that has the irule code I will use
iruleCode = open('zaleski_include/irule1.txt', 'r').read()

# create rules
for ruleName in ruleNameList:
    irule1 = mgmt.tm.ltm.rules.rule.create(name= ruleName, partition = 'Common', apiAnonymous= iruleCode)

# cleanup irule example
#time.sleep(20)
#for ruleName in ruleNameList:
#    delRule = mgmt.tm.ltm.rules.rule.load(name= ruleName, partition = 'Common')
#    delRule.delete()









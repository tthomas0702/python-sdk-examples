#!/usr/bin/python

# script to create a lab webfarm on a BIG-IP using irules
# may be specific for tha iqlab to test statiscs
# I am not trying to make flexible to used in other circumstances
# ver 0.0.0


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



#### make certs for profile ####

keyName = options.namePrefix + "_key"
certName = options.namePrefix + "_cert"
# here is how to do it when file is on BIG-IP
#key1 = mgmt.tm.sys.file.ssl_keys.ssl_key.create(name= keyName, partition='Common', sourcePath='file:/var/tmp/fake1_1.key')
#cert1 = mgmt.tm.sys.file.ssl_certs.ssl_cert.create(name= certName, partition='Common', sourcePath='file:/var/tmp/fake1_1.crt')
# Here is how to use certs on web server
key1 = mgmt.tm.sys.file.ssl_keys.ssl_key.create(name= keyName, partition='Common', sourcePath='http://10.1.212.8/fake1_1.key')
cert1 = mgmt.tm.sys.file.ssl_certs.ssl_cert.create(name= certName, partition='Common', sourcePath='http://10.1.212.8/fake1_1.crt')

#### make client-ssl profile ####

sslProfileClientsideName1 = options.namePrefix + "_client_ssl_profile"
clientSslProfile1 = mgmt.tm.ltm.profile.client_ssls.client_ssl.create(name= sslProfileClientsideName1 , partition='Common', ciphers= 'DEFAULT:!RSA', cert= certName, key= keyName)



#### make http profile ####

httpProfileName = options.namePrefix + "_http_profile"
httpProfile = mgmt.tm.ltm.profile.https.http.create(name= httpProfileName )
httpProfile = mgmt.tm.ltm.profile.https.http.load(name= httpProfileName)
httpProfile.enforcement = { 'maxHeaderCount' : '60', 'maxHeaderSize' : '3200'}
httpProfile.insertXforwardedFor = 'enabled'
httpProfile.update()


# make irule
iruleName1 = options.namePrefix + "_irule"

# open on text file that has the irule code I will use
iruleCode = open('data_webfarm/webfarm_irule1.txt', 'r').read()


# create rules
irule1 = mgmt.tm.ltm.rules.rule.create(name= iruleName1, partition = 'Common', apiAnonymous= iruleCode)


#### make virutals ####
# port 80 
destAndPort80 = options.vsAddress + ':80'
virtName = options.namePrefix + "_vs"
print "creating VS ", virtName
vip80 = mgmt.tm.ltm.virtuals.virtual.create(
    name= virtName, 
    partition='Common', 
    type= 'Standard', 
    destination= destAndPort80,
    mask= '255.255.255.255',
    ipProtocol= 'tcp',    
    sourceAddressTranslation= {'type':'automap'},
    #pool= poolObj80.fullPath

)

# now add some stuff to the virtual above
vip80 = mgmt.tm.ltm.virtuals.virtual.load(name= virtName)
vip80.profiles = [
        {'name' : httpProfileName,'context': 'all', "partition": "Common"}, 
        {'name' : 'oneconnect', 'context': 'all', 'partition': 'Common'},
        {'name' : 'tcp-wan-optimized', 'context': 'clientside', 'partition': 'Common'},
        {'name' : 'tcp-lan-optimized', 'context': 'serverside', 'partition': 'Common'}        
    ]
vip80.persist = ['cookie']
vip80.fallbackPersistence = '/Common/source_addr'
vip80.rules = [iruleName1]
vip80.update()


# port 443
destAndPort443 = options.vsAddress + ':443'
virtName443 = options.namePrefix + "_vs_443"
print "creating VS ", virtName443
vip443 = mgmt.tm.ltm.virtuals.virtual.create(
    name= virtName443,
    partition='Common',
    type= 'Standard',
    destination= destAndPort443,
    mask= '255.255.255.255',
    ipProtocol= 'tcp',
    sourceAddressTranslation= {'type':'automap'},
    #pool= poolObj443.fullPath

)

# now add some stuff to the virtual above
vip443 = mgmt.tm.ltm.virtuals.virtual.load(name= virtName443)
vip443.profiles = [
        {'name' : httpProfileName,'context': 'all', "partition": "Common"},
        {'name' : 'oneconnect', 'context': 'all', 'partition': 'Common'},
        {'name' : 'tcp-wan-optimized', 'context': 'clientside', 'partition': 'Common'},
        {'name' : 'tcp-lan-optimized', 'context': 'serverside', 'partition': 'Common'},
        {'name' : sslProfileClientsideName1, 'context': 'clientside', 'partition': 'Common'},
        {'name' : 'serverssl', 'context': 'serverside', 'partition': 'Common'}
    ]
vip443.persist = ['cookie']
vip443.fallbackPersistence = '/Common/source_addr'
vip443.rules = [iruleName1 ]
vip443.update()





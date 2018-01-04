#!/usr/bin/python

from f5.bigip import ManagementRoot
import optparse

# disable insecure warnings
import requests
requests.packages.urllib3.disable_warnings()

parser = optparse.OptionParser(usage='%prog -a <BIG-IP IP>' )
parser.add_option(
    '-u', '--user',
    dest="remUser",
    default='admin',
    action="store",
    help="Remote user name"
    )

parser.add_option(
    '-p', '--pass',
    dest="remPass",
    default='admin',
    action="store",
    help="Remote user name"
    )

parser.add_option(
    '-a', '--address',
    dest="address",
    action="store",
    help="address of remote BIG-IP device"
    )

options, remainder = parser.parse_args()

# check for needed opts
if not options.address:  # if -a not give
    parser.error('IP address/host not given')

# Connect to the BIG-IP
mgmt = ManagementRoot(options.address, options.remUser, options.remPass)

# create global_settings collection object and print hostname property
globalSettings = mgmt.tm.sys.global_settings.load()
print globalSettings.hostname

# get and print provision information
provisionCollection = mgmt.tm.sys.provision.get_collection()
print "\nProvisioning:\n-------------"
for module in provisionCollection:
    if module['level'] == 'none':
        pass
    else:
        print '{}\t{}'.format(module['name'], module['level'])

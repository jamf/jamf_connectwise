#! /usr/local/bin/python

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#
# Copyright (c) 2017 Jamf.  All rights reserved.
#
#       Redistribution and use in source and binary forms, with or without
#       modification, are permitted provided that the following conditions are met:
#               * Redistributions of source code must retain the above copyright
#                 notice, this list of conditions and the following disclaimer.
#               * Redistributions in binary form must reproduce the above copyright
#                 notice, this list of conditions and the following disclaimer in the
#                 documentation and/or other materials provided with the distribution.
#               * Neither the name of the Jamf nor the names of its contributors may be
#                 used to endorse or promote products derived from this software without 
#                 specific prior written permission.
#
#       THIS SOFTWARE IS PROVIDED BY JAMF SOFTWARE, LLC "AS IS" AND ANY
#       EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#       WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#       DISCLAIMED. IN NO EVENT SHALL JAMF SOFTWARE, LLC BE LIABLE FOR ANY
#       DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#       (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#       LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#       ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#       (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#       SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# 
# This script can be attached to a policy in Jamf Pro that will update a field in 
# ConnectWise.
# For instance, this script, when attached to a policy that is set to remove licensed 
# software/framework from a client machine, can trigger settings of that device found in 
# the ConnectWise database entry for that client machine to be adjusted.  In this case, 
# sets the ConnectWise configuration to "inactive" and changes the SLA to "No  SLA" 
#
# REQUIREMENTS:
#                       - Jamf Pro
#                       - ConnectWise
#
#
# Written by: Jonathan Yuresko | Professional Services Engineer | Jamf
#
# Created On: June 8, 2017
# 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

import urllib
import urllib2
import json
from time import sleep
import codecs
import subprocess
import os

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# VARIABLES
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

# Your ConnectWise URL
cw_url = "na.myconnectwise.net"

# Your ConnectWise API Key
cw_api_key = "<CONNECTWISE_API_KEY>"

###############################################
###############################################

# Finds serial number of client computer
get_serial = subprocess.check_output("system_profiler SPHardwareDataType | awk '/Serial/ {print $4}'", shell=True)
serial_number = get_serial.rstrip()

# Finds computer name of client computer
get_computer_name = subprocess.check_output("scutil --get ComputerName", shell=True)
computer_name = get_computer_name.rstrip()

# Determines if client comptuer is "Server" or "Workstation"
computer_type = os.path.isdir('/Applications/Server.app')
if computer_type is True:
	machine = "Server"
else:
	machine = "Workstation"

# Prints computer data 
print 'New computer name = {}'.format(computer_name)
print 'Serial Number = {}'.format(serial_number)
print 'Computer Type = {}'.format(machine)

# Begins finding ConnectWise ID
full_cw_url = "https://api-" + cw_url  + "/v4_6_release/apis/3.0/company/configurations/?conditions=type/name='BTITS%20-%20" + machine + "'%20and%20SerialNumber='" + serial_number + "'"
request = urllib2.Request(full_cw_url)
request.add_header('Content-Type', 'application/json')
request.add_header('Authorization', 'Basic ' + cw_api_key)

response = urllib2.urlopen(request)
response_json = json.load(response)
cw_id = response_json[0]['id']

# ConnectWise ID
print "ConnectWise ID = {}".format(cw_id)

# Begins the deactivation (set to "Inactive", and "No  SLA")
update_cw_url = "https://api-" + cw_url  + "/v4_6_release/apis/3.0/company/configurations/{}".format(cw_id)

# Updating parameters
post_params=[{
   "op": "replace",
   "path": "name",
   "value": "{}".format(computer_name)
   }]

params = json.dumps(post_params)

request = urllib2.Request(update_cw_url)
request.get_method = lambda: 'PATCH'
request.add_header('Content-Type', 'application/json')
request.add_header('Authorization', 'Basic ' + cw_api_key)
resp = urllib2.urlopen(request, params)

print resp

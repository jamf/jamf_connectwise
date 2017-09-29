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
# This script allows syncing of information from Jamf Pro to ConnectWise.
# For instance, this script can run once a night for newly enrolled machines in Jamf and  
# port them to the ConnectWise database.  This can be based on a group membership for newly  
# enrolled machines into Jamf Pro.
#
# REQUIREMENTS:
#                       - Requests python module on server/host machine
#                       - Jamf Pro with Smart Group of computers to port
#                       - ConnectWise
#
#
# Written by: Jonathan Yuresko | Professional Services Engineer | Jamf
#
# Created On: June 8, 2017
# 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

import json
from time import sleep
import requests
import codecs

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
# VARIABLES
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

# Your JSS information, Fill it in
# Full JSS url: https://jss.yourcompany.com/JSSResource
jss_url = '<JSS_URL>'
jss_username = '<JSS_USERNAME>'
jss_password = '<JSS_PASSWORD'

# Endpoint of smart group.  
# If contains spaces, use %20 for the space: /computergroups/name/All%20Computers
get_ids_endpoint = '/computergroups/name/All'

# Your ConnectWise URL
cw_url = "na.myconnectwise.net"

# Your ConnectWise API Key
cw_api_key = "<CONNECTWISE_API_KEY>"

###############################################
###############################################

# Gets list of configuration profile ids in JSS
print "Gathering active computer IDs from the Smart Group..."
get_ids_request = requests.get(jss_url + get_ids_endpoint,
	auth=(jss_username, jss_password),
	headers={'Accept': 'application/json'}
	)

response_json = json.loads(get_ids_request.text)

x = 0
id_list = []
while True:
	try:
		id_list.append(response_json['computer_group']['computers'][x]['id'])
		x += 1
		str_error = None
	except Exception as str_error:
		pass
	if str_error:
		sleep(2)
		break
	else:
		continue

print 'Found computers with ids: {}'.format(id_list)

# Gets computer information based on gathered IDs
for id_number in id_list:
	print "Gathering computer information for id: {}".format(id_number)
	get_info = '/computers/id/{}'.format(id_number)
	get_info_request = requests.get(jss_url + get_info,
		auth=(jss_username, jss_password),
		headers={'Accept': 'application/json'}
		)

	response_json = json.loads(get_info_request.text)

	# Variables from Jamf to be submitted to ConnectWise
	serial_number = response_json['computer']['general']['serial_number']
	computer_name = response_json['computer']['general']['name']
	encoded_computer_name = computer_name.encode('utf-8')
	site = response_json['computer']['general']['site']['name']
	username = response_json['computer']['location']['username']
	model = response_json['computer']['hardware']['model_identifier']
	warranty_expire = response_json['computer']['purchasing']['warranty_expires_utc']
	server_check = response_json['computer']['software']['applications']
	formatted_server_check = json.dumps(server_check)
	if "Server.app" in formatted_server_check: 
		computer_type = "BTITS - Server"
	else:
		computer_type = "BTITS - Workstation"

	# Prints data to logs found in Jamf
	print 'Computer ID {} information:'.format(id_number)
	print 'Computer is a {}'.format(computer_type)
	print 'Serial Number = {}'.format(serial_number)
	print 'Site = {}'.format(site)
	print 'Username = {}'.format(username)
	print 'Model = {}'.format(model)
	print 'Warranty Expires = {}'.format(warranty_expire)
	print 'Computer Name = {}'.format(encoded_computer_name)
	print ''

	# Combined Connectwise URL
	full_cw_url = "https://api-" + cw_url  + "/v4_6_release/apis/3.0/company/configurations".format(cw_url)

	cw_computer_name = "Mac - {} - {}".format(username, encoded_computer_name)
	cw_warranty_expire = warranty_expire.split(".")[0] + "Z"

	# Data gathered and formatted from Jamf
	mydata={

	   "name": "{}".format(cw_computer_name),
	   "type": {
	       "id": None,
	       "name": "{}".format(computer_type),
	       "_info": {}
	   },
	   "company": {
	       "id": None,
	       "identifier": "{}".format(site),
	       "name": None,
	       "_info": {}
	   },
	   "manufacturer": {
	       "id": None,
	       "name": "Apple Inc.",
	       "_info": {}
	   },
	   "warrantyExpirationDate": "{}".format(cw_warranty_expire),
	   "modelNumber": "{}".format(model),
	   "serialNumber": "{}".format(serial_number),
	   "sla": {
	       "id": None,
	       "name": "MSA SLA",
	       "_info": {} 
	   }

	}

	# Does the posting of the data from Jamf to ConnectWise
	r = requests.post(full_cw_url, headers={

	   'Authorization': 'Basic {}'.format(cw_api_key),
	   'Content-Type': 'application/json'},
	   data = json.dumps(mydata)
	)

	# Code 201 means successful posting to ConnectWise
	print r.status_code
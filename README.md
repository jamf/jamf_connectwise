# jamf_connectwise
## An integration between ConnectWise and Jamf Pro

This project currently consists of 3 python scripts that automate the integration between Connectwise and Jamf Pro.

# cw_bulk_new_enrollment.py
This script allows syncing of information from Jamf Pro to ConnectWise.
For instance, this script can run once a night for newly enrolled machines in Jamf and  
port them to the ConnectWise database.  This can be based on a group membership for newly  
enrolled machines into Jamf Pro.

## REQUIREMENTS:
- Requests python module on server/host machine
- Jamf Pro with Smart Group of computers to port
- A valid ConnectWise API Key

# cw_deactivate.py
This script can be attached to a policy in Jamf Pro that will update a field in ConnectWise.
For instance, this script, when attached to a policy that is set to remove licensed 
software/framework from a client machine, can trigger settings of that device found in 
the ConnectWise database entry for that client machine to be adjusted.  In this case, 
sets the ConnectWise configuration to "inactive" and changes the SLA to "No  SLA" 

## REQUIREMENTS:
- Jamf Pro
- ConnectWise

# cw_rename_computer.py
This script can be attached to a policy in Jamf Pro that will update a field in ConnectWise.
For instance, this script, when attached to a policy that is set to remove licensed 
software/framework from a client machine, can trigger settings of that device found in 
the ConnectWise database entry for that client machine to be adjusted.  In this case, 
sets the ConnectWise configuration to "inactive" and changes the SLA to "No  SLA" 

## REQUIREMENTS:
- Jamf Pro
- ConnectWise

V2 Plugins
-----------

  v2/                                                                                                                                                                                                                                      
  ├── eltek_checks/agent_based/     (6 files)                                                                                                                                                                                              
  ├── narada_checks/agent_based/    (1 file)                                                                                                                                                                                               
  ├── edfamux_checks/agent_based/   (5 files)                                                                                                                                                                                              
  └── kea_checks/agent_based/       (1 file)                                                                                                                                                                                               
                                                                                                                                                                                                                                           
  Changes Applied to All v1 Plugins (12 files)                                                                                                                                                                                             
                                                                                                                                                                                                                                           
  - Import: from .agent_based_api.v1 import register, ... → from cmk.agent_based.v2 import SNMPSection, CheckPlugin, ...                                                                                                                   
  - SNMP registration: register.snmp_section(...) → snmp_section_xxx = SNMPSection(...)                                                                                                                                                    
  - Check registration: register.check_plugin(...) → check_plugin_xxx = CheckPlugin(...)                                                                                                                                                   
  - Removed all debug print() statements                                                                                                                                                                                                   
                                                                                                                                                                                                                                           
  Merges                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                           
  - eltek_door.py + eltek_door_v2.py → single eltek_door.py using the business-hours-aware version                                                                                                                                         
                                                                                                                                                                                                                                           
  Bug Fixes                                                                                                                                                                                                                                
                                                                                                                                                                                                                                           
  - edfamux_check.py: Removed broken Metric yield referencing undefined battery_runtime variable
  - edfamux_light_old.py: Added missing from ctypes import pointer, c_int, cast, POINTER, c_float import
  - kea_check.py: Removed unused struct/datetime imports and print() statements

  Deployment

  Copy each family folder to your CheckMK site:
  # Example for eltek:
  cp -r v2/eltek_checks ~/local/lib/python3/cmk_addons/plugins/eltek_checks/
  # Repeat for narada_checks, edfamux_checks, kea_checks

  Then verify with:
  -----------------

  cmk -vI --detect-plugins=<plugin_name> <hostname>

  cmk --detect-plugins=<plugin_name> -v <hostname>

  cmk -R

##############################################################################################################


V1 Plugins
----------


# check_mk_plugins
CheckMK Plugins

## Login to CheckMK
```
ssh user@checkmk
sudo su
omd su monitoring
```

## Create a plugin
```
cd ~/local/lib/check_mk/base/plugins/agent_based
~/local/lib/check_mk/base/plugins/agent_based$ nano eltek_check.py
```

## SNMP Walk a Device (make sure SNMP is configured for that device)
```
time cmk -Iv eltek-palm
cmk -v --snmpwalk eltek-palm
cmk --snmptranslate eltek-palm > /tmp/eltek-palm-translated
less /omd/sites/monitoring/var/check_mk/snmpwalks/eltek-palm
less /tmp/eltek-palm-translated
```

## Try out the plugin
```
cmk -v --detect-plugins=eltek_check eltek-palm
cmk -vvII --detect-plugins=eltek_check eltek-palm
cmk -vvII --detect-plugins=eltek_door eltek-palm

# Test plugin on devices

cmk -nv JAX-ELTEK-FARIO-SP-03

# Restart core monitoring service
cmk -R

# Check device
cmk -IIv eltek-palm
```

# Develop the Plugin
```
Live edit on production! That is how we do it (for now anyway). In the future, we should consider setting up a staging version of Checkmk.

# Change to the plugin directory:
cd /omd/sites/monitoring/local/lib/check_mk/base/plugins/agent_based/

# See git status of repo
git status

# To add a new file to the repo:
echo "<file>" >> .git/info/sparse-checkout
git add <file>

# To commit your changes with a commit messages
git commit -a -m "<your messages>"

# To push your changes up to Github
git push

# Pull down latest from github (danger, this could overwrite local work)
git pull origin main
```

# About Git Sparse Checkout
```
We have configured Git Sparse Checkout on this machine so that it only checks out specified files to this directory and not everything. The repo contains other files that you can download and look at locally if you want.
```

#!/usr/bin/python3
########
##SCRIPT BY STEPHAN HAAK
########
import requests
import json
import time

##DISABLE SSL WARNING
requests.packages.urllib3.disable_warnings()

##ENTER GLOBAL VARIABLES
apic = 'ip.ip.ip.ip'
username = 'username'
password = 'password'
checkinterval = 15

##START LOOP 
while True:
  ##LOGIN, CREATE SESSION
  s = requests.Session()
  url_login = ('https://' + apic + '/api/aaaLogin.json')
  payload_login = {"aaaUser" : {"attributes" : {"name" : username , "pwd" : password} } }
  headers = {'content-type': 'application/json'}
  login_response = str(s.post(url_login, data=json.dumps(payload_login), headers=headers, verify=False).status_code)

  if login_response == '200':
    print('APIC Login OK. Proceeding...')
  else:
    print('APIC login failed. Exiting.')
    exit()

  ##GET VMM DOMAIN INFO 
  ##FIRST CHECK ALL STATUS
  while True:
    print('Searching domains...')
    time.sleep(0.5)
    req_vmm_all = 'https://' + apic + '/api/class/compCtrlr.json'
    data_on = s.get(req_vmm_all, verify=False).json()
    if data_on['totalCount'] != '0':
      for d in data_on['imdata']:
        print('VMM domain: {} found. State is {}'.format(d['compCtrlr']['attributes']['domName'],d['compCtrlr']['attributes']['operSt']))
      time.sleep(0.5)
      break
    else:
      print('No VMM domain found. Checking again after checkinterval.')
      time.sleep(checkinterval)   
  
  ##CHECK UNKNOWN STATUS
  req_vmm_unknown= 'https://' + apic + '/api/class/compCtrlr.json?query-target-filter=and(wcard(compCtrlr.operSt,"unknown"))'
  data_unk = s.get(req_vmm_unknown,verify=False).json()

  if data_unk['totalCount'] == "0":
    print('No VMM controllers with unknown state found')
    time.sleep(0.5)
  else:
    print('!WARNING! UNKOWN STATE VMM CONTROLLER: {} FOUND. CHECK CONFIG'.format(data_unk['imdata'][0]['compCtrlr']['attributes']['domName']))
    time.sleep(0.5)
    print('Checking for OFFLINE status...')

  #THEN CHECK OFFLINE STATUS 

  req_vmm_offline = 'https://' + apic + '/api/class/compCtrlr.json?query-target-filter=and(wcard(compCtrlr.operSt,"offline"))'
  data_off = s.get(req_vmm_offline, verify=False).json()

  if data_off['totalCount'] == "0":
    print('No VMM controllers with offline state found')
    time.sleep(0.5)
  else:
    print('!WARNING! OFFLINE VMM CONTROLLER {} FOUND!'.format(data_off['imdata'][0]['compCtrlr']['attributes']['domName']))

  time.sleep(checkinterval)
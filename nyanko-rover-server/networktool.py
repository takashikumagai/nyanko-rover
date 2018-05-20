#!/usr/bin/env python3

import subprocess
import re


def get_subnet():
  ip_and_subnetbits = get_ip_and_num_subnet_bits()
  if ip_and_subnetbits[1] == '24':
    octets = ip_and_subnetbits[0].split('.')
    if len(octets) == 4:
      return '{}.{}.{}'.format(octets[0],octets[1],octets[2])

def get_ip():
  ip_and_subnetbits = get_ip_and_num_subnet_bits()
  return ip_and_subnetbits[0]

def get_ip_and_num_subnet_bits():
  completed_process = subprocess.run(['ip','addr'], stdout=subprocess.PIPE)
  lines = completed_process.stdout.decode('utf-8').split('\n')
  found_network_adapter = False
  for line in lines:
    if 0 < len(line) and line[0].isdigit():
      if 0 <= line.find('LOOPBACK'):
        found_network_adapter = False
        continue
      else:
        # Assume we found either eth or wlan
        found_network_adapter = True
    
    elif found_network_adapter and line[0:9] == '    inet ':
      # Found an IPv4 address
      #print(line)
      words = re.split('\s+', line)
      words = [x for x in words if x] # Filter out empty strings (empty string are falsy)
      #print('words: {}'.format(words))
      if 2 <= len(words):
        ip_and_subnetbits = words[1].split('/')
        #print('ip & subnet bits: {}'.format(ip_and_subnetbits))
        if 1 < len(ip_and_subnetbits):
          return ip_and_subnetbits
        else:
          return ['x.x.x.x','0']
      return ['#.#.#.#','0']

  


# Returns the list of IP addresses
# '--send-ip' ensures that the arp table is populated.
# nmap with priviledged user does not fill the arp table unless '--send-ip' is specified.
def scan_with_nmap(subnet):
  ip_range = subnet + '.1-254'
  completed_process = subprocess.run(['nmap','--send-ip','-sP',ip_range], stdout=subprocess.PIPE)
  #print(completed_process.stdout)
  # completed_process.stdout is a bytes object so we first need to decode() it to UTF-8 string
  return completed_process.stdout.decode('utf-8').split('\n')


def get_connected_devices():
  scan_results = scan_with_nmap(get_subnet())
  ip_addresses = []
  for line in scan_results:
    #print(line)
    if line.startswith('Nmap scan report for'):
      ip = line[len('Nmap scan report for'):]
      ip_addresses.append(ip)
      #print(ip)

  #for ip in ip_addresses:
  #  completed_process = subprocess.run(['ping','-c','1',ip], stdout=subprocess.PIPE)
  
  #print('running arp')
  # Now the devices in the specified subnet have been pinged,
  # they should show up in the output of arp -a with their MAC addresses
  cp = subprocess.run(['arp','-a'], stdout=subprocess.PIPE)
  arp_results = cp.stdout.decode('utf-8').split('\n')
  #print('arp_results: ',arp_results)
  results = [x for x in arp_results if '<incomplete>' not in x]
  
  # results = []
  # for x in arp_results:
  #   try:
  #     if x.index('<incomplete>') >= 0:
  #       pass
  #   except:
  #     results.append(x)

  #print("filtered arp results: " + str(results))

  ip_at_mac = []
  for line in results:
    #print(line)
    m = re.search('\(.+\)\sat\s[0-9a-f:]+',line)
    #print(m)
    if not m:
      continue
    ip_at_mac.append(m.group(0))
  
  mac2ip = {}
  for item in ip_at_mac:
    words = item.split(' ')
    if len(words) == 3:
      mac2ip[words[2]] = words[0][1:-1]
  
  #print(mac2ip)
  return mac2ip


def get_ip_from_mac(mac_address):
  #print('MAC: ', mac_address)
  mac2ip = get_connected_devices()
  return mac2ip.get(mac_address.lower(),'')

def ip_from_mac(mac_address):
  ip_address = get_ip_from_mac(mac_address)
  print(ip_address)

def get_connected_network_ssid():
  cp = subprocess.run(['nmcli','-t','-f','active,ssid','dev','wifi'],stdout=subprocess.PIPE)
  lines = cp.stdout.decode('utf-8').split('\n')
  for line in lines:
    if line.find('yes:') == 0:
      #print(line[4:])
      return line[4:]


# \return Signal strength in the range [0,100]
def get_connected_network_signal_strength():
  cp = subprocess.run(['nmcli','-t','-f','active,signal','dev','wifi'],stdout=subprocess.PIPE)
  lines = cp.stdout.decode('utf-8').split('\n')
  for line in lines:
    if line.find('yes:') == 0:
      #print(line[4:])
      return line[4:]


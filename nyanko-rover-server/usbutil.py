import subprocess

def has_id(lsusb_line,device_id):
  num_max_splits = 7
  words = lsusb_line.split(b' ',num_max_splits)
  if len(words) < 6:
    return False

  #print(words, device_id.encode())
  encoded_id = device_id.encode()

  return True if (words[5] == encoded_id) else False

# Returns a line matching the specified id in the stdout output of lsusb
def find_lsusb_entry_by_id(device_id):
  lsusb = subprocess.check_output('lsusb')
  lines = lsusb.splitlines()
  print('{} lsusb entries'.format(len(lines)))
  for line in lines:
    if has_id(line,device_id):
      print(line)
      return line
  return None

# device_id is a pair of 4 hex digits separated by colon, e.g. 1d6b:0002
def reset_device(device_id):
  #lsusb = subprocess.check_output('lsusb')
  #lines = lsusb.splitlines()
  line = find_lsusb_entry_by_id(device_id)

  if line is None:
    print('Device with the id {} not found.'.format(device_id))
    return

  # A typical entry is like this:
  # Bus 002 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub

  words = line.split()
  bus_number = words[1].decode('utf-8')
  usb_number = words[3].decode('utf-8')[0:3]
  dev_path = '/dev/bus/usb/{}/{}'.format(bus_number,usb_number)
  print('Resetting a USB device: {}'.format(dev_path))
  subprocess.check_output('sudo ./usbreset {}'.format(dev_path))

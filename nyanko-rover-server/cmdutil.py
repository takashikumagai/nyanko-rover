#!/usr/bin/env python3

import subprocess
import threading

# Usage
# 
# def on_exit():
#   print('Nyanko detected.')
# 
# cmdutil.exec_cmd_async(['grep','-nrI','nyanko','./'],on_exit)

# Source: https://stackoverflow.com/questions/2581817/python-subprocess-callback-when-cmd-exits
def exec_cmd_async(cmd, on_cmd_exit):
  """
  Runs the given args in a subprocess.Popen, and then calls the function
  on_cmd_exit when the subprocess completes.
  on_cmd_exit is a callable object, and cmd is a list of strings consisting
  of a command and its arguments which would be given to subprocess.Popen().
  """
  def run_in_thread(cmd, on_cmd_exit):
    proc = subprocess.Popen(cmd)
    proc.wait()
    on_cmd_exit()
    return

  thread = threading.Thread(target=run_in_thread, args=(cmd,on_cmd_exit))
  thread.start()
  return thread


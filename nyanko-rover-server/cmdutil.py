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
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()
    on_cmd_exit(proc.stdout.read(), proc.stderr.read())
    return

  thread = threading.Thread(target=run_in_thread, args=(cmd,on_cmd_exit))
  thread.start()
  return thread


def test_exec_cmd_async_callback_echo(stdout,stderr):
  print('test stdout', stdout)
  print('test stderr', stderr)
  if stdout == b'hello-nyanko\n':
    print('PASS')
  else:
    print('FAILED')


def test_exec_cmd_async_callback_cal(stdout,stderr):
  if stdout == b'      May 1950        \nSu Mo Tu We Th Fr Sa  \n    1  2  3  4  5  6  \n 7  8  9 10 11 12 13  \n14 15 16 17 18 19 20  \n21 22 23 24 25 26 27  \n28 29 30 31           \n                      \n':
    print('PASS')
  else:
    print('FAILED')


def test_exec_cmd_async():
  exec_cmd_async(['echo', 'hello-nyanko'], test_exec_cmd_async_callback_echo)
  exec_cmd_async(['cal', 'May', '1950'], test_exec_cmd_async_callback_cal)


if __name__ == "__main__":
  test_exec_cmd_async()


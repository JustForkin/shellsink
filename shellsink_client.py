#!/usr/bin/env python
import urllib2
import urllib
import socket
import getopt
import sys
import os

SOCKET_TIMEOUT=10
URL="http://localhost:8080/history/add"
#URL="http://bash-history.appspot.com/history/add"

class Client:
  def __init__(self):
    self.verify_environment
    self.history_file = os.environ['HOME'] + "/.bash_history"
    self.history_timestamp = os.environ['HOME'] + "/.bash_history_timestamp"
    self.config = os.environ['HOME'] + "/.faucet"
    self.config_file = os.environ['HOME'] + "/.faucet/config"
    self.disable_slug = os.environ['HOME'] + "/.faucet/disable_slug"
    self.id = os.environ['SHELL_SINK_ID']
    self.tags = os.environ['SHELL_SINK_TAGS']

  def verify_environment(self):
    if not os.environ.has_key('HOME'):
      raise Exception, "HOME environment variable must be set"
    if not os.environ.has_key('SHELL_SINK_ID'):
      raise Exception, "SHELL_SINK_ID environment variable must be set"
    if not os.environ.has_key('SHELL_SINK_TAGS'):
      raise Exception, "SHELL_SINK_TAGS can be empty but must exist"

  def url_with_command(self):
    params = {'hash' : self.id, 'command' : self.latest_from_history(), 'tags' : self.tags}
    data = urllib.urlencode(params)
    return URL + '?' + data

  def send_command(self):
    if self.has_new_command():
      self.spawn_process(http_get, self.url_with_command())
    
  def spawn_process(self, func, arg):
    pid = os.fork()
    if pid > 0:
      sys.exit(0)
    os.setsid()
    pid = os.fork()
    if pid > 0:
      sys.exit(0)
    func(arg)

  def has_new_command(self):
    new_history_timestamp = self.history_file_timestamp()
    timestamp_if_there_is_no_last_recorded = new_history_timestamp - 1
    last_recorded_history_timestamp = self.last_recorded_history_timestamp()
    if not last_recorded_history_timestamp:
      last_recorded_history_timestamp = timestamp_if_there_is_no_last_recorded

    self.record_new_last_recorded_history_timestamp(new_history_timestamp)
    return new_history_timestamp > last_recorded_history_timestamp

  def history_file_timestamp(self):
    return os.path.getmtime(self.history_file)

  def last_recorded_history_timestamp(self):
    if os.path.exists(self.history_timestamp):
      file = open(self.history_timestamp,"r")
      old_history_timestamp = float(file.readline())
      file.close()
      return old_history_timestamp
    return None

  def record_new_last_recorded_history_timestamp(self, timestamp):
    file = open(self.history_timestamp,"w")
    file.writelines([str(timestamp)])
    file.close()

  def latest_from_history(self):
    file = open(self.history_file, "r")
    latest = file.readlines()[-1]
    file.close()
    return latest

  def enable(self):
    if os.path.exists(self.disable_slug):
      os.remove(self.disable_slug) 
    
  def disable(self):
    file = open(self.disable_slug, "w")
    file.close()

  def is_enabled(self):
    return not os.path.exists(self.disable_slug)

  def conf(self):
    base = ["""#faucet, a client for remote archiving your shell history"""]
    if not os.path.exists(self.config):
      os.mkdir(self.config)
    if not os.path.exists(self.config_file):
      file = open(self.config_file,"w")
      file.writelines(base)
      file.close()
    file = open(self.config_file, "r")
    self.config = file.readlines()
    file.close()

def http_get(url):
  try:
    urllib2.urlopen(url)
  except:
    pass

def usage():
  print """usage: faucet [hed] [help|enable|disable]"""

def main():
  try:
    opts, args = getopt.getopt(sys.argv[1:], "hed", ["help", "enable", "disable"])
  except getopt.GetoptError, err:
    # print help information and exit:
    print str(err) # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

  client = Client()
  client.conf()
  for o, a in opts:
    if o in ("-h", "--help"):
      usage()
      sys.exit()
    elif o in ("-e", "--enable"):
      client.enable()
      sys.exit(0)
    elif o in ("-d", "--disable"):
      client.disable()
      sys.exit(0)
    else:
      assert False, "unhandled option"

  socket.setdefaulttimeout(SOCKET_TIMEOUT)
  if client.is_enabled():
    client.send_command()

if __name__== '__main__':
  main()



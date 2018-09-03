#!/usr/bin/python
from koge48 import Koge48
import ConfigParser
kogeconfig = ConfigParser.ConfigParser()
kogeconfig.read("koge48.conf")
koge48core = Koge48(
  kogeconfig.get("mysql","host"),
  kogeconfig.get("mysql","user"),
  kogeconfig.get("mysql","passwd"),
  kogeconfig.get("mysql","database")
)

koge48core.BNBAirDrop()

from enigma import getDesktop,eConsoleAppContainer
from Screens.Screen import Screen
from Components.MenuList import MenuList
#from Components.Label import Label
from Components.Button import Button
from Components.ActionMap import ActionMap
from Components.ScrollLabel import ScrollLabel

from crossepglib import *
from crossepg_locale import _

import os
import sys

class CrossEPG_Log(Screen):
	def __init__(self, session):
		self.session = session
		if (getDesktop(0).size().width() < 800):
			skin = "%s/skins/log_sd.xml" % (os.path.dirname(sys.modules[__name__].__file__))
		else:
			skin = "%s/skins/log_hd.xml" % (os.path.dirname(sys.modules[__name__].__file__))
		f = open(skin, "r")
		self.skin = f.read()
		f.close()

		Screen.__init__(self, session)
		Screen.setTitle(self, _("CrossEPG") + " - " + _("Log"))

		self["CrossEpgLogScrollLabel"] = ScrollLabel(_("Please wait"))
		self["actions"] = ActionMap(["OkCancelActions", "DirectionActions", "ColorActions"],
		{
			"ok": self.close,
			"cancel": self.close,
			"up": self["CrossEpgLogScrollLabel"].pageUp,
			"down": self["CrossEpgLogScrollLabel"].pageDown,
			"red": self.delete_log,
		})

		self.container = eConsoleAppContainer()
		self.container.appClosed.append(self.appClosed)
		self.container.dataAvail.append(self.dataAvail)

		self.config = CrossEPG_Config()
		self.config.load()
		self.db_root = self.config.db_root

		self.onLayoutFinish.append(self.read_log)

	def appClosed(self, retval):
		if retval:
			self["CrossEpgLogScrollLabel"].setText(_("An error occurred - Please try again later"))

	def dataAvail(self, data):
		self["CrossEpgLogScrollLabel"].appendText(data)

	def run_console(self, cmd):
		self["CrossEpgLogScrollLabel"].setText("")
#		self.setTitle(_("CrossEPG log"))
		if cmd.startswith("cat "):
			try:
				self["CrossEpgLogScrollLabel"].setText(open(cmd[4:], "r").read())
			except:
				self["CrossEpgLogScrollLabel"].setText(_("Logfile does not exist anymore"))
		else:
			try:
				if self.container.execute(cmd):
					raise Exception, "failed to execute: ", cmd
			except Exception, e:
				self["CrossEpgLogScrollLabel"].setText("%s\n%s" % (_("An error occurred - Please try again later"), e))

	def cancel(self):
		self.container.appClosed.remove(self.appClosed)
		self.container.dataAvail.remove(self.dataAvail)
		self.container = None
		self.close()

	def read_log(self):
		cmd = "cat %s/crossepg.log" % (self.db_root)
		print "[CrossEPG_Log] cmd:  %s" % (cmd)
		self.run_console(cmd)

	def delete_log(self):
		cmd = "rm -f %s/crossepg.log" % (self.db_root)
		print "[CrossEPG_Log] cmd:  %s" % (cmd)
		self.run_console(cmd)		



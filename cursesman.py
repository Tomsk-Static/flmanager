#!/usr/bin/env python3
import curses
import curses.ascii
import sys
import helper
from math import *
import os
from functools import reduce
import shutil


class Window():
	def __init__(self):
		self.screen = curses.initscr()
		curses.noecho()
		curses.cbreak()
		curses.start_color()
		self.screen.keypad(1)
		curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_CYAN)
		self.highlightText = curses.color_pair(1)
		self.normalText = curses.A_NORMAL
		curses.curs_set(0)
		self.max_files = 8
		self.box = curses.newwin(self.max_files + 5, 44, 1, 1)
		self.box.box()

		self.position = 0
		self.page = 1
		self.current_path = os.getcwd()
		self.new_path = ''

		self.moving_keys = [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]
		self.folder_keys = [curses.ascii.NL, curses.KEY_BACKSPACE]

		self.helper_active = False
		self.notisfy_active = False
		self.notisfy_text = str()

		self.commands = helper.commands

		#start
		self.printList()
		self.listenKey()

	def printList(self):
		self.all_files = os.listdir()
		self.all_pages = len(self.all_files) // (self.max_files + 1)
		if self.all_pages == 0: self.all_pages = 1
		elif len(self.all_files) % (self.max_files + 1) != 0:
			self.all_pages += 1

		edge_left = (self.page - 1) * self.max_files
		edge_right = self.page * self.max_files

		self.files = self.all_files[edge_left:edge_right]

		self.box.addstr(1, 1, "Current path: \n " + self.current_path)
		self.box.addstr(3, 1, "Current page: {}, all pages: {}, files: {}"
                                      .format(self.page, self.all_pages, len(self.all_files))
                               )

		self.box.box()
		for obj in enumerate(self.files):
			if obj[0] == self.position:
				color = self.highlightText
			else:
				color = self.normalText

			self.box.addstr(obj[0] + 4, 2, str(obj[0]) + ' ' + obj[1], color)

		self.screen.refresh()
		self.printNotisfy()
		self.printHelp()
		self.box.refresh()


	def printNotisfy(self):
		if not self.notisfy_text:
			return
		text = self.separateText(self.notisfy_text, 20)
		self.helper_active = False
		notisfy = curses.newwin(len(text) + 2, len(max(text, key=len)) + 2, 1, 45)
		notisfy.box()

		for line in enumerate(text):
			notisfy.addstr(line[0] + 1, 1, line[1])

		notisfy.refresh()


	def printHelp(self):
		if not self.helper_active:
			return
		self.helper = curses.newwin(len(self.commands) + 2, 80, 1, 45)
		self.helper.box()

		for comm in enumerate(self.commands):
			self.helper.addstr(comm[0] + 1, 1, "{} - {}"
						           .format(comm[1].hotkey, comm[1].descr)
                                          )
		self.helper.refresh()


	def listenKey(self):
		key = self.screen.getch()
		#position down
		if key == curses.KEY_DOWN:
			self.downFunc()
		#position up
		elif key == curses.KEY_UP:
			self.upFunc()
		#open
		elif key == curses.ascii.NL:
			self.openFunc()
		#back
		elif key == curses.KEY_BACKSPACE:
			self.backFunc()
		#delete
		elif key == 100:
			self.deleteFunc()
		#make dir
		elif key == 109:
			self.mkfolderFunc()
		#make empty file
		elif key == 102:
			self.mkfileFunc()
		#copy file/dir
		elif key == 99:
			self.copyFunc()
		#show/hide helper
		elif key == 104:
			self.helperFunc()
		#swipe page right
		elif key == curses.KEY_RIGHT:
			self.rightFunc()
		#swipe page left
		elif key == curses.KEY_LEFT:
			self.leftFunc()
		#exit
		elif key == curses.ascii.ESC:
			self.exitFunc()

		self.clearWin()
		self.printList()
		self.listenKey()

	########!!!!all key's functions!!!!!!###########
	def upFunc(self):
		if self.position > 0:
			self.position -= 1


	def downFunc(self):
		if self.position + 1 < len(self.files):
			self.position += 1


	def rightFunc(self):
		if self.page < self.all_pages:
			self.page += 1
			self.position = 0


	def leftFunc(self):
		if self.page > 1:
			self.page -= 1
			self.position = 0


	def openFunc(self):
		file = self.files[self.position]
		try:
			self.page = 1
			self.current_path = os.getcwd() + '/' + file
			os.chdir(self.current_path)
			self.position = 0
		except NotADirectoryError:
			self.screen.clear()
			self.screen.refresh()
			curses.endwin()
			os.system('nano ' + file)
			exit()
		except PermissionError:
			self.notisfy_text = 'Permission Error'


	def backFunc(self):
		if self.current_path == '/home':
			self.listenKey()
		self.page = 1
		ind = self.current_path.rfind('/')
		self.new_path = self.current_path[:ind]
		os.chdir(self.new_path)
		self.position = 0
		self.current_path = self.new_path


	def deleteFunc(self):
		file = self.files[self.position]
		self.screen.addstr(17, 1, 'Remove file "{}"? y/n'
					   .format(file)
                                  )

		self.screen.refresh()
		if self.awaitAccept():
			try:
				os.rmdir(file)
			except NotADirectoryError:
				os.remove(file)
			except OSError:
				shutil.rmtree(file)
		self.position = 0


	def mkfolderFunc(self):
		curses.echo()
		self.screen.addstr(15, 1, "Enter folder name: ")
		self.screen.refresh()
		folder_name = self.screen.getstr(15, 19, 20)
		os.mkdir(folder_name)
		curses.noecho()


	def mkfileFunc(self):
		curses.echo()
		self.screen.addstr(15, 1, "Enter file name: ")
		self.screen.refresh()
		file_name = self.screen.getstr(15, 17, 20)
		os.mknod(file_name)
		curses.noecho()


	def copyFunc(self):
		curses.echo()
		file = self.files[self.position]
		self.screen.addstr(15, 1, "Enter path for copying:/home/alex/ ")
		self.screen.refresh()
		new_path = self.screen.getstr(15, 35, 50)
		new_path = new_path.decode()

		new_path = '/home/alex/' + new_path

		try:
			if os.path.isfile(file):
				shutil.copy(file, new_path)
			else:
				shutil.copytree(file, new_path)
		except:
			self.notisfy_text = str(sys.exc_info()[0])

		curses.noecho()


	def helperFunc(self):
		self.notisfy_text = str()
		self.helper_active = not self.helper_active


	def exitFunc(self):
		curses.endwin()
		exit()

	#######!!!!! end of key's functions!!!!!#######


	#separate long text and convert to list of lines
	def separateText(self, text, length):
		ln = int()
		line = str()
		textList = list()
		for symb in text:
			if ln >= length and symb == ' ':
				textList.append(line)
				line = str()
				ln = 0
				continue
			line += symb
			ln += 1
		if line: textList.append(line)
		return textList


	def inputMode(self, strpos, text, name):
		self.clearWin()
		self.screen.addstr(strpos, 1, text.format(name))
		self.screen.refresh()
		symb = self.screen.getch()
		if symb == curses.ascii.NL:
			return name
		name += chr(symb)
		return self.inputMode(strpos, text, name)


	def parseFile(self, file):
		unexp_symb = '+-./=,{}()*&^%$#@!'
		res = map(lambda symb: file.find(symb), unexp_symb)
		return reduce(lambda acc, x: acc * x, res) > 0

	def awaitAccept(self):
		rm_key = self.screen.getch()
		if rm_key == 121:
			return True
		elif rm_key == 110:
			return False
		return self.awaitAccept()

	def clearWin(self):
		self.screen.clear()
		self.box.clear()
		self.screen.refresh()
		self.box.refresh()




#!	/usr/bin/python3
'''A command-line aid in creating PCB footprints'''

import argparse
import sys

fp = None

class Pad:
	def __init__(self, xsiz=1.0, ysiz=1.0, xpos=0.0, ypos=0.0):
		self.w = xsiz
		self.h = ysiz
		self.x = xpos
		self.y = ypos
	
	def __str__(self):
		return 'XPOS=%s, YPOS=%s, XSIZ=%s, YSIZ=%s' % (self.x, self.y, self.w, self.h)

class Footprint:
	def __init__(self, name='new_footprint', pads=None):
		self.name = name
		if pads:
			self.pads = pads
		else:
			self.pads = []
			
	def display(self):
		for i,p in enumerate(self.pads):
			print('Pad %d: %s' % (i, p))
		
	def add_pad(self, pad):
		self.pads.append(pad)

def	main():
	global fp
	topparser = init_topparser()	# parser for program start
	args = topparser.parse_args()
	
	cmdparser = init_cmdparser()	# parser for program command-prompt
	
	fp = Footprint()
	while(True):
		s = input('bigfoot >> ')
		try:
			args = cmdparser.parse_args(s.split())
		except SystemExit as ex:
#			print(repr(ex))
			continue
		args.func(args)
		
def cmd_quit(args):
	sys.exit(0)

def cmd_add(args):
	global fp
	p = Pad(xsiz=args.w, ysiz=args.h, xpos=args.x, ypos=args.y)
	fp.add_pad(p)
	
def cmd_del(args):
	global fp
	del fp.pads[args.pad]
	
def cmd_ls(args):
	global fp
	fp.display()
	
def init_topparser():
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('-V','--version',
						help='display the version of %(prog)s',
						action='version',	
						version='%(prog)s 0.1')
	return parser
	
def init_cmdparser():
	parser = argparse.ArgumentParser()
	subs = parser.add_subparsers()
	
	sp = subs.add_parser('quit')
	sp.set_defaults(func=cmd_quit)
	
	sp = subs.add_parser('ls')
	sp.set_defaults(func=cmd_ls)
	
	sp = subs.add_parser('add', add_help=False)
	sp.add_argument('-w', type=float)
	sp.add_argument('-h', type=float)
	sp.add_argument('-x', type=float)
	sp.add_argument('-y', type=float)
	sp.set_defaults(func=cmd_add)
	
	sp = subs.add_parser('del')
	sp.add_argument('pad', type=int)
	sp.set_defaults(func=cmd_del)
	
	return parser
	
if	__name__== "__main__":
	main()

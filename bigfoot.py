#!	/usr/bin/python3
'''A command-line aid in creating PCB footprints'''

import argparse
import sys

fp = None

class Pad:
	def __init__(self, xsiz, ysiz, xpos, ypos):
		self._w = xsiz
		self._h = ysiz
		self._x = xpos
		self._y = ypos
		self.update_corners()
	
	def __str__(self):
		return 'X=%5s, Y=%5s, W=%5s, H=%5s' % (self._x, self._y, self._w, self._h)

	def change(self, xsiz=None, ysiz=None, xpos=None, ypos=None):
		if xsiz:
			self._w = xsiz
		if ysiz:
			self._h = ysiz
		if xpos:
			self._x = xpos
		if ypos:
			self._y = ypos
		self.update_corners()

	def update_corners(self):
		xh = self._w/2
		yh = self._h/2
		self._corn = (	(self._x - xh, self._y - yh),
						(self._x + xh, self._y - yh),
						(self._x + xh, self._y + yh),
						(self._x - xh, self._y + yh))
		
class Footprint:
	def __init__(self, name='new_footprint', pads=None):
		self.name = name
		if pads:
			self.pads = pads
		else:
			self.pads = []
			self.pads.append(None)
			
	def display(self):
		for i,p in enumerate(self.pads):
			if p:
				s = p
			else:
				s = 'Origin'
			print('Pad %d: %s' % (i, s))
		
	def add_pad(self, pad):
		self.pads.append(pad)

def main():
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
			continue
		args.func(args)

def cmd_quit(args):
	sys.exit(0)

def cmd_add(args):
	global fp
	p = Pad(xsiz=args.w, ysiz=args.h, xpos=args.x, ypos=args.y)
	fp.add_pad(p)

def cmd_edit(args):
	global fp
	p = fp.pads[args.pad].change(xsiz=args.w, ysiz=args.h, xpos=args.x, ypos=args.y)

def cmd_del(args):
	global fp
	del fp.pads[args.pad]

def cmd_ls(args):
	global fp
	fp.display()

def cmd_pos(args):
	global fp
	
	offset = [None, None]
	if args.dir == 'N' or args.dir == 'S': # vertical orientation
		for i,(pi,r) in enumerate(zip(args.pad, args.ref)):
			#print('%d %d %s' % (i, pi, r))
			p = fp.pads[pi]
			if r == 'f':
				offset[i] = p._h/2.0
			elif r == 'n':
				offset[i] = -p._h/2.0
			elif r == 'c':
				offset[i] = 0
	elif args.dir == 'E' or args.dir == 'W': # horizontal orientation
		for i,(pi,r) in enumerate(zip(args.pad, args.ref)):
			p = fp.pads[pi]
			if r == 'f':
				offset[i] = p._w/2.0
			elif r == 'n':
				offset[i] = -p._w/2.0
			elif r == 'c':
				offset[i] = 0
	d = sum(offset)
	if args.dir == 'N':
		d += -args.dist + fp.pads[args.pad[1]]._y
		fp.pads[args.pad[0]].change(ypos=d)
	elif args.dir == 'E':
		d += args.dist + fp.pads[args.pad[1]]._x
		fp.pads[args.pad[0]].change(xpos=d)
	elif args.dir == 'S':
		d += args.dist + fp.pads[args.pad[1]]._y
		fp.pads[args.pad[0]].change(ypos=d)
	elif args.dir == 'W':
		d += -args.dist + fp.pads[args.pad[1]]._x
		fp.pads[args.pad[0]].change(xpos=d)
		
def myfloat(val):
    return float(val)

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
	sp.add_argument('-w', type=float, default=1.0)
	sp.add_argument('-h', type=float, default=1.0)
	sp.add_argument('-x', type=float, default=0.0)
	sp.add_argument('-y', type=float, default=0.0)
	sp.set_defaults(func=cmd_add)

	sp = subs.add_parser('edit', add_help=False)
	sp.add_argument('pad', type=int)
	sp.add_argument('-w', type=float)
	sp.add_argument('-h', type=float)
	sp.add_argument('-x', type=float)
	sp.add_argument('-y', type=float)
	sp.set_defaults(func=cmd_edit)
	
	sp = subs.add_parser('del')
	sp.add_argument('pad', type=int)
	sp.set_defaults(func=cmd_del)
	
	sp = subs.add_parser('pos')
	sp.add_argument('pad', type=int, nargs=2)
	sp.add_argument('dist', type=myfloat)
	sp.add_argument('dir', choices=('N','S','E','W'), default='N')
	sp.add_argument('ref', choices=('f','n','c'), nargs=2, default='c')
	sp.set_defaults(func=cmd_pos)
	
	return parser
	
if __name__== "__main__":
	main()

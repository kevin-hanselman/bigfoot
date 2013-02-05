#!	/usr/bin/python3
'''A command-line aid in creating PCB footprints'''

import argparse
import sys
import os
try:
	import cPickle as pickle
except:
	import pickle

fp = None

class Pad:
	def __init__(self, xsiz, ysiz, xpos, ypos):
		self._w = xsiz
		self._h = ysiz
		self._x = xpos
		self._y = ypos
		self.update_corners()
	
	def __str__(self):
		return 'X= %.4f, Y= %.4f, W= %.4f, H= %.4f' \
				% (self._x, self._y, self._w, self._h)

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
	def __init__(self, name='new', pads=None):
		self.name = name
		if pads:
			self._pads = pads
		else:
			self._pads = []
			self._pads.append(Pad(0,0,0,0)) # add origin pad
			
	def display(self):
		print(' '+fp.name)
		print('-'*60)
		for i,p in enumerate(self._pads):
			if not i:
				s = 'Origin'
			else:
				s = p
			print('Pad %d: %s' % (i, s))
		print('-'*60)
		
	def add_pad(self, pad):
		self._pads.append(pad)
		
	def del_pad(self, i):
		if self.assert_pads(i):
			del self._pads[i]

	def get_pads(self, p):
		'''Returns either a list of pads or a single Pad.'''
		if self.assert_pads(p):
			if type(p) == type(list()):
				out = []
				for i in p:
					out.append(self._pads[i])
				return out
			else:
				return self._pads[p]
				
	def assert_pads(self, p):
		if type(p) == type(list()):
			for i in p:
				try:
					self._pads[i]
				except IndexError:
					print('Footprint %s has no pad numbered %d' % (self.name, i))
					return False
		else:
			try:
				self._pads[p]
			except IndexError:
				print('Footprint %s has no pad numbered %d' % (self.name, p))
				return False
		return True
			
def main():
	'''Entry point for program.'''
	global fp
	topparser = init_topparser()	# parser for program start
	args = topparser.parse_args()
		
	cmdparser = init_cmdparser()	# parser for program command-prompt
	
	fp = Footprint()
	
	if args.batch:
		for line in args.batch:
			#print(repr(line))
			if line.strip():
				try:
					exec_cmd(cmdparser, line)
				except SystemExit:
					pass
	
	while(True):
		try:
			s = input('BGFT: %s >> ' % fp.name)
		except KeyboardInterrupt:
			print()
			sys.exit(0)
		try:
			exec_cmd(cmdparser, s)
		except SystemExit:
			continue
		
def exec_cmd(parser, str):
	try:
		args = parser.parse_args(str.split())
	except Exception as ex:
		print(str(ex))
	args.func(args)

def cmd_quit(args):
	'''Quit bigfoot.py.
	input:
		args = argparse Namespace
	'''
	sys.exit(0)

def cmd_add(args):
	'''Adds a pad to the current footprint.
	input:
		args = argparse Namespace
	'''
	global fp
	p = Pad(xsiz=args.w, ysiz=args.h, xpos=args.x, ypos=args.y)
	fp.add_pad(p)

def cmd_edit(args):
	'''Edit the attributes of a pad on the current footprint.
	input:
		args = argparse Namespace
	'''
	global fp
	if args.pad == 0:
		print('Cannot edit origin (Pad 0).')
	else:
		p = fp.get_pads(args.pad)
		p.change(xsiz=args.w, ysiz=args.h, xpos=args.x, ypos=args.y)

def cmd_del(args):
	'''Deletes a pad from the current footprint.
	input:
		args = argparse Namespace
	'''
	global fp
	if args.pad == 0:
		print('Cannot delete origin (Pad 0).')
	else:
		fp.del_pad(args.pad)

def cmd_ls(args):
	'''List all pads on a given footprint.
	input:
		args = argparse Namespace
	output:
		print()
	'''
	global fp
	fp.display()
	
def cmd_save(args):
	'''Saves a footprint to a file.
	input:
		args = argparse Namespace
	'''
	global fp
	if args.out:
		fp.name, fext = os.path.splitext(os.path.basename(args.out))
		path = args.out
		if not fext:
			path += '.bfp'
	else:
		path = fp.name + '.bfp'
	try:
		pickle.dump(fp, open(path, 'wb') )
	except IOError as ex:
		print(str(ex))
	
def cmd_load(args):
	'''Loads a footprint from a file.
	input:
		args = argparse Namespace
	'''
	global fp
	fext = os.path.splitext(args.path)[1]
	if not fext:
		args.path += '.bfp'
	try:
		fp = pickle.load(open(args.path, 'rb'))
	except IOError as ex:
		print(str(ex))

def cmd_pos(args):
	'''Places a pad relative to another pad.
	input:
		args = argparse Namespace
	'''
	global fp
	offset = [None, None]
	if args.dir == 'N' or args.dir == 'S': # vertical orientation
		for i,(pi,r) in enumerate(zip(args.pad, args.ref)):
			#print('%d %d %s' % (i, pi, r))
			p = fp.get_pads(pi)
			if r == 'f':
				offset[i] = -p._h/2.0
			elif r == 'n':
				offset[i] = p._h/2.0
			elif r == 'c':
				offset[i] = 0
	elif args.dir == 'E' or args.dir == 'W': # horizontal orientation
		for i,(pi,r) in enumerate(zip(args.pad, args.ref)):
			p = fp.get_pads(pi)
			if r == 'f':
				offset[i] = -p._w/2.0
			elif r == 'n':
				offset[i] = p._w/2.0
			elif r == 'c':
				offset[i] = 0
	d = sum(offset)
	if args.dir == 'N':
		d += -args.dist + fp._pads[args.pad[1]]._y
		fp._pads[args.pad[0]].change(ypos=d)
	elif args.dir == 'E':
		d += args.dist + fp._pads[args.pad[1]]._x
		fp._pads[args.pad[0]].change(xpos=d)
	elif args.dir == 'S':
		d += args.dist + fp._pads[args.pad[1]]._y
		fp._pads[args.pad[0]].change(ypos=d)
	elif args.dir == 'W':
		d += -args.dist + fp._pads[args.pad[1]]._x
		fp._pads[args.pad[0]].change(xpos=d)

def cmd_dist(args):
	'''Compute the x and y distance between two reference points on two pads.
	input:
		args = argparse Namespace
	output:
		print()
	'''
	global fp
	pd = fp.get_pads(args.pad)
	points = []
	for r,p in zip(args.ref, pd):
		if r == 0: # center
			points.append((p._x, p._y))
		else: # corner
			points.append(p._corn[r-1])
	d = twopoint_dist(points)
	print('dx = %.4f, dy = %.4f' % (d[0], d[1]))

def twopoint_dist(pts):
	'''Compute the x and y distance between two points.
	input:
		pts = a 2-element tuple containing 2-element tuples
	output:
		2-element tuple
	'''
	return (pts[0][0]-pts[1][0], pts[0][1]-pts[1][1])
	
def init_topparser(): # top-level script arg parser
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('-V','--version',
						help='display the version of %(prog)s',
						action='version',	
						version='%(prog)s 0.1')
	parser.add_argument('-b','--batch',
						help='input batch file',
						metavar='FILE',
						type=argparse.FileType('r'))
	return parser
	
def init_cmdparser(): # script commands arg parser
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
	sp.add_argument('dist', type=float)
	sp.add_argument('dir', choices=('N','S','E','W'), default='N')
	sp.add_argument('ref', choices=('f','n','c'), nargs=2, default='c')
	sp.set_defaults(func=cmd_pos)
	
	sp = subs.add_parser('dist')
	sp.add_argument('pad', type=int, nargs=2)
	sp.add_argument('ref', type=int, nargs=2, choices=range(0,5))
	sp.set_defaults(func=cmd_dist)
	
	sp = subs.add_parser('save')
	sp.add_argument('-o', '--out')
	sp.set_defaults(func=cmd_save)
	
	sp = subs.add_parser('load')
	sp.add_argument('path')
	sp.set_defaults(func=cmd_load)
	
	return parser
	
if __name__== "__main__":
	main()

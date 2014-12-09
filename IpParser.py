class IPParser:
	def __init__(self):
		pass

	def _parse_ip( self, line ):
		segs = line.split(".")
		if len(segs) != 4:
			return (False,"Invalid input format : %s" %(line))

		cells = []
		for seg in segs:
			cell = []
			for i in seg.split(","):
				if '-' not in i:
					cell.append(i)
				else:
					start,end = i.split("-")
					cell +=  [ str(i) for i in range( int(start), int(end) + 1)]
			cells.append(cell)

		hosts = []
		for s0 in cells[0]:
			for s1 in cells[1]:
				for s2 in cells[2]:
					for s3 in cells[3]:
						host = ".".join([s0,s1,s2,s3])
						hosts.append(host)
		return hosts

	def parse_ip( self, lines ):
	    hosts = []
	    for line in lines:
	    	for sub_line in line.split(" "):
	    		 hosts += self._parse_ip(sub_line)
	    return hosts

def test():
	lines = [ '10.0.1.2-4,5,6-8' ]
	 
	parser = IPParser( )
	hosts = parser.parse_ip(lines)
	print hosts
 
# test()
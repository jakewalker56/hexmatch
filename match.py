import json
import random
import sys
import itertools
import time

start = time.time()
random.seed(0)

with open("grid.json", "r") as read_content:
	spec = json.load(read_content)

#if (spec["width"] * spec["height"] - spec["num_free_hexes"]) > (spec["num_tiles"] * spec["max_tile_size"]):
#	print("constraints impossible to satisfy")
#	sys.exit()

def print_layout(hex_list):
	print("printing " + str(hex_list))

	'''
		we should draw an x if the drawing coordinate maps to one of the included axial coordinates.  This is true when:
			-the drawing offset plus the min value offset (converted to axial) map to the hex

		Mapping hex to cartesian can be done with:
			x = 2 * Q + S
			y = S
		
		So we can invert this mapping as: 
			S = y
			Q = (x - S) / 2 = (x - y) / 2

	'''
	min_x = min(hex_list, key=lambda x:x[0]+x[1]/2)
	min_x = 2 * int(min_x[0] + (min_x[1] - 1)/2)
	
	max_x = max(hex_list, key=lambda x:x[0]+x[1]/2)
	max_x = 2 * int(max_x[0] + (max_x[1]+1)/2)

	min_y = min(hex_list, key=lambda x:x[1])[1]
	max_y = max(hex_list, key=lambda x:x[1])[1]

	#note we are indexing with the min offset so this doesn't fall apart for layouts far away from the origin (since we're indexing using the absolute axial coordinates)
	print_chars = []
	min_r = 0
	min_s = 0
	if len(hex_list[0]) > 2:
		min_r = min(hex_list, key=lambda x:x[0])[0]
		max_r = max(hex_list, key=lambda x:x[0])[0]
		min_s = min(hex_list, key=lambda x:x[1])[1]
		max_s = max(hex_list, key=lambda x:x[1])[1]
		for r in range(0,max_r - min_r + 1):
			print_chars.append([0] * (max_s - min_s + 1))
		for h in hex_list:
			print_chars[h[0] - min_r][h[1] - min_s] = h[2]
		hex_list = list(h[0:2] for h in hex_list)


	print(str(min_x) + ", " + str(max_x) + " | " + str(min_y) + ", " + str(max_y))
	for y in reversed(range(min_y, max_y + 1)):  #we want to iterate "high to low" because we draw left to right, top to bottom
		for x in range(min_x, max_x + 1):
			if [(x - y) / 2, y] in hex_list:
				if print_chars != []:
					print(print_chars[int((x - y) / 2 - min_r)][int(y - min_s)], end='')
					#print("z", end='')
				else:
					print("x", end='')
			else:
				print(" ", end='')
		print("")

def print_layouts(layout_list):
	for layout in layout_list:
		print_layout(layout)

def print_base(base):
	base_layout = []
	for i in range(0,len(base)):
		for j in range(0,len(base[i])):
			base_layout.append([i,j,base[i][j]])
	print_layout(base_layout)


def test_printing():
	print_layout([[-1,1],[-1,-1],[-1,0],[0,0],[1,0],[1,1],[1,2],[2,-1]])
	print_layout([[-2, 0], [-1, 0], [0, 0]])
	print_layout([[0, -2], [0, -1], [0, 0]])
	print_layout([[0, -5], [1, -3], [-3, 0], [4,5]])
	print_layout([[0, 0], [0, 1], [0, 2]])

def find_all_layouts(hex_list, min_tile_size, max_tile_size):
	if len(hex_list) >= max_tile_size:
		return [hex_list]
	
	return_list = []
	if len(hex_list) >= min_tile_size:
		return_list.append(hex_list)

	#print("hex list:")
	#print(hex_list)
	'''find possible bridging hexes'''
	bridges = []
	for h in hex_list:
		bridges.append([h[0]-1,h[1]])
		bridges.append([h[0]+1,h[1]])
		bridges.append([h[0],h[1]-1])
		bridges.append([h[0],h[1]+1])
		bridges.append([h[0]-1,h[1]+1])
		bridges.append([h[0]+1,h[1]-1])

	'''apparrently this dedupes'''
	bridges.sort()
	bridges = list(bridges for bridges,_ in itertools.groupby(bridges))
	for bridge in bridges:
		if bridge in hex_list:
			#we've backtracked, don't bother continuing down this path
			continue
		return_list.extend(find_all_layouts(hex_list + [bridge], min_tile_size, max_tile_size))
	return return_list

def normalize_layout(layout):
	base_q = min(layout, key=lambda x:x[0])[0]
	base_s = min(layout, key=lambda x:x[1])[1]
	result = []
	for i in range(0, len(layout)):
		result.append([layout[i][0] - base_q, layout[i][1] - base_s])
		result[-1].extend(layout[i][2:])

	#result = [[x[0] - base_q, x[1] - base_s] for x in layout]
	result.sort()
	return result

def generate_rotations(layout):
	'''
	clockwise rotation is done by "swapping" axes and inverting signs: 
		-Q->S
		-S->R
		-R = -(-S-Q) = Q+S->Q

	Note generate_rotations assumes the first two elements in a hex are axial coordinates; additional elements are propogated but otherwise ignored
	'''
	results = [layout]
	for i in range(0,5):
		results.append([])
		for h in results[i]:
			results[i+1].append([(h[0]+h[1]), -h[0]])
			results[i+1][-1].extend(h[2:])
		results[i+1] = normalize_layout(results[i+1])
		
	#because results are normalized, we can dedupe them here
	results.sort()
	results = list(result for result,_ in itertools.groupby(results))
	
	return results

def find_all_unique_layouts(min_tile_size, max_tile_size):
	layouts = find_all_layouts([[0,0]], min_tile_size, max_tile_size)
	'''shift all layouts to 0 min on r and s axis and filter dupes'''
	for i in range(0, len(layouts)):
		layouts[i] = normalize_layout(layouts[i])
	layouts.sort()
	layouts = list(layouts for layouts,_ in itertools.groupby(layouts))

	print("finished enumerating all layouts of size (" + str(min_tile_size) + "-" + str(max_tile_size) + ") | time elapsed: " + str(time.time() - start))
	
	'''now for each layout, see if any of its rotations match any of the other layouts; if so, remove dupes from the list'''
	for l in range(0, len(layouts)-1):
		if layouts[l] == []:
			continue
		rotations = generate_rotations(layouts[l])
		for r in rotations[1:]:
			for k in range(l+1,len(layouts)):
				if r == layouts[k]:
					layouts[k] = []
	return [l for l in layouts if l != []]

def tile_matches_base(color_layout, base, origin, offset):
	for h in color_layout:
		x = h[0] + origin[0] + offset
		y = h[1] + origin[1]
		if x < 0 or y < 0 or x >= len(base) or y >= len(base[0]):
			#hex in color_layout is not a valid position on base
			return False
		if base[x][y] == 0:
			#color_layout is overlapping with OOB
			return False
		if h[2] != base[x][y]:
			return False
	return True


def find_all_unique_tiles(base, min_tile_size, max_tile_size):
	'''find all tiles that have a single unique alignment'''
	'''algorithm:
		enumerate all possible layouts within constraints (deduped list of contiguous tuples with length between min and max)
		for each layout:
			for each origin hex in the base board + surrounding hexes:
				clone base colors into proposed tile shape at location
				for each of 6 rotations:
					for each target hex in the base board + surrounding hexes:
						if rotation is partially out of bounds, continue
						if rotation matches colors at target, record match
				if exactly one unique match (symmetric rotations with the same origin are fine), this layout at this position + origin combo is a valid tile
	'''
	layouts = find_all_unique_layouts(min_tile_size, max_tile_size)
	print(str(len(layouts)) + " valid unique layouts found"  + " | time elapsed: " + str(time.time() - start))
	
	origins = []
	width = spec["width"]
	height = spec["height"]
	offset = int((width + height / 2) / 2)
	
	origin_q_min = -offset
	origin_q_max = offset
	
	origin_s_min = 0
	origin_s_max = len(base[0])
	
	#there needs to be some buffer that is in principle calculatable... but I'm pretty sure whatever it is is small, so just hardcoding some stuff
	for q in range(origin_q_min - 2, origin_q_max):
		for s in range(origin_s_min, origin_s_max):
			if q + s < -width / 2 - 1:
				continue
			if q + s > width / 2 + 1:
				continue
			origins.append([q,s])
	tiles = []
	for layout in layouts:
		for origin in origins:
			color_layout = []
			matches = []
			for h in layout:	
				x = h[0] + origin[0] + offset
				y = h[1] + origin[1]
				if x < 0 or y < 0 or x >= len(base) or y >= len(base[0]):
					#hex is outside base, so invalid.
					color_layout = []
					break
				base_color = base[x][y]
				if base_color == 0:
					#0 means OOB, so we should never copy a 0 into a valid layout
					color_layout = []
					break
				color_layout.append([h[0], h[1], base_color])
			if color_layout == []:
				continue
			rotations = generate_rotations(color_layout)
			#rotations should already be deduped
			for r in rotations:
				for target in origins:
					if tile_matches_base(r,base,target,offset):
						matches.append([r,target])
			if len(matches) == 1:
				#print("unique match found (target = " + str(target) + ")")
				#print_layout(matches[0][0])
				tiles.append(matches[0])
	return tiles
			
def fill_base(spec):
	'''
	randomly tile board with colors
	note the format here is hexes[r + offset,s] = color rather than hexes[[r,s,color],...] because it's easier to lookup a color in a 
	2D array than it is to search for r and s every time we want a color lookup... and the offset is because r can't be negative
	'''

	hexes = []
	width = spec["width"]
	height = spec["height"]
	roffset = int((width + height / 2) / 2)
	soffset = int(height/2)
	for q in range(-roffset, roffset + int(height/4)):
		hexes.append([0]*(height))
		for s in range(-soffset, soffset):
			if (q + s/2) < (-width / 2):
				#print("OOB: " + str(q) + ", " + str(s))
				continue
			if (q + s/2) > (width / 2):
				#print("OOB: " + str(q) + ", " + str(s))
				continue
			#print("IB: " + str(q) + ", " + str(s))
			hexes[q + roffset][s + soffset] = random.randint(1,spec["colors"])

	return hexes


def solution_matches_spec(solution, spec):
	for tile in solution:
		'''check if tile matches grid'''
		'''check if tile uniquely maps to exactly one spot in grid'''
	
	'''check if number of uncovered tiles is correct'''
	uncovered = uncovered_hexes(merge_tiles(solution),base)
	if uncovered != spec["num_free_squares"]:
		print("incorrect number of uncovered hexes: " + str(uncovered))

def main():
	tries = 1000
	try_count = 0
	solution = False
	found_solution = False
	
	while try_count < tries and not found_solution:
		base = fill_base(spec)
		print("base: " + str(base))

		unique_tiles = find_all_unique_tiles(base, spec["min_tile_size"], spec["max_tile_size"])
		for tile,origin in unique_tiles[-300:]:
			print("origin: (" + str(origin[0]) + ", " + str(origin[1]) + ")")
			print_layout(tile)
		print_base(base)
		print("found " + str(len(unique_tiles)) + " unique tiles")
		
		solution = 1 
		'''find_solution(base, unique_tiles, spec["num_tiles"], spec["num_free_hexes"])'''
		if solution:
			found_solution = True
		else:
			tries = tries + 1

	'''
	"width" : "5",
	"height" : "5",
	"colors" : "3",
	"min_tile_size" : "3",
	"max_tile_size" : "5",
	"num_tiles" : "4",
	"num_free_squares" : "8"
	'''
	if found_solution:
		print("solution found? - " + " | time elapsed: " + str(time.time() - start))

main()
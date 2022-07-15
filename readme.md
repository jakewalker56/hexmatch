# Constraints and TODOs
Max tile size of 7 gives around 620 unique tiles and takes 20 seconds to calculate.  Profiler:
find_all_unique_layouts - 2.1
fina_all_layouts - 3.2
normalize_layout - 1.1
<listcompare> - 4.9
lambda (x2) - 1.1
min - 2.6
list sort - 3.4


Max tile size of 8 gives around X unique tiles and didn't finish after grabbing 4GB of RAM on my machine for an hour

Number of tiles goes as O(6^N) where n is tile size, and calculating uniqueness goes as O(N^2) where N is number of tiles.  However, most of the work happens in generating all layouts, not in checking for rotational equivalence

- Almost certainly I am doing stupid things because I'm not a Python expert
 - Apparently python passess mutable objects by reference(ish) by default - so I could stop returning data structures / assigning, and I could do in-place editing in functions? (tried this; didn't work; think I did it wrong)
 - Always suspect recursion of your performance issues.  I could run a profiler (seems like it's actually sorting / comparing / editing lists that's the bottleneck, not recursion)
 - I could try to make recursion more efficient (moving to an iterative approach could avoid generating exact dupes in the first place, but wouldn't avoid rotational dupes)
- I could also just pre-calculate unique layouts up to 8 and store them in a config file

python -m cProfile match.py

# Terminology
Unique
Layout
Base
Tile
Hex
Axial


# Axial Coordinates 
Hex space is weird - https://www.redblobgames.com/grids/hexagons/
We're using axial coordinate system: 

 /\s
|  |q
 \/r

q axis is "left and right"
s axis is "up and to the right"
(r axis is implied from q and s)

Imposing the constrain that r + q + s = 0 allows us to disambiguate hexes that would otherwise have multiple valid coordinates 
(since we don't have linearly independent basis vectors, becaue we have one too many coordinate dimensions). Thus, you can pick any 
two of these to keep track of, and the third is implied.  We keep track of q and s.

Because my specific project involves a page of hex graph paper that is taller than it is wide, I also want to impose the constraint that:
-6 < q + s / 2 < 6


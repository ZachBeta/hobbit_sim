# Known Issues
## Terrain
- [ ] Hobbits get stuck on walls (need pathfinding)
- [ ] Victory condition counts wrong after captures

##
* [ ] collision handling of entities - hobbit stacking
* [ ] distance handling of manhattan distance vs diagonals and speed calculations
* [ ] Inconsistent signatures:
```
find_nearest_hobbit() -> Position | None          # No distance
find_nearest_nazgul() -> tuple[Position | None, float]  # With distance
```
Options:
Make both return distance
Make both NOT return distance (calculate separately when needed)
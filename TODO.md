* [ ] collision handling
* [ ] Inconsistent signatures:
```
find_nearest_hobbit() -> Position | None          # No distance
find_nearest_nazgul() -> tuple[Position | None, float]  # With distance
```
Options:
Make both return distance
Make both NOT return distance (calculate separately when needed)
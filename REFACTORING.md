# REFACTORING.md

This document tracks potential refactoring opportunities for future work sessions. These are improvements to working code, organized by effort and decision-making complexity.

## Purpose

When you want to code but have limited decision-making capacity (recovery days, end of day, etc.), grab an item from "Easy Wins." When you're feeling sharp and want to tackle architecture, pick from "Architectural Improvements."

---

## Easy Wins

Mechanical refactors with clear benefits and low decision-making overhead:

### Type Improvements

- [ ] **Convert Position to frozen dataclass**
  - Current: `Position = tuple[int, int]` (just an alias)
  - Target: Frozen dataclass with `.x`, `.y` named fields
  - Benefits: Named access, can add methods (`.distance_to()`, `.adjacent_positions()`), immutable, better IDE support
  - Impact: ~50 callsites to update from `[0]`/`[1]` to `.x`/`.y`
  - Estimated effort: 1-2 hours

- [ ] **Convert EntityPositions to NewType or custom class**
  - Current: `EntityPositions = list[Position]` (just an alias)
  - Target: NewType for type safety or custom class with methods
  - Benefits: Type checker can distinguish hobbit positions from nazgul positions
  - Impact: Minimal - already used throughout
  - Estimated effort: 30 minutes

- [ ] **Add GridDimensions methods**
  - Current: `GridDimensions = tuple[int, int]`
  - Target: Frozen dataclass with `.width`, `.height` and `.contains(position)` method
  - Benefits: Named access, bounds checking helper
  - Impact: ~20 callsites
  - Estimated effort: 1 hour

### Extract Magic Numbers

- [ ] **Extract game constants to module-level**
  - Candidates: `DANGER_DISTANCE = 6`, `HOBBIT_SPEED = 2`, `NAZGUL_SPEED = 1`
  - Current: Hardcoded in `update_hobbits()` and `update_nazgul()`
  - Target: Module-level constants at top of file (after type definitions)
  - Benefits: Single source of truth, easier to tune gameplay
  - Impact: 3-5 locations
  - Estimated effort: 15 minutes

- [ ] **Extract world generation constants**
  - Candidates: `WORLD_WIDTH = 20`, `WORLD_HEIGHT = 20`, `SHIRE = (1, 1)`, `RIVENDELL = (18, 18)`
  - Current: Hardcoded in `create_world()`
  - Benefits: Easier to experiment with different map sizes
  - Impact: 1 function
  - Estimated effort: 10 minutes

---

## Architectural Improvements

Larger refactors requiring more design thinking:

### File Organization (SOLID Principles)

- [ ] **Split hobbit_sim.py into modules**
  - Current: ~900 lines in single file
  - Proposed structure:
    ```
    hobbit_sim/
      __init__.py          # Public API exports
      types.py             # WorldState, Position, Grid, type definitions
      movement.py          # move_toward, move_away_from, move_with_speed, pathfinding
      rendering.py         # Grid creation, entity placement, print/display
      simulation.py        # _run_simulation_loop, run_simulation, update functions
      world.py             # create_world, terrain generation
      events.py            # Event logging, NarrativeBuffer
    ```
  - Benefits: Easier navigation, focused modules, clearer dependencies
  - Blockers: Need to resolve circular imports, update CLAUDE.md philosophy
  - Estimated effort: 4-6 hours (includes test updates)

- [ ] **Update CLAUDE.md philosophy**
  - Current: "Single file initially"
  - Reality: Project has graduated beyond single-file phase
  - Action: Update design philosophy to reflect multi-module reality
  - Estimated effort: 15 minutes

### Separation of Concerns

- [ ] **Extract collision detection**
  - Current: Inline in `_run_simulation_loop()` (lines ~847-862)
  - Target: `detect_captures(*, hobbits, nazgul) -> list[Position]`
  - Benefits: Testable in isolation, clearer main loop
  - Impact: 1 location
  - Estimated effort: 30 minutes

- [ ] **Split WorldState into GameConfig + GameState**
  - Current: Single dataclass mixes immutable (terrain, rivendell) with mutable (hobbits, tick)
  - Target: Separate frozen config from mutable state
  - Benefits: Makes mutability explicit, clearer ownership
  - Trade-offs: More parameter passing, higher cognitive overhead
  - Decision needed: Is the explicit separation worth the complexity?
  - Estimated effort: 2-3 hours

### Single Responsibility

- [ ] **Review update_hobbits() and update_nazgul()**
  - Current: Each function handles movement logic for multiple entities
  - Concern: Mixing "decide where to move" with "execute movement"
  - Possible split: `decide_hobbit_move()` + `execute_moves()`
  - Benefits: More testable, clearer separation of "mind vs body"
  - Note: Already partially done with `_move_hobbit_evading()` and `_move_hobbit_traveling()`
  - Estimated effort: Evaluate 30 mins, implement if warranted 2-3 hours

---

## Performance

We're not optimizing yet (pure Python is fine), but track opportunities here:

- [ ] **Profile simulation loop** - Establish baseline before any optimization
- [ ] **Cache terrain lookups** - Currently using `set` which is already O(1), no action needed
- [ ] **Distance calculations** - Currently using Manhattan distance which is fast, no action needed

---

## Completed

*(Move items here when done, with date)*

---

## Notes

- **Philosophy**: "Make the change easy, then make the easy change" - Kent Beck
- **Constraint**: Prioritize simplicity and forward momentum over perfect architecture
- **Recovery-friendly**: Easy Wins are designed for low-capacity coding sessions
- **Test-driven**: All refactors must maintain green tests (33 passing, 7 skipped)

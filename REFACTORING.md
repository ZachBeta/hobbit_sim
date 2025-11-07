# REFACTORING.md

**Last Updated**: 2025-11-07
**Purpose**: Bite-sized polish tasks for Zone 1 coding sessions when you want to code but have limited decision-making capacity.

This document tracks polish opportunities for the **current working simulation** (hobbits fleeing Nazgûl). Tasks are sized for 15-60 minute sessions and ordered by value + ease.

---

## 🏃‍♂️ Now (Ready to Grab - 15-30 min each)

These are mechanical refactors with clear benefits. Grab any of these for a quick win.

### Extract Movement Constants
**Current**: Speed and danger distance are magic numbers scattered in code
**Action**: Create module-level constants
```python
# At top of hobbit_sim.py, after type definitions
DANGER_DISTANCE = 6      # Distance at which hobbits start evading (move_hobbit_one_step:522)
HOBBIT_SPEED = 2         # Steps per tick (_update_hobbits_dict:654)
NAZGUL_SPEED = 1         # Steps per tick (update_nazgul:712)
```
**Why**: Makes game tuning obvious, clearer intent
**Risk**: Minimal - just variable extraction
**Test strategy**: All 33 tests should pass unchanged
**Estimated**: 15 minutes

### Extract World Dimensions
**Current**: Grid size hardcoded as `(20, 20)` in create_world()
**Action**: Create constants
```python
WORLD_WIDTH = 20
WORLD_HEIGHT = 20
```
**Why**: Makes world size configurable, clearer what 20x20 represents
**Risk**: Minimal
**Test strategy**: Tests already parameterized with dimensions
**Estimated**: 15 minutes

### Add `get_hobbit_name()` Helper Function
**Current**: Name lookup logic duplicated in multiple places
```python
# Current pattern (scattered):
name = HOBBIT_NAMES.get(hobbit_id, f"Hobbit {hobbit_id}")
```
**Action**: Centralize in helper function
```python
def get_hobbit_name(*, hobbit_id: int) -> str:
    """Get display name for hobbit by ID. Falls back to generic name."""
    return HOBBIT_NAMES.get(hobbit_id, f"Hobbit {hobbit_id}")
```
**Why**: DRY principle, single source of truth for name logic
**Risk**: Low
**Estimated**: 20 minutes

---

## 🔜 Soon (After "Now" items - 30-60 min each)

These make sense once the constants are extracted.

### Document Movement System
**Current**: Manhattan movement is implicit, no comments explaining why
**Action**: Add docstring/comment explaining movement philosophy
```python
# Movement System Philosophy:
# - Manhattan distance (no diagonals): |dx| + |dy|
# - Move one axis at a time (creates "staircase" pattern)
# - Prioritizes axis with greater remaining distance
# - Matches how Nazgûl track hobbits (consistent pursuit logic)
```
**Why**: Makes design decisions explicit for future contributors (human or AI)
**Risk**: None (documentation only)
**Estimated**: 30 minutes

### Add Type Alias Documentation
**Current**: Type aliases lack usage examples
**Action**: Add comments explaining when to use each type
```python
Position = tuple[int, int]  # Grid coordinates (x, y)
EntityPositions = list[Position]  # Multiple entity locations (Nazgûl, etc.)
Hobbits = dict[HobbitId, Position]  # Maps hobbit IDs to positions
```
**Why**: Clarifies intent of each type
**Risk**: None
**Estimated**: 15 minutes

---

## 🤔 Maybe (Needs Validation - 1-2 hours each)

These might be YAGNI. Only tackle if you're feeling the pain.

### Extract Landmark Positions (Probably YAGNI)
**Current**: Shire at (1,1), Rivendell at (18,18) hardcoded
**Question**: Is this YAGNI since `world.rivendell` already tracks this?
**Concern**: Adding constants might duplicate WorldState fields
**Insight**: Landmark positions will naturally evolve with map concepts (entrances, exits, multiple maps/dungeons, surface world)
**Decision**: Wait until you need multiple map configurations

### Convert Position to Dataclass
**Current**: `Position = tuple[int, int]` (type alias)
**Target**: Frozen dataclass with `.x`, `.y` fields
**Impact**: ~50 callsites to update from `[0]`/`[1]` to `.x`/`.y`
**Why**: Named access, can add methods later (`.distance_to()`, etc.)
**Concern**: Big surgery for modest gain. Wait until you need position methods?
**Decision needed**: Do we need position methods yet?
**Estimated**: 2-3 hours

### Split Collision Detection
**Current**: Collision checks inline in `_run_simulation_loop` (lines ~902-915)
**Target**: Extract to `detect_captures(*, hobbits, nazgul) -> list[HobbitId]`
**Why**: Testable in isolation, clearer main loop
**Concern**: Is 14 lines worth extracting?
**Decision needed**: Wait until collision logic gets more complex?
**Estimated**: 30 minutes

---

## 🔮 Later (Architectural - 2-6 hours)

Don't tackle these yet. Revisit when you feel the pain.

### Split Into Modules
**Current**: ~950 lines in single file (still comfortable)
**When to do**: When navigation feels cramped OR when adding Bombadil features (entity states, abilities, etc.)
**Proposed structure**:
```
hobbit_sim/
  __init__.py          # Public API
  types.py             # WorldState, Position, type definitions
  movement.py          # move_toward, move_away_from, pathfinding
  rendering.py         # Grid creation, display
  simulation.py        # Core loop, update functions
  world.py             # create_world, terrain generation
  events.py            # Event logging, NarrativeBuffer
```
**Consideration**: Abstractions must be clear for both humans and AI agents
**Estimated**: 4-6 hours

### Update CLAUDE.md Philosophy
**Current**: Says "single file initially"
**Reality**: Ready to split when needed, but comfortable now
**Action**: Update to reflect multi-module readiness
**When**: After actually splitting into modules
**Estimated**: 15 minutes

---

## ✅ Completed

*(Move items here with completion date)*

**2025-11-05**: Migrated hobbits from list indices to dict with explicit IDs
**2025-11-05**: Added hobbit collision avoidance (hobbits don't stack during evasion)
**2025-11-05**: Implemented Nazgûl collision prevention (Nazgûl don't stack)

---

## Notes

**Philosophy**: "Make the change easy, then make the easy change" - Kent Beck
**Zone 1 friendly**: Tasks sized for low-capacity coding sessions
**YAGNI principle**: Don't extract until you feel the pain
**Test-driven**: All refactors must keep 33 tests passing
**Agent-friendly**: Keep abstractions simple and intuitive

**Why "Now/Soon/Maybe/Later"?**
- **Now**: Clear value, low risk, mechanical changes
- **Soon**: Depends on "Now" items, still low risk
- **Maybe**: Might be over-engineering, validate need first
- **Later**: Big changes, wait until current structure hurts

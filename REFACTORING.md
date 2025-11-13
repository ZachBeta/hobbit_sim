# REFACTORING.md

**Last Updated**: 2025-11-13
**Purpose**: Bite-sized polish tasks for Zone 1 coding sessions when you want to code but have limited decision-making capacity.

This document tracks polish opportunities for the **current working simulation** (hobbits fleeing Nazgûl). Tasks are sized for 15-60 minute sessions and ordered by value + ease.

**📍 For immediate next session work, see [NEXT_SESSION.md](NEXT_SESSION.md)**

---

## ✅ Done (Completed Refactorings)

### Quick Wins - Naming Consistency (2025-11-13)
Completed in ~35 minutes during low-capacity session:
- ✅ Standardized variable naming to `world_state` (~70 references)
- ✅ Renamed `render_world()` → `render_world_to_string()`
- ✅ Removed `_render_simulation_state()` wrapper function

**Result**: Consistent, self-documenting naming throughout codebase

---

## 🏃‍♂️ Now (Ready to Grab - 15-30 min each)

*(All "Now" items completed! See "Completed" section below)*

---

## 🔜 Soon (After "Now" items - 30-60 min each)

**📍 Cleanup tasks now in [NEXT_SESSION.md](NEXT_SESSION.md)**

The following refactoring task is ready to tackle (deferred to separate session):
- Complete rivendell cleanup (30 min) - Remove all `rivendell` references, standardize on `exit_position`

See NEXT_SESSION.md for full details.

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

**2025-11-13**: Documented Movement System - Added philosophy section comment + enhanced docstrings for `move_toward()` and `move_with_speed()` (makes Manhattan distance design explicit for contributors)
**2025-11-12**: Extracted duplicate rendering logic to `_render_world_to_grid()` helper (DRY - eliminated 40 lines of duplication)
**2025-11-12**: Removed `show_hobbit_ids` parameter (simplified API - always show IDs, consistent with production behavior)
**2025-11-12**: Replaced `rivendell` field usages with `exit_position` in escape count logic (partial cleanup - parameter name deferred)
**2025-11-07**: Added type alias documentation (inline comments for Position, Hobbits, etc.)
**2025-11-07**: Added `get_hobbit_name()` helper function (DRY principle for name lookups)
**2025-11-07**: Extracted movement constants (DANGER_DISTANCE, HOBBIT_SPEED, NAZGUL_SPEED)
**2025-11-07**: Extracted world dimension constants (WORLD_WIDTH, WORLD_HEIGHT)
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

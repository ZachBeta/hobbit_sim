# FEATURES.md

**Last Updated**: 2025-11-12
**Purpose**: Feature development pipeline - polish, testing, and enhancements for the simulation

This document tracks feature work, bug fixes, and test coverage improvements for the **current working simulation** (multi-map hobbit escape). Tasks are sized for Zone 1 sessions and ordered by urgency + value.

**📍 For immediate next session work, see [NEXT_SESSION.md](NEXT_SESSION.md)**

---

## ⏭️ Skipped Tests (Deferred Features)

**Test Suite Status:** 52 passed, 2 skipped

These tests represent **intentionally deferred features**, not bugs. They are skipped because the current implementation works and the features are YAGNI until proven otherwise.

### SKIP #1: Exit Buffer System
**Test:** `test_escaped_hobbits_tracked_separately_from_active` (test_hobbit_sim.py:232)
**What:** Separate tracking for exited hobbits vs active ones
**Current Behavior:** Hobbits "stack" at exit position to represent escaped state
**When to implement:** When multi-map journey tracking needs to distinguish "truly escaped" from "still fleeing"
**Estimated:** 4-6 hours (architectural change)

### SKIP #2: Pathfinding Around Nazgûl
**Test:** `test_hobbit_routes_around_nazgul_to_avoid_capture` (test_hobbit_sim.py:333)
**What:** Hobbits detect Nazgûl in their path and route around them
**Current Behavior:** Hobbits move directly toward goal, may walk into Nazgûl
**When to implement:** When playtesting reveals frustrating/unfair captures
**Estimated:** 2-3 hours (pathfinding enhancement)

**Decision:** Keep tests skipped. Unskip only when features become necessary.

---

## 🐛 Now (Bugs/Missing Pieces - 15-30 min each)

*(All "Now" items completed! Check "Soon" section for test coverage improvements)*

---

## 🧪 Soon (Test Coverage - 30-60 min each)

**Current coverage:** 89% (41 lines uncovered). **Target:** 92-95% on core simulation logic.

**📍 For detailed test coverage work, see [NEXT_SESSION.md](NEXT_SESSION.md) Path A (Foundation)**

### System Test: Multi-Map Victory Journey
**Current**: Only one system test (`test_system_three_hobbits_escape_single_rider`), written pre-multi-map
**Gap**: No test verifying full 3-map journey with transitions
**Action**: Write `test_system_all_hobbits_complete_three_map_journey()`
**Test scenario**:
- Call `_run_simulation_loop(max_ticks=500)` with favorable spawn config
- Verify `outcome == "victory"` (not just reaching first exit)
- Verify hobbits traverse all 3 maps
- Check event log contains 2 "map_transition" events + 1 "victory" event
**Coverage target**: Lines 982-1016 (transition logic, final victory detection)
**Why**: Core feature needs end-to-end validation
**Estimated**: 45 minutes

### System Test: Capture on Second Map
**Current**: No system test for defeat during map transitions
**Gap**: Defeat handling (lines 1019-1030) untested at system level
**Action**: Write `test_system_hobbits_captured_on_map_1_triggers_defeat()`
**Test scenario**:
- Mock/configure Map 1 with Nazgûl spawns surrounding hobbits
- Verify simulation ends with `outcome == "defeat"`
- Verify `hobbits_captured > 0`
**Coverage target**: Lines 1019-1030 (defeat handling in multi-map context)
**Why**: Negative path testing - verify failure conditions work across maps
**Estimated**: 30 minutes

### System Test: Timeout Handling
**Current**: Timeout branch (lines 972-975) untested
**Gap**: No test verifying simulation halts at max_ticks
**Action**: Write `test_system_timeout_returns_partial_progress()`
**Test scenario**:
- Set `max_ticks=10` (too short to complete journey)
- Verify `outcome == "timeout"`
- Verify `ticks == 10`
**Coverage target**: Lines 972-975
**Why**: Edge case validation, ensures infinite loops can't happen
**Estimated**: 20 minutes

### Coverage: Interactive Display Code
**Current**: Lines 1080-1097 (`run_simulation()` and `display_tick`) untested
**Decision needed**: Should we test interactive display?
**Options**:
1. **Exclude from coverage** - add `# pragma: no cover` (it's UI code)
2. **Smoke test only** - manual verification sufficient
3. **Mock test** - capture print output, verify format
**Recommendation**: Option 1 (exclude) - interactive display is outside core logic
**Estimated**: 10 minutes (add pragma comments)

---

## 🤔 Maybe (Needs Design Discussion - 1-3 hours)

These might add value but need validation. Playtest and feel the pain before implementing.

### Exit Buffer System (Skipped Test)
**Current**: Hobbits "stack" at exit position, then respawn together on next map
**Skipped test**: `test_escaped_hobbits_tracked_separately_from_active` (line 236)
**Question**: Should we track "permanently escaped" vs "still active in journey"?
**Use case**: Display "2/3 hobbits safe" when one gets captured on Map 1
**Current behavior**: If hobbit captured on Map 1, they're just... gone. No "2 escaped earlier" tracking.
**Design considerations**:
- Add `escaped_hobbits: set[HobbitId]` to WorldState?
- Update transition: move exiting hobbits to escaped set, spawn only active ones on next map?
- Victory condition: `len(escaped_hobbits) + len(hobbits) == starting_count`?
- Display: "3 hobbits active, 0 safe" → "2 active, 1 safe" → "0 active, 3 safe"
**Concern**: Adds complexity for unclear benefit - is current "all or nothing" fine?
**Decision needed**: Do we care about partial party escape tracking?
**Estimated**: 2-3 hours (design + implementation + tests)

### Variable Map Sizes
**Current**: All maps 20x20 (hardcoded in `WORLD_WIDTH`/`WORLD_HEIGHT`)
**Question**: Should maps grow/shrink for variety and pacing?
**Proposed progression**:
- Map 0 (Bag End): 15x15 - tight, claustrophobic, 1 Nazgûl
- Map 1 (Shire Forest): 20x20 - standard, 2 Nazgûl
- Map 2 (Crickhollow): 25x25 - sprawling, harder to navigate, 3 Nazgûl
**Changes needed**:
- Add `width`/`height` to `MapConfig`
- Update `create_map()` to use config dimensions
- Update terrain generation to respect variable size
- Update all position calculations to use `state.width`/`state.height`
**Concern**: More complexity in terrain generation, unclear gameplay benefit
**Decision needed**: Playtest current maps first - do they feel samey/repetitive?
**Estimated**: 1-2 hours (update MapConfig, refactor terrain, test all maps)

### Hobbit Pathfinding (Skipped Test)
**Current**: Hobbits move directly toward goal, may walk into Nazgûl
**Skipped test**: `test_hobbit_routes_around_nazgul_to_avoid_capture` (line 337)
**Question**: Should hobbits detect and avoid Nazgûl in their path?
**Current behavior**: "Dumb but fast" - hobbits flee when Nazgûl close, but don't anticipate collisions
**Proposed behavior**: Check 1-2 moves ahead, route around known Nazgûl positions
**Concern**:
- May be too "smart" - reduces challenge/drama
- Adds pathfinding complexity (A*, Dijkstra, or simple lookahead?)
- Could make game too easy if hobbits perfectly avoid threats
**Decision needed**: Is current movement causing frustrating/unfair captures?
**Recommendation**: Playtest first - if hobbits regularly walk into avoidable captures, revisit
**Estimated**: 3-4 hours (pathfinding algorithm + collision prediction + tests)

---

## 🔮 Later (New Features - 4+ hours)

Don't tackle these yet. Complete "Now" and "Soon" sections first.

### Old Man Willow Encounter
**Status**: Next major feature per `hobbit-sim-bombadil-design.md`
**Depends on**: Map transitions ✅ (complete)
**New concepts**:
- Entity states (alert/stunned)
- Ranged abilities (hypnosis)
- Rescue mechanics (Tom Bombadil's touch)
- Map triggers (on_enter spawns Old Man Willow)
**Design approach**: Add to Map 1 (Shire Forest) as scripted encounter
**Test strategy**: System test "4 hobbits enter forest → stunned → Tom spawns → rescued → continue"
**Estimated**: 6-8 hours (state system + abilities + Tom NPC + tests)

### Tom Bombadil Rescue System
**Status**: Second Bombadil phase
**Depends on**: Old Man Willow encounter (entity states + abilities)
**New concepts**:
- Touch-based abilities (range=1)
- Area effects (multiple targets)
- NPC spawning via map triggers
**Design approach**: Extract ability system from Old Man Willow, generalize
**Estimated**: 4-6 hours

### Barrow-wights Encounter
**Status**: Third Bombadil phase
**Depends on**: Tom Bombadil mechanics (area effects)
**New concepts**:
- Multiple enemies with same ability
- Feared state (enemies flee)
- Enemy AI state transitions
**Design approach**: Reuse ability framework, add enemy behavior system
**Estimated**: 6-8 hours

### Weathertop Encounter
**Status**: Fourth Bombadil phase (Aragorn + fire)
**Depends on**: Barrow-wights (enemy AI, area effects)
**New concepts**:
- Environmental effects (fire repels Nazgûl)
- Targeted wounding (Frodo-specific)
- Counterattack triggers
**Design approach**: Add environmental hazard system, conditional state transitions
**Estimated**: 8-10 hours

---

## ✅ Completed

*(Move items here with completion date)*

**2025-11-12**: Display entry point on maps (entry_position field + rendering)
**2025-11-12**: Show victory/defeat message after simulation completes
**2025-11-12**: Test for entry marker visibility after hobbits leave spawn
**2025-11-12**: Extract duplicate rendering logic to `_render_world_to_grid()` helper (refactor)
**2025-11-12**: Remove `show_hobbit_ids` parameter (always show hobbit IDs now)
**2025-11-12**: Replace `rivendell` field usages with `exit_position` in escape count logic
**2025-11-12**: Map transition system (3 maps, progressive difficulty, roguelike spawning)
**2025-11-12**: Unit tests for map transitions (4 new tests)
**2025-11-07**: Movement system documentation
**2025-11-07**: Movement/world constants extraction
**2025-11-05**: Hobbit dict migration, collision avoidance
**2025-11-05**: Nazgûl collision prevention

---

## Notes

**Philosophy**: "Test what you fear breaking" - pragmatic TDD
**Zone 1 friendly**: Features sized for sustainable, low-capacity sessions
**Coverage goal**: 92-95% on core simulation logic (interactive display excluded)
**Playtest often**: Run `uv run python hobbit_sim.py` to feel the changes
**YAGNI principle**: Don't add exit buffers/pathfinding/variable sizes until needed
**Test strategy**: System tests for user scenarios, unit tests for components

**Why "Now/Soon/Maybe/Later"?**
- **Now**: Bugs or missing polish, immediate user impact
- **Soon**: Test coverage gaps, technical debt
- **Maybe**: Might be over-engineering, validate need via playtesting first
- **Later**: Big features, wait until current foundation is solid

**Coverage interpretation**:
- **88% overall**: Good baseline
- **Uncovered lines 1080-1097**: Interactive display (UI code, can exclude)
- **Uncovered lines 931-949**: Internal rendering helper (covered via integration tests)
- **Uncovered lines 972-975, 1019-1030**: Edge cases (timeout, defeat) - add system tests

**Next recommended session** (60-90 min):
1. Fix entry point rendering (15 min)
2. Add victory/defeat message (15 min)
3. Write multi-map system test (45 min)
→ Playtest manually, enjoy the polished experience!

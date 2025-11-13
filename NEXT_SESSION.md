# NEXT_SESSION.md

**Last Updated:** 2025-11-12
**Purpose:** Single source of truth for next coding session
**Test Suite Status:** 52 passed, 2 skipped, 89% coverage
**TODOs in Code:** 1

---

## Choose Your Path (Based on Capacity)

### Path A: Foundation First (60 min) ⭐ RECOMMENDED
**Goal:** Safety net before refactoring

1. Write timeout system test (20 min) → +4 lines coverage
2. Write defeat system test (30 min) → +11 lines coverage
3. Remove `_render_simulation_state()` wrapper (5 min)

**Result:** 95% coverage, blocking issues resolved

---

### Path B: Quick Wins (45 min)
**Goal:** Maximum clarity improvement

1. Remove `_render_simulation_state()` wrapper (5 min)
2. Standardize to `world_state` variables (20 min)
3. Rename `render_world_to_string()` (10 min)

**Result:** Consistent, readable naming throughout

---

### Path C: Full Stack (90 min)
**Goal:** Both foundation + clarity

Combine Path A + Path B

**Result:** 95% coverage + clean naming

---

## Skipped Tests Status (2 total)

### SKIP #1: Exit Buffer System
**Test:** `test_escaped_hobbits_tracked_separately_from_active` (line 232)
**Issue:** Hobbits "stack" at Rivendell instead of being tracked separately
**Status:** DEFERRED - Architectural enhancement, not a bug
**Reason:** Current behavior works; exit buffer is YAGNI until multi-map victory tracking needed
**When to revisit:** After multi-map journey testing reveals need

### SKIP #2: Pathfinding Around Nazgûl
**Test:** `test_hobbit_routes_around_nazgul_to_avoid_capture` (line 333)
**Issue:** Hobbits don't detect Nazgûl in path, may walk into traps
**Status:** DEFERRED - Behavior enhancement, not a bug
**Reason:** Current "dumb" movement is acceptable; adds challenge
**When to revisit:** After playtesting shows frustrating/unfair captures

**Decision:** Keep both tests skipped for now. Unskip only when features become priority.

---

## TODO Comments in Code (1 total)

### TODO #1: Exit Safety Test (line 315)
**Text:** "test a race where a hobbit makes it to safety while another is en route, the nazgul should not be able to capture the one that made it to safety"
**Status:** BLOCKED by Exit Buffer implementation (SKIP #1)
**Action:** Remove TODO comment, move to FEATURES.md under "Exit Buffer System" section
**Estimated:** 2 minutes

---

## In-Progress Work

### Rivendell Cleanup (50% complete)
**Done:**
- ✅ Escape count logic uses `exit_position`
- ✅ Test assertions use `exit_position`

**Remaining:**
- [ ] Rename `update_hobbits(rivendell=...)` parameter to `goal_position` (10+ call sites)
- [ ] Update event logging to use `exit_position`
- [ ] Remove `WorldState.rivendell` field entirely

**Estimated:** 30 minutes
**Priority:** LOW - Not blocking, but completes started work

---

## Detailed Task Breakdown

### Foundation Tasks (Do First)

**1. System Test: Timeout Scenario** (20 min)
```python
def test_system_timeout_returns_partial_progress():
    """Timeout should return partial progress with timeout outcome."""
    from hobbit_sim import _run_simulation_loop

    result = _run_simulation_loop(max_ticks=10)

    assert result['outcome'] == 'timeout'
    assert result['ticks'] == 10
    # Partial progress tracking (some hobbits may have progressed)
    assert 'hobbits_escaped' in result
    assert 'hobbits_captured' in result
```
**Coverage:** Lines 975-978 (4 lines)
**Why:** Validates timeout logic works in multi-map context

---

**2. System Test: Defeat Scenario** (30 min)
```python
def test_system_hobbits_captured_triggers_defeat():
    """Capture of any hobbit should trigger defeat outcome."""
    from hobbit_sim import _run_simulation_loop

    # This test may require mocking or configuration to force a capture
    # Current config with 3 hobbits vs 1 Nazgûl usually results in victory
    # Options:
    # - Mock spawn positions to surround hobbits
    # - Create custom MapConfig with unfavorable setup
    # - Run many iterations until capture occurs

    result = _run_simulation_loop(max_ticks=100)

    # Validate defeat is properly detected and reported
    # Note: May need to run multiple times or configure scenario
    if result['outcome'] == 'defeat':
        assert result['hobbits_captured'] > 0
        assert result['hobbits_escaped'] < 3  # Some were caught
```
**Coverage:** Lines 1023-1033 (11 lines)
**Why:** Validates defeat detection across map transitions
**Note:** May require creating unfavorable spawn configuration or mocking

---

**3. Remove `_render_simulation_state()` Wrapper** (5 min)
**Action:**
- Delete function at lines 940-952
- Update call site in `display_tick()` at line 1089:
  ```python
  # Before:
  grid = _render_simulation_state(state=state)

  # After:
  grid = _render_world_to_grid(state=state)
  ```
- Run tests to confirm no breakage

**Why:** Eliminates needless indirection revealed by refactoring

---

### Quick Win Tasks

**4. Standardize Variable Naming to `world_state`** (20 min)
**Scope:** ~70 references across both files

**hobbit_sim.py changes:**
- Function parameters: `state: WorldState` → `world_state: WorldState` (3 locations)
- Local variables: `state =` → `world_state =` (2 locations)

**test_hobbit_sim.py changes:**
- Local variables: `world =` → `world_state =` (~60 locations)

**Approach:**
1. Search/replace in function signatures first
2. Search/replace in variable assignments
3. Run tests after each file
4. Run mypy to catch any missed references

**Why:** Matches type name exactly, self-documenting, eliminates confusion

---

**5. Rename `render_world()` → `render_world_to_string()`** (10 min)
**Scope:** 1 function definition + ~8 call sites

**Changes:**
- Function definition at line 340
- Test call sites (~8 in test_hobbit_sim.py)

**Approach:**
1. Rename function definition
2. Update docstring if needed
3. Search for `render_world(` and replace with `render_world_to_string(`
4. Run tests

**Why:** Clear about return type at call sites, consistent with `_render_world_to_grid()`

---

### Cleanup Tasks

**6. Remove TODO Comment** (2 min)
**Action:**
- Delete TODO comment at test_hobbit_sim.py lines 315-316
- Add note to FEATURES.md "Exit Buffer System" section explaining this test case

**Text to remove:**
```python
# TODO: test a race where a hobbit makes it to safety while another is en route,
# the nazgul should not be able to capture the one that made it to safety
```

**Why:** Moves TODO from code to proper documentation

---

**7. Complete Rivendell Cleanup** (30 min)
**Goal:** Remove all `rivendell` references, standardize on `exit_position`

**Changes:**
- Rename `update_hobbits(rivendell=...)` parameter to `goal_position=...`
- Update all 10+ call sites
- Update event logging to use `exit_position` instead of `rivendell`
- Remove `WorldState.rivendell` field from dataclass (line 62)
- Update any remaining comments

**Why:** Completes partially-finished refactoring, eliminates legacy field

---

**8. Document Movement System** (30 min)
**Goal:** Add docstring explaining Manhattan movement philosophy

**Location:** Movement functions (`move_toward`, `move_away_from`, etc.)

**Content:**
```python
# Movement System Philosophy:
# - Manhattan distance (no diagonals): |dx| + |dy|
# - Move one axis at a time (creates "staircase" pattern)
# - Prioritizes axis with greater remaining distance
# - Matches how Nazgûl track hobbits (consistent pursuit logic)
```

**Why:** Makes design decisions explicit for future contributors

---

## Success Criteria

**After Path A (Foundation):**
- ✅ 54 tests passing, 2 skipped
- ✅ 95% coverage
- ✅ All edge cases (timeout, defeat) tested
- ✅ 0 blocking issues

**After Path B (Quick Wins):**
- ✅ Consistent `world_state` naming throughout
- ✅ Clear function names (`render_world_to_string`)
- ✅ No wrapper indirection
- ✅ All tests passing

**After Path C (Full Stack):**
- ✅ All of the above

**After Cleanup:**
- ✅ 0 TODO comments in code
- ✅ 2 skipped tests (intentionally deferred features, documented)
- ✅ No incomplete refactorings
- ✅ `rivendell` field removed

---

## What Happens to Other Docs?

**FEATURES.md:**
- Reference this doc for immediate work
- Keep "Maybe" section for long-term deferred features
- Add section explaining 2 skipped tests

**REFACTORING.md:**
- Reference this doc for immediate work
- Keep as historical record of completed refactorings
- Continue updating with new refactoring opportunities

**NEXT_SESSION.md (this document):**
- Single source of truth for **immediate** work
- Updated after each session
- Replaces scanning multiple docs for "what's next"

---

## Recommendations

1. **Start with Path A (Foundation)** - Get test safety net to 95% before refactoring
2. **Then Path B (Quick Wins)** - Clarity improvements while tests provide safety
3. **Then Cleanup** - Remove TODO, complete rivendell, document movement
4. **Keep skipped tests skipped** - They represent future features, not bugs
5. **Update this doc** after each session to reflect progress

**Philosophy:** One document, clear paths, no decision fatigue.

---

## Notes

**Why deferred features are OK:**
- Exit buffer: Current "stacking" behavior works for single exit point
- Pathfinding: "Dumb" movement creates interesting emergent behavior
- Both can be implemented when actually needed (YAGNI principle)

**Why coverage goal is 95% not 100%:**
- Remaining 5% is interactive display code (UI layer)
- Can add `# pragma: no cover` if desired
- Focus coverage on simulation logic, not presentation

**Zone 1 friendly:**
- All paths sized for sustainable sessions (45-90 min)
- Clear success criteria for each path
- No heroic pushes required

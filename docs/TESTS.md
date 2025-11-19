# Test Strategy & Training Corpus

## Philosophy

Tests serve dual purposes:
1. **Validation** - Ensure code works correctly
2. **Training Corpus** - Progressive difficulty scenarios that teach the "AI" (hobbit behavior system) to handle complexity

## Test Categories

### Baseline Tests (Must Always Pass)
These tests define the foundation - if these break, something fundamental is wrong.

- `test_create_world_returns_valid_state` - World initialization works
- `test_move_toward_moves_diagonally` - Basic movement primitives
- `test_move_away_from_uses_manhattan_movement` - Evasion primitives
- `test_is_valid_position` - Boundary and terrain checking
- `test_distance_calculations_use_manhattan_distance` - Distance consistency

### Training Corpus (Progressive Difficulty)

These tests represent scenarios of increasing complexity, ordered by difficulty:

#### Level 1: Single Hobbit, Single Threat
**Teaches**: Basic evasion, wall awareness

- ✅ `test_single_hobbit_escapes_single_nazgul` - Simple chase scenario
- ✅ `test_hobbit_evading_at_south_edge_doesnt_get_stuck` - Wall evasion (no terrain)
- ✅ `test_hobbit_evading_at_south_edge_with_terrain_doesnt_get_stuck` - Wall evasion (with terrain)

**What the AI learned**: Don't pin yourself against walls, use perpendicular escape

---

#### Level 2: Multi-Directional Threats
**Teaches**: Threat awareness from multiple angles

- ✅ `test_hobbit_with_threats_on_two_axes_doesnt_flee_into_trap` - Cornered by 2 Nazgûl
- ✅ `test_hobbit_threads_between_two_nazgul_to_reach_goal` - Navigate through gap
- ✅ `test_hobbit_navigates_through_three_nazgul_blockade` - Navigate around blockade

**What the AI learned**: Goal bias helps navigate toward safety even when multiple threats present. Hobbits are cautious (take long routes) but survive.

---

#### Level 3: Multiple Hobbits (Group Behavior)
**Teaches**: Coordination, collision avoidance

- ✅ `test_baseline_three_hobbits_can_reach_rivendell` - Group travel with obstacles
- ✅ `test_system_three_hobbits_escape_single_rider` - Group evasion
- ✅ `test_hobbits_at_rivendell_represent_exited_state` - Goal stacking allowed
- ⏭️ `test_hobbits_fleeing_to_corner_cannot_stack` - **NEXT**: Collision detection during evasion

**Current limitation**: Hobbits don't avoid each other during movement (will stack)

---

#### Level 4: Advanced Pathfinding (Future)
**Teaches**: Avoiding obvious traps, planning ahead

- ⏭️ `test_hobbit_routes_around_nazgul_to_avoid_capture` - Don't walk into enemies
- ⏭️ `test_escaped_hobbits_tracked_separately_from_active` - Exit buffer (architecture)

---

### Integration Tests
These test the full simulation stack:

- ✅ `test_current_simulation_configuration_completes` - Default config works
- ✅ `test_acceptance_full_simulation_succeeds` - Full `_run_simulation_loop()` path
  - Validates victory outcome, all hobbits escaped, no captures
  - **NEW (2025-11-19):** Verifies multi-map journey with 2 map transitions (0→1, 1→2)
  - **NEW (2025-11-19):** Validates cumulative tick count across all 3 maps (> 50 ticks total)

### Rendering Tests
Display layer validation:

- ✅ `test_render_grid_with_hobbits_and_nazgul` - Basic entity rendering
- ✅ `test_render_world_shows_terrain` - Terrain rendering
- ✅ `test_render_world_shows_hobbit_names` - Named hobbits (F, S, P, M)
- ⏭️ `test_render_grid_with_named_hobbits` - Individual hobbit symbols (future)

---

## Current AI Capabilities

**What Hobbits Can Do**:
- ✅ Move toward Rivendell when safe
- ✅ Detect nearby threats (distance ≤ 6)
- ✅ Flee directly away from threats (with goal bias)
- ✅ Use perpendicular escape when direct evasion blocked
- ✅ Navigate around terrain obstacles
- ✅ Thread through narrow gaps between threats (cautiously!)

**What Hobbits Cannot Do (Yet)**:
- ❌ Avoid stacking on each other during movement
- ❌ Detect Nazgûl positions to avoid walking into them
- ❌ Plan ahead beyond current step (purely reactive)
- ❌ Coordinate as a group (each acts independently)

---

## Test Naming Conventions

- `test_<entity>_<action>_<condition>` - Unit tests
  - Example: `test_hobbit_evading_at_south_edge_doesnt_get_stuck`

- `test_system_<scenario>` - Integration/system tests
  - Example: `test_system_three_hobbits_escape_single_rider`

- `test_baseline_<scenario>` - Hardcoded baseline (stable reference point)
  - Example: `test_baseline_three_hobbits_can_reach_rivendell`

- `test_acceptance_<feature>` - Full-stack acceptance tests
  - Example: `test_acceptance_full_simulation_succeeds`

---

## Adding New Training Scenarios

When adding a new test to the training corpus:

1. **Write the test** describing the scenario
2. **Run it** - expect failure (RED)
3. **Implement** just enough to pass (GREEN)
4. **Document here** what the AI learned
5. **Commit** with clear message

The test suite becomes a portfolio of progressive mastery.

---

## Future Training Scenarios (Bombadil Phase)

From `hobbit-sim-bombadil-design.md`:

### Old Man Willow
- Ranged state transitions (hypnosis → stunned)
- Touch-based rescue (Tom's wake_touch)
- Map trigger spawning

### Barrow-wights
- Area-effect abilities
- Multiple enemies with feared state
- Enemy fleeing behavior

### Weathertop
- Environmental effects (fire)
- Targeted wounding (Frodo-specific)
- Counterattack mechanics

---

## Test Quality Guidelines

**Good tests**:
- Clear scenario description in docstring
- Explicit setup (positions, goals, threats)
- Single responsibility (test one behavior)
- Deterministic (reproducible)

**Avoid**:
- Testing implementation details
- Brittle assertions (exact tick counts for complex scenarios)
- Coupling to internal function names (test behavior, not structure)

---

## Running Tests

```bash
# All tests
pytest test_hobbit_sim.py

# Specific test
pytest test_hobbit_sim.py::test_single_hobbit_escapes_single_nazgul -v

# With output (for debugging)
pytest test_hobbit_sim.py::test_name -s

# Training corpus only (tag-based, future)
pytest -m training_corpus

# Coverage
pytest --cov=hobbit_sim --cov-report=term-missing
```

---

**Last Updated**: 2025-11-19
**Test Count**: 54 total (52 passing, 2 skipped)
**Coverage**: 89%

### Recent Test Enhancements (2025-11-19)

**Multi-Map Journey Validation**
- Enhanced `test_acceptance_full_simulation_succeeds()` to verify hobbits actually travel through all 3 maps
- Added event collection infrastructure to `SimulationResult` for testing/analytics
- Fixed cumulative tick tracking bug (was showing only last map's ticks instead of total)

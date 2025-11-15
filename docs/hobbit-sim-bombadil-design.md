# Hobbit Simulation: Tom Bombadil Phase Design

## Vision
A **state-based simulation** following LOTR narrative beats, not a traditional combat system. No HP/damage numbers - just entity states and transitions. Each scene is a training kata for progressive system complexity.

## Core Entity States

### Hobbits
- `alert` - normal, can act
- `stunned` - incapacitated by hypnosis/trap/fear
- `wounded` - Frodo after Weathertop (mobile but damaged)

### Enemies
- `active` - threatening
- `feared` - fleeing/repelled  
- `defeated` - removed from encounter

## Spell/Ability Framework

Each ability defines:
- **Source entity** (who can cast)
- **Target state requirement** (what states can be affected)
- **Effect** (state transition)
- **Range** (touch, ranged, area-effect)

### Example Abilities

**Old Man Willow:**
- `hypnosis`: ranged, alert→stunned

**Tom Bombadil:**
- `wake_touch`: touch-range, stunned→alert
- `banish_evil`: ranged/area, active→feared (wights, Nazgûl)

**Nazgûl:**
- `fear_aura`: area-effect, alert→stunned
- `morgul_blade`: melee, alert→wounded (Frodo-specific)

**Fire (environmental):**
- `repel_wraith`: area-effect, Nazgûl→feared

## Narrative Progression as Training Curriculum

### Level 1: Old Man Willow
**System test:** "4 hobbits enter forest → get stunned by tree → Tom spawns → touches hobbits → all alert"

**New concepts:**
- Ranged state transitions (hypnosis)
- Touch-based healing
- Event-triggered entity spawning
- Map triggers

**Complexity:** Single threat, simple rescue pattern

---

### Level 2: Barrow-wights
**System test:** "4 hobbits enter downs → wights stun them → Tom spawns → casts banish → wights flee"

**New concepts:**
- Ranged rescue spell
- Multiple enemies
- Feared state and fleeing behavior
- Area-effect abilities

**Complexity:** Multiple enemies, area effects, enemy AI

---

### Level 3: Weathertop
**System test:** "Nazgûl encircle party → Aragorn lights fire → most Nazgûl feared → one stabs Frodo (wounded) → Frodo counterattacks → all Nazgûl flee"

**New concepts:**
- Environmental effects (fire)
- Targeted wounding (specific entity)
- Counterattack triggers
- Conditional state transitions

**Complexity:** Environmental interactions, specific targeting, chained reactions

---

### Future: Moria/Balrog
- Running/chase mechanics
- Timed escape sequences
- Unbeatable enemies
- Party splitting (Gandalf falls)

## Map Trigger System

Enables scene orchestration:

**Trigger types:**
- `on_enter` - step on tile/area
- `on_exit` - leave area
- `conditional` - check game state
- `repeatable` vs `one_shot`

**Event payloads:**
- Spawn entity (Bombadil appears)
- Apply state transition (all hobbits stunned)
- Change terrain (door opens)
- Transition map (next scene)

## Victory/Defeat Conditions

**Per-scene examples:**
- **Trapped:** All hobbits stunned, no rescuer present
- **Rescued:** All hobbits alert, threat neutralized
- **Escaped:** All enemies feared/defeated OR party reaches exit

## Implementation Strategy (Zone 1)

Each coding session:
1. **Pick one narrative beat**
2. **Write the system test** (describe the scene outcome)
3. **Implement just enough to pass** (TDD)
4. **Commit when green**
5. **Reflect and rest**

When flow stalls:
- Drop to simpler test (refactor existing)
- Switch domains (physical break)
- Stop and rest

The Git history becomes a portfolio artifact showing progressive mastery.

## Current Status

- ✅ Basic map navigation
- ✅ Nazgûl pursuit/evasion
- 🎯 **Next:** Old Man Willow encounter (ranged stun + touch rescue)
- 📋 **After:** Barrow-wights (area effects, multiple enemies)
- 📋 **Future:** Weathertop, Moria, beyond

## Design Principles

- **State over stats** - no HP math, just clean state machines
- **Narrative-driven** - book scenes as test cases
- **Incremental complexity** - each scene adds one new concept
- **Lore as guideline** - not canon-strict, but informed by source
- **Reusable systems** - abilities work across all encounters

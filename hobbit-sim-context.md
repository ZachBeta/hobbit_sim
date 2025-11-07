# Hobbit Sim - Development Context

**Date:** 2025-11-05  
**Week 3, Day 18** of dopamine detox  
**Status:** Ready to build, research phase complete

---

## Decision Made

**Focus on building hobbit sim, not playing Dwarf Fortress.**

- DF research complete → architectural patterns extracted
- Surface-level DF interaction only (wiki references when needed)
- Primary work: Build portfolio-quality Tolkien-inspired simulation
- Zone 1 sustainable work, good edge detection on this project

---

## Project Vision

### What This Is
A Lord of the Rings inspired hobbit life simulator focusing on peaceful Shire routines:
- Hobbits with names, homes, daily activities
- Social connections and community events
- Simple needs simulation (hunger, social, rest)
- Test-driven development approach
- Portfolio demonstration of system design + clean code

### What This Is NOT
- Not a Dwarf Fortress clone
- Not a combat/survival game
- Not a dungeon crawler
- Not a grid-based roguelike (initially)

### Unique Angle
Tolkien lore + clean Python architecture + TDD = portfolio differentiator

---

## Week 3 Immediate Goals (Zone 1 Quick Wins)

### Priority 1: Hobbit Naming System
```python
# Tolkien-appropriate name generation
first_names = ["Bilbo", "Frodo", "Samwise", "Merry", "Pippin", "Peregrin", "Meriadoc"]
surnames = ["Baggins", "Gamgee", "Took", "Brandybuck", "Boffin", "Bolger", "Proudfoot"]
# Generate combinations, maybe add families/relationships
```

### Priority 2: Map Structure (Location Graph)
```python
# Named locations with connections (not grid coordinates yet)
locations = {
    'bag_end': {
        'name': 'Bag End',
        'type': 'home',
        'exits': ['hobbiton']
    },
    'hobbiton': {
        'name': 'Hobbiton',
        'type': 'town',
        'exits': ['bag_end', 'green_dragon', 'bywater']
    },
    'green_dragon': {
        'name': 'The Green Dragon',
        'type': 'tavern',
        'exits': ['hobbiton']
    }
}
```

### Priority 3: Entity Structure
```python
# Simple hobbit entity (class or dict)
class Hobbit:
    def __init__(self, name, location):
        self.id = object()  # Unique identifier
        self.name = name
        self.location = location
        self.needs = {'hunger': 50, 'social': 50, 'rest': 50}
        self.activity = None
        self.home = None
```

**Approach:** Write tests first, then implement features.

---

## Key Architectural Patterns (From Research)

### 1. Entity Component System (ECS) - Simplified

**Core Concept:**
- Entities = unique IDs (not complex objects)
- Components = data dictionaries keyed by entity ID
- Systems = functions that operate on entities with specific components
- Composition over inheritance

**Python Implementation:**
```python
# Minimal ECS pattern
entity_id = object()  # Just a unique ID

# Components stored separately
components = {
    'position': {entity_id: 'hobbiton'},
    'name': {entity_id: "Bilbo Baggins"},
    'activity': {entity_id: "gardening"},
    'needs': {entity_id: {'hunger': 30, 'social': 60}}
}

# Systems operate on entities with specific components
def update_hunger(components):
    for entity_id, needs in components['needs'].items():
        needs['hunger'] += 1  # Hunger increases over time
```

**Why ECS:**
- Flexible: Easy to add new hobbit types or behaviors
- Maintainable: No inheritance hell
- Data-driven: Can serialize/load easily

### 2. Task Priority System (Dwarf Fortress Pattern)

**Core Concept:**
- Entities assigned one task at a time
- Priority-based decision making (no complex state machines)
- Idle entities look for next task

**Python Implementation:**
```python
def choose_action(hobbit, world_state):
    """Priority check from top to bottom"""
    # Critical needs first
    if hobbit.needs['hunger'] > 80:
        return Action.EAT
    
    # Social needs
    if hobbit.needs['social'] > 60:
        return Action.VISIT_NEIGHBOR
    
    # Location-based activities
    if hobbit.location == 'garden' and is_daytime():
        return Action.GARDEN
    
    if hobbit.location == 'green_dragon':
        return Action.SOCIALIZE
    
    # Default
    return Action.REST
```

**No state needed** - run priority list each turn, entity does "the right thing"

### 3. Turn-Based Simulation Loop

**Core Concept:**
- Each turn advances game time
- All entities get their turn
- World state updates
- Render/display

**Python Implementation:**
```python
def simulation_loop():
    current_turn = 0
    
    while running:
        current_turn += 1
        
        # 1. Each hobbit acts
        for hobbit in world.hobbits:
            action = choose_action(hobbit, world)
            execute_action(hobbit, action, world)
        
        # 2. Update world state
        update_needs(world.hobbits)
        check_events(world, current_turn)
        
        # 3. Render
        display_state(world)
        
        # 4. Wait for next turn (or user input)
        time.sleep(TURN_DELAY)
```

### 4. Map Data Structures

**Option A: Location Graph (START HERE)**
```python
# Named locations with connections
# Good for: Small worlds, narrative focus, simple navigation
locations = {
    'bag_end': {'exits': ['hobbiton'], 'type': 'home'},
    'hobbiton': {'exits': ['bag_end', 'green_dragon'], 'type': 'town'}
}
```

**Option B: Grid Map (LATER IF NEEDED)**
```python
# 2D coordinate system
# Good for: Spatial puzzles, pathfinding, larger worlds
map_grid[x][y] = {'terrain': 'grass', 'entity_id': hobbit_123}
```

**Decision:** Start with location graph. Add grid later only if needed.

---

## Technical Guidelines

### Test-Driven Development
```python
# Write tests FIRST
def test_hobbit_gets_hungry():
    hobbit = Hobbit("Bilbo", "bag_end")
    initial_hunger = hobbit.needs['hunger']
    
    advance_turn(hobbit)
    
    assert hobbit.needs['hunger'] > initial_hunger

# THEN implement
def advance_turn(hobbit):
    hobbit.needs['hunger'] += 1
```

### Simple Before Complex
- Dict-based components before full ECS framework
- Location names before grid coordinates
- Single file before multiple modules
- Text output before fancy rendering

### Zone 1 Development Pattern
- Small features that work quickly
- Good edge detection (stop when tired)
- Iterative refinement
- Sustainable pace, not heroic pushes

---

## Shire-Specific Design

### Locations to Include
**Homes:**
- Bag End (Bilbo's home)
- #3 Bagshot Row (Sam's home)
- Brandy Hall (Merry's home)
- Great Smials (Pippin's home)

**Community Spaces:**
- Hobbiton (town center)
- The Green Dragon (tavern)
- Bywater (village)
- The Mill
- Market

**Natural Areas:**
- Gardens
- Party Field
- The Water (river)
- The Hill

### Activities to Simulate
**Daily Routines:**
- Gardening
- Cooking/Eating (multiple meals!)
- Pipe-smoking
- Reading/Writing
- Walking/Visiting

**Social Events:**
- Birthday parties
- Market days
- Tavern gatherings
- Neighbor visits

**Hobbit Needs:**
- Hunger (needs 6+ meals per day!)
- Social (community-oriented)
- Rest (comfort-loving)
- Routine (love predictability)

---

## What to Avoid

### Technical Anti-Patterns
❌ **Over-engineering:** Full ECS framework before basic sim works
❌ **Premature optimization:** Worrying about performance with 10 hobbits
❌ **Feature creep:** Combat systems, complex crafting, etc.
❌ **Inheritance hell:** `HobbitWarrior extends Hobbit extends Entity extends GameObject...`

### Process Anti-Patterns
❌ **Playing Dwarf Fortress instead of building**
❌ **Researching more instead of coding**
❌ **Perfect architecture before first working version**
❌ **Pushing into Zone 2-3 when capacity flags**

### Scope Anti-Patterns
❌ **Trying to simulate all of Middle-earth**
❌ **Complex economic systems**
❌ **Detailed combat mechanics**
❌ **3D rendering or advanced graphics**

---

## Success Metrics (Week 3)

### Minimum Viable Progress
- [ ] Hobbits have names (generated or assigned)
- [ ] Map has named locations with connections
- [ ] Hobbits can move between locations
- [ ] Basic turn-based loop running
- [ ] Some tests written and passing

### Nice to Have
- [ ] Multiple hobbits with different routines
- [ ] Simple needs system (hunger tracking)
- [ ] Activity selection based on location
- [ ] Text-based display of world state

### Stretch Goals
- [ ] Social connections between hobbits
- [ ] Events (birthday party, market day)
- [ ] Save/load simulation state

---

## November Context (Why This Matters)

### Portfolio Building Theme
- **Goal:** Produce job-ready evidence by Feb/March 2026
- **Strategy:** Sustained Zone 1 capacity building
- **Filter:** Does this produce portfolio evidence? Can I sustain it?

### Week 3 Focus
- Gentle expansion in Zone 0/1
- Maintain cognitive gains from Week 2
- Consistent 4-6hr coding per week target
- Body baseline ~7-8k steps, spirit daily practices

### Capacity State
- **Mind:** 6-7hr mixed cognitive load ceiling
- **Zone 1:** Hobbit sim has good edge detection
- **Zone 2:** Architectural decisions need careful dosing
- **Avoid:** Zone 3+ work causes crashes

---

## Reference Resources

### When Stuck on Architecture
- **ECS Patterns:** https://www.roguebasin.com/index.php/Entity_Component_System
- **Python Roguelike Tutorial:** https://rogueliketutorials.com/tutorials/tcod/v2/
- **DF Wiki (reference only):** https://www.dwarffortresswiki.org/

### Tolkien Lore
- Appendices of LOTR (family trees, calendars, cultures)
- The Hobbit (Shire daily life descriptions)
- Prologue of LOTR (hobbit customs and characteristics)

### Ask Agent For
- Specific design pattern questions
- Code review and suggestions
- Architecture decisions when stuck
- "How did X handle Y?" research queries

---

## Starting Point Recommendations

### Session 1: Basic Entity System
```python
# File: entities.py
class Hobbit:
    """A hobbit entity in the Shire simulation"""
    def __init__(self, first_name, surname, home_location):
        self.id = object()
        self.name = f"{first_name} {surname}"
        self.location = home_location
        self.home = home_location
        self.needs = {'hunger': 50, 'social': 50, 'rest': 50}
        self.current_activity = None

# File: test_entities.py
def test_hobbit_creation():
    hobbit = Hobbit("Bilbo", "Baggins", "bag_end")
    assert hobbit.name == "Bilbo Baggins"
    assert hobbit.location == "bag_end"
    assert hobbit.needs['hunger'] == 50
```

### Session 2: Location Graph
```python
# File: world.py
class World:
    """The Shire world state"""
    def __init__(self):
        self.locations = {
            'bag_end': {
                'name': 'Bag End',
                'type': 'home',
                'exits': ['hobbiton'],
                'owner': None  # Will be set to Bilbo
            },
            'hobbiton': {
                'name': 'Hobbiton',
                'type': 'town',
                'exits': ['bag_end', 'green_dragon']
            },
            'green_dragon': {
                'name': 'The Green Dragon',
                'type': 'tavern',
                'exits': ['hobbiton']
            }
        }
        self.hobbits = []
        self.current_turn = 0

# File: test_world.py
def test_location_connections():
    world = World()
    bag_end = world.locations['bag_end']
    assert 'hobbiton' in bag_end['exits']
```

### Session 3: Basic Simulation Loop
```python
# File: simulation.py
def run_simulation(world, num_turns=10):
    """Run the simulation for a specified number of turns"""
    for turn in range(num_turns):
        world.current_turn += 1
        print(f"\n--- Turn {world.current_turn} ---")
        
        for hobbit in world.hobbits:
            # Simple action: just report location
            print(f"{hobbit.name} is at {hobbit.location}")
        
        # Wait or continue
        input("Press Enter for next turn...")
```

---

## Key Mantras

**"Working with what is, not what should be"**
- Build what works, not perfect architecture upfront

**"Zone 1 builds capacity, Zone 2 tests it"**
- Tinkering and exploration, not execution pressure

**"1.01^365"**
- Small consistent wins compound over time

**"Tolkien lore > DF mechanics"**
- Let the Shire guide design, not fortress simulation

**"Test-driven, feature-focused"**
- Tests first, minimal implementation, iterate

---

## Next Actions

1. **Open Claude Code** with this context document
2. **Create project structure:** `hobbit_sim/` directory
3. **Start with tests:** `test_entities.py` 
4. **Implement minimal Hobbit class**
5. **Verify tests pass**
6. **Add location graph**
7. **Iterate**

**Remember:** You have good edge detection on this project. Trust the Zone 1 flow. Stop when capacity flags. This is sustainable portfolio building, not a sprint.

---

**Last Updated:** 2025-11-05  
**For:** Claude Code continuation  
**Zone:** 1 (sustainable building)  
**Mood:** Ready to Strike the Earth Code

🏡🌿💻✨

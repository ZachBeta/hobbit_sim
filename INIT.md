# Hobbit Nazgûl Escape Simulation - Project Context

## Project Vision
An autonomous simulation (no player input) of hobbits fleeing from Nazgûl, attempting to reach Rivendell. Pure theater - we watch the drama unfold.

## Core Design Principles
1. **Easy mode first** - avoid scope creep and over-engineering
2. **Single file initially** - maximize simplicity
3. **Print statements before visualizations** - text output first
4. **Hardcoded before configurable** - get it working, then make it flexible
5. **No performance optimization until actually slow** - pure Python is fine

## Version 0.1 Scope (Minimum Viable Simulation)

### What we're building:
- Grid-based ASCII art display
- 4 hobbits starting at "The Shire" (one corner)
- 9 Nazgûl starting scattered across the map
- Rivendell at opposite corner (goal destination)

### Behavior per tick:
- **Hobbits:** Move toward Rivendell (simple pathfinding or just move toward goal)
- **Nazgûl:** Move toward nearest hobbit
- **Collision:** If Nazgûl touches hobbit, hobbit is caught (removed)
- Print grid state each tick

### Win/Lose Conditions:
- **Win:** Any hobbit reaches Rivendell
- **Lose:** All hobbits caught before reaching safety

### Explicitly NOT in V0.1:
- No player control
- No inventory system
- No combat mechanics
- No items or power-ups
- No complex pathfinding algorithms
- No performance optimization
- No fancy visualization (just ASCII)

## Technical Constraints
- Pure Python (most training data, batteries included)
- Single file to start
- Can use basic Python stdlib (no exotic dependencies initially)

## Development Approach
Build incrementally. Each version adds ONE feature, test it, verify it feels good, then continue or pivot.

**After V0.1 works, possible next features (one at a time):**
- Obstacles on the map (forests, rivers)
- Hobbits have simple behaviors (group together, hide, sprint)
- Nazgûl have different speeds or detection ranges
- Simple visualization upgrade (pygame, tkinter, or web canvas)
- Config file for map size, entity counts, speeds
- Multiple scenarios/maps

## Context for Development
This project is part of mind fitness work during long COVID recovery. The goal is to find flow state in coding through:
- Playful, intrinsically interesting problems
- Clear forward progress without mystery debugging
- Well-trodden paths in training data (Python basics, grid simulations, simple agents)
- Avoiding performance traps and scope creep that lead to frustration

The ping-pong pairing approach with Cursor in ask mode should:
- Break problems into tiny pieces
- Maintain conversational flow
- Create small wins without pressure
- Allow breaks as needed

## Implementation Notes
Start with the absolute simplest thing:
1. Can we print a grid?
2. Can we place entities on the grid?
3. Can we make them move?
4. Do the rules work?

Each question is its own micro-milestone. Build confidence through tiny successes.

## Success Metrics
- Code runs without errors
- Simulation produces interesting outcomes
- Process feels engaging (not frustrating)
- Forward momentum maintained across sessions

Remember: The goal isn't perfect code. The goal is rebuilding coding capacity through playful, sustainable practice.
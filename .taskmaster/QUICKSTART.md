# Taskmaster-AI Quick Start Guide

## Getting Started

Taskmaster-ai is now configured for your Digital Ant Farm project with 12 initial MVP tasks. Here's how to get started:

## 1. Install Taskmaster-AI

If you haven't already installed taskmaster-ai:

```bash
pip install taskmaster-ai
```

## 2. Initialize in Your Project

Navigate to your project directory and initialize:

```bash
cd /Users/jakepfitsch_home/Documents/digital_ant_farm
taskmaster init
```

## 3. View Your Tasks

```bash
# View all tasks
taskmaster list

# View only critical tasks
taskmaster list --priority critical

# View tasks by category
taskmaster list --category core-engine
```

## 4. Start Working

Begin with the most critical tasks for MVP:

```bash
# Start working on the core ant entity system
taskmaster start TASK-002

# Start the pheromone system (also critical)
taskmaster start TASK-005
```

## 5. Track Progress

```bash
# Update task status
taskmaster update TASK-002 --status in-progress

# Add notes to tasks
taskmaster note TASK-002 "Implemented basic ant movement mechanics"

# Mark tasks as complete
taskmaster complete TASK-001
```

## 6. Recommended First Steps

1. **Complete TASK-001** (Project Setup) first
2. **Work on TASK-002** (Core Ant Entity) - this is the foundation
3. **Implement TASK-005** (Pheromone System) - critical for ant behavior
4. **Add TASK-004** (Food Sources) - provides the resource system
5. **Create TASK-003** (Colony Management) - coordinates everything

## 7. Add New Tasks

As you develop, you may need to add new tasks:

```bash
# Add a new task
taskmaster add "Implement ant collision detection" \
  --category core-engine \
  --priority high \
  --phase mvp \
  --description "Add collision detection between ants to prevent overlapping"
```

## 8. Useful Commands

```bash
# View task details
taskmaster show TASK-002

# Search tasks
taskmaster search "pheromone"

# View task history
taskmaster history TASK-002

# Export tasks to different formats
taskmaster export --format csv
taskmaster export --format json
```

## 9. Project-Specific Tips

### Phase Management
- Focus on MVP tasks first (phase: mvp)
- Use `taskmaster list --phase mvp` to see only MVP tasks
- Mark tasks as complete before moving to V2 features

### Priority Order
1. **Critical**: TASK-002 (Ant Entity), TASK-005 (Pheromone)
2. **High**: TASK-001 (Setup), TASK-003 (Colony), TASK-004 (Food)
3. **Medium**: UI and visualization tasks
4. **Low**: Documentation and optimization (can be done in parallel)

### Category Focus
- Start with `core-engine` tasks
- Move to `simulation` tasks
- Add `ui-interface` tasks after core systems work
- Include `performance` optimization throughout

## 10. Integration with Development

### Git Integration
```bash
# Create a branch for a task
git checkout -b feature/TASK-002-ant-entity

# Commit with task reference
git commit -m "TASK-002: Implement basic ant movement mechanics"
```

### Daily Workflow
1. `taskmaster list --status in-progress` - see what you're working on
2. `taskmaster start TASK-XXX` - start a new task
3. `taskmaster update TASK-XXX --status done` - complete tasks
4. `taskmaster list --status todo` - see what's next

## 11. Performance Tracking

Monitor your progress toward the MVP goals:

```bash
# See completion status
taskmaster stats

# View tasks by priority
taskmaster list --priority critical --status todo

# Check phase progress
taskmaster list --phase mvp --status done
```

## 12. Getting Help

```bash
# View taskmaster help
taskmaster --help

# Get help for specific commands
taskmaster add --help
taskmaster list --help
```

## Next Steps

1. Start with TASK-001 (Project Setup)
2. Follow the dependency order outlined in the README
3. Use the project structure template in `.taskmaster/templates/`
4. Keep tasks updated as you progress
5. Add new tasks as needed during development

Happy coding! 🐜 
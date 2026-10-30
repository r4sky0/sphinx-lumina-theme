# Diagrams

Lumina supports [Mermaid](https://mermaid.js.org/) diagrams via the `sphinxcontrib-mermaid` extension. Diagrams automatically adapt to the current light or dark theme.

## Choosing a Diagram Type

| You want to show…               | Use this         | Example                          |
|---------------------------------|------------------|----------------------------------|
| Decision logic, workflows       | Flowchart        | Build pipelines, if/else logic   |
| Message passing between systems | Sequence diagram | API calls, authentication flows  |
| Object relationships            | Class diagram    | Data models, inheritance         |
| Transitions between states      | State diagram    | Order lifecycle, document review |
| Project timelines               | Gantt chart      | Release planning, sprints        |
| Database schema                 | ER diagram       | Table relationships              |
| Proportions of a whole          | Pie chart        | Survey results, usage breakdown  |
| Hierarchical ideas              | Mindmap          | Feature planning, brainstorming  |

## Flowchart

Show one decision at a time. This documentation pipeline makes the happy path and the revision loop easy to follow.

The MyST syntax:

```markdown
```{mermaid}
flowchart LR
    accTitle: Publish documentation
    accDescr: Build the documentation, fix any warnings, then publish a clean build.
    source[Write docs] --> build[Build]
    build --> checks{Warnings?}
    checks -->|None| publish([Publish])
    checks -->|Found| revise[Revise]
    revise --> build
    classDef ready stroke-width:2px
    class publish ready
```
```

### Node shapes

Mermaid supports different shapes to convey meaning:

### Direction options

Control layout direction with `TB` (top-bottom), `BT`, `LR` (left-right), or `RL`:

## Sequence Diagram

Show how systems communicate over time.

### With activation and notes

## Class Diagram

Document object relationships, inheritance, and data models.

### With inheritance

## State Diagram

Show how an entity transitions between states.

## Gantt Chart

Visualize project timelines and task dependencies.

## Entity-Relationship Diagram

Document database schema and table relationships.

### Relationship notation

| Symbol   | Meaning            | Example                 |
|----------|--------------------|-------------------------|
| `||--||` | One to one         | User has one profile    |
| `||--o{` | One to many        | Author has many posts   |
| `}o--o{` | Many to many       | Students and courses    |
| `||--o|` | One to zero or one | User may have an avatar |

## Pie Chart

Show proportional breakdowns. These illustrative counts use distinct colors and direct values so the proportions are easy to compare.

The MyST syntax:

```markdown
```{mermaid}
pie title Chart Title
    "Label A" : 40
    "Label B" : 35
    "Label C" : 25
```
```

## Mindmap

Organize ideas hierarchically.

The MyST syntax:

```markdown
```{mermaid}
mindmap
    root((Central Topic))
        Branch 1
            Leaf A
            Leaf B
        Branch 2
            Leaf C
```
```

## Tips for Writing Diagrams

# Diagrams

Lumina supports [Mermaid](https://mermaid.js.org/) diagrams via the `sphinxcontrib-mermaid` extension. Diagrams automatically adapt to the current light or dark theme.

:::{tip}
See {doc}`../extensions` for installation and setup instructions.
:::

## Choosing a Diagram Type

```{list-table}
:header-rows: 1
:widths: 25 40 35

* - You want to show…
  - Use this
  - Example
* - Decision logic, workflows
  - Flowchart
  - Build pipelines, if/else logic
* - Message passing between systems
  - Sequence diagram
  - API calls, authentication flows
* - Object relationships
  - Class diagram
  - Data models, inheritance
* - Transitions between states
  - State diagram
  - Order lifecycle, document review
* - Project timelines
  - Gantt chart
  - Release planning, sprints
* - Database schema
  - ER diagram
  - Table relationships
* - Proportions of a whole
  - Pie chart
  - Survey results, usage breakdown
* - Hierarchical ideas
  - Mindmap
  - Feature planning, brainstorming
```

## Flowchart

Model decision logic, pipelines, and workflows.

```{mermaid}
flowchart LR
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```

The MyST syntax:

````markdown
```{mermaid}
flowchart LR
    A[Start] --> B{Decision}
    B -->|Yes| C[Action 1]
    B -->|No| D[Action 2]
    C --> E[End]
    D --> E
```
````

### Node shapes

Mermaid supports different shapes to convey meaning:

```{mermaid}
flowchart LR
    A[Rectangle] --> B(Rounded)
    B --> C{Diamond}
    C --> D([Stadium])
    D --> E[[Subroutine]]
    E --> F[(Database)]
```

### Direction options

Control layout direction with `TB` (top-bottom), `BT`, `LR` (left-right), or `RL`:

```{mermaid}
flowchart TB
    A[Top] --> B[Middle]
    B --> C[Bottom]
```

## Sequence Diagram

Show how systems communicate over time.

```{mermaid}
sequenceDiagram
    participant Browser
    participant Server
    participant Database

    Browser->>Server: GET /api/users
    Server->>Database: SELECT * FROM users
    Database-->>Server: Result set
    Server-->>Browser: JSON response
```

### With activation and notes

```{mermaid}
sequenceDiagram
    participant Client
    participant Auth
    participant API

    Client->>Auth: Login request
    activate Auth
    Auth-->>Client: JWT token
    deactivate Auth

    Note over Client: Stores token locally

    Client->>API: Request with token
    activate API
    API->>Auth: Validate token
    Auth-->>API: Valid
    API-->>Client: Protected data
    deactivate API
```

## Class Diagram

Document object relationships, inheritance, and data models.

```{mermaid}
classDiagram
    class Document {
        +String title
        +String content
        +build()
    }
    class Theme {
        +String name
        +apply()
    }
    class Extension {
        +String name
        +setup(app)
    }
    Document --> Theme : uses
    Document --> Extension : loads
```

### With inheritance

```{mermaid}
classDiagram
    class Animal {
        +String name
        +int age
        +makeSound()*
    }
    class Dog {
        +String breed
        +makeSound()
        +fetch()
    }
    class Cat {
        +bool indoor
        +makeSound()
        +purr()
    }
    Animal <|-- Dog
    Animal <|-- Cat
```

## State Diagram

Show how an entity transitions between states.

```{mermaid}
stateDiagram-v2
    [*] --> Draft
    Draft --> Review : Submit
    Review --> Published : Approve
    Review --> Draft : Request changes
    Published --> Archived : Archive
    Published --> Draft : Revise
    Archived --> [*]
```

## Gantt Chart

Visualize project timelines and task dependencies.

```{mermaid}
gantt
    title Project Timeline
    dateFormat  YYYY-MM-DD
    section Planning
        Requirements     :done, req, 2024-01-01, 2024-01-14
        Design           :done, des, after req, 14d
    section Development
        Implementation   :active, impl, after des, 30d
        Testing          :test, after impl, 14d
    section Release
        Documentation    :doc, after test, 7d
        Deployment       :deploy, after doc, 3d
```

## Entity-Relationship Diagram

Document database schema and table relationships.

```{mermaid}
erDiagram
    PROJECT ||--o{ DOCUMENT : contains
    DOCUMENT ||--|{ PAGE : has
    PAGE ||--o{ SECTION : includes
    PROJECT {
        string name
        string version
    }
    DOCUMENT {
        string title
        string format
    }
    PAGE {
        string title
        int order
    }
```

### Relationship notation

```{list-table}
:header-rows: 1
:widths: 20 40 40

* - Symbol
  - Meaning
  - Example
* - `||--||`
  - One to one
  - User has one profile
* - `||--o{`
  - One to many
  - Author has many posts
* - `}o--o{`
  - Many to many
  - Students and courses
* - `||--o|`
  - One to zero or one
  - User may have an avatar
```

## Pie Chart

Show proportional breakdowns.

```{mermaid}
pie title Documentation Formats
    "Markdown (MyST)" : 60
    "reStructuredText" : 30
    "Jupyter Notebooks" : 10
```

The MyST syntax:

````markdown
```{mermaid}
pie title Chart Title
    "Label A" : 40
    "Label B" : 35
    "Label C" : 25
```
````

## Mindmap

Organize ideas hierarchically.

```{mermaid}
mindmap
    root((Sphinx Theme))
        Layout
            Sidebar
            TOC
            Breadcrumbs
        Styling
            Dark mode
            Accent colors
            Typography
        Search
            Pagefind
            Built-in
        Extensions
            MyST
            sphinx-design
            Mermaid
```

The MyST syntax:

````markdown
```{mermaid}
mindmap
    root((Central Topic))
        Branch 1
            Leaf A
            Leaf B
        Branch 2
            Leaf C
```
````

## Tips for Writing Diagrams

:::{tip}
- **Keep diagrams simple.** If a diagram has more than 15 nodes, consider splitting it into multiple diagrams.
- **Use meaningful labels.** `Auth Service` is better than `S2`.
- **Choose the right direction.** `LR` (left-right) works well for workflows; `TB` (top-bottom) for hierarchies.
- **Test in both themes.** Lumina auto-switches colors, but verify your diagrams are readable in both light and dark modes.
:::

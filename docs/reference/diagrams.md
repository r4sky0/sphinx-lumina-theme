# Diagrams

Lumina supports [Mermaid](https://mermaid.js.org/) diagrams via the `sphinxcontrib-mermaid` extension. Diagrams automatically adapt to the current light or dark theme.

:::{tip}
See {doc}`/extensions/mermaid` for installation and setup instructions. Use the **fullscreen ⛶ button** to inspect a dense diagram at a larger size. Press **Escape** to return to the page.
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

Show one decision at a time. This documentation pipeline makes the happy path and the revision loop easy to follow.

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

The MyST syntax:

````markdown
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
````

### Node shapes

Mermaid supports different shapes to convey meaning:

```{mermaid}
flowchart LR
    accTitle: Shapes communicate roles
    accDescr: An input goes through validation, a decision, a build step, storage, and completion.
    A[Input] --> B(Validate) --> C{Ready?}
    C --> D[[Build]] --> E[(Artifacts)] --> F([Done])
```

### Direction options

Control layout direction with `TB` (top-bottom), `BT`, `LR` (left-right), or `RL`:

```{mermaid}
flowchart TB
    accTitle: Documentation hierarchy
    accDescr: A documentation hub links to tutorials, guides, and reference material.
    hub[Documentation] --> tutorials[Tutorials]
    hub --> guides[Guides]
    hub --> reference[Reference]
```

## Sequence Diagram

Show how systems communicate over time.

```{mermaid}
sequenceDiagram
    accTitle: Search a documentation site
    accDescr: A reader searches locally through Pagefind and follows a matching page.
    autonumber
    participant Reader
    participant Search
    participant Index as Pagefind index
    Reader->>Search: Enter a query
    Search->>Index: Find matching pages
    Index-->>Search: Ranked results
    Search-->>Reader: Titles and excerpts
```

### With activation and notes

```{mermaid}
sequenceDiagram
    accTitle: Preview documentation changes
    accDescr: Saving a source file triggers a rebuild; the browser reloads the preview when it is ready.
    participant Author
    participant Builder as Sphinx
    participant Browser
    Author->>Builder: Save a source file
    activate Builder
    Note over Builder: Rebuild changed pages
    Builder-->>Browser: Preview ready
    deactivate Builder
    Browser-->>Author: Reload the page
```

## Class Diagram

Document object relationships, inheritance, and data models.

```{mermaid}
classDiagram
    accTitle: Documentation building blocks
    accDescr: A document uses a theme and loads extensions.
    direction LR
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
    accTitle: Sphinx builder inheritance
    accDescr: HTML and LaTeX builders share the Builder interface.
    direction LR
    class Builder {
        <<abstract>>
        +build()
        +write()
    }
    class HTMLBuilder {
        +render_page()
    }
    class LaTeXBuilder {
        +write_document()
    }
    Builder <|-- HTMLBuilder
    Builder <|-- LaTeXBuilder
```

## State Diagram

Show how an entity transitions between states.

```{mermaid}
stateDiagram-v2
    accTitle: Document review lifecycle
    accDescr: A draft is reviewed, published, and archived. A review can return it to draft.
    direction LR
    [*] --> Draft
    Draft --> Review : Submit
    Review --> Published : Approve
    Review --> Draft : Request changes
    Published --> Archived : Archive
    Archived --> [*]
```

## Gantt Chart

Visualize project timelines and task dependencies.

```{mermaid}
gantt
    accTitle: Documentation release plan
    accDescr: Planning is complete, writing is active, and review precedes publication.
    title Documentation release
    dateFormat YYYY-MM-DD
    axisFormat %d %b
    tickInterval 1week
    todayMarker off
    section Plan
        Outline       :done, plan, 2026-09-01, 5d
    section Create
        Write guides  :active, write, after plan, 12d
        Add examples  :examples, after plan, 8d
    section Ship
        Review        :review, after write, 5d
        Publish       :milestone, after review, 0d
```

## Entity-Relationship Diagram

Document database schema and table relationships.

```{mermaid}
erDiagram
    accTitle: Documentation content model
    accDescr: A project contains documents, and each document has one or more pages.
    direction LR
    PROJECT ||--o{ DOCUMENT : contains
    DOCUMENT ||--|{ PAGE : has
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

Show proportional breakdowns. These illustrative counts use distinct colors and direct values so the proportions are easy to compare.

```{mermaid}
:config: {"themeVariables": {"pie1": "#6ee7b7", "pie2": "#93c5fd", "pie3": "#fcd34d"}}

pie showData
    accTitle: Example documentation sources
    accDescr: An illustrative project uses 60 Markdown pages, 30 reStructuredText pages, and 10 notebooks.
    title Documentation sources
    "MyST Markdown" : 60
    "reStructuredText" : 30
    "Notebooks" : 10
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
    root((Documentation))
        Learn
            Tutorials
            Examples
        Build
            Guides
            Configuration
        Look up
            API reference
            Changelog
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
- **Add a text alternative.** Use `accTitle` and `accDescr` in supported diagram types, and explain the conclusion in the surrounding prose.
- **Keep diagrams simple.** If a diagram has more than 15 nodes, consider splitting it into multiple diagrams.
- **Use meaningful labels.** `Auth Service` is better than `S2`.
- **Choose the right direction.** `LR` (left-right) works well for workflows; `TB` (top-bottom) for hierarchies.
- **Test in both themes.** Lumina auto-switches colors, but verify your diagrams are readable in both light and dark modes.
:::

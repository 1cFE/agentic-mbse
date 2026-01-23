---
document: SysML_KerMLSpec
generated: 2026-01-13T00:19:29Z
source_checksum: sha256:2796da486d533910f40546364526267677e24b4f9d8bcc54dd33e8662127d4f1
total_lines: 13958
depth: 3
section_count: 111
---

# SysML_KerMLSpec Index

## 0 Preface
**Lines:** 778-807

Provides organizational background on OMG (Object Management Group), a standards consortium that produces specifications like UML and CORBA, along with contact information and instructions for obtaining specifications and reporting issues.

## 1 Scope
**Lines:** 808-821

KerML (Kernel Modeling Language) is an application-independent modeling language with formal mathematical semantics for system modeling, featuring constructs for structuring models (relationships, namespaces), classification-based semantics, and common modeling capabilities (associations, behaviors). The language uses a textual syntax parsed to abstract syntax, with semantics defined through a Semantic Library that provides ontological meaning—allowing KerML to serve as a kernel for building specialized, syntactically diverse but semantically integrated modeling languages.

## 2 Conformance
**Lines:** 822-836

Defines conformance requirements for KerML models and modeling tools, specifying four conformance levels: Abstract Syntax (required), Concrete Syntax, Semantic, and Model Interchange (required), with rules for how models must be represented and validated against the specification.

## 3 Normative References
**Lines:** 837-862

Lists external standards and specifications that KerML/SysML v2 normatively references, including OMG specifications (MOF, OCL, fUML, Alf, XMI), data formats (JSON, ZIP, UUID), cryptographic hash algorithms (MD5, SHA, BLAKE), character encoding standards (ISO 10646), and the Systems Modeling API specification.

## 4 Terms and Definitions
**Lines:** 863-866

Indicates that terminology definitions are distributed throughout the specification document rather than being collected in a dedicated glossary section.

## 5 Symbols
**Lines:** 867-870

Specifies that the concrete syntax for KerML is defined in subclause 8.2, serving as a brief reference pointer rather than containing substantive content itself.

## 6 Introduction
**Lines:** 871-872 | **Subsections:** 6.1, 6.2, 6.3

SysML v2 is a general-purpose modeling language for MBSE, specified as a metamodel extending KerML (replacing v1's UML profile approach), with enhanced precision, expressiveness, and interoperability. The document organization covers user-oriented constructs (Clause 7), normative metamodel specification including concrete/abstract syntax and semantics (Clause 8), and model libraries for systems-specific semantics and domain-specific reference models (Clause 9).

### 6.1 Language Architecture
**Lines:** 873-888

Covers KerML's three-layer syntax architecture (Root, Core, Kernel) and its semantic foundation based on mathematical logic and a Semantic Library written in KerML itself, enabling consistent model interpretation across users and tools.

### 6.2 Document Organization
**Lines:** 889-899

Describes the organization of the KerML specification document: Clause 7 covers user-level language constructs (informative), Clause 8 specifies the normative metamodel (grammar, abstract syntax, formal semantics), Clause 9 defines the Kernel Model Libraries (Semantic, Data Type, Function libraries), and Clause 10 specifies file-based interchange format.

### 6.3 Acknowledgements
**Lines:** 900-958

Credits and attribution for KerML specification development, listing the original KerML Working Group leaders (Bock, Galey, Cole), primary document authors (Seidewitz, Bock, Cole, Gomes, de Koning, Molnár), submitting organizations (including IBM, INCOSE, Lockheed Martin, PTC), SST leadership roles, and tool/infrastructure supporters who used CATIA No Magic and OpenMBEE for preparation.

## 7 Language Description
**Lines:** 959-962 | **Subsections:** 7.1, 7.2, 7.3, 7.4

Based on the content I read, here's the summary: Informative description of KerML language constructs and their usage, covering the Root, Core, and Kernel layers. Defines foundational concepts including elements, relationships, ownership hierarchies, namespaces, and naming conventions (element IDs, names, short names), with examples of textual notation syntax.

### 7.1 Language Description Overview
**Lines:** 963-974

Provides an informative, non-normative description of KerML organized by Root, Core, and Kernel layers, explaining how language constructs and the Kernel Model Library are used to build models. Includes references to normative metamodel specifications and uses stylistic conventions (code font, boldface keywords) for textual notation examples.

### 7.2 Root
**Lines:** 975-976 | **Subsections:** 7.2.1, 7.2.2, 7.2.3, 7.2.4, 7.2.5

[Summary generation timed out]

#### 7.2.1 Root Overview
**Lines:** 977-980

Defines the foundational syntactic capabilities of KerML: elements, relationships between elements, annotations, and namespace membership. These constructs provide structural organization for models but have no semantic meaning themselves—semantics are added by the Core and Kernel layers built on top of Root.

#### 7.2.2 Elements and Relationships
**Lines:** 981-1043

Defines the core graph structure of KerML models: elements as nodes, relationships as edges connecting related elements, with ownership semantics that cascade deletions through ownership trees. Covers element identification (element ID, alias IDs, names, short names), naming syntax (basic names, unrestricted quoted names, escape sequences), element bodies for nesting owned elements, and relationship directionality (source/target elements, binary relationships).

#### 7.2.3 Dependencies
**Lines:** 1044-1069

Dependencies model client-supplier relationships between elements where changes to suppliers may affect clients, declared with `dependency` keyword followed by optional name, `from` (clients), and `to` (suppliers) qualified name lists. Useful for representing abstract architectural relationships like layer dependencies in a stack.

#### 7.2.4 Annotations
**Lines:** 1070-1143

Annotations define relationships between annotated elements and annotating elements (comments, textual representations, or metadata) that provide additional information. Comments have textual bodies with optional locales and can be documentation (`doc`), while textual representations (`rep`) express elements in specified languages like "kerml", "ocl", or "alf".

#### 7.2.5 Namespaces
**Lines:** 1144-1262

Namespaces are elements that contain other elements via membership relationships, supporting owned members, imported members (via membership or namespace imports), and aliases. Covers namespace declaration syntax, visibility modifiers (public/protected/private), root namespaces (implicit, unowned containers for top-level elements), qualified/unqualified name resolution, recursive imports, and filtered imports with boolean conditions.

### 7.3 Core
**Lines:** 1263-1264 | **Subsections:** 7.3.1, 7.3.2, 7.3.3, 7.3.4

The Core layer in KerML defines the fundamental constructs for modeling systems, introducing **types** (which classify things in a modeled system), **classifiers**, **features** (which classify relations between things), and **specialization relationships** that enable taxonomies and inheritance of features from general to specific types.

#### 7.3.1 Core Overview
**Lines:** 1265-1272

Introduces the Core layer's classification-based semantics for modeling systems, where **types** classify things, **classifiers** are types that classify entities like cars or people, and **features** are types that classify relations between things (including chained relations). Covers **specialization relationships** (subclassification, subsetting, redefinition, feature typing) that enable taxonomies with feature inheritance from general to specific types.

#### 7.3.2 Types
**Lines:** 1273-1454

Defines types as classifiers whose extents contain instances, with necessary/sufficient conditions determining membership. Covers type declarations (abstract, multiplicity, sufficiency via `all`), specialization (inheritance via `:>` or `specializes`), conjugation (reverses input/output feature directions via `~`), disjoining (mutually exclusive extents), feature membership (owned features vs member features), and set operations on extents (unions, intersects, differences).

#### 7.3.3 Classifiers
**Lines:** 1455-1500

Classifiers are types that classify things in a modeled system (as opposed to features which model relations), with subclassification being the specialization relationship between classifiers. Classifiers use the `classifier` keyword, default to inheriting from `Base::Anything` if no explicit superclassifier is specified, and support conjugation and multiple inheritance via `specializes` or `:>` syntax.

#### 7.3.4 Features
**Lines:** 1501-1776

Defines **Features** as types that relate domain instances to co-domain values, covering feature declaration syntax (typing with `:`, subsetting with `:>`, redefinition with `:>>`), multiplicity/ordering/uniqueness modifiers, directional keywords (`in`/`out`/`inout`), and property keywords (`derived`, `abstract`, `composite`, `portion`, `var`, `const`). Also covers feature chaining (dot notation for navigating nested features), feature inverting (declaring inverse relationships like parent/children), and type featuring (explicitly specifying a feature's domain types).

### 7.4 Kernel
**Lines:** 1777-1778 | **Subsections:** 7.4.1, 7.4.2, 7.4.3, 7.4.4, 7.4.5, 7.4.6, 7.4.7, 7.4.8, 7.4.9, 7.4.10, 7.4.11, 7.4.12, 7.4.13, 7.4.14

The KerML Kernel (Section 7.4) extends the Core layer with specialized classifiers: **data types** (immutable values without spatiotemporal existence), **classes** (occurrences existing in time/space), **associations** (reified relationships), **structures**, **behaviors** (change specifications), **functions** (behaviors yielding results), **expressions**, **interactions**, **connectors**, **feature values**, **multiplicities**, **metadata**, and **packages**—defining their syntax keywords and implicit library specializations.

#### 7.4.1 Kernel Overview
**Lines:** 1779-1788

Defines the Kernel layer's specialized classifiers: **data types** (value semantics), **classes** (existence in time/space), and **associations** (reified relationships). Classes divide into **structures** (constrain changes) and **behaviors** (specify changes), with **functions** as result-yielding behaviors and **interactions** combining behaviors with associations. Kernel semantics are defined through implicit specializations of library types (e.g., classes subclassify `Occurrence`, behaviors subclassify `Performance`).

#### 7.4.2 Data Types
**Lines:** 1789-1808

Defines **data types** as classifiers for immutable data values that exist outside time/space, declared with the `datatype` keyword. Data types are disjoint from classes and associations, default to specializing `DataValue`, and their features default to subsetting `dataValues`.

#### 7.4.3 Classes
**Lines:** 1809-1834

Classes are classifiers for occurrences that exist in time and space with persistent identity, declared using the `class` keyword and defaulting to specialize `Occurrences::Occurrence`. Covers variable features (`var`) whose values can change over an occurrence's lifetime, constant features (`const`) with unchanging values, and the constraint that class-typed features cannot also have data type types.

#### 7.4.4 Structures
**Lines:** 1835-1854

Structures are classes that classify objects (a kind of occurrence) and typically constrain how instances and their relations can change over time, in contrast to behaviors which describe change. Declared with the `struct` keyword, structures default to specializing `Objects::Object`, and features typed by structures default to subsetting `Objects::objects`.

#### 7.4.5 Associations
**Lines:** 1855-1968

Associations are classifiers that define links between things, with binary associations having exactly two ends (source and target types) and n-ary associations having more. The section covers association declaration syntax using `assoc` keyword, cross subsetting for bidirectional navigation between related types, cross feature multiplicity constraints, owned cross features, association inheritance rules, and association structures (`assoc struct`) for link objects whose end features are constant but non-end features can change over time.

#### 7.4.6 Connectors
**Lines:** 1969-2115

Connectors are features typed by associations that represent "instance-specific" relationships between features within the same domain instance, with their values (links) restricted to connecting things identified by related features on that same instance. The section covers binary connectors, binding connectors (which require source and target to have equal values, typed by `SelfLink`), and successions (which order occurrences in time, typed by `HappensBefore`), along with detailed declaration syntax including the `connector`, `binding`, and `succession` keywords, connector ends with `references`/`::>` notation, and shorthand forms using `from`/`to` or `first`/`then`.

#### 7.4.7 Behaviors
**Lines:** 2116-2183

Behaviors are classes that classify performances (occurrences spread across space and time), supporting parameters with directional flow (in/out/inout), steps typed by other behaviors, and temporal ordering via succession connectors. Steps are features typed by behaviors that can be nested, connected by flows, and must follow specific parameter redefinition rules when specializing parent behaviors.

#### 7.4.8 Functions
**Lines:** 2184-2299

Functions are behaviors that produce results via a designated result parameter, with expressions being steps typed by functions that evaluate to results. Covers function, expression, predicate (Boolean-result functions), boolean expression, and invariant declarations with keywords `function`, `expr`, `predicate`, `bool`, and `inv`.

#### 7.4.9 Expressions
**Lines:** 2300-2569

Covers KerML expression tree structure and notation, including invocation expressions, feature reference expressions, literal expressions, and null expressions as tree nodes. Details operator expressions (conditional, binary, unary, classification, metaclassification, extent), primary expressions (index, sequence, feature chain, collect, select, function operation), base expressions, and literal expression syntax for Boolean, string, integer, rational, and infinity values.

#### 7.4.10 Interactions
**Lines:** 2570-2631

Interactions are behaviors that also function as associations, classifying performances that link occurrences to specify how participants affect each other and collaborate. The section covers transfers (interactions carrying payload values between occurrences), flows (steps that are binary connectors transferring values between output and input features), and succession flows (flows constrained by temporal ordering), along with their declaration syntax using `interaction`, `flow`, and `succession flow` keywords.

#### 7.4.11 Feature Values
**Lines:** 2632-2681

Feature values define membership relationships between features and value expressions, specifying how features obtain their values through four variants: bound (`=`) or initial (`:=`), and fixed or default. Bound values create implicit binding connectors asserting equivalence with the expression result, while initial values only bind at starting snapshots (for variable features), and default values apply during instance construction when no explicit values are provided.

#### 7.4.12 Multiplicities
**Lines:** 2682-2717

Multiplicities specify cardinalities (number of instances) of a type using range notation `[lowerBound..upperBound]`, where bounds can be literal values or feature references, and `*` represents infinity (with `[*]` equivalent to `[0..*]`). Multiplicity features can be declared with the `multiplicity` keyword and attached to types either in their declaration or body.

#### 7.4.13 Metadata
**Lines:** 2718-2799

Metadata provides a mechanism for attaching structured, tool-specific or domain-specific information to model elements without affecting instance-level semantics, using metadata features typed by metaclasses (declared with `metaclass` keyword) and applied via `@` annotations or `#` user-defined keywords. Special `SemanticMetadata` metaclasses can automatically add implicit specializations to annotated types based on a `baseType` binding.

#### 7.4.14 Packages
**Lines:** 2800-2843

Packages are namespaces for grouping elements without instance-level semantics, supporting filter conditions (Boolean expressions) to selectively import members based on metadata or abstract syntax metaclass properties. Library packages (marked with `library` keyword) are reusable across models, with `standard` reserved for official Kernel Model Libraries.

## 8 Metamodel
**Lines:** 2844-2845 | **Subsections:** 8.1, 8.2, 8.3, 8.4

Defines how the SysML metamodel extends KerML, covering the concrete syntax (textual EBNF notation and graphical notation), abstract syntax (metaclasses and their properties), and semantics (relating abstract syntax to the Systems Model Library).

### 8.1 Metamodel Overview
**Lines:** 2846-2865

Normative specification of the KerML metamodel covering three facets: concrete syntax (textual notation for modelers), abstract syntax (linguistic terms and their relations), and semantics (interpretation of models using mathematical logic). Organized into Root, Core, and Kernel layers, with naming conventions for metaclasses and properties throughout the specification.

### 8.2 Concrete Syntax
**Lines:** 2866-2867 | **Subsections:** 8.2.1, 8.2.2, 8.2.3, 8.2.4, 8.2.5

Defines the KerML textual notation grammar using EBNF, covering lexical structure (whitespace, notes, tokens), syntactic structure for mapping text to abstract syntax, and name resolution rules organized by the Root, Core, and Kernel layers.

#### 8.2.1 Concrete Syntax Overview
**Lines:** 2868-2905

KerML's concrete syntax is a textual notation parsed into abstract syntax using EBNF grammars, with lexical rules defining tokens (whitespace, notes, tokens) and syntactic rules mapping token sequences to model elements. The grammar is organized into Root, Core, and Kernel layers, with productions using property assignment notation (`p = Element`, `p += Element`) to synthesize abstract syntax elements.

#### 8.2.2 Lexical Structure
**Lines:** 2906-2989

Defines KerML's lexical structure: line terminators, whitespace, comments (`//`, `//*`, `/*`), name syntax (basic and unrestricted with escape sequences), numeric and string literals, reserved keywords (about 100 words like `abstract`, `class`, `feature`, `import`), and operator symbols with their tokenization rules.

#### 8.2.3 Root Concrete Syntax
**Lines:** 2990-3171

Defines the concrete (textual) syntax grammar rules for KerML's root elements including: element identification and relationship bodies, dependency declarations, annotations (comments, documentation, textual representations), namespace structure (visibility, members, aliases, qualified names, imports with filtering), and the complete name resolution algorithm for qualified names (local/global namespaces, visible vs full resolution, handling of specializations and feature chainings).

#### 8.2.4 Core Concrete Syntax
**Lines:** 3172-3273

Defines the concrete grammar rules for KerML's core elements: **Types** (with abstract/sufficient modifiers, specialization, conjugation, disjoining, and set operations like unions/intersects/differences), **Classifiers** (with subclassification), and **Features** (with direction, multiplicity, typing, subsetting, redefinition, chaining, and inverting). Specifies the textual syntax for declaring these elements and their relationships.

#### 8.2.5 Kernel Concrete Syntax
**Lines:** 3274-3548

KerML concrete syntax grammar rules for defining data types, classes, structures, associations, connectors (including binding connectors and successions), behaviors, steps, functions, expressions, predicates, interactions, flows, feature values, multiplicities, metadata, and packages. Includes comprehensive operator expression syntax with operator-to-library-function mappings (Table 5), operator precedence rules (Table 6), and primary expression operators (Table 7).

### 8.3 Abstract Syntax
**Lines:** 3549-3550 | **Subsections:** 8.3.1, 8.3.2, 8.3.3, 8.3.4

[Summary generation timed out]

#### 8.3.1 Abstract Syntax Overview
**Lines:** 3551-3579

KerML abstract syntax is a MOF-compliant UML model organized into three layered packages (Root, Core, Kernel) with element and relationship hierarchies. It defines three constraint types: derivation constraints (compute derived property values), semantic constraints (may be satisfied by implied relationships), and validation constraints (required for proper semantic interpretation).

#### 8.3.2 Root Abstract Syntax
**Lines:** 3580-4308

Defines the fundamental KerML abstract syntax metaclasses: Element (base constituent with identity, ownership, naming, and relationships), Relationship (directed connections between elements with source/target), Dependency (client-supplier relationships), AnnotatingElement/Annotation/Comment/Documentation/TextualRepresentation (metadata and documentation attachments), and Namespace/Membership/Import infrastructure (scoping, visibility, and member resolution including recursive imports).

#### 8.3.3 Core Abstract Syntax
**Lines:** 4309-5483

Defines the core abstract syntax for Types in KerML, including Type (the base class for classification), Multiplicity (cardinality constraints), and type relationships: Specialization (subtype/supertype), Conjugation (input/output reversal), Disjoining (mutual exclusion), Unioning, Intersecting, and Differencing (set operations on type instances). Also covers Classifiers as Types that classify things and their Feature relationships.

#### 8.3.4 Kernel Abstract Syntax
**Lines:** 5484-7315

Defines KerML abstract syntax for core classifier types (DataType, Class, Structure), relationships (Association, AssociationStructure), connectors (Connector, BindingConnector, Succession), and behaviors (Behavior, Step, ParameterMembership), including their attributes, specialization constraints, and required base library types.

### 8.4 Semantics
**Lines:** 7316-7317 | **Subsections:** 8.4.1, 8.4.2, 8.4.3, 8.4.4

Defines the formal semantics for KerML models through a three-layer approach: Root (syntactic foundation), Core (mathematical semantics grounded in set theory and first-order logic), and Kernel (semantics via Model Library relationships). Specifies four categories of semantic constraints (specialization, redefinition, type-featuring, and binding-connector) with implied relationships, plus mathematical interpretation rules for Types, Classifiers, and Features based on model-theoretic vocabulary, universe, and interpretation functions.

#### 8.4.1 Semantics Overview
**Lines:** 7318-7337

KerML semantics define how models are interpreted to make statements about modeled systems (existing or planned), using a three-layer approach: Root Layer (syntactic foundation, no semantic interpretation), Core Layer (grounded in mathematical semantics via the Base library package), and Kernel Layer (semantics defined through the Kernel Model Library).

#### 8.4.2 Semantic Constraints and Implied Relationships
**Lines:** 7338-7360

Defines four categories of semantic constraints in KerML that enforce required relationships: (1) specialization constraints linking user elements to Kernel Semantic Library types, (2) redefinition constraints between features in user models, (3) type-featuring constraints for TypeFeaturing relationships, and (4) binding-connector constraints requiring BindingConnectors between features. Also explains how tools should insert implied relationships to satisfy constraints while avoiding redundancy.

#### 8.4.3 Core Semantics
**Lines:** 7361-7662

Defines the mathematical framework for KerML Core semantics using model-theoretic first-order logic, specifying how Types, Classifiers, and Features are interpreted as sequences over a universe with markings. Covers semantic constraints (specialization, subsetting, redefinition), implied relationships to base library elements (Anything, things), and formal rules for feature interpretation including multiplicity, ordering, uniqueness, inversion, and feature chaining.

#### 8.4.4 Kernel Semantics
**Lines:** 7663-8539

Kernel semantics are defined by mapping Kernel Layer constructs to Core Layer patterns through specialization and redefinition constraints, with required relationships to Kernel Semantic Model Library elements (e.g., DataTypes must specialize Base::DataValue, Classes must specialize Occurrences::Occurrence, Behaviors must specialize Performances::Performance). The section includes comprehensive tables of semantic constraints and their implied relationships, plus detailed semantics for data types, classes, structures, associations, connectors, behaviors, functions, and expressions.

## 9 Model Libraries
**Lines:** 8540-8541 | **Subsections:** 9.1, 9.2, 9.3, 9.4

Defines KerML's three standard model libraries: the Semantic Library (providing foundational types like `Anything`, `DataValue`, `Occurrence`, and behavioral elements for model semantics), the Data Type Library (standard data types like `Boolean`, `Integer`, `Real`, `String`), and the Function Library (functions operating on those data types). These reusable libraries establish the base type hierarchy and semantic foundations that all user models inherit.

### 9.1 Model Libraries Overview
**Lines:** 8542-8558

Model libraries are reusable collections of library models; KerML includes three standard libraries: Semantic, Data Type, and Function libraries. The section also specifies how element IDs must be constructed as name-based UUIDs for normative interchange, ensuring stable identifiers across different serialization formats.

### 9.2 Semantic Library
**Lines:** 8559-8560 | **Subsections:** 9.2.1, 9.2.2, 9.2.3, 9.2.4, 9.2.5, 9.2.6, 9.2.7, 9.2.8, 9.2.9, 9.2.10, 9.2.11, 9.2.12, 9.2.13, 9.2.14, 9.2.15, 9.2.16, 9.2.17

The Semantic Library defines the foundational KerML model elements that underpin the language's type system, including the root classifier `Anything`, base data types (`DataValue`), occurrences (things that exist in time/space), objects, performances, transfers, control flow, state machines, clocks, observation, triggers, spatial frames, and metaobjects—all of which user models implicitly specialize.

#### 9.2.1 Semantic Library Overview
**Lines:** 8561-8570

The Semantic Library provides foundational KerML models that define the semantics of the metamodel, including hierarchies for Types (Anything, DataValue), Occurrences (things existing in time/space), Objects, Performances/Behaviors, Transfers/Flows, and control/state coordination patterns. These library models establish specialization hierarchies that user models must conform to and can be extended for domain-specific applications like systems modeling.

#### 9.2.2 Base
**Lines:** 8571-8788

Defines the root of the KerML type hierarchy: `Anything` (most general Classifier), `things` (most general Feature), `DataValue`/`dataValues` (for values distinguished only by relationships), and standard multiplicity ranges (`zeroOrOne`, `exactlyOne`, `oneToMany`, `zeroToMany`). Also introduces the `self` feature that relates each thing to itself and `naturals` as the basis for multiplicities.

#### 9.2.3 Links
**Lines:** 8789-8956

Defines the KerML library model for Links (association instances): `Link` is the most general association with participants, `BinaryLink` specializes it to exactly two ends (source/target), and `SelfLink` further specializes for when both ends are the same thing (used by BindingConnectors to specify features with identical values).

#### 9.2.4 Occurrences
**Lines:** 8957-9741

Defines **Occurrences** as the foundational abstraction for things existing in time and space, including concepts of Lives (maximal portions), time/space slices and snapshots, and temporal-spatial relationships (HappensBefore, HappensDuring, OutsideOf, InsideOf, Within, Without). Provides associations and features for modeling how occurrences relate temporally (predecessors/successors, coincidence) and spatially (boundaries, interiors, dimensions), with detailed element definitions for each relationship type.

#### 9.2.5 Objects
**Lines:** 9742-10019

Objects are Occurrences occupying a single region of time and space, serving as the most general Structure type, with subtypes including LinkObjects (Objects that are also Links with permanent participants), and spatial primitives (Body, Surface, Curve, Point) distinguished by innerSpaceDimension (3, 2, 1, 0). StructuredSpaceObjects decompose into hierarchical cells (faces, edges, vertices) that can form closed boundaries when cells properly mate along their boundaries.

#### 9.2.6 Performances
**Lines:** 10020-10457

Performances are occurrences that can span disconnected space-time regions, serving as the most general Behavior with features for subperformances, involved objects, and performers. Evaluations are performances that produce results (typed by Functions), with specialized variants for booleans, literals, nulls, and metadata access.

#### 9.2.7 Transfers
**Lines:** 10458-10792

Transfers are Performances and BinaryLinks that carry payloads between source and target Occurrences, with FlowTransfers specifically picking up from sourceOutput and dropping off at targetInput features, supporting options like instant transfer (isInstant), move vs copy semantics (isMove), and push-triggered starts (isPush). The section defines Transfer, FlowTransfer, MessageTransfer, TransferBefore, SendPerformance, and AcceptPerformance elements along with their corresponding flow features (transfers, flowTransfers, messageTransfers, transfersBefore, flowTransfersBefore).

#### 9.2.8 Feature Referencing Performances
**Lines:** 10793-11070

Defines Behaviors for reading and writing Feature values on Occurrences at Performance completion time, including `FeatureAccessPerformance` (read values), `FeatureWritePerformance` (replace values), `FeatureMonitorPerformance` (wait for value changes), and specialized Boolean evaluation monitors that detect when evaluation results change to specific values.

#### 9.2.9 Control Performances
**Lines:** 11071-11260

Control flow behaviors for sequencing steps in SysML v2: **DecisionPerformance** (selects exactly one outgoing succession path), **MergePerformance** (joins multiple incoming succession paths), **IfPerformance** variants (conditional execution with then/else clauses based on BooleanEvaluation), and **LoopPerformance** (iterative body execution controlled by whileTest and untilTest boolean evaluations).

#### 9.2.10 Transition Performances
**Lines:** 11261-11377

Defines the semantics of conditional transitions between Occurrences, specifying how TransitionPerformances determine Succession values based on triggers, guards, and effects. Covers TransitionPerformance, NonStateTransitionPerformance, and TPCGuardConstraint elements with their features for modeling state transitions and conditional behavior execution.

#### 9.2.11 State Performances
**Lines:** 11378-11457

StatePerformances and StateTransitionPerformances define the semantic model for state-based behavior, specifying how states execute (entry, middle/do, exit steps), how transfers trigger transitions between states, and constraints like dispatch ordering and run-to-completion semantics. Key features include acceptable/accepted transfers for triggering exits, guards that execute between non-do middle steps and exit, and composition rules for nested state machines.

#### 9.2.12 Clocks
**Lines:** 11458-11685

Defines Clock structures for time quantification in occurrences, including abstract Clock with monotonically advancing currentTime, BasicClock using Real numbers, TimeOf/DurationOf functions for computing occurrence timing relative to clocks, and a universalClock singleton for default time reference.

#### 9.2.13 Observation
**Lines:** 11686-11873

Defines a framework for monitoring Boolean conditions and notifying observers when they change from false to true. Contains the ChangeSignal (condition to watch), ChangeMonitor (manages observations), ObserveChange (waits for condition changes and sends signals), and StartObservation/CancelObservation behaviors for controlling the observation lifecycle.

#### 9.2.14 Triggers
**Lines:** 11874-12027

Defines trigger functions for event-driven behavior: `TriggerWhen` for Boolean condition changes, `TriggerAt` for specific clock times, and `TriggerAfter` for time delays. Also defines `TimeSignal` as a specialized `ChangeSignal` for clock-based triggering.

#### 9.2.15 SpatialFrames
**Lines:** 12028-12359

Defines spatial frames of reference for 3D positioning, including `SpatialFrame` (a 3D body acting as reference frame), `CartesianSpatialFrame`, and functions for computing position/displacement vectors (`PositionOf`, `DisplacementOf`, `CurrentPositionOf`, `CurrentDisplacementOf`) of points relative to frames at specific times.

#### 9.2.16 Metaobjects
**Lines:** 12360-12445

Defines metaclasses and features for typing syntactic and semantic metadata. Includes `Metaobject` (the base metaclass for annotating elements), `metaobjects` (the base metadata feature), and `SemanticMetadata` (metadata requiring annotated elements to specialize a base type).

#### 9.2.17 KerML
**Lines:** 12446-12479

Defines the mapping rules for generating a reflective KerML model from the normative MOF abstract syntax, including how metaclasses, properties, generalizations, enumerations, and their various attributes (composite, derived, ordered, etc.) are transformed into corresponding KerML elements like Metaclass, Feature, DataType, and their relationships.

### 9.3 Data Type Library
**Lines:** 12480-12481 | **Subsections:** 9.3.1, 9.3.2, 9.3.3, 9.3.4

Defines the standard library of KerML data types including scalar values (Boolean, String, and a numeric hierarchy from Complex to Positive integers), collection types (Array, Bag, List, Map, Set, OrderedCollection), and vector value types (CartesianVectorValue, ThreeVectorValue).

#### 9.3.1 Data Types Library Overview
**Lines:** 12482-12485

Provides standard DataTypes for scalar, vector, and collection values used throughout SysML v2 models.

#### 9.3.2 Scalar Values
**Lines:** 12486-12733

Defines primitive scalar data types including Boolean, String, and a numeric type hierarchy (Complex → Real → Rational → Integer → Natural → Positive), all inheriting from ScalarValue as non-collection, non-structure primitives.

#### 9.3.3 Collections
**Lines:** 12734-13005

Defines standard Collection data types (Array, Bag, List, Set, Map, OrderedSet, OrderedMap, KeyValuePair) with their inheritance hierarchy, features, and ordering/uniqueness constraints—enabling nested collections unlike simple multiplicity-based sequences.

#### 9.3.4 Vector Values
**Lines:** 13006-13131

Defines vector value data types for SysML v2: abstract `VectorValue`, `NumericalVectorValue` (1D array of numerical values with optional dimension), `CartesianVectorValue` (Real elements with vector-space function support), `ThreeVectorValue` (dimension 3), and `CartesianThreeVectorValue` (Cartesian + dimension 3). These types support vector operations defined in VectorFunctions.

### 9.4 Function Library
**Lines:** 13132-13135 | **Subsections:** 9.4.1, 9.4.2, 9.4.3, 9.4.4, 9.4.5, 9.4.6, 9.4.7, 9.4.8, 9.4.9, 9.4.10, 9.4.11, 9.4.12, 9.4.13, 9.4.14, 9.4.15, 9.4.16, 9.4.17, 9.4.18

Defines library models of basic Functions that operate on DataTypes, which KerML operator expressions translate into. These library Functions can be specialized for domain-specific DataTypes while reusing the same KerML expression syntax.

#### 9.4.1 Function Library Overview
**Lines:** 13136-13139

Provides library models of basic Functions that operate on DataTypes from the Data Type Library, with KerML operator expressions translating to invocations of these Functions. Languages built on KerML can specialize these Functions for domain-specific DataTypes while reusing the same expression syntax.

#### 9.4.2 Base Functions
**Lines:** 13140-13155

Defines fundamental operations available on all values: equality (`==`, `!=`), identity (`===`, `!==`), string conversion (`ToString`), sequence indexing (`#`), concatenation (`,`), type checking (`istype`, `hastype`, `as`), and metadata access (`@`, `@@`, `meta`). These correspond to KerML expression notation operators.

#### 9.4.3 Data Functions
**Lines:** 13156-13171

Defines abstract base functions for all unary and binary operators in KerML expression notation that operate on DataValues, including arithmetic (`+`, `-`, `*`, `/`, `**`, `%`), comparison (`<`, `>`, `<=`, `>=`, `==`), logical (`not`, `xor`), bitwise (`~`, `|`, `&`, `^`), and utility functions (`max`, `min`, `..` range).

#### 9.4.4 Scalar Functions
**Lines:** 13172-13187

Defines abstract scalar functions that specialize DataFunctions for ScalarValue types, including arithmetic operators (+, -, *, /, **, ^, %), logical/bitwise operators (not, xor, ~, |, &), comparison operators (<, >, <=, >=), and utility functions (max, min, range '..').

#### 9.4.5 Boolean Functions
**Lines:** 13188-13199

Defines standard Boolean functions including logical operators (`not`, `xor`, `|`, `&`), equality comparison (`==`), and type conversion functions (`ToString`, `ToBoolean`) that correspond to KerML expression notation operators.

#### 9.4.6 String Functions
**Lines:** 13200-13215

KerML String Functions package: defines string concatenation (`+`), comparison operators (`<`, `>`, `<=`, `>=`, `==`), `Length`, `Substring`, and `ToString` functions operating on String values.

#### 9.4.7 Numerical Functions
**Lines:** 13216-13231

Abstract functions for arithmetic operations (`+`, `-`, `*`, `/`, `**`, `^`, `%`), comparison operators (`<`, `>`, `<=`, `>=`), utility functions (`isZero`, `isUnit`, `abs`, `max`, `min`), and collection aggregations (`sum`, `product`) on NumericalValue types, all specializing corresponding ScalarFunctions.

#### 9.4.8 Complex Functions
**Lines:** 13232-13243

Defines SysML v2 functions for Complex number operations: constructors (`rect`, `polar`), accessors (`re`, `im`, `abs`, `arg`), arithmetic operators (`+`, `-`, `*`, `/`, `**`, `^`), comparison (`==`), conversion (`ToString`, `ToComplex`), and aggregation (`sum`, `product`), all specializing the general numerical function interfaces.

#### 9.4.9 Real Functions
**Lines:** 13244-13259

Defines functions for Real number operations including arithmetic operators (+, -, *, /, **, ^), comparison operators (<, >, <=, >=, ==), mathematical functions (abs, sqrt, floor, round, min, max), and type conversions (ToString, ToInteger, ToRational, ToReal), all specializing ComplexFunctions or NumericalFunctions.

#### 9.4.10 Rational Functions
**Lines:** 13260-13275

Defines functions for Rational number operations including construction (`rat`), decomposition (`numer`, `denom`), arithmetic (`+`, `-`, `*`, `/`, `**`, `^`), comparison (`<`, `>`, `<=`, `>=`, `==`), rounding (`floor`, `round`), conversion (`ToString`, `ToInteger`, `ToRational`), and aggregation (`sum`, `product`, `gcd`, `min`, `max`, `abs`), all specializing RealFunctions.

#### 9.4.11 Integer Functions
**Lines:** 13276-13291

Defines Integer-specific arithmetic operations (`+`, `-`, `*`, `/`, `**`, `%`), comparison functions (`<`, `>`, `<=`, `>=`, `max`, `min`), range generation (`..`), type conversions (`ToString`, `ToNatural`, `ToInteger`), and collection aggregations (`sum`, `product`), all specializing corresponding RationalFunctions or other base function packages.

#### 9.4.12 Natural Functions
**Lines:** 13292-13303

Defines arithmetic operations (`+`, `*`, `/`, `%`), comparison functions (`<`, `>`, `<=`, `>=`, `max`, `min`, `==`), and string conversion (`ToString`, `ToNatural`) for Natural values, all specializing corresponding IntegerFunctions.

#### 9.4.13 Trig Functions
**Lines:** 13304-13315

Defines basic trigonometric functions on real numbers including `sin`, `cos`, `tan`, `cot`, `arcsin`, `arccos`, and `arctan`, along with degree/radian conversion functions (`deg`, `rad`), a `pi` constant with precision constraint, and a `UnitBoundedReal` datatype constrained to the range [-1.0, 1.0] for function return types.

#### 9.4.14 Sequence Functions
**Lines:** 13316-13335

Defines functions for operating on ordered, nonunique sequences of values, including: indexing (`#`), comparison (`equals`, `same`), size/emptiness checks (`size`, `isEmpty`, `notEmpty`), membership tests (`includes`, `excludes`, `includesOnly`), set operations (`union`, `intersection`), element manipulation (`including`, `excluding`, `includingAt`, `excludingAt`), subsequence extraction (`subsequence`, `head`, `tail`, `last`), and in-place modification behaviors (`add`, `addAt`, `remove`, `removeAt`).

#### 9.4.15 Collection Functions
**Lines:** 13336-13347

Defines functions for operating on Collections: equality (`==`), `size`, `isEmpty`, `notEmpty`, `contains`, `containsAll`, and for OrderedCollections specifically: `head`, `tail`, `last`, indexing (`#`), and array multi-dimensional indexing (`array#`).

#### 9.4.16 Vector Functions
**Lines:** 13348-13375

Defines abstract and concrete functions for vector space operations on VectorValues, including addition, subtraction, scalar multiplication, inner product, norm, and angle calculations, with concrete implementations provided for CartesianVectorValues (1D, 2D, and 3D real-valued vectors).

#### 9.4.17 Control Functions
**Lines:** 13376-13395

Defines KerML control functions for conditional evaluation and collection operations: conditional branching (`if`, `??`), short-circuit boolean operators (`and`, `or`, `implies`), feature chaining (`.`), and collection processing functions (`collect`, `select`, `selectOne`, `reject`, `reduce`, `forAll`, `exists`, `allTrue`, `anyTrue`, `minimize`, `maximize`).

#### 9.4.18 Occurrence Functions
**Lines:** 13396-13415

Utility functions for working with occurrences and their temporal relationships, including identity testing (`===` for same-life portions), temporal queries (`isDuring`), lifecycle management (`create`, `destroy`), and collection operations (`addNew`, `addNewAt`, `removeOld`, `removeOldAt`) that combine creation/destruction with group membership.

## 10 Model Interchange
**Lines:** 13416-13417 | **Subsections:** 10.1, 10.2, 10.3, 10.4

Defines how KerML/SysML models are exchanged between tools using file-based resources, specifying three interchange formats (textual notation, JSON, and XMI), project archive structure (.kpar files with metadata), and JSON serialization rules for model elements.

### 10.1 Model Interchange Overview
**Lines:** 13418-13427

Defines **project** as the unit of model interchange—a set of root namespaces with their ownership trees plus references to used projects. Covers serialization into model interchange files (formats in 10.2) and compressed project interchange archives (structure in 10.3), with provisions for KerML-based language adaptations.

### 10.2 Model Interchange Formats
**Lines:** 13428-13445

Defines three model interchange file formats for KerML: textual notation (.kerml), JSON (.json using the mapping from section 10.4), and XML/XMI (.xmi). Conformant tools must support import/export for at least textual or JSON format, and KerML-based languages can define their own file extensions while following the same serialization strategies.

### 10.3 Model Interchange Projects
**Lines:** 13446-13509

ZIP-based project interchange format (`.kpar`) containing model files plus two required metadata files: `.project.json` (project name, version, dependencies with optional semantic version constraints) and `.meta.json` (global scope index, creation timestamp, checksums, and flags for derived/implied content inclusion).

### 10.4 JSON Serialization
**Lines:** 13510-13511 | **Subsections:** 10.4.1, 10.4.2, 10.4.3, 10.4.4, 10.4.5, 10.4.6

Defines how KerML models are serialized to JSON format, covering primitive type mappings (Boolean→boolean, Integer→integer, Real→number, String→string), enumeration literal serialization, element references via `@id` fields containing elementId values, element object structure with `@id`, `@type`, and attribute fields, and root namespace serialization as JSON arrays of owned elements.

#### 10.4.1 Serialization Overview
**Lines:** 13512-13517

Defines the JSON serialization format for KerML model interchange, where each root namespace maps to a `.json` file containing all owned model elements, conforming to the KerML.json schema. Other KerML-based languages may extend or define their own schemas following this strategy.

#### 10.4.2 Primitive Type Serialization
**Lines:** 13518-13530

Defines the mapping between UML primitive types (Boolean, Integer, Real, String) and their corresponding JSON Schema types (boolean, integer, number, string) for KerML abstract syntax serialization.

#### 10.4.3 Enumeration Serialization
**Lines:** 13531-13534

Enumeration values are serialized as JSON Schema strings using the exact enumeration literal name with preserved capitalization (e.g., `VisibilityKind::public` becomes `"public"`).

#### 10.4.4 Element Reference Serialization
**Lines:** 13535-13542

Defines how references to model elements are serialized in JSON: properties typed by Element or its subclasses become objects with a single `@id` field containing the referenced element's `elementId` string value.

#### 10.4.5 Element Serialization
**Lines:** 13543-13554

Defines JSON Schema mapping for SysML model elements: each element becomes an object with `@id` (from elementId), `@type` (MOF type name), and fields for all owned/inherited attributes. Attribute serialization follows MOF multiplicity rules—required [1..1], optional [0..1] allowing null, or arrays for upper bounds >1.

#### 10.4.6 Model Serialization
**Lines:** 13555-13958

Covers model serialization (root namespace maps to JSON Schema array of serialized elements) and an informative annex on model execution, including: instantiation procedures for classifiers using atoms (modeled instances), feature value assignment, connector handling (one-to-one and one-to-unrestricted), timing semantics for structures (composite parts, HappensDuring/HappensWhile), and timing for behaviors (sequences with successions, decisions/merges, and feature value changes via time slices).

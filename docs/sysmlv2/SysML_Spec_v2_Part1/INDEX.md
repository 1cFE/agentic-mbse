---
document: SysML_Spec_v2_Part1
generated: 2026-01-13T00:41:24Z
source_checksum: sha256:1d0295b9957681f8322b02cdaf79e8c5b0cee9cfc580ebb5850dde6bf6b0df6e
total_lines: 47798
depth: 3
section_count: 52
---

# SysML_Spec_v2_Part1 Index

## 0 Preface
**Lines:** 1552-1614

OMG (Object Management Group) is a non-profit consortium that develops computer industry standards including UML and CORBA, following the Model Driven Architecture approach. The preface provides contact information for obtaining specifications and instructions for reporting issues.

## 1 Scope
**Lines:** 1615-1646

Specifies the Systems Modeling Language (SysML) standard for model-based systems engineering, covering its purpose as a general-purpose language for modeling system requirements, structure, behavior, analysis, and verification. SysML extends the Kernel Modeling Language (KerML) and supports domain-specific customization for industries like automotive, aerospace, and healthcare.

## 2 Conformance
**Lines:** 1647-1735

Defines SysML model conformance requirements and five conformance levels for modeling tools: Abstract Syntax Conformance (required), Concrete Syntax Conformance (textual and/or graphical notation), Semantic Conformance (model interpretation/execution), Model Interchange Conformance (required, using `.kpar` files with `.sysml` extension), and optional Domain Library Support.

## 3 Normative References
**Lines:** 1736-1861

Lists normative standards required by the SysML v2 specification, including foundational OMG specifications (KerML, MOF, OCL, UML, SysML v1) and ISO/IEC 80000 series standards for quantities and units across physics domains (space/time, mechanics, thermodynamics, electromagnetism, etc.).

## 4 Terms and Definitions
**Lines:** 1862-1872

Terms and definitions used in the SysML v2 specification are defined throughout the document body rather than in a centralized glossary section.

## 5 Symbols
**Lines:** 1873-1883

Concrete syntax for SysML is specified in subclause 8.2; no substantive content appears in this section beyond that reference.

## 6 Introduction
**Lines:** 1884-1885 | **Subsections:** 6.1, 6.2, 6.3

SysML v2 is a general-purpose systems modeling language specified as a metamodel extending KerML (rather than as a UML profile like v1), providing textual and graphical concrete syntax, abstract syntax, semantics, and model libraries (Systems Library and Domain Libraries) to support model-based systems engineering. The document is organized into clauses covering user-facing modeling constructs (Clause 7), normative metamodel specification (Clause 8), and model libraries (Clause 9).

### 6.1 Document Overview
**Lines:** 1886-1917

SysML v2 is a general-purpose modeling language for model-based systems engineering, specified as a metamodel extending KerML (rather than as a UML profile like v1). The specification defines textual and graphical concrete syntax, abstract syntax, semantics via the Systems Library, and Domain Libraries for quantities, units, and analysis.

### 6.2 Document Organization
**Lines:** 1918-1954

Describes the organization of the SysML v2 specification into three major clauses: Clause 7 (user-facing modeling constructs with syntax and notation), Clause 8 (normative metamodel specification including concrete/abstract syntax and semantics), and Clause 9 (model libraries including Systems Library and Domain Libraries). Also references KerML Clause 10 for model interchange and mentions an informative example annex.

### 6.3 Acknowlegements
**Lines:** 1955-2077

Lists the primary authors (Friedenthal, Seidewitz, Burkhart, Gery, Miyashita, de Koning), contributing organizations, SST leadership roles, and individuals who supported specification development, pilot implementation, and tooling for SysML v2.

## 7 Language Description
**Lines:** 2078-2081 | **Subsections:** 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9, 7.10, 7.11, 7.12, 7.13, 7.14, 7.15, 7.16, 7.17, 7.18, 7.19, 7.20, 7.21, 7.22, 7.23, 7.24, 7.25, 7.26, 7.27

Based on the KerML specification, here's the summary: Informative description of KerML language constructs and their usage, covering the Root, Core, and Kernel layers. Defines foundational concepts including elements, relationships, ownership hierarchies, namespaces, and naming conventions, with examples of textual notation syntax.

### 7.1 Language Overview
**Lines:** 2082-2215

SysML v2 extends KerML and organizes modeling constructs around a definition/usage pattern for reuse, directly inheriting elements, relationships, dependencies, annotations, namespaces, specialization, and expressions from KerML. The SysML-specific constructs cover structure (items, parts, ports, connections, interfaces, allocations), behavior (flows, actions, states), calculations, constraints, requirements, cases (analysis, verification, use cases), viewpoints/views, variability/configuration, and user-defined metadata for domain extensions.

### 7.2 Elements and Relationships
**Lines:** 2216-2365

Defines the fundamental building blocks of SysML models: **elements** (model constituents with unique IDs, names, and short names) and **relationships** (elements that connect other elements, with ownership semantics that cascade deletions through ownership trees). Covers element naming conventions (basic names vs. unrestricted names with escape sequences), relationship properties (binary/n-ary, directed/undirected, sources/targets), and how owned elements are represented textually (curly-brace bodies) and graphically (compartments).

### 7.3 Dependencies
**Lines:** 2366-2442

Dependencies are relationships between client (source) and supplier (target) elements that indicate a change to a supplier may require changes to clients, useful for representing abstract relationships like architectural layer dependencies. Dependencies are declared with the `dependency` keyword followed by `from` (clients) and `to` (suppliers) element lists, and can optionally contain annotating elements in a body.

### 7.4 Annotations
**Lines:** 2443-2652

Annotations are elements that provide additional information about other model elements, including comments (textual descriptions), documentation (comments that document their owning element), and textual representations (bodies in a specified language like SysML, OCL, or ALF). User-defined metadata for syntactic and semantic extension is covered separately in section 7.27.

### 7.5 Namespaces and Packages
**Lines:** 2653-3112

Namespaces contain and name member elements, with membership relationships controlling visibility (public/protected/private) and ownership; packages are namespaces used purely as organizational containers with optional import filtering based on metadata conditions. Qualified names (segments separated by `::`) resolve element references, and imports allow namespaces to access members from other namespaces either individually, via wildcard (`::*`), or recursively (`::**`).

### 7.6 Definition and Usage
**Lines:** 3113-3826

Definitions classify reusable element types (parts, actions, attributes, etc.) while usages instantiate definitions in specific contexts with multiplicities, composition rules, and inheritance. Specialization mechanisms include subclassification for definitions, and subsetting/redefinition for usages, with support for variability modeling through variation points and variants.

### 7.7 Attributes
**Lines:** 3827-3934

Attribute definitions specify sets of data values (numbers, quantities with units, text strings, or structured data), while attribute usages are always referential features typed by those definitions or KerML data types like `String`, `Boolean`, `Integer`, and `Real`. Quantities with units use the Quantities and Units Domain Library, which associates unit kinds (e.g., `MassUnit`) with definitions while specific units (e.g., `kg`) are given only with actual values, enabling automatic unit conversion.

### 7.8 Enumerations
**Lines:** 3935-4069

Enumerations restrict attribute values to a fixed set of enumerated values, declared with the `enum` keyword. Enumeration definitions can specialize non-enumeration attribute definitions (binding values to expressions) but cannot specialize other enumerations, and may only contain enumerated value declarations.

### 7.9 Occurrences
**Lines:** 4070-4423

Occurrences are definitions and usages representing things with temporal extent (lifetimes), including structural entities like parts and behavioral performances; they support time slices, snapshots, individual identification (unique objects with specific identity), and events that reference happenings during an occurrence's lifetime.

### 7.10 Items
**Lines:** 4424-4513

Item definitions and usages model identifiable objects that may be acted on over time but don't necessarily perform actions themselves (unlike parts). Items can represent inputs/outputs to actions (water, fuel, signals, data), have spatial properties (shape, bounding/enveloping shapes, voids), and are declared with the `item` keyword with default multiplicity `[1..1]`.

### 7.11 Parts
**Lines:** 4514-4638

Part definitions model structural units (systems, components, external entities) as temporal occurrences with composite structure, while part usages instantiate those definitions. Parts can have attributes, ports for interconnection, perform actions, exhibit states, and represent any abstraction level from logical components to physical hardware, software, facilities, or users.

### 7.12 Ports
**Lines:** 4639-4772

Port definitions and usages define connection points enabling interactions between parts. Ports have directed features (`in`, `out`, `inout`) that specify what can be exchanged; two ports conform when their directed features match with conjugate directions, and every port definition has an implicit conjugated version (prefixed with `~`) with reversed `in`/`out` directions.

### 7.13 Connections
**Lines:** 4773-5400

Connections in SysML v2 are relationship-based part definitions that link items/parts through connection ends, supporting binary and n-ary connections, logical vs. physical modeling with interface media, and cross-feature multiplicity constraints. Bindings assert value equality between features, successions enforce temporal ordering between occurrences, and feature values provide fixed or default initialization through expressions.

### 7.14 Interfaces
**Lines:** 5401-5568

Interfaces are specialized connections whose ends must be ports, enabling reusable port-to-port connection patterns between parts (e.g., connecting appliances to wall power). Interface definitions can include constraints on port feature values such as across/through variables for physical conservation laws, and when used with send actions, transfers from one port automatically target the connected port at the other end.

### 7.15 Allocations
**Lines:** 5569-5672

Allocations are connection definitions that map a source element to a target element responsible for realizing it, used for flexible cross-structure mappings in system models (e.g., logical-to-physical). They are declared with the `allocation` keyword, are always binary with two ends, and can be nested for finer-grained decomposition.

### 7.16 Flows and Messages
**Lines:** 5673-5887

Flows and messages define how payloads are transferred between occurrences (parts, actions) in SysML v2, with three variants: messages (abstract logical transfers), streaming flows (specify source output and target input features), and succession flows (add temporal ordering constraints requiring source completion before transfer and transfer completion before target starts).

### 7.17 Actions
**Lines:** 5888-7307

Actions are behavioral occurrences that coordinate subactions, transform input/output parameters, and generate effects on items over time. The section covers action definitions/usages with `in`/`out`/`inout` parameters, sequencing via successions and control nodes (fork, join, decision, merge), data transfer via bindings and flows (including send/accept), assignment actions for changing feature values, terminate actions, and structured control actions (if, while loop, for loop).

### 7.18 States
**Lines:** 7308-7844

State definitions and usages model event-triggered behavior with entry/do/exit actions, hierarchical substates (exclusive or parallel), and transition usages that connect states via triggers, guards, and effect actions. Exhibited states allow parts to reference state behaviors, while transitions control state activation/deactivation with optional accepters for incoming transfers and guard conditions.

### 7.19 Calculations
**Lines:** 7845-8030

Calculation definitions and usages are specialized action types with a distinguished `out` result parameter (declared with `return`), used to specify reusable computations that return values; they can include intermediate steps, subcalculations, and a final result expression, with pure calculations guaranteeing deterministic results without side effects.

### 7.20 Constraints
**Lines:** 8031-8230

Constraint definitions are predicates (logical expressions returning Boolean values) with input parameters, where a constraint is satisfied when its expression evaluates to `true` and violated otherwise. Assert constraint usages declare that a constraint must always be true (or always false if negated), flagging logical inconsistencies when violated.

### 7.21 Requirements
**Lines:** 8231-8718

Requirements in SysML v2 are specialized constraints that capture stakeholder-imposed conditions a design must satisfy, featuring required constraints (what must be true) and assumed constraints (preconditions), along with a subject parameter identifying the constrained entity, plus optional actors and stakeholders. Satisfaction is asserted using `satisfy requirement` usages that bind subjects to specific design elements, and requirements can be hierarchically decomposed into subrequirements that automatically become required constraints of their parent.

### 7.22 Cases
**Lines:** 8719-8813

Cases are calculation definitions/usages that produce results to achieve specific objectives regarding a subject, serving as the foundation for analysis cases, verification cases, and use cases. Key elements include a subject parameter (first parameter, declared with `subject` keyword), an objective (a requirement to be satisfied), and optional actor parameters representing external entities involved in the case.

### 7.23 Analysis Cases
**Lines:** 8814-8995

Analysis cases are case definitions used to perform analyses on subjects (like fuel economy analysis on vehicles), returning results that can be evaluated against objectives. They can specify analysis actions with calculations, integrate with external solvers, or define simultaneous equations via constraints, and include specialized trade-off analyses (`TradeStudy`) for evaluating and comparing alternatives using weighted evaluation functions.

### 7.24 Verification Cases
**Lines:** 8996-9166

Verification cases are specialized case definitions for evaluating whether a subject (the "unit under test") satisfies specified requirements, returning a verdict of pass, fail, inconclusive, or error. They typically include actions to collect data using verification methods (analysis, inspection, demonstration, test), analyze the data, and evaluate results against the objective requirements.

### 7.25 Use Cases
**Lines:** 9167-9350

Use case definitions specify required behavior of a subject relative to external actors, modeled as sequences of interactions (messages) between subject and actors to achieve an observable result of value. Include use case usages allow composing use cases by including the behavior of one use case within another, with automatic subject binding and explicit actor parameter binding.

### 7.26 Views and Viewpoints
**Lines:** 9351-9736

Viewpoint definitions frame stakeholder concerns as a kind of requirement, while view definitions specify how to extract and render model content to satisfy those viewpoints using filter conditions and renderings. Views expose model elements, apply filters, and produce artifacts (including diagrams and compartments) that address stakeholder needs.

### 7.27 Metadata
**Lines:** 9737-10031

Metadata usages and metadata definitions provide structured, modeler-specified annotations on model elements, enabling tool-specific or domain-specific tagging with optional typed attribute values. Semantic metadata (specializing `SemanticMetadata`) can establish implicit specialization relationships, and user-defined keywords (`#name`) offer shorthand syntax for applying metadata annotations in declarations.

## 8 Metamodel
**Lines:** 10032-10033 | **Subsections:** 8.1, 8.2, 8.3, 8.4

The metamodel clause specifies the normative structure for KerML through three interconnected facets: concrete syntax (textual notation for modelers), abstract syntax (linguistic terms and relationships), and semantics (interpretation of models using mathematical logic). The clause is organized by KerML's Root, Core, and Kernel layers, with grammar productions using EBNF notation to define the mapping between concrete and abstract syntax representations.

### 8.1 Metamodel Overview
**Lines:** 10034-10076

SysML metamodel extends KerML, providing textual and graphical concrete syntax, an abstract syntax that imports and specializes KerML metaclasses, and semantics defined through the Systems Model Library and transformations to equivalent KerML models. Also establishes typographic conventions: `code` font for metaclass/metaproperty names (e.g., `Usage`, `ownedUsage`) and _`italic code`_ for model elements (e.g., _`Action`_, _`actions`_).

### 8.2 Concrete Syntax
**Lines:** 10077-14954

Covers SysML v2 concrete syntax specification, including textual notation (EBNF grammar conventions, lexical structure with reserved keywords, and grammar productions for elements like packages, definitions, usages, annotations, and relationships) and graphical notation options, explaining how models can be rendered in text, graphics, or both.

### 8.3 Abstract Syntax
**Lines:** 14955-26919

Defines the MOF-based abstract syntax for SysML v2, which is the underlying structural representation for all SysML models independent of textual or graphical notation. Covers three constraint types (derivation, semantic, validation), and details the metaclass hierarchies for Elements, Relationships, Dependencies, Annotations, Namespaces, Packages, Definitions, and Usages—including variation points and variant memberships.

### 8.4 Semantics
**Lines:** 26920-31628

Specifies SysML semantics through four categories of semantic constraints (specialization, redefinition, type-featuring, and binding-connector) that define required relationships between model elements, along with rules for implied relationships that tools may insert to satisfy these constraints—covering Definitions, Usages, variations, attributes, and enumerations.

## 9 Model Libraries
**Lines:** 31629-31630 | **Subsections:** 9.1, 9.2, 9.3, 9.4, 9.5, 9.6, 9.7, 9.8

Defines KerML's three standard model libraries: the Semantic Library (foundational types like `Anything`, `DataValue`, `Occurrence`), the Data Type Library (standard types like `Boolean`, `Integer`, `Real`, `String`), and the Function Library (operations on those types). These libraries establish the base type hierarchy and semantic foundations that all user models implicitly inherit and specialize.

### 9.1 Model Libraries Overview
**Lines:** 31631-31683

SysML model libraries provide foundational type hierarchies that all user-defined elements must specialize (e.g., `ItemDefinition` specializes `Item` which specializes KerML's `Object`), plus normative domain libraries covering metadata, analysis/trade studies, cause-and-effect, requirement derivation, geometry, and quantities/units (ISO 80000, ISO 8601-1). Library elements use stable name-based UUIDs for interchange across textual, XMI, and JSON formats.

### 9.2 Systems Model Library
**Lines:** 31684-36804

Defines the Systems Model Library containing base types for all SysML Definition and Usage elements, including library packages for Attributes, Items, Parts, Ports, Connections, Interfaces, Allocations, Actions, States, Constraints, Requirements, Cases, Calculations, Flows, Metadata, Views, and a reflective SysML model of the abstract syntax.

### 9.3 Metadata Domain Library
**Lines:** 36805-37610

Defines standard metadata definitions for annotating model elements, including `Issue`, `Rationale`, `Refinement`, and `StatusInfo` (with status values like open/done/closed), plus risk assessment metadata (`Risk`, `RiskLevel`, `Level`) for tracking cost, schedule, and technical risks with probability and impact levels.

### 9.4 Analysis Domain Library
**Lines:** 37611-38415

Defines library models for analysis cases including: metadata definitions for external tool integration (`ToolExecution`, `ToolVariable`), discretely sampled mathematical functions (`SampledFunction`, `SamplePair`, interpolation calculations), and state space representation for dynamical systems with continuous and discrete dynamics (`StateSpaceDynamics`, `getNextState`, `getDerivative`).

### 9.5 Cause and Effect Domain Library
**Lines:** 38416-38943

Defines the Causation domain library for modeling cause-effect relationships between occurrences, including `Causation` (binary cause-effect) and `Multicausation` (multiple causes to multiple effects) connection definitions, with constraints ensuring causes precede effects and are disjoint from effects. Also provides metadata definitions (`CausationMetadata`, `CauseMetadata`, `EffectMetadata`) for annotating causation connections with properties like necessity, sufficiency, and probability.

### 9.6 Requirement Derivation Domain Library
**Lines:** 38944-39295

Defines the `Derivation` connection type for modeling requirement derivation relationships, where one or more derived requirements must be satisfied whenever an original requirement is satisfied. Includes metadata definitions (`DerivationMetadata`, `DerivedRequirementMetadata`, `OriginalRequirementMetadata`) for tagging derivation connections and their requirement ends.

### 9.7 Geometry Domain Library
**Lines:** 39296-41618

Defines the Geometry Domain Library for modeling physical items with spatial extent, including SpatialItems (3D reference frames with coordinate systems, clocks, and origin points), calculations for position and displacement vectors (PositionOf, DisplacementOf, CurrentPositionOf, CurrentDisplacementOf), and geometric shape items like curves, surfaces, circles, ellipses, cones, cylinders, and discs with their dimensional properties.

### 9.8 Quantities and Units Domain Library
**Lines:** 41619-47798

Defines the Quantities and Units Domain Library for representing physical quantities (scalar, vector, tensor), measurement units, scales, quantity dimensions, coordinate frames, and systems of quantities/units aligned with ISO 80000 and SI standards. Includes AttributeDefinitions like `ScalarQuantityValue`, `VectorQuantityValue`, `TensorQuantityValue`, `QuantityDimension`, `MeasurementUnit`, and `CoordinateFrame`, plus operators for quantity arithmetic and unit conversion.

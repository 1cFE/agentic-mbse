---
document: SysML_Spec_v2_Part2
generated: 2026-01-13T01:24:30Z
source_checksum: sha256:3a89ad5a4d6e46dba910ca83ac2d5724b8a9adb255d5e42f41496554890bf4dc
total_lines: 32376
depth: 3
section_count: 50
---

# SysML_Spec_v2_Part2 Index

## 0 Preface
**Lines:** 1139-1168

OMG (Object Management Group) organizational overview and specification access information, including contact details, website references for downloading specifications (UML, CORBA, CWM), and instructions for reporting specification issues.

## 1 Scope
**Lines:** 1169-1176

Defines the scope of a specification for transforming/translating SysML v1 (v1.7) models to SysML v2 (v2.0), intended to enable automated model conversion tools and serve as an educational comparison between the two versions.

## 2 Conformance
**Lines:** 1177-1188

Defines conformance requirements for SysML v1 to v2 transformation tools: must implement both UML4SysML/SysML v1 profile and SysML v2 abstract syntax, and must transform between them per the specification. Partial conformance is allowed by implementing only a subset of the defined mappings.

## 3 Normative References
**Lines:** 1189-1206

Lists the foundational specifications that SysML v2 builds upon and references: KerML 1.0 (the kernel language), MOF 2.5.1, OCL 2.4, SysML v1.7, UML 2.5.1, and XMI 2.5.1 for metadata interchange.

## 4 Terms and Definitions
**Lines:** 1207-1210

Indicates that terminology definitions are distributed throughout the specification document rather than consolidated in a dedicated glossary section.

## 5 Symbols
**Lines:** 1211-1214

Declares that no special symbols are defined in this specification.

## 6 Introduction
**Lines:** 1215-1216 | **Subsections:** 6.1, 6.2

There are multiple "Section 6: Introduction" sections across different documents. Could you clarify which specification you're referring to? The options are: 1. **SysML v2 Part 1** - SysML Language specification 2. **SysML v2 Part 2** - SysML API and Services 3. **SysML v2 Part 3** - SysML Annexes 4. **KerML Spec** - Kernel Modeling Language specification Which document's Section 6 would you like summarized?

### 6.1 Mapping Approach
**Lines:** 1217-1234

Defines the formal approach for SysML v1 to v2 transformation using directed mappings between UML/SysML v1 metaclasses and KerML/SysML v2 metaclasses. Each mapping is a UML class with `from`/`to` associations and OCL operations that compute target property values, with inheritance-based applicability rules and optional filter operations to restrict which source objects are transformed.

### 6.2 Acknowledgements
**Lines:** 1235-1278

Acknowledgements listing the primary authors (Yves Bernard, Tim Weilkiens), the 12 submitting organizations (including IBM, INCOSE, Lockheed Martin, PTC), SST leadership roles, and tooling support contributors who helped develop the SysML v2 specification.

## 7 Mappings
**Lines:** 1279-1280 | **Subsections:** 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8

Defines the transformation framework for mapping UML/SysML v1 models to KerML/SysML v2, including foundational abstract classes (Mapping, UniqueMapping, MainMapping, Factory, Initializer) that control how source elements are converted to target elements, with OCL-based computation rules and helper operations for specifying property values.

### 7.1 Overview
**Lines:** 1281-1286

Describes the organizational structure of the transformation model specification, covering foundational abstract classes, a Helper utility class with reusable OCL operations, SysML v2 libraries for UML/SysML semantic equivalence, and the arrangement of initializers, factories, generic mappings, and specific mappings for UML metaclasses and SysML stereotypes.

### 7.2 Foundations
**Lines:** 1287-1288 | **Subsections:** 7.2.1, 7.2.2

Foundational classes for UML/SysML v1 to KerML/SysML v2 model transformations, including Mapping (explicit element-to-element transformations), UniqueMapping (one target per source), MainMapping (implicitly called for matching elements), Factory (create targets without sources), and Initializer (shared default value specifications).

#### 7.2.1 Overview
**Lines:** 1289-1304

Defines foundational transformation classes for UML/SysML v1 to KerML/SysML v2 conversion: **Mapping** (explicit calls, new target per call), **UniqueMapping** (one target per source), **MainMapping** (auto-executed for matching elements), plus **Factory** (generates targets without source links) and **Initializer** (factors out default property values). All reside in the Foundations package.

#### 7.2.2 Foundational class specifications
**Lines:** 1305-1396

UniqueMapping ensures one-to-one source-to-target mapping (returning the same target for repeated calls), Factory creates target elements without source elements (using parameters instead), Mapping is the abstract base class defining source-to-target transformations with filter and getMapped operations, MainMapping auto-executes for matching source elements with unique results, and Initializer is the common ancestor specifying target type computation rules.

### 7.3 Mapping Helper and Library
**Lines:** 1397-1398 | **Subsections:** 7.3.1, 7.3.2

Defines the `Helper` class containing reusable operations for UML-to-SysML v2 transformations, including functions for mapping enumeration types, visibility kinds, parameter/feature directions, multiplicity ranges, scalar value types, and stereotype tag value retrieval.

#### 7.3.1 Helper
**Lines:** 1399-1534

Helper class provides shared utility operations for UML-to-SysML v2 model transformations, including mapping enumerations (visibility, direction kinds), type conversions (primitives to scalar values), stereotype handling, UUID generation, and reusable relationship mapping rules for actions, activities, packages, and states.

#### 7.3.2 SysML v1 Library
**Lines:** 1535-1550

Defines a SysML v2 library for annotating elements transformed from SysML v1 models, including action definitions for value manipulation (AddValueAction, RemoveVariableValueAction) and metadata definitions for preserving SysML v1/UML properties that lack direct v2 equivalents (BlockData, PortData, ModelData, ViewpointData, etc.).

### 7.4 Initializers
**Lines:** 1551-1552 | **Subsections:** 7.4.1, 7.4.2

Initializers are QVTo transformation classes that provide default values for all non-derived features of SysML v2 metamodel elements, covering both KerML elements (like Annotation, Association, Behavior, Classifier, Connector, etc.) and SysML system elements (like ActionUsage, PartUsage, PortDefinition, etc.).

#### 7.4.1 Overview
**Lines:** 1553-1556

Initializer classes provide default values for non-derived features of target metaclasses. They intentionally omit source elements to simplify specialization, but this means some feature computations must be declared abstract rather than algorithmically defined.

#### 7.4.2 Mapping Specifications
**Lines:** 1557-3028

KerML initializer specifications that define how SysML v2 model elements are initialized during mapping transformations, covering element types from AnnotatingElement through InvocationExpression with their inheritance hierarchies, association ends, operations, and default values.

### 7.5 Factories
**Lines:** 3029-3030 | **Subsections:** 7.5.1, 7.5.2

Factories are element creation utilities that generate target model elements from input parameters (strings, features, memberships) without preserving links to input values. Includes factory classes like `LiteralString_Factory`, `StringParameterFeature_Factory`, `StringParameterFeatureValue_Factory`, and `StringParameterMembership_Factory` for creating expressions, features, and membership relationships.

#### 7.5.1 Overview
**Lines:** 3031-3034

Specifies facilities for creating model elements from zero or more input parameters, with no persistent link between the created element and its inputs after creation.

#### 7.5.2 Mapping Specifications
**Lines:** 3035-3991

Factory classes for creating KerML and SysML v2 model elements during mapping transformations, including factories for literal strings, string parameters, subject memberships, assignment action usages, reference usages with directions, objective/requirement usages, feature typings, and flow-related elements (flow ends, items, and memberships).

### 7.6 Generic Mappings
**Lines:** 3992-3993 | **Subsections:** 7.6.1, 7.6.2

Generic mappings are abstract, reusable transformation rule templates that provide default values for non-derived attributes of target metaclasses and define abstract operations for attribute initialization. Section 7.6.2 defines common mappings for elements like FeatureReferenceExpression, Membership, ParameterReferenceUsage, ReturnParameterFeature, and ReferenceUsage, each specifying source/target metaclasses and mapping rules.

#### 7.6.1 Overview
**Lines:** 3994-4001

Generic mappings are abstract, reusable transformation rule templates that provide default values for non-derived attributes of target metaclasses or declare abstract operations. They function like initializers but include a source element, and their operations can be redefined by specializations based on redefined source types.

#### 7.6.2 Common Mappings
**Lines:** 4002-4639

Defines reusable mapping classes for transforming UML elements to SysML v2 constructs, including feature reference expressions, membership relationships, parameter reference usages (typed/untyped, in/out directions), return parameters, and feature typing relationships—each specifying source elements, target elements, and OCL-based mapping rules.

### 7.7 Mappings from UML4SysML metaclasses
**Lines:** 4640-4641 | **Subsections:** 7.7.1, 7.7.2, 7.7.3, 7.7.4, 7.7.5, 7.7.6, 7.7.7, 7.7.8, 7.7.9, 7.7.10, 7.7.11, 7.7.12, 7.7.13, 7.7.14

Defines how SysML v1 metaclasses from the UML4SysML subset map to SysML v2 abstract syntax elements, including detailed mapping tables for Actions, Activities, and other UML constructs, along with rationale for elements that are not mapped or only partially supported.

#### 7.7.1 Overview
**Lines:** 4642-4645

Defines UML4SysML as the subset of UML model elements reused by SysML, with the complete element list specified in SysML v1 specification subclause 4.1.

#### 7.7.2 Actions
**Lines:** 4646-11362

Maps SysML v1 action types (AcceptEventAction, CallBehaviorAction, SendSignalAction, pins, structured nodes, etc.) to SysML v2 equivalents (primarily ActionUsage, AcceptActionUsage, and ReferenceUsage), with detailed transformation rules for event handling, parameters, control flow, and object operations—noting that some v1 concepts like CallEvent, ReclassifyObjectAction, and Clause lack v2 equivalents.

#### 7.7.3 Activities
**Lines:** 11363-13748

Mapping of SysML v1 activity diagram elements to SysML v2 equivalents, covering Activities→ActionDefinition, control/object flows→SuccessionAsUsage/TransitionUsage, and control nodes (fork, join, merge, decision). Includes detailed mapping specifications for activity edges, initial nodes, and metadata handling, with several v1 concepts (ActivityParameterNode, ActivityPartition, ExceptionHandler) not mapped due to token semantics differences or pending specification.

#### 7.7.4 Classification
**Lines:** 13749-15468

Mapping specifications for translating SysML v1 classification concepts (Generalization, InstanceSpecification, Property, Operation, Parameter, Slot, Substitution) to SysML v2 equivalents (Subclassification, PartUsage/ConnectionUsage, various Usage types, Feature, Dependency). Includes detailed mapping rules for default multiplicity bounds, feature memberships, default values, and instance specification handling.

#### 7.7.5 CommonBehavior
**Lines:** 15469-17573

Mapping specifications for translating SysML v1 CommonBehavior elements (ChangeEvent, TimeEvent, Trigger, FunctionBehavior, OpaqueBehavior) to SysML v2 equivalents (CalculationUsage, AcceptActionUsage, ActionDefinition), with detailed OCL-based transformation rules for each mapping class including parameter handling, binding connectors, and constraint usages. CallEvent, SignalEvent, and AnyReceiveEvent are explicitly not supported in SysML v2.

#### 7.7.6 CommonStructure
**Lines:** 17574-18246

Mappings from SysML v1/UML abstract syntax elements to SysML v2 equivalents, covering common structural constructs like Abstraction, Comment, Constraint, Dependency, ElementImport, and PackageImport. Provides detailed OCL-based transformation rules for each mapping, including how comments are annotated, constraints become ConstraintDefinitions with AssertConstraintUsages, and various dependency types (Abstraction, Realization, Usage) all map to the v2 Dependency relationship.

#### 7.7.7 InformationFlows
**Lines:** 18247-18564

Defines mappings from SysML v1 InformationFlows and InformationItems to SysML v2 equivalents: InformationFlow maps to FlowDefinition (when it has realizing connectors or associations), while InformationItem maps to ItemDefinition. Includes detailed OCL-based mapping rules for creating end features, feature memberships, typing relationships, and subclassifications.

#### 7.7.8 Interactions
**Lines:** 18565-19277

Mappings from SysML v1 interaction diagram elements (sequence diagrams) to SysML v2 equivalents: Lifelines map to PartUsage, Messages to Flow, Interactions to Interaction behaviors, ExecutionSpecifications to ActionUsage, InteractionUse to Step, and StateInvariant to Invariant. Several v1 concepts like Gate, Continuation, and OccurrenceSpecification have no specified mapping yet.

#### 7.7.9 Packages
**Lines:** 19278-20477

Mappings from SysML v1 package-related elements (Package, Model, Profile, ElementImport, PackageImport, Stereotype) to SysML v2 equivalents, primarily Package, MembershipImport, NamespaceImport, and MetadataDefinition. Includes detailed transformation rules for URI and viewpoint properties via metadata, and notes that PackageMerge and Image concepts are not supported in v2.

#### 7.7.10 SimpleClassifiers
**Lines:** 20478-21237

Mappings from SysML v1 simple classifier concepts (DataType, Enumeration, EnumerationLiteral, Interface, PrimitiveType, Signal) to their SysML v2 equivalents (AttributeDefinition, EnumerationDefinition, EnumerationUsage, PortDefinition, ItemDefinition), including detailed OCL-based transformation rules for properties, attributes, and feature memberships.

#### 7.7.11 StateMachines
**Lines:** 21238-22175

Mapping specifications for converting SysML v1 state machine elements (StateMachine, State, Region, Pseudostate, FinalState, Transition, ConnectionPointReference) to SysML v2 equivalents (StateDefinition, StateUsage, TransitionUsage, ActionUsage), including detailed OCL rules for handling state behaviors (entry/do/exit actions), initial states, parallel states, triggers, guards, and transition effects.

#### 7.7.12 StructuredClassifiers
**Lines:** 22176-23624

Covers SysML v1 to SysML v2 migration mappings for structured classifiers: Association→ConnectionDefinition, AssociationClass→ConnectionDefinition, Class→OccurrenceDefinition, Connector→ConnectionUsage, ConnectorEnd→Feature, and Port→various usages. Includes detailed OCL-based transformation rules, filter conditions, and helper mappings for converting connector ends, metadata annotations, and feature memberships.

#### 7.7.13 UseCases
**Lines:** 23625-24118

Mappings from SysML v1 use case elements to SysML v2: Actor maps to PartDefinition, UseCase maps to UseCaseDefinition, and Include maps to IncludeUseCaseUsage, while Extend and ExtensionPoint are not supported in v2. Includes detailed mapping specifications for actors, subjects, objectives, and include relationships within use cases.

#### 7.7.14 Values
**Lines:** 24119-25295

Mappings from SysML v1 value-related concepts (literals, expressions, durations, time constraints, intervals) to SysML v2 equivalents, with detailed specifications for literal types (Boolean, Integer, Real, String, Null) and operator expressions. Several time and duration-related mappings remain unspecified.

### 7.8 Mappings from SysML v1.7 stereotypes
**Lines:** 25296-25297 | **Subsections:** 7.8.1, 7.8.2, 7.8.3, 7.8.4, 7.8.5, 7.8.6, 7.8.7, 7.8.8

[Summary generation timed out]

#### 7.8.1 Overview
**Lines:** 25298-25301

Describes how the SysML v2 specification organizes its mapping documentation from SysML v1.7 stereotypes, structuring subclauses according to the main packages of SysML v1.

#### 7.8.2 Activities
**Lines:** 25302-26029

Mappings from SysML v1 activity stereotypes (Probability, Rate, Continuous, Discrete) to SysML v2 MetadataUsage constructs, with detailed OCL-based transformation rules for feature typing, membership, and redefinition relationships. Also documents unmapped concepts like ControlOperator (not supported in v2) and NoBuffer/Overwrite (not yet specified).

#### 7.8.3 Allocations
**Lines:** 26030-26804

Mapping specifications for converting SysML v1 Allocate relationships to SysML v2 AllocationDefinition and AllocationUsage elements, including detailed OCL rules for feature memberships, typing, redefinitions, and feature chaining to handle source/target ends of allocation relationships between definitions and usages.

#### 7.8.4 Blocks
**Lines:** 26805-27404

Covers SysML v1 to SysML v2 migration mappings for Blocks package elements: Block maps to PartDefinition, BindingConnector to BindingConnectorAsUsage, ValueType to AttributeDefinition, and AssociationBlock to ConnectionDefinition. Includes detailed OCL filter conditions and transformation rules for encapsulated blocks, flow properties, and part properties, plus rationale for unmapped concepts like AdjunctProperty and ConnectorProperty.

#### 7.8.5 ConstraintBlocks
**Lines:** 27405-27496

ConstraintBlock from SysML v1 maps to ConstraintDefinition in SysML v2, with constraint parameters becoming AttributeUsage elements. The mapping preserves constraint expressions (e.g., OCL) and generalizations while converting owned properties and constraints to feature memberships.

#### 7.8.6 Model Elements
**Lines:** 27497-29796

Mappings from SysML v1 Model Elements (ElementGroup, Problem, Rationale, Stakeholder, Concern) to SysML v2 constructs, with ElementGroup→Package, Problem/Rationale→Comment with metadata, Stakeholder→ItemDefinition, and detailed OCL mapping rules for concern-stakeholder relationships. View, Viewpoint, Conform, and Expose mappings are not yet specified.

#### 7.8.7 PortsAndFlows
**Lines:** 29797-30588

Mappings from SysML v1 port and flow concepts (FullPort, ProxyPort, FlowProperty, InterfaceBlock, ItemFlow) to SysML v2 equivalents (PartUsage, AttributeUsage, ReferenceUsage, PortDefinition), including detailed OCL filter conditions and transformation rules for each mapping type. Several v1 concepts like nested port actions and triggers are noted as not yet mapped.

#### 7.8.8 Requirements
**Lines:** 30589-32376

Mappings from SysML v1 requirements concepts (DeriveReqt, Refine, Requirement, Satisfy, TestCase, Trace, Verify) to SysML v2 equivalents, with detailed transformation rules for each relationship type including ConnectionUsage for derivations, Dependency for refinements/traces, and RequirementVerificationMembership for verification relationships.

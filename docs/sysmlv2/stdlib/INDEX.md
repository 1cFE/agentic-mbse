---
syside_version: "0.8.3"
generated: "2026-01-13T04:08:30Z"
total_files: 94
---

# SysML v2 Standard Library Index

This index provides navigation for the SysML v2 standard library source files.
Use grep to search for specific functions, types, or units.

## Quick Reference

### Common Functions

| Function | Signature | Package |
|----------|-----------|---------|
| `sum` | `sum(collection: NumericalValue[0..*]) → NumericalValue` | NumericalFunctions |
| `product` | `product(collection: NumericalValue[0..*]) → NumericalValue` | NumericalFunctions |
| `abs` | `abs(x: NumericalValue) → NumericalValue` | NumericalFunctions |
| `max` | `max(x, y: NumericalValue) → NumericalValue` | NumericalFunctions |
| `min` | `min(x, y: NumericalValue) → NumericalValue` | NumericalFunctions |
| `size` | `size(seq: Anything[0..*]) → Natural` | SequenceFunctions |
| `isEmpty` | `isEmpty(seq: Anything[0..*]) → Boolean` | SequenceFunctions |
| `notEmpty` | `notEmpty(seq: Anything[0..*]) → Boolean` | SequenceFunctions |
| `head` | `head(seq: Anything[0..*]) → Anything[0..1]` | SequenceFunctions |
| `tail` | `tail(seq: Anything[0..*]) → Anything[0..*]` | SequenceFunctions |
| `includes` | `includes(seq, value) → Boolean` | SequenceFunctions |
| `union` | `union(seq1, seq2) → Anything[0..*]` | SequenceFunctions |
| `intersection` | `intersection(seq1, seq2) → Anything[0..*]` | SequenceFunctions |
| `collect` | `collection->collect { mapper }` | ControlFunctions |
| `select` | `collection->select { predicate }` | ControlFunctions |
| `reject` | `collection->reject { predicate }` | ControlFunctions |
| `reduce` | `collection->reduce operator` | ControlFunctions |
| `forAll` | `collection->forAll { test } → Boolean` | ControlFunctions |
| `exists` | `collection->exists { test } → Boolean` | ControlFunctions |
| `not` | `not(x: Boolean) → Boolean` | BooleanFunctions |
| `xor` | `xor(x, y: Boolean) → Boolean` | BooleanFunctions |
| `ToString` | `ToString(x: Anything) → String` | BaseFunctions |
| `sin` | `sin(x: Real) → Real` | TrigFunctions |
| `cos` | `cos(x: Real) → Real` | TrigFunctions |
| `sqrt` | `sqrt(x: Real) → Real` | RealFunctions |

### Core Types

| Type | Package | Description |
|------|---------|-------------|
| `Boolean` | ScalarValues | True/false values |
| `String` | ScalarValues | Text values |
| `Real` | ScalarValues | Real numbers |
| `Integer` | ScalarValues | Whole numbers |
| `Natural` | ScalarValues | Non-negative integers (≥0) |
| `Positive` | ScalarValues | Positive integers (>0) |

### Common SI Units

| Symbol | Unit | Quantity |
|--------|------|----------|
| `m` | metre | Length |
| `kg` | kilogram | Mass |
| `s` | second | Duration |
| `K` | kelvin | Temperature |
| `A` | ampere | Electric current |
| `mol` | mole | Amount of substance |
| `cd` | candela | Luminous intensity |
| `W` | watt | Power |
| `J` | joule | Energy |
| `N` | newton | Force |
| `Pa` | pascal | Pressure |
| `V` | volt | Electric potential |
| `Hz` | hertz | Frequency |
| `T` | tesla | Magnetic flux density |

---

## File Index

### Domain Libraries/Analysis

| File | Summary |
|------|---------|
| `AnalysisTooling.sysml` | Metadata annotations (ToolExecution, ToolVariable) for external analysis tool integration with actions. |
| `SampledFunctions.sysml` | SamplePair key-value type and SampledFunction ordered map for discretely sampled monotonic mathematical functions |
| `StateSpaceRepresentation.sysml` | State-space system modeling for control: StateSpace/Input/Output vectors, derivative calcs, dynamics actions |
| `TradeStudies.sysml` | Trade study framework with EvaluationFunction calc and TradeStudyObjective requirement for comparing alternatives |

### Domain Libraries/Cause and Effect

| File | Summary |
|------|---------|
| `CausationConnections.sysml` | Cause-effect relationships: Multicausation and Causation connection types with ordering constraints |
| `CauseAndEffect.sysml` | Metadata definitions for cause-effect modeling: CauseMetadata, EffectMetadata, CausationMetadata |

### Domain Libraries/Geometry

| File | Summary |
|------|---------|
| `ShapeItems.sysml` | Geometric shape items: PlanarCurve, PlanarSurface, Line, Path definitions with length/area attributes |
| `SpatialItems.sysml` | Spatial items with 3D extent acting as reference frames, providing coordinate systems, origin points, and position/di... |

### Domain Libraries/Metadata

| File | Summary |
|------|---------|
| `ImageMetadata.sysml` | Image attribute def with content/encoding/type/location, plus Icon metadata for graphical rendering |
| `ModelingMetadata.sysml` | StatusKind enum (open/tbd/tbr/tbc/done/closed) + StatusInfo, Rationale, Issue metadata defs |
| `ParametersOfInterestMetadata.sysml` | MOE/MOP metadata annotations (`<moe>`, `<mop>`) for tagging key performance parameters |
| `RiskMetadata.sysml` | Risk assessment metadata: Level (0-1 Real), LevelEnum (low/med/high), RiskLevel with probability/impact, Risk annotation |

### Domain Libraries/Quantities and Units

| File | Summary |
|------|---------|
| `ISQ.sysml` | ISO/IEC 80000 quantity system - re-exports base, space-time, mechanics, thermo, EM, light, acoustics, chemistry, nucl... |
| `ISQAcoustics.sysml` | Acoustic quantities from ISO-80000-8: frequency range, sound pressure, velocity, power, intensity, impedance |
| `ISQAtomicNuclear.sysml` | ISQ atomic/nuclear physics quantities: atomic/mass numbers, nuclear radii, binding energy, cross-sections, decay cons... |
| `ISQBase.sysml` | SI base quantities: Length (L) and Duration (T) with their units, values, and dimension definitions |
| `ISQCharacteristicNumbers.sysml` | Dimensionless characteristic numbers for fluid dynamics (Reynolds, etc.) from ISO-80000-11. |
| `ISQChemistryMolecular.sysml` | ISQ chemistry/molecular physics quantities: number of entities, Avogadro constant, molecular mass, molar quantities |
| `ISQCondensedMatter.sysml` | Condensed matter physics quantities: lattice vectors, Bragg angles, Fermi energy, Hall coefficients per ISO-80000-12 |
| `ISQElectromagnetism.sysml` | ISQ electromagnetism quantities: charge, voltage, resistance, capacitance, inductance, magnetic flux/field units |
| `ISQInformation.sysml` | ISQ information science quantities: traffic intensity, storage capacity, entropy, data rates, bit/byte units (IEC-800... |
| `ISQLight.sysml` | Light/radiation quantities and units (ISO-80000-7): speed of light, radiant energy, luminous intensity, etc. |
| `ISQMechanics.sysml` | ISQ Mechanics quantities: mass density, force, momentum, pressure, torque, velocity, acceleration |
| `ISQSpaceTime.sysml` | ISQ Space and Time quantities (width, height, depth, altitude) based on ISO-80000-3:2019 standard |
| `ISQThermodynamics.sysml` | ISQ thermodynamic quantities: temperature, Celsius temperature, with units and scalar value types from ISO-80000-5 |
| `MeasurementRefCalculations.sysml` | Arithmetic operations (*, /, **, ^) for MeasurementUnits and CoordinateFrames, plus ToString for references |
| `MeasurementReferences.sysml` | Measurement reference types (tensor, vector, scalar) for quantity units and coordinate systems. |
| `Quantities.sysml` | Root representations for quantities: TensorQuantityValue, VectorQuantityValue, ScalarQuantityValue with measurement refs |
| `QuantityCalculations.sysml` | Scalar quantity arithmetic (+, -, *, /, **, ^), comparison (<), and utility calcs (abs, isZero, isUnit) |
| `SI.sysml` | SI base units (m, kg, s, A, K, mol, cd) and the ISO/IEC 80000 International System of Units definition |
| `SIPrefixes.sysml` | SI unit prefixes (yocto to peta) with symbols and decimal conversion factors per ISO/IEC 80000-1 |
| `TensorCalculations.sysml` | Tensor arithmetic: construction, zero/unit checks, +/-, scalar/vector multiplication operations |
| `Time.sysml` | Universal clock, Clock part def, TimeInstantValue/DateTime types, TimeOf/DurationOf calcs, epoch defs |
| `USCustomaryUnits.sysml` | US customary measurement units (acre, barrel, BTU variants) with SI conversion factors from NIST SP811 |
| `VectorCalculations.sysml` | Vector quantity arithmetic: construction, zero/unit checks, add/subtract, scalar-vector multiply/divide ops |

### Domain Libraries/Requirement Derivation

| File | Summary |
|------|---------|
| `DerivationConnections.sysml` | Requirements derivation connections linking original to derived requirements with validation constraints. |
| `RequirementDerivation.sysml` | Metadata definitions for tagging original/derived requirements and derivation connections in SysML models |

### Kernel Libraries/Kernel Data Type Library

| File | Summary |
|------|---------|
| `Collections.kerml` | Array, Bag, Set, List, Map, KeyValuePair collection datatypes with ordered/unique variants |
| `ScalarValues.kerml` | Primitive scalar datatypes: Boolean, String, and numeric hierarchy (Complex→Real→Rational→Integer→Natural→Positive) |
| `VectorValues.kerml` | Abstract/concrete vector datatypes: VectorValue, NumericalVectorValue, CartesianVectorValue, ThreeVectorValue |

### Kernel Libraries/Kernel Function Library

| File | Summary |
|------|---------|
| `BaseFunctions.kerml` | Core equality, identity, type-checking, indexing, and casting operators for all KerML values. |
| `BooleanFunctions.kerml` | Boolean logic operations: not, xor, |, &, ==, ToString, ToBoolean for Boolean values |
| `CollectionFunctions.kerml` | Collection operations: ==, size, isEmpty, notEmpty, contains, containsAll, head, tail, last, index access (#) |
| `ComplexFunctions.kerml` | Complex number operations: rect/polar constructors, re/im extraction, abs/arg, arithmetic (+,-,*,/,**,^), comparison |
| `ControlFunctions.kerml` | Conditional & collection operators: if/else, and/or/implies, null-coalesce (??), collect, select |
| `DataFunctions.kerml` | Abstract base operators for DataValue: equality, arithmetic (+,-,*,/,**,%,^), logical (not,xor), bitwise (~,|,&), com... |
| `IntegerFunctions.kerml` | Integer arithmetic (+, -, *, /, %, **), comparison (<, >, <=, >=), abs, min, max, range (..) |
| `NaturalFunctions.kerml` | Arithmetic (+, *, /, %), comparison (<, >, <=, >=, ==), min/max, and string conversion ops for Natural values |
| `NumericalFunctions.kerml` | Abstract arithmetic (+, -, *, /, **, %, abs) and comparison (<, >, <=, >=) functions for NumericalValue |
| `OccurrenceFunctions.kerml` | Utility functions for occurrence identity (`===`), timing (`isDuring`), and lifecycle (`create`/`destroy`) |
| `RationalFunctions.kerml` | Rational arithmetic and comparison functions (rat, numer, denom, abs, +, -, *, /, comparisons, gcd) |
| `RealFunctions.kerml` | Real number arithmetic, comparison, and math functions (abs, sqrt, min, max, +, -, *, /, <, >, etc.) |
| `ScalarFunctions.kerml` | Abstract arithmetic, logical, bitwise, and comparison operators for ScalarValue types |
| `SequenceFunctions.kerml` | Sequence operations: indexing (#), equals, same, size, isEmpty, includes, union, intersection for ordered value seque... |
| `StringFunctions.kerml` | String operations: concatenation (+), Length, Substring, comparison (<, >, <=, >=, ==), and ToString |
| `TrigFunctions.kerml` | Trigonometric functions (sin, cos, tan, arcsin, etc.), degree/radian conversion, pi constant, UnitBoundedReal type |
| `VectorFunctions.kerml` | Vector space operations on VectorValues: add, subtract, scale, dot/cross product, norm, angle, unit vector |

### Kernel Libraries/Kernel Semantic Library

| File | Summary |
|------|---------|
| `Base.kerml` | Root types (Anything, DataValue) and top-level features (things, dataValues, naturals) for all KerML typing |
| `Clocks.kerml` | Clock abstraction with monotonic currentTime, universalClock singleton, and TimeOf function for occurrence timing Hum... |
| `ControlPerformances.kerml` | Control flow behaviors: DecisionPerformance (branching) and MergePerformance (joining) for step sequencing |
| `FeatureReferencingPerformances.kerml` | KerML behaviors for reading, writing, and monitoring feature values on Occurrences (access, write, monitor) |
| `KerML.kerml` | Reflective KerML abstract syntax metamodel with Element, Annotation, Comment, Dependency, Documentation metaclasses |
| `Links.kerml` | General associations (Link, BinaryLink, SelfLink) and features for typing links between things |
| `Metaobjects.kerml` | Metaobject and SemanticMetadata metaclasses for typing syntactic/semantic metadata annotations |
| `Objects.kerml` | Object typing for structural occurrences, with subobjects, performances, and link relationships |
| `Observation.kerml` | Boolean condition monitoring framework with ChangeMonitor, ChangeSignal, and observer notification system |
| `Occurrences.kerml` | Temporal/spatial occurrence modeling with time slices, space slices, portions, and happens-during relationships |
| `Performances.kerml` | KerML base types for behavioral occurrences: Performance, Evaluation, functions, and performer/object tracking |
| `SpatialFrames.kerml` | Spatial reference frames for 3D positioning with PositionOf function and defaultFrame singleton |
| `StatePerformances.kerml` | State machine semantics: StatePerformance behavior with entry/do/exit steps and transition triggers |
| `Transfers.kerml` | Transfer interaction for payload flow between source/target occurrences with instant flag |
| `TransitionPerformances.kerml` | Conditional occurrence transitions with triggers, guards, effects, and accept semantics |
| `Triggers.kerml` | Trigger functions (TriggerWhen, TriggerAt, TriggerAfter) and TimeSignal struct for event-based transitions. |

### Systems Library

| File | Summary |
|------|---------|
| `Actions.sysml` | Base action types and behavioral elements: Action, subactions, Send/Accept/Assign actions, control flow (If/Loop/Merg... |
| `Allocations.sysml` | Allocation def and base feature for source-target binary connections between any elements |
| `AnalysisCases.sysml` | Base types for analysis cases: AnalysisCase definition and analysisCases feature extending Case |
| `Attributes.sysml` | Base types for SysML attributes: AttributeValue (data values for qualities) and attributeValues feature |
| `Calculations.sysml` | Base types for calculations: abstract `Calculation` (extends Action + Evaluation) and `calculations` feature |
| `Cases.sysml` | Base types for cases: Case def (extends Calculation) with subject, actors, objective, result, and subcases Human: 1 m... |
| `Connections.sysml` | Binary/n-ary connection definitions and usages for structural links between parts |
| `Constraints.sysml` | Base constraint types: ConstraintCheck def and constraintChecks/assertedConstraintChecks/negatedConstraintChecks usages |
| `Flows.sysml` | Flow/message base types: MessageAction, Message, FlowConnectionDefinition, FlowConnection, StreamFlowConnection |
| `Interfaces.sysml` | Interface base types: Interface (multi-port Connection), BinaryInterface (2-port), and their usage aliases |
| `Items.sysml` | Base types for Items (general objects in systems) with shape, enveloping shapes, and lifecycle elements. |
| `Metadata.sysml` | Base types for metadata definitions: MetadataItem (abstract def) and metadataItems feature |
| `Parts.sysml` | Base types for parts: Part definition extending Item, with owned ports, actions, and states. |
| `Ports.sysml` | Port base types: abstract Port definition with subports, interfacingPorts, and transfer routing to connected ports |
| `Requirements.sysml` | Base types for requirements checking with assumptions, constraints, subject, and actor parts |
| `StandardViewDefinitions.sysml` | SysML standard view definitions: GeneralView, InterconnectionView, ActionFlowView for model visualization |
| `States.sysml` | State machine base types: StateAction, TransitionAction, entry/do/exit actions, substates, transitions |
| `SysML.sysml` | SysML v2 reflective metamodel: metadata definitions for all SysML element types (actions, parts, ports, etc.) |
| `UseCases.sysml` | UseCase base type extending Case with subject, objective, sub-usecases, and included use cases |
| `VerificationCases.sysml` | Verification case base types with VerdictKind enum (pass/fail/inconclusive/error) and PassIf calc |
| `Views.sysml` | View/Viewpoint/Rendering base types for model visualization and stakeholder concern validation |

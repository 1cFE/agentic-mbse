---
document: SysML_Spec_v2_Part3
generated: 2026-01-13T01:29:26Z
source_checksum: sha256:28a1c11b3b4df0a4573314df0ee459198831c7f642827b787507d5a118a0879c
total_lines: 2000
depth: 3
section_count: 34
---

# SysML_Spec_v2_Part3 Index

## 0 Preface
**Lines:** 147-178

OMG (Object Management Group) organizational overview and specification availability information, including contact details and issue reporting procedures for their standards like UML, CORBA, and MDA.

## 1 Scope
**Lines:** 179-186

Defines the Systems Modeling API and Services standard for accessing, navigating, and operating on KerML/SysML models, enabling interoperability between modeling environments and other engineering tools. Includes a Platform Independent Model (PIM) and two Platform Specific Models (REST/HTTP PSM and OSLC PSM).

## 2 Conformance
**Lines:** 187-221

Defines conformance requirements for Systems Modeling API and Services implementations, distinguishing between PSM-level (REST/HTTP, OSLC) and PIM-level conformance, and specifies six service conformance categories (ProjectService, ElementNavigationService, ProjectDataVersioningService, QueryService, ExternalRelationshipService, ProjectUsageService) that providers must implement and validate against test cases.

## 3 Normative References
**Lines:** 222-244

Lists normative references and standards that SysML v2 depends on or relates to, including KerML, UML, query languages (GraphQL, Gremlin, SPARQL, SQL), interchange formats (XMI, STEP), API specifications (OpenAPI, OSLC), and systems engineering references (SEBoK, INCOSE SE Handbook).

## 4 Terms and Definitions
**Lines:** 245-248

Indicates that terminology definitions are distributed throughout the specification document rather than collected in a dedicated glossary section.

## 5 Symbols
**Lines:** 249-252

Declares that no special symbols are defined in this specification.

## 6 Introduction
**Lines:** 253-254 | **Subsections:** 6.1, 6.2, 6.3, 6.4

Based on this INDEX.md file, Section 6 introduces the SysML v1 to v2 transformation specification, covering the formal mapping approach between UML/SysML v1 and KerML/SysML v2 metaclasses using OCL-based rules, along with acknowledgements of the specification's authors and contributing organizations.

### 6.1 API and Services Architecture
**Lines:** 255-287

Defines the Systems Modeling API architecture using a Platform-Independent Model (PIM) as the logical specification, with Platform-Specific Models (PSMs) providing technology bindings (REST/HTTP and OSLC). This layered approach enables service providers with varied architectures to implement the same API while ensuring consumers remain interoperable across providers.

### 6.2 Document Conventions
**Lines:** 288-305

Defines naming conventions for the Systems Modeling API PIM: service classes use UpperCamelCase (e.g., ElementNavigationService), operations use lowerCamelCase italicized (e.g., *getElementById*), data classes use UpperCamelCase, and data attributes use lowerCamelCase italicized.

### 6.3 Document Organization
**Lines:** 306-321

Describes the document structure: Clause 7 covers the Platform Independent Model (PIM), Clause 8 covers Platform Specific Models (PSMs) for REST/HTTP and OSLC, Annex A defines conformance tests, and Annex B provides REST/HTTP API examples and Jupyter notebook cookbook recipes.

### 6.4 Acknowledgements
**Lines:** 322-374

Lists the primary authors, submitting organizations, and key contributors to the SysML v2 API and Services specification, including SST leadership roles and pilot implementation contributors.

## 7 Platform Independent Model (PIM)
**Lines:** 375-376 | **Subsections:** 7.1, 7.2

Platform Independent Model (PIM) defines system architecture and behavior without specifying implementation technology, serving as a bridge between requirements and platform-specific designs in model-driven development. It captures abstract structural and behavioral elements that can be mapped to multiple concrete platforms.

### 7.1 API Model
**Lines:** 377-378 | **Subsections:** 7.1.1, 7.1.2, 7.1.3, 7.1.4

Defines the data structures and versioning model for the Systems Modeling API, including Record (base type with UUID and identifiers), Project/Commit/Branch/Tag for version control, DataIdentity/DataVersion for tracking element versions, ExternalData/ExternalRelationship for cross-tool linking, and Query for language-independent information retrieval.

#### 7.1.1 Record
**Lines:** 379-392

Defines the abstract **Record** type, the base data structure for all API inputs/outputs. Records have five attributes: `id` (UUID), `resourceIdentifier` (IRI), `alias` (external identifiers), `humanIdentifier` (human-readable ID), and `description`.

#### 7.1.2 Project Data Versioning
**Lines:** 393-500

Defines the Project Data Versioning API model with core concepts: Data (any entity with UUID), DataIdentity (version-independent representation), DataVersion (data at specific version), Project (container with branches/tags/commits), Commit (immutable change records), Branch (mutable development line pointer), Tag (immutable commit annotation), and ProjectUsage (cross-project references). Specifies mutability/destructibility semantics: Commits are immutable and non-destructible, Branches are mutable and destructible, Tags are immutable but destructible.

#### 7.1.3 ExternalData and ExternalRelationship
**Lines:** 501-517

Defines the API model for cross-tool/repository relationships: **ExternalRelationship** links a KerML Element to external resources (with optional mapping specifications in a formal language), while **ExternalData** represents the external resource identified by an IRI.

#### 7.1.4 Query
**Lines:** 518-550

Defines the Query API for language-independent information retrieval, including Query records (with name, select, scope, where, orderBy attributes) and Constraint types (PrimitiveConstraint for simple property-operator-value conditions, CompositeConstraint for combining constraints with AND/OR operators).

### 7.2 API Services
**Lines:** 551-552 | **Subsections:** 7.2.1, 7.2.2, 7.2.3, 7.2.4, 7.2.5, 7.2.6

Defines six service interfaces for the SysML v2 API: ProjectService (CRUD operations for projects), ElementNavigationService (element retrieval and relationship navigation), ProjectDataVersioningService (commits, branches, and tags management), QueryService (query creation and execution), ExternalRelationshipService (cross-project relationship retrieval), and ProjectUsageService (project dependency management).

#### 7.2.1 ProjectService
**Lines:** 553-570

ProjectService provides CRUD operations for managing projects: create (with name and optional description), read (single by ID or all), update (by ID), and delete (by ID).

#### 7.2.2 ElementNavigationService
**Lines:** 571-589

Defines the ElementNavigationService API operations for querying KerML/SysML elements within a project: retrieving all elements, fetching by ID, finding relationships relative to an element, and getting root elements—all scoped to a specific commit.

#### 7.2.3 ProjectDataVersioningService
**Lines:** 590-630

Defines the ProjectDataVersioningService API operations for version control of SysML project data, including commit management (create, get, diff, merge), branch operations (create, delete, get default/head), tag operations (create, delete, get tagged commit), and change tracking via DataVersion records with semantics for creating, updating, and deleting data elements.

#### 7.2.4 QueryService
**Lines:** 631-650

QueryService provides CRUD operations for managing queries within projects (getQueryById, getQueries, createQuery, updateQuery, deleteQuery) and two execution methods (executeQueryById, executeQuery) that run queries against a specified commit or default to the project's default branch head commit.

#### 7.2.5 ExternalRelationshipService
**Lines:** 651-668

ExternalRelationshipService provides three operations for retrieving external relationships within a project at a specific commit: by ID, by associated element ID, or all relationships in the project.

#### 7.2.6 ProjectUsageService
**Lines:** 669-686

ProjectUsageService provides operations for managing project usage relationships: `createProjectUsage` and `deleteProjectUsage` create new commits that add or remove project usages on a branch, while `getProjectUsages` retrieves all project usages at a specific commit.

## 8 Platform Specific Models (PSMs)
**Lines:** 687-688 | **Subsections:** 8.1, 8.2

Platform Specific Models (PSMs) represent system designs tailored to a particular implementation platform or technology, containing platform-dependent details like specific hardware, software frameworks, or communication protocols. They are typically derived from Platform Independent Models (PIMs) through model transformation, bridging abstract system specifications with concrete implementation artifacts.

### 8.1 REST/HTTP PSM
**Lines:** 689-690 | **Subsections:** 8.1.1, 8.1.2, 8.1.3

Defines the REST/HTTP binding of the Systems Modeling API using OpenAPI 3.1, including mappings from PIM concepts (Project, Commit, Branch, Element, etc.) to JSON models and PIM service operations to REST endpoints (GET, POST, PUT, DELETE), plus cursor-based pagination for collection responses.

#### 8.1.1 Overview
**Lines:** 691-697

Defines the REST/HTTP Platform-Specific Model (PSM) for the Systems Modeling API using OpenAPI 3.1, covering two main mappings: PIM API Model concepts to JSON Models, and PIM API Services/operations to REST endpoints.

#### 8.1.2 PIM API Model - REST/HTTP PSM Model Mapping
**Lines:** 698-724

Maps Platform-Independent Model (PIM) API concepts to REST/HTTP Platform-Specific Model (PSM) JSON representations in the OpenAPI specification. Most concepts map directly by name (Project→Project, Commit→Commit, Element→Element, etc.), with MergeResult being the exception where its fields map to Commit and DataIdentity array types.

#### 8.1.3 PIM API Services - REST/HTTP PSM Endpoints Mapping
**Lines:** 725-832

Maps Platform-Independent Model (PIM) service operations to REST/HTTP Platform-Specific Model (PSM) endpoints for the SysML v2 API, covering ProjectService, ElementNavigationService, ProjectDataVersioningService, QueryService, and ExternalRelationshipService CRUD operations. Also defines cursor-based pagination using `page[size]`, `page[before]`, and `page[after]` query parameters with Link headers conforming to IETF Web Linking.

### 8.2 OSLC 3.0 PSM
**Lines:** 833-834 | **Subsections:** 8.2.1, 8.2.2, 8.2.3, 8.2.4

OSLC 3.0 Platform-Specific Model (PSM) maps the Systems Modeling API and Services PIM to OSLC standards, defining how PIM concepts (Project, Branch, Tag, DataVersion) map to OSLC resource types (Component, Stream, Baseline, VersionResource), and how PIM services map to OSLC REST operations using discovery, creation factories, query capabilities, and RDF-based linked data protocols.

#### 8.2.1 Overview
**Lines:** 835-848

Introduces the OSLC Platform-Specific Model (PSM) for the Systems Modeling API, noting it uses OpenAPI Specification 2.0 with implementation-specific URLs discovered via OSLC discovery mechanisms. Outlines the subsection structure covering OSLC nomenclature, PIM-to-OSLC resource mappings, and service mappings.

#### 8.2.2 OSLC Nomenclature
**Lines:** 849-904

OSLC (Open Services for Lifecycle Collaboration) is a specification framework for integrating lifecycle tools using W3C Linked Data, RDF vocabularies, and HTTP for CRUD operations on artifacts. It covers discovery mechanisms (service provider catalogs, creation factories, query capabilities, dialogs), resource shapes for describing RDF types and properties, Linked Data Platform Containers, and supported media types (RDF/XML, Turtle, JSON-LD).

#### 8.2.3 PIM API Model Ð OSLC PSM Resource Mapping
**Lines:** 905-931

Defines the mapping from PIM API Model concepts to OSLC PSM resource types, including KerML/SysML abstract syntax elements mapped to OSLC resource shapes, and API concepts (Project, Branch, Tag, Commit, DataIdentity, DataVersion, Query, constraints) mapped to OSLC Configuration Management and Query specification resources, with some concepts (Commit, ProjectUsage, DataDifference, MergeResult) having no OSLC equivalent.

#### 8.2.4 PIM API Services Ð OSLC PSM Service Mapping
**Lines:** 932-2000

Defines the mapping between Platform-Independent Model (PIM) API services (ProjectService, ElementNavigationService, ProjectDataVersioningService, QueryService, ExternalRelationshipService, ProjectUsageService) and their corresponding OSLC 3.0 Platform-Specific Model implementations, including HTTP methods, query patterns, and noting which operations are not available in OSLC. Also includes normative conformance test cases with OCL preconditions and postconditions for each PIM service operation.

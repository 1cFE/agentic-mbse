# SysML v2 Textual Notation — Quick Cheatsheet (Beta 4)

*Cheat sheet aligns with the SysML v2.0 **Beta 4** specification and was prepared for INCOSE IS 2025.*  

---

## Contents
- [Language Overview](#language-overview)
- [Actions](#actions)
- [Constraints & Requirements](#constraints--requirements)
- [Constructs & Expressions](#constructs--expressions)
- [Keywords & Shorthand](#keywords--shorthand)
- [Packages](#packages)
- [Parts](#parts)
- [Items](#items)
- [Connections & Ports](#connections--ports)

---

## Language Overview
SysML v2 covers:
- **Requirements**
- **Behavior**
  - Action-based
  - State-based
  - Use cases
- **Structure**
  - Classification
  - Decomposition
  - Interconnection

> Tip: Use these snippets with a SysML v2 toolchain that understands textual notation (Beta 4).

---

## Actions

### Action Definitions
```sysml
action def StartEngine {
    in ignitionSignal : Boolean;
    out status : EngineStatus;
}
```

### Composite Action & Sequencing
```sysml
action def Drive {
    action accelerate : Accelerate;
    first start then accelerate;
}
```

### Performing an Action from a Part
```sysml
part vehicle : Vehicle {
    action driveVehicle : Drive;
    action pressGas {
        perform driveVehicle;
    }
}
```

### State Definition
```sysml
state def EngineStates {
    state Off;
    state Running;
}
```

---

## Constraints & Requirements

### Constraint Definition & Usage
```sysml
constraint def IsFull {
    in tank : FuelTank;
    tank.fuelLevel == tank.maxFuelLevel
}

part def Vehicle {
    part fuelTank : FuelTank;
    constraint tankIsFull : IsFull {
        in tank = fuelTank;
    }
}
```

### Requirement Definition & Usage with Satisfy
```sysml
requirement def MassRequirement {
    subject vehicle : Vehicle;
    attribute massActual  : ISQ::MassValue;
    attribute massLimit   : ISQ::MassValue;
    require constraint { massActual <= massLimit }
}

requirement <R1> vehicleMass : MassRequirement {
    attribute :>> massActual = vehicle.mass;
    attribute :>> massLimit  = 1800 [kg];
}

satisfy R1 by vehicle;
```

**Legend (concepts referenced above):**
- **Constraint Definition / Usage**
- **Requirement Definition / Usage**
- **Satisfy Requirement**
- **Action Definition / Composite Action / Perform Action**
- **State Definition**

---

## Constructs & Expressions

### Notes & Documentation
| Construct     | Expression            | Example                 |
|---------------|------------------------|-------------------------|
| Line note     | `// <text>`           | `// this is a comment`  |
| Block note    | `//* <text> */`       | `//* also comment */`   |
| Comment       | `/* <text> */`        | `/* a comment */`       |
| Documentation | `doc /* <text> */`    | `doc /* Doc text */`    |

### Core Declarations
| Construct        | Expression                         | Example                      |
|------------------|------------------------------------|------------------------------|
| Definition       | `<kind> def <name>`                | `part def Vehicle`           |
| Classifier       | `classifier <name>`                | `classifier Person`          |
| Usage            | `<kind> <name> : <type>`           | `part bike : Vehicle`        |
| Feature          | `feature <name> : <type>`          | `feature age : Integer`      |
| Specialization   | `<child> :> <parent>`              | `SportsCar :> Vehicle`       |
| Redefinition     | `:>> <property>`                   | `:>> total_wheels = 2`       |
| Import           | `<visibility> import <name>`       | `private import ISQ::*;`     |
| Qualified ref    | `<namespace>::<member>`            | `ISQ::MassValue`             |
| Assignment       | `<target> = <value>`               | `mass = 1500 [kg]`           |
| Comparison ops   | `<  <=  ==  !=  >=  >  ===  !==`   | `a == b`                     |
| Metadata         | `@<metadata>`                      | `@ToolMetadata`              |

### Multiplicity
| Construct         | Expression                                  | Example        |
|-------------------|---------------------------------------------|----------------|
| Range             | `<name> [<lowerBound> .. <upperBound>]`     | `Wheel [0..*]` |
| Fixed count       | `<name> [<count>] : <Type>`                  | `wheel [4] : Wheel` |

---

## Keywords & Shorthand

| Keyword       | Short Form | Repeatable |
|---------------|------------|-----------:|
| `defined by`  | `:`        | ✔          |
| `specializes` | `:>`       | ✔          |
| `subsets`     | `:>`       | ✔          |
| `references`  | `::>`      | ✘          |
| `crosses`     | `=>`       | ✘          |
| `redefines`   | `:>>`      | ✔          |

> **Note:** Shorthand `a:b,c` is allowed; `a::>b,c` is **not** allowed.

---

## Packages

### Package Definition, Imports, and Alias
```sysml
package VehicleModel {
    public import VehicleParts;
    private import ISQ::MassValue;
    alias MV for ISQ::MassValue;
}
```

---

## Parts

### Part Definitions and Specialization
```sysml
part def Engine;

part def Vehicle {
    attribute mass   : MassValue;
    attribute wheels : Integer;
}

part def SportsCar :> Vehicle {
    :>> wheels = 4;
}
```

### Part Usage & Property Redefinition
```sysml
part vehicle : Vehicle {
    :>> mass = 1500 [kg];
    part engine : Engine;
}
```

---

## Items

### Item Definition
```sysml
item def Fuel {
    attribute fuelMass :> ISQ::mass;
}
```

---

## Connections & Ports

### Connection Definition & Usage
```sysml
connection def DeviceConn {
    end part hub    : Hub;
    end part device : Device;
    attribute bandwidth : Real;
}

connection connection : DeviceConn {
    end part hub    ::> mainSwitch;
    end part device ::> sensorFeed;
}
```

### Port Definition & Usage
```sysml
port def FuelingPort {
    attribute flowRate : Real;
    out fuelOut : Fuel;
    in  fuelIn  : Fuel;
}

port fuelTankPort : FuelingPort;
```

---

## Attribution
- Excerpts and examples are derived from the OMG® **SysML® v2.0 Beta 4** specification.  
- © 2019–2025 Object Management Group, Inc. and its contributors. All rights reserved.  

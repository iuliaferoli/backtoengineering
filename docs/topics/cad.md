---
id: cad
title: "CAD"
type: topic
category: mechanical
tree_icon: vector
prerequisites: [3d-printing]
contributors:
  - username: sunkmechie
    url: https://github.com/sunkmechie
    pr: https://github.com/iuliaferoli/backtoengineering/pull/
---

# CAD

Designing parts on screen before they exist. Sketches, constraints, and assemblies.

## You can move on when you can...

- Fully constrain a sketch and explain the difference between geometric
  and dimensional constraints
- Build a multi-feature part using at least extrude, revolve, fillet, and
  pattern, and explain why feature order matters
- Design an assembly using mates/joints and explain how a revolute joint
  in CAD maps to the \(\theta_i\) in a kinematic chain
- Choose an appropriate fit (clearance/transition/interference) for a
  given mechanical requirement
- Calculate a worst-case and RSS tolerance stack-up for a simple chain of
  toleranced dimensions
- Explain why a fillet at an internal corner isn't just cosmetic
- Export the right file format for a given purpose (STEP to collaborate
  and edit, STL to print)
- Write a simple parametric part in OpenSCAD or CadQuery


## Sketches and constraints

Almost all modern CAD (SolidWorks, Fusion 360, Onshape, FreeCAD) is **parametric**: you don't draw a line of a fixed length, you draw a line and then *constrain* it, 
- "this length is 40mm,"
- "this edge is parallel to that one,"
- "this hole is centered on this face." 

Change one dimension later and every downstream feature updates automatically.

Two constraint types you'll use constantly:

- **Geometric constraints**: parallel, perpendicular, concentric, tangent, symmetric. These constraint *shape* without constraining the *size*.
- **Dimensional constraints**: an explicit length, angle, or radius. These constraint *size*.

A sketch is **fully constrained** when there's exactly one way to satisfy every constraint, i.e no degrees of freedom left to drag around. Most CAD tools color fully-constrained sketches differently (often black/green) vs. under-constrained ones (often blue/red) specifically so you can catch this at a glance. An under-constrained sketch is one of the most common sources of
 "this part looks right until I change one dimension and the whole thing falls apart" bugs.

!!! tip "Fully constrain every sketch, always"
    It's tempting to eyeball a sketch until it "looks right" and move on.
    Don't. An under-constrained sketch will silently shift shape the moment
    someone (including future you) edits an earlier feature.

## From sketch to solid: features

A 2D sketch becomes a 3D solid through **features**, the parametric operations that build the part up (or cut it down):

| Feature | What it does |
|---|---|
| Extrude | Pushes a 2D sketch profile out in a straight line to become a solid |
| Revolve | Spins a sketch profile around an axis (e.g. how you'd model a bolt or a bushing) |
| Sweep | Moves a profile along a path (e.g. a wire conduit, a handle) |
| Loft | Blends between two or more different profiles (e.g. a tapered enclosure) |
| Fillet / Chamfer | Rounds or bevels an edge, this removes stress concentrations at sharp internal corners and also adds design aesthetic|
| Shell | Hollows out a solid to a given wall thickness (how most enclosures are actually modeled) |
| Pattern (linear/circular) | Repeats a feature along a line or around a circle (e.g. a bolt circle, a row of cooling vents) |

The sequence of features is recorded as a **feature tree** (also called a design history or timeline). This is the single biggest thing that distinguishes parametric CAD from toolslike Blender: you can go back, edit step 3 of 40, and everything downstream recomputes. It's also why feature order matters, a fillet applied before a pattern behaves very differently than one applied after.

## Assemblies: mates and joints

An assembly brings multiple parts together and constrains how they move relative to each other, using the same idea as sketch constraints but in 3D:

- **Mates / constraints** (SolidWorks/Fusion terminology): coincident, concentric, parallel, distance, angle, fix how two parts sit relative to each other.
- **Joints**: revolute (rotation about an axis, like a hinge), slider (translation along an axis), cylindrical (rotation + translation along the same axis), ball (free rotation about a point).



## Tolerances and fits

Nothing manufactures to an exact dimension, every process has variation.

A **tolerance** specifies the acceptable range: a hole spec'd as \(10.0 \pm 0.1\text{mm}\) is acceptable anywhere from 9.9mm to 10.1mm.

When two parts mate (a shaft in a hole, a pin in a bracket), the combination of both parts' tolerances determines the **fit**:

| Fit type | Relationship | Typical use |
|---|---|---|
| Clearance fit | Hole always larger than shaft | Parts that need to rotate or slide freely |
| Transition fit | Could go either way depending on tolerance stack | Alignment pins, light press |
| Interference fit | Shaft always larger than hole | Permanent or semi-permanent joints (bearing press-fits) |

**Tolerance stack-up** when you chain several toleranced dimensions together

\[
T_{total} = \sum_{i=1}^{n} T_i \quad \text{(worst case)}
\]

\[
T_{total} = \sqrt{\sum_{i=1}^{n} T_i^2} \quad \text{(statistical / RSS method)}
\]

The worst-case sum is guaranteed-safe but overly conservative for anything with more than a couple of toleranced dimensions in the chain; the RSS (root-sum-square) method assumes tolerances are normally distributed, which is usually a fair assumption for independently-manufactured parts, and gives a much tighter (less wasteful) estimate

For 3D-printed parts specifically, we commonly under- or over-size holes/pins by 0.1-0.3mm depending on machine calibration; always print a tolerance test coupon (a small part with a range of hole/pin clearances) on a new printer/material combination before committing to a fit in a real assembly.

## GD&T (Geometric Dimensioning & Tolerancing)

Beyond simple linear tolerances, **GD&T** (standardized in ASME Y14.5) gives a symbolic language for controlling *form*, *orientation*, *location*, and *runout*. A hole can be perfectly sized but still unusable if it's tilted or off-center. 

Common symbols you'll actually encounter:

| Symbol | Controls |
|---|---|
| ⏥ Flatness | How flat a surface is, independent of size |
| ⏊ Perpendicularity | Angle of a feature relative to a reference (datum) |
| ⌖ Position | Location of a feature (e.g. a hole) relative to datums |
| ⌭ Concentricity | Whether an axis is centered relative to a reference axis |


## A quick intuition for stress and stiffness

**Moment of inertia** (of the cross-section, not to be confused with mass moment of inertia from dynamics) determines bending stiffness. For a solid rectangular cross-section of width \(b\) and height \(h\), bent about its centroidal axis:

\[
I = \frac{b h^3}{12}
\]

Note the *cube* on \(h\), doubling a beam's height in the bending direction increases stiffness 8x, while doubling its width only doubles it. This is why ribs and gussets in 3D-printed/injection-molded parts are almost always oriented to add height in the load direction, not width.

**Stress concentration**: sharp internal corners concentrate stress far above the nominal average, a small fillet radius \(r\) at a corner can cut peak stress dramatically compared to a sharp corner, which is why "add a fillet, even a tiny one" is a universal CAD advice at any internal corner that will see load, not just a cosmetic choice.

!!! warning "Sharp internal corners are real failure points"
    On 3D-printed parts especially, layer adhesion is already weaker than
    the bulk material, combine that with an unfilleted internal corner
    concentrating stress, that's the most common place a
    printed bracket cracks under load.

## Parametric modeling in code

Beyond GUI-based CAD, code-driven CAD lets you define geometry programmatically, useful for robotics when you want a part that scales with a variable (e.g. a bracket that needs to fit different motor sizes) or when you want version-controlled, diffable design files instead of binary CAD files.

**OpenSCAD** (script-based, functional/CSG style):

```openscad
// Parametric motor mount bracket
motor_diameter = 28;   // NEMA-11 stepper, for example
wall_thickness = 3;
mount_height = 20;
bolt_hole_dia = 3.2;   // clearance for M3
bolt_circle_dia = 35;

difference() {
    cylinder(h=mount_height, d=motor_diameter + 2*wall_thickness, $fn=64);
    translate([0, 0, -1])
        cylinder(h=mount_height + 2, d=motor_diameter, $fn=64);
    for (angle = [0, 90, 180, 270]) {
        rotate([0, 0, angle])
            translate([bolt_circle_dia/2, 0, -1])
                cylinder(h=mount_height + 2, d=bolt_hole_dia, $fn=32);
    }
}
```

Change `motor_diameter` once and every dependent dimension (the outer cylinder, the bolt circle) updates, the same core idea as GUI-based parametric constraints, just expressed as code instead of dragging dimensions.

**CadQuery** (Python-based):

```python
import cadquery as cq

motor_d = 28
wall = 3
height = 20

bracket = (
    cq.Workplane("XY")
    .circle(motor_d / 2 + wall)
    .circle(motor_d / 2)
    .extrude(height)
)

result = bracket.faces(">Z").workplane().polygon(4, 35, forConstruction=True) \
    .vertices().hole(3.2)

cq.exporters.export(result, "motor_mount.step")
```

## File formats: which one to use when

| Format | Type | Use it for |
|---|---|---|
| STEP (.step/.stp) | Exact parametric geometry (boundary representation) | Sharing a fully editable, exact model between different CAD programs |
| STL | Mesh (triangulated surface, no exact curves) | 3D printing input is sufficient because slicers only need the surface mesh, not exact parametric geometry |
| IGES | Exact geometry, older standard | Legacy interchange, mostly superseded by STEP |
| Native (.sldprt, .f3d, etc.) | Full parametric history, vendor-specific | Only useful within the same CAD package, don't rely on it for collaboration across tools |

A common mistake: sending someone an STL when they need to *edit* the design. STL has already thrown away the sketches, constraints, and feature history, it's a dead-end mesh, useful for printing but not for further parametric editing. Always share STEP (or native format, if the collaborator uses the same CAD tool) when a design still needs to change.

## Software landscape

| Tool | Type | Notes |
|---|---|---|
| [Onshape](https://www.onshape.com/) | Cloud, parametric | Free tier for public/non-commercial projects, real-time multi-user collaboration, a strong default for open-source hardware projects |
| [Fusion 360](https://www.autodesk.com/products/fusion-360) | Cloud-hybrid, parametric | Free for hobbyists/personal use, widely used in industry, includes basic simulation/FEA and CAM |
| [FreeCAD](https://www.freecad.org/) | Desktop, parametric, open source | Fully free and open source, improving fast (v1.0 released 2024), good choice if you want to avoid vendor lock-in entirely |
| [SolidWorks](https://www.solidworks.com/) | Desktop, parametric | Industry-standard in mechanical engineering firms, expensive, the one you'll most likely meet in a professional setting |
| [OpenSCAD](https://openscad.org/) | Script-based, open source | Code-first CSG modeling, great for fully parametric, version-controllable parts; no sketch-based UI |
| [CadQuery](https://cadquery.readthedocs.io/) | Python library, open source | OpenSCAD's ideas but in Python, integrates naturally with a robotics/scripting workflow |

## References

- ASME Y14.5-2018. *Dimensioning and Tolerancing.* 
- Drake, S. *Dimensioning and Tolerancing Handbook.* McGraw-Hill, practical reference for tolerance stack-up methods (worst-case vs. RSS).
- Shigley, J.E., Mischke, C.R., & Budynas, R.G. *Shigley's Mechanical Engineering Design.* McGraw-Hill. [**GOD-TIER BOOK FOR EVERY STUDENT/PRACTICING ENGINEER**]


## External Resources

- [Onshape Learning Center (free)](https://learn.onshape.com/)
- [Fusion 360 for beginners (Autodesk)](https://www.autodesk.com/products/fusion-360/learn-explore)
- [FreeCAD documentation](https://wiki.freecad.org/)
- [OpenSCAD User Manual](https://en.wikibooks.org/wiki/OpenSCAD_User_Manual)
- [CadQuery documentation](https://cadquery.readthedocs.io/)
- [Engineers Edge: Fits and Tolerances reference tables](https://www.engineersedge.com/fits_and_tolerances.htm)
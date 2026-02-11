

<!-- PAGE:1 -->

_J. Plasma Phys._ (2020), _vol._ 86, 865860502 © The Author(s), 2020. 1
Published by Cambridge University Press

This is an Open Access article, distributed under the terms of the Creative Commons
[Attribution-NonCommercial-NoDerivatives licence (http://creativecommons.org/licenses/by-nc-nd/4.0/), which](http://creativecommons.org/licenses/by-nc-nd/4.0/)
permits non-commercial re-use, distribution, and reproduction in any medium, provided the original work is
unaltered and is properly cited. The written permission of Cambridge University Press must be obtained for
commercial re-use or in order to create a derivative work.
doi:10.1017/S0022377820001257
# Overview of the SPARC tokamak

A. J. Creely 1,†, M. J. Greenwald 2, S. B. Ballinger2, D. Brunner1, J. Canik3,
J. Doody [2], T. Fülöp 4, D. T. Garnier2, R. Granetz2, T. K. Gray3, C. Holland5,
N. T. Howard [2], J. W. Hughes 2, J. H. Irby2, V. A. Izzo6, G. J. Kramer7,
A. Q. Kuang 2, B. LaBombard2, Y. Lin 2, B. Lipschultz8, N. C. Logan7,
J. D. Lore [3], E. S. Marmar [2], K. Montes [2], R. T. Mumgaard [1], C. Paz-Soldan 9,
C. Rea 2, M. L. Reinke3, P. Rodriguez-Fernandez 2, K. Särkimäki 4,
F. Sciortino [2], S. D. Scott [1], A. Snicker [10], P. B. Snyder [9], B. N. Sorbom [1],
R. Sweeney [11], R. A. Tinguely [2], E. A. Tolman [2], M. Umansky [12], O. Vallhagen [4],
J. Varje [10], D. G. Whyte [2], J. C. Wright [2], S. J. Wukitch [2], J. Zhu [2]

and the SPARC Team [1][,][2]

1Commonwealth Fusion Systems, Cambridge, MA, USA

2Plasma Science and Fusion Center, Massachusetts Institute of Technology, Cambridge, MA, USA

3Oak Ridge National Laboratory, Oak Ridge, TN, USA

4Chalmers University of Technology, Göteborg, Sweden

5University of California – San Diego, San Diego, CA, USA

6Fiat Lux, San Diego, CA, USA

7Princeton Plasma Physics Laboratory, Princeton, NJ, USA

8York Plasma Institute, University of York, Heslington, York, UK

9General Atomics, San Diego, CA, USA

10Aalto University, Espoo, Finland

11ORISE, Oak Ridge National Laboratory, Oak Ridge, TN, USA

12Lawrence Livermore National Laboratory, Livermore, CA, USA

(Received 18 May 2020; revised 9 September 2020; accepted 10 September 2020)

The SPARC tokamak is a critical next step towards commercial fusion energy. SPARC
is designed as a high-field ( _B_ 0 = 12 _._ 2 T), compact ( _R_ 0 = 1 _._ 85 m, _a_ = 0 _._ 57 m),
superconducting, D-T tokamak with the goal of producing fusion gain _Q >_ 2 from a
magnetically confined fusion plasma for the first time. Currently under design, SPARC
will continue the high-field path of the Alcator series of tokamaks, utilizing new
magnets based on rare earth barium copper oxide high-temperature superconductors to
achieve high performance in a compact device. The goal of _Q >_ 2 is achievable with
conservative physics assumptions ( _H_ 98 _,y_ 2 = 0 _._ 7) and, with the nominal assumption of
_H_ 98 _,y_ 2 = 1, SPARC is projected to attain _Q_ ≈ 11 and _P_ fusion ≈ 140 MW. SPARC will
therefore constitute a unique platform for burning plasma physics research with high
density (⟨ _ne_ ⟩≈ 3 × 10 [20] m [−][3] ), high temperature (⟨ _Te_ ⟩≈ 7 keV) and high power density

[† Email address for correspondence: alex@cfs.energy](mailto:alex@cfs.energy)

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

<!-- PAGE:2 -->

( _P_ fusion _/V_ plasma ≈ 7 MW m [−][3] ) relevant to fusion power plants. SPARC’s place in the path
to commercial fusion energy, its parameters and the current status of SPARC design
work are presented. This work also describes the basis for global performance projections
and summarizes some of the physics analysis that is presented in greater detail in the
companion articles of this collection.

Key words: fusion plasma, plasma confinement, plasma devices

## 1 Introduction

The world faces an increasingly urgent need for clean energy, as the effects of climate
change are already manifesting and the existing portfolio of clean energy sources has not
been deployed quickly enough to broadly reduce greenhouse gas emissions. Fusion energy
is one possible solution to this need, but it must be developed and deployed rapidly in order
to make a difference on the time scales necessary to have an impact on climate change.
Fusion is safe, energy-dense and dispatchable; produces no greenhouse gas emissions;
and generates minimal radiological waste. Although the plasma physics governing fusion
devices is relatively well understood, no fusion device has yet demonstrated gain _Q >_ 1,
which is a critical step on the path to commercializing fusion as an energy source.
Achieving fusion gain _Q >_ 1 [1] in a magnetic confinement device has long been the aim
of fusion research around the world. Recently, several studies have also emphasized that
construction of a pilot fusion power plant should be a near-term priority of fusion research
in the USA (National Academies of Sciences, Engineering and Medicine 2019; American
Physical Society Division of Plasma Physics Community Planning Process 2020). Beyond
demonstrating _Q >_ 1 and constructing a pilot power plant, however, it is vital that fusion’s
path to commercial power generation be both timely and economical if the goal is to
transform the energy economy and combat climate change.
This motivation led to the founding of the SPARC project with two central mission
objectives. The first is to achieve a fusion gain _Q >_ 2, demonstrating fusion energy
production from the plasma with margin over break-even ( _Q_ = 1), as a critical next step
on the path to commercial fusion energy. If SPARC exceeds this goal and achieves higher
gain, it will also address many novel challenges in burning plasma research (including burn
control, burning plasma self-organization, alpha particle–magnetohydrodynamic (MHD)
mode interactions, divertor physics and disruption prediction and mitigation). Second, it is
SPARC’s mission to demonstrate the viability of rare earth barium copper oxide (REBCO)
high-temperature superconducting (HTS) magnets in an integrated fusion confinement
facility, thereby paving the way for future power plants based on this technology, such
as the ARC power plant concept (Sorbom _et al._ 2015; Kuang _et al._ 2018). The SPARC
project aims to show that the high magnetic fields possible with REBCO-based magnets
allow one to reduce the size of fusion devices and facilitate rapid and lower-cost progress
(Meade 2002 _a_ ; Maingi _et al._ 2018; National Academies of Sciences, Engineering and
Medicine 2019).
SPARC’s focus on high magnetic field and compact size is an extension of what is often
called the ‘high-field path’ to fusion energy (Whyte _et al._ 2016), and is based on the same
principles as those that led to proposals for high-field copper devices such as CIT (Furth
1987), BPX (Goldston 1992), FIRE (Meade 2002 _b_ ) and Ignitor (Coppi _et al._ 1999, 2001;

1Fusion gain is defined as the fusion power generated in the plasma divided by the external heating power absorbed
in the plasma, including ohmic power.

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

<!-- PAGE:3 -->

Feresin 2010). The high-field path, and SPARC’s place in it, is described further in § 2.
SPARC’s use of REBCO superconductors also builds upon the legacy of past designs that
focused on high magnetic field, including VULCAN (Olynyk _et al._ 2012), ARC (Sorbom
_et al._ 2015; Kuang _et al._ 2018) and designs by Tokamak Energy (Costley 2016).
In line with the focus on high magnetic field and new magnet technology, it is
the philosophy of the SPARC project to design a machine based on conservative,
well-established physics assumptions and to rely on innovative engineering and technology
to minimize the size and cost of a _Q >_ 2 device. Performance projections for SPARC,
which are described further in § 4, are based largely on the ITER Physics Basis (ITER
Physics Basis Editors _et al._ 1999; Shimada _et al._ 2007), and SPARC is designed with
considerable margin in plasma performance in order to ensure that the machine’s mission
is feasible even given the uncertainties in performance projections. SPARC’s engineering
design also builds on the work of many other machines and design studies, including
experience of past D-T devices such as TFTR and JET, and designs for ITER.
The remainder of this article, which is the first of a collection describing the status
of and work to date on SPARC, will address the following. First, § 2 describes where
SPARC fits into the greater fusion ecosystem and how its design came about. Next, § 3
presents the major SPARC parameters and the machine cross-section. Section 4 then
discusses the methodology used to project SPARC’s plasma performance and describes
the projected performance in several operational scenarios. Finally, § 5 introduces the other
major physics analyses that have been performed for SPARC V2 (Version 2, referring to
the latest design), including work on core confinement, H-mode access and pedestals,
divertor physics, MHD and disruptions, radio-frequency heating and alpha physics, many
of which are presented in greater detail in other articles in this collection (Hughes _et al._
2020; Kuang _et al._ 2020; Lin, Wright & Wukitch 2020; Rodriguez-Fernandez _et al._ 2020;
Scott _et al._ 2020; Sweeney _et al._ 2020).

## 2 SPARC and the high-field path to commercial fusion energy

Since the early days of fusion research, the science and technology of tokamaks have
made enormous progress. New records were set in the triple product, the primary metric
of plasma performance, every few years. Building on this progress, TFTR and JET made
another leap forward, setting records not just in triple product but in D-T fusion gain
(Strachan _et al._ 1997; Keilhacker 1999). Unfortunately, however, this progress has largely
stalled since the 1990s. While the science of plasma physics and fusion has advanced
considerably since that time, the record fusion gains from TFTR and JET (and the record
D-T equivalent performance in JT-60U (Kishimoto _et al._ 2005)) still stand many years
later.
In order to understand what led to this delay in progress, one must ask what the primary
factors in increasing the triple product, or the fusion gain, are. As is laid out in the ITER
Physics Basis (ITER Physics Basis Editors _et al._ 1999), the Progress in the ITER Physics
Basis (Shimada _et al._ 2007) and elsewhere (see Zohm 2010; Whyte _et al._ 2016), one can
primarily improve fusion performance in three ways. The first is to discover new operating
regimes (such as the discovery of H-mode (Wagner _et al._ 1982)) or ways of overcoming
known physical limits. The second is to increase the magnetic field of the machine. The
third is to increase the physical size of the machine. In the absence of the discovery of new
physics, increased machine performance must rely on either increased magnetic field or
increased size.
Plotting the achievable fusion gain _Q_ against toroidal field on axis _B_ 0 and major radius
_R_ 0 gives the relationship shown in figure 1. The calculations in figure 1 keep _ϵ_, shaping
( _κ_ and _δ_ ), _q_ [∗], impurity content and _H_ 98 _,y_ 2 constant, and limit operation to below 0 _._ 9 _nG_

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

<!-- PAGE:4 -->

FIGURE 1. Fusion gain _Q_ plotted against toroidal field on axis _B_ 0 and major radius _R_ 0. Gain
_Q_ is calculated with the empirical scaling methods presented in § 4, keeping _ϵ_ = 0 _._ 31, _κa_ =
1 _._ 75, _δ_ sep = 0 _._ 54, _q_ [∗] = 3 _._ 05, impurity content and _H_ 98 _,y_ 2 = 1 constant, and limiting operation
to below 0 _._ 9 _nG_ . In order to compare these calculated contours with specific design points, other
machines (both built and proposed) are marked at their respective _R_ 0 and _B_ 0 values (Parker _et al._
1985, 1988; Hutchinson 1989; Neilson 1992; Coppi _et al._ 1999, 2001; Keilhacker _et al._ 2001;
Meade 2002 _b_ ; Shimada _et al._ 2007; Sorbom _et al._ 2015; Federici _et al._ 2018). Despite differences
in shaping and other parameters, the gain (or D-T equivalent gain) predicted or observed in most
other machines aligns with the plotted _Q_ contours, showing the generality of the relationship
between _B_ 0, _R_ 0 and _Q_ . The vertical dashed grey line is the approximate on-axis field limit for
LTS-based machines. Plasma volume is shown on the right vertical axis as an indicator of project
scale.

(see § 4 for further details of these empirical scaling calculations). Note that this particular
calculation considers only core confinement and does not take into account plasma
exhaust, neutron loading or engineering constraints. The gain is a nonlinear function of
both field and size, and by increasing field, one can decrease size and obtain the same
gain without changing any physics assumptions (Whyte _et al._ 2016). The good agreement
between the _Q_ contours in figure 1 and predictions or observations from other machine
design points reveal the generality of the relationship between toroidal field, size and gain.
This motivates aiming for the highest field possible given technological constraints.
On the path to commercial fusion energy, one must also consider the applicability of
any given technology to an economical power plant. For this reason, it is infeasible to use
copper toroidal field magnets, as it would be extremely challenging for a power plant to
overcome the electricity cost of running the magnets. This has led to the general conclusion
that any viable power plant must have superconducting magnets.
At the time of ITER’s design, the state-of-the-art superconductor was Nb3Sn, and the
‘magnetic field that [was] practically achievable with available superconducting materials

[was] limited to approximately 13 T on the conductor’ (Huguet 1993). This field on coil,
in a standard aspect ratio tokamak ( _ϵ_ ≈ 0 _._ 3), limited the field on axis to roughly 5 or 6 T
(Whyte _et al._ 2016). As figure 1 shows, limiting the toroidal field to 5.3 T requires a major
radius of approximately 6 m to achieve _Q_ ≈ 10. In this sense, ITER FEAT was designed
to be the smallest machine that would achieve _Q_ ≈ 10 while respecting hard limits in the
allowable magnetic field given the technology at the time. Unfortunately, anything this
large is inevitably expensive and time consuming, which, along with other political and
organizational factors arising from the scale of the undertaking, contributed to the slowed
progress in fusion gain over the last 20 years. The pace and cost of such large, complex

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

![](images/tmp7a0ae_mb.pdf-3-4.png)

<!-- PAGE:5 -->

projects also do not bode well for the economic viability of a commercial power plant
based on this approach. The current EU-DEMO design point (Federici _et al._ 2018) is also
shown in figure 1. Note that the shaping for EU-DEMO (and for ITER) is less than is
assumed in figure 1, and so the projected performance of EU-DEMO, _Q_ ≈ 40 (Federici
_et al._ 2018), is less than that indicated.
Even at the time of ITER’s design, however, it was recognized that without the constraint
in magnetic field, it would be possible to build a high-gain device that was much smaller.
This sentiment is manifested in designs for several high-field copper devices, such as
CIT (Furth 1987; Parker _et al._ 1988; Thome _et al._ 1991), BPX (Goldston 1992), FIRE
(Meade 2002 _b_ ) and Ignitor (Coppi _et al._ 1999, 2001; Feresin 2010) (see table 1 for more
information on the parameters for these machines), that aimed to achieve high gain on
much smaller scales than ITER. These devices followed the high-field path of the Alcator
series of tokamaks and aimed at accessing high gain with the knowledge that their magnet
technology would not be applicable in a power plant. Given what has been discovered since
their design, it still seems likely that these machines would have achieved break-even (and
possibly high gain), if they had been constructed. BPX, CIT, FIRE and Ignitor are also
shown in figure 1, and fall right along the _Q_ ≈ 10 curve.
In recent years, however, new HTS materials have emerged as viable alternatives to
older low-temperature superconductor (LTS) ones. One of these, REBCO, has previously
been recognized as having the potential for use in fusion magnets (Bangerter, Navratil
& Sauthoff 2003; Greenwald _et al._ 2007; Hazeltine _et al._ 2009; Maingi _et al._ 2018;
National Academies of Sciences, Engineering and Medicine 2019), but until recently was
not mature enough for large-scale production. Now it is available in large quantities and at
high performance and provides access to much higher magnetic fields than was possible
with Nb3Sn (Whyte _et al._ 2016). This technology allows for a new design optimization
of a superconducting _Q >_ 1 tokamak (and the path afterwards to a commercial power
plant), with different engineering constraints but built on the same physics basis as
ITER.
As was the case when ITER was designed, a _Q >_ 1 device is still an essential part
of any path to a fusion power plant for political and commercial reasons. SPARC’s
mission of _Q >_ 2 achieves this milestone with enough margin to be definitive. Achieving
a burning plasma ( _Q_ ≈ 5) would also unlock access to new physics regimes that have not
been explored on current devices. With the existence of HTS magnets, however, one can
build a much smaller device, similar in scale to current devices such as DIII-D, ASDEX
Upgrade, EAST and KSTAR (and to CIT, BPX, FIRE and Ignitor), and achieve these
goals quickly and at low cost. Perhaps even more importantly, this technology may lead to
an economically attractive power plant (Sorbom _et al._ 2015; Maingi _et al._ 2018; National
Academies of Sciences, Engineering and Medicine 2019), which will be essential for the
widespread adoption of fusion energy.
SPARC is the result of combining new HTS technology with the same proven physics
that led to the ITER, CIT, BPX and FIRE designs. With _R_ 0 = 1 _._ 85 m and _B_ 0 = 12 _._ 2 T
(other details of the SPARC design are given in § 3), SPARC falls onto a similar _Q_ curve
in figure 1 to ITER, achieving _Q_ ≈ 10 under nominal physics assumptions (more on this
in § 4), though at roughly 2 % of the volume of ITER. This operating point provides
considerable margin over SPARC’s mission of _Q >_ 2 to account for various uncertainties
such as the scatter in the confinement scaling relationship. The natural progression from
SPARC is then a power plant based on HTS, embodied in the ARC design (Sorbom _et al._
2015) in figure 1. The ARC power plant is considerably smaller (similar in size to JET) and
thus will likely be considerably less expensive (Meade 2002 _a_ ; Sorbom _et al._ 2015; Maingi
_et al._ 2018; National Academies of Sciences, Engineering and Medicine 2019) than larger

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

<!-- PAGE:6 -->

Parameter SPARC C-Mod AUG DIII-D EAST KSTAR Ignitor CIT FIRE BPX ITER

_R_ 0 m 1 _._ 85 0 _._ 67 1 _._ 65 1 _._ 66 1 _._ 70 1 _._ 80 1 _._ 32 2.10 2 _._ 14 2 _._ 59 6 _._ 2
_a_ m 0 _._ 57 0 _._ 21 0 _._ 50 0 _._ 67 0 _._ 40 0 _._ 50 0 _._ 47 0.65 0 _._ 60 0 _._ 80 2 _._ 0
_ϵ_ 0 _._ 31 0 _._ 31 0 _._ 30 0 _._ 40 0 _._ 24 0 _._ 28 0 _._ 36 0.31 0 _._ 28 0 _._ 31 0 _._ 32
_B_ 0 T 12 _._ 2 8 _._ 0 3 _._ 9 2 _._ 2 3 _._ 5 3 _._ 5 13 _._ 0 10.0 10 _._ 0 9 _._ 0 5 _._ 3
_Ip_ MA 8 _._ 7 2 _._ 0 1 _._ 6 2 _._ 0 1 _._ 0 2 _._ 0 11 _._ 0 11.0 7 _._ 7 11 _._ 8 15 _._ 0
_κ_ sep _[a]_ 1 _._ 97 1 _._ 8 1 _._ 6 2 _._ 01 2 _._ 0 2 _._ 0 1 _._ 83 2.0 2 _._ 0 2 _._ 0 1 _._ 85
_δ_ sep _[a]_ 0 _._ 54 0 _._ 40 0 _._ 50 0 _._ 75 0 _._ 60 0 _._ 80 0 _._ 4 0.25 0 _._ 7 0 _._ 45 0 _._ 48
_P_ aux _,_ max MW 25 6 30 27 28 16 24 20 20 20 73
Δ _t_ flattop s 10 1 10 6 1000 20 4 5 20 10 400
_Φ_ tot Wb 42 8 9 12 10 17 33 75 43 77 277
_P_ fus MW 140 96 800 150 100 500
_Q_ 11 9 ∞ 10 5 10

_a_ The elongation and triangularity values for BPX are given for the 95 % flux surface.
TABLE 1. SPARC V2 machine parameters and a comparison to representative design parameters for other tokamaks (Furth 1987; Parker _et al._ 1988;
Hutchinson 1989; Thome _et al._ 1991; Neilson 1992; Coppi _et al._ 1999, 2001; Lee _et al._ 2001; Luxon 2002; Meade 2002 _b_ ; Streibl _et al._ 2003; Luxon
2005; Schultz _et al._ 2005; Shimada _et al._ 2007; Weiyue _et al._ 2006; Song _et al._ 2013). Parameter _B_ 0 is the toroidal magnetic field on axis, _R_ 0 is major
radius, _a_ is minor radius, _ϵ_ is the inverse aspect ratio, _Ip_ is the plasma current, _κ_ sep is the elongation at the plasma separatrix, _δ_ sep is the triangularity
at the plasma separatrix, _P_ aux _,_ max is the maximum coupled auxiliary heating power, Δ _t_ flattop is the plasma current flattop duration, _Φ_ tot is the flux
swing available to drive plasma current, _P_ fusion is projected total fusion power and _Q_ is projected fusion gain. Parameters for other devices are nominal
design parameters and do not reflect the full range of possible operating space. Note that fusion power and gain projections were made with different
methodologies for SPARC, Ignitor, CIT, BPX, FIRE and ITER.

<!-- PAGE:7 -->

designs based on LTS, such as EU-DEMO (Federici _et al._ 2018), though detailed costing
estimates require further engineering design.
SPARC is being designed jointly by Commonwealth Fusion Systems (CFS) and the
Massachusetts Institute of Technology Plasma Science and Fusion Center. The SPARC
project is well underway, and has been divided into two main phases. Phase 1 lasts three
years (2018–2021) and consists of two major milestones: (i) the construction and operation
of an HTS-based toroidal field model coil and (ii) the completion of the SPARC design.
Early Phase 1 work from testing of high-current HTS cables in background magnetic fields
has recently demonstrated excellent performance at SPARC-relevant electromagnetic
loading and thousands of cycles (Hartwig _et al._ 2020). The SPARC device design has
moved through several iterations to reach its current state. The V0 design (Greenwald
_et al._ 2018) stood from 2018 until mid-2019 and was used to assess the overall viability of
the project, including analysis of key subsystems. From mid-2019 through early 2020 there
were five V1 iterations, including the V1C iteration presented at APS DPP 2019 (Brunner
2019; Creely _et al._ 2019; Greenwald _et al._ 2019; Howard _et al._ 2019; Hughes _et al._ 2019;
Kuang _et al._ 2019; Rodriguez-Fernandez _et al._ 2019; Scott _et al._ 2019; Tinguely _et al._
2019; Wright _et al._ 2019). The primary focus of the V1 iterations was to further increase
the self-consistent engineering validity across systems and to increase the conservative
nature of the fusion gain performance. Moving forward, the SPARC Version 2 (V2) design
described in this article stands as the baseline.
Phase 2 is projected to last four years (starting in 2021) and consists of completing
the last stages of the tokamak design as well as construction and commissioning of
the device. This timeline is intentionally aggressive, approximately 7 years from start
of design to start of SPARC operations (3 years for design and R&D and 4 for
construction and commissioning), but has historical precedent in the design, construction
and commissioning of previous (larger) devices such as TFTR (7 years) (French _et al._
1983) and JET (9 years) (Keilhacker _et al._ 2001). Plasma operations in SPARC will begin
with brief campaigns in helium, hydrogen and deuterium in order to build experience with
operations and refine performance projections, among other things. SPARC will then move
as rapidly as possible to deuterium–tritium operation and _Q >_ 2. While the exact duration
of helium, hydrogen and deuterium operation is uncertain, all efforts will be made to
optimize the path to full power D-T operation by utilizing the experience developed though
operation of other tokamaks.
Following the operation of SPARC, CFS plans to complete fusion’s transition from
laboratory to market by moving as rapidly as possible to the construction and operation
of a pilot commercial fusion power plant, likely based on the ARC design (Sorbom _et al._
2015; Kuang _et al._ 2018) and lessons learned on SPARC.

## 3 Machine parameters and cross-section

The SPARC V2 design described in this article is the result of an iterative process
that consisted of analyses of many different aspects of plasma physics and engineering
design. The engineering design of SPARC is not the focus of this article, so only general
descriptions of the various engineering systems are given. The major parameters of the
SPARC tokamak are given in table 1. With a major radius of 1.85 m and an inverse aspect
ratio of 0.31, SPARC is similar in size and aspect ratio to many present-day ‘medium-sized’
tokamaks, such as DIII-D (Luxon 2005), ASDEX Upgrade (Streibl _et al._ 2003), EAST
(Weiyue _et al._ 2006) and KSTAR (Lee _et al._ 2001). A much higher toroidal field
(12.2 T), however, allows for a larger plasma current at the same safety factor and
significantly higher triple product than is possible in present devices.

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

<!-- PAGE:8 -->

FIGURE 2. SPARC V2 poloidal cross-section. The toroidal field coil is light grey. The central
solenoid and poloidal field coils are blue. Error-field correction coils are orange-red. The vacuum
vessel is dark grey. The ICRH antenna is pink. The divertor and first limiting surfaces are black.
Vertical stability plates are green. The plasma separatrix is red.

Figure 2 shows the poloidal cross-section of SPARC V2. The entire SPARC device
is up–down symmetric to the maximum degree possible, enabling tests of symmetric
double-null operation. SPARC’s central solenoid consists of a total of three pairs of HTS
upper and lower coils, labelled CS1, CS2 and CS3. The machine has four upper/lower pairs
of HTS poloidal field coils outside of the toroidal field coils, labelled PF1 to PF4, moving
outward in major radius. In addition, there are two pairs of copper coils that are internal
to the toroidal field coils but external to the vacuum vessel. Since these coils are primarily
used to actuate the divertor magnetic field, they are labelled Div1 and Div2 upper and
lower. There is also a pair of vertical stability coils inside of the vacuum vessel, labelled
VS1 upper and lower. Finally, there are three sets of picture-frame error-field correction
coils, one upper, one lower and one midplane.
The vacuum vessel is double-walled, with space in between the walls for gas heating
and cooling of the vessel. Roughly half of the space between the vacuum vessel walls,
as well as the space between the vacuum vessel and the toroidal field coils, is filled with
neutron shielding material in order to reduce the nuclear heating of the superconducting
magnets. The vacuum vessel has three ports at each toroidal location, one midplane port
and a symmetric pair of off-midplane ports above and below.

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

![](images/tmp7a0ae_mb.pdf-7-3.png)

<!-- PAGE:9 -->

The divertor is toroidally continuous and tightly baffled to contain neutral particles
in the divertor volume. Both carbon and tungsten are currently under consideration
as the material for plasma-facing components. This trade-off is described in detail in
Kuang _et al._ (2020) and to a lesser extent in Sweeney _et al._ (2020), but in short,
carbon plasma-facing components would result in lower core impurity radiation and
more forgiving divertor operation relative to tungsten, but would also result in increased
tritium retention due to higher rates of erosion and co-deposition. While tungsten-based
plasma-facing components are thought to better project to a power plant (Neu _et al._ 2016),
the relatively short integrated plasma time in SPARC means that carbon is an option as a
plasma-facing material and so both materials are being examined. Upper and lower passive
stability plates are located between the vacuum vessel and the plasma to improve vertical
stability and allow operation at high elongation.
SPARC has 18 toroidal field coils in an attempt to balance the competing constraints of
minimizing magnetic field ripple and maximizing vacuum vessel port width. It is being
designed to have up to 25 MW of 120 MHz ion cyclotron resonance heating (ICRH)
coupled into the plasma as the sole source of auxiliary heating.
The central solenoid and poloidal field coil set will be capable of producing 42 Wb
of magnetic flux to initiate and drive the plasma current with a plasma flattop time
of 10 s and all systems are being designed to support full-power operation for a 10 s
flattop, as is described further in § 4. The compact size of SPARC allows it to achieve
a well-equilibrated plasma (in terms of energy confinement and magnetic equilibrium)
in a relatively short discharge ( _<_ 10 s) compared to a larger machine like ITER, easing
the design of many engineering systems. SPARC’s predicted energy confinement time
is _τE_ ≈ 0 _._ 77 s (see § 4 for details of this calculation) such that the flattop encompasses
more than 10 energy confinement times. Figure 3 shows representative plasma current and
safety factor traces as calculated with Tokamak Simulation Code (TSC) (Jardin, Pomphrey
& Delucia 1986) for the full-performance SPARC discharge described in more detail in
§ 4 (which also contains more information about the TSC simulations themselves). As
this figure shows, the current profile is well equilibrated within approximately 5 s of the
beginning of flattop and after this point changes to the _q_ -profile due to sawteeth dominate
any additional relaxation. This result is consistent with more detailed time-dependent
transport simulations described in Rodriguez-Fernandez _et al._ (2020).
The iterations of the SPARC design that led to V2 incorporated a wide variety of
engineering analysis. As the toroidal field coils are perhaps the most novel aspect of the
SPARC design, considerable effort has been dedicated to their structural, thermal and
electromagnetic analysis. Similar efforts have been made for the central solenoid and
poloidal field coils. The vacuum vessel has also been a key focus of the early design work,
as it interfaces with many other systems and must withstand large disruption loading. Since
ICRH is the only external heating source, its design has also progressed considerably in
order to ensure that it will be able to reliably couple the necessary amount of power to the
plasma. In addition, the effects of neutron heating have been modelled for the entire device,
including determining the requirements for cooling of the superconducting magnets during
D-T operation. The high volume-averaged fusion power density and tight radial build
of SPARC mean that volumetric neutron heating of various components is of particular
importance, though as stated above, detailed engineering analysis is beyond the scope of
the work presented here.

## 4 SPARC scenarios and performance projections
To ensure achievement of the SPARC mission of fusion gain _Q >_ 2, several scenarios
are being analysed to demonstrate both the feasibility of the mission and necessary

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

<!-- PAGE:10 -->

|Col1|A. J. Creely and others|Col3|Col4|Col5|
|---|---|---|---|---|
||||||
||||||
||||||

FIGURE 3. Time traces of plasma current and safety factor for the full-performance H-mode
SPARC discharge described in § 4, as calculated using TSC.

steps in the experimental research plan. Specifically, three operational scenarios are
described here: a full-performance (full field, current and shaping) H-mode discharge,
a full-performance L-mode discharge and a reduced field and current H-mode discharge.
The performance for these scenarios is estimated in a manner similar to that used
for the initial design of ITER (ITER Physics Basis Editors _et al._ 1999; Shimada _et al._
2007): zero-dimensional scaling laws (energy confinement, L–H power threshold, density
peaking, etc.) are combined with estimates of plasma profiles and assumptions about other
properties of the core plasma in order to calculate the operational range of a machine with
a given set of input parameters. These calculations were examined with plasma operating
contours (POPCONs) (Houlberg, Attenberger & Hively 1982), an example of which is
shown later in figure 4. In addition to these empirical zero-dimensional projections,
integrated modelling with physics-based models has been performed to predict SPARC
performance, described in another paper in this collection (Rodriguez-Fernandez _et al._
2020), showing remarkable agreement in the predicted machine performance.
The POPCON analysis used to make the initial baseline estimates of SPARC
performance in the scenarios described below is based on the following assumptions. The
ITER _H_ 98 _,y_ 2 energy confinement time scaling relationship (ITER Physics Expert Group on
Confinement and Transport, ITER Physics Expert Group on Confinement Modeling and
Database & ITER Physics Basis Editors 1999) is used, given by

_τE_ = 0 _._ 0562 _H_ 98 _,y_ 2 _Ip_ [0] _[.]_ [93] _Bt_ [0] _[.]_ [15] _n_ [0] _e,_ _[.]_ [41] 19 _[P]_ [−] loss [0] _[.]_ [69] _[R]_ [1] 0 _[.]_ [97] _κa_ [0] _[.]_ [78] _ϵ_ [0] _[.]_ [58] _M_ [0] _[.]_ [19] _,_ (4.1)

where _H_ 98 _,y_ 2 is a multiplicative pre-factor (typically set to 1.0), _Ip_ is the plasma current
in MA, _Bt_ is the toroidal field on axis in T, _ne,_ 19 is the line-averaged electron density in
10 [19] m [−][3], _P_ loss is the power lost through the separatrix via plasma transport in MW (this
term does not include radiated power), _R_ 0 is the plasma major radius in m, _κa_ is the plasma
elongation (defined as the cross-sectional area divided by π _a_ [2] ), _ϵ_ is the inverse aspect ratio
and _M_ is the average ion mass in AMU. While several other scaling relationships have been
derived for the energy confinement time in H-mode (McDonald _et al._ 2007; Verdoolaege
_et al._ 2018, 2020), the _H_ 98 _,y_ 2 scaling is by far the most widely used in scoping analysis
and so is taken as the basis for the analysis performed in this paper (including for the
comparisons made in figure 5).

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

<!-- PAGE:11 -->

FIGURE 4. Plasma operating contour (POPCON) for full-field, full-current H-mode operation
in SPARC. Red contours are _Q_, purple contours are fusion power in MW, the black contour
is the available auxiliary heating power in MW, the blue contour is the L–H threshold power
and the green contour is _nG_ . The yellow shaded region represents the operational space where
SPARC is above the L–H power threshold but below the available auxiliary heating power.
Temperature and density are the volume-averaged values. The red circle is the operating point
for the full-performance H-mode discharge.

Analysis here typically assumes _H_ 98 _,y_ 2 = 1, though sensitivity studies were performed
to assess the impact of lower confinement quality as well as using different scalings for the
energy confinement time in H-mode. Note that the performance estimate for the L-mode
discharge uses the _H_ 89 energy confinement scaling law (Yushmanov _et al._ 1990).
Peaking is assumed in both the temperature and density profiles, quantified as _νx_, where
_νx_ is the central value of quantity _x_ divided by the volume average value. Density peaking
is calculated from the empirical scaling in Angioni _et al._ (2007), Greenwald _et al._ (2007 _a_ ),
Takenaga _et al._ (2008) and Angioni _et al._ (2009) (neglecting the neutral beam source from
the original formula, since SPARC will not have neutral beam injection):

_ν_ ne [Angioni] = 1 _._ 347 − 0 _._ 117 ln _ν_ eff − 4 _._ 03 _β._ (4.2)

In this equation:

_ν_ eff = [0] _[.]_ [1] _[Z]_ [eff][⟨] _[n][e]_ [⟩] _[R]_ [geo] _,_ (4.3)

⟨ _Te_ ⟩ [2]

where ⟨ _ne_ ⟩ is the volume-averaged density (in 10 [19] m [−][3] ), _Z_ eff is the effective charge, _R_ geo
is the geometric plasma radius (in m) and ⟨ _Te_ ⟩ is the volume-averaged plasma temperature
(in keV), and

_β_ = [4] _[.]_ [02][ ×][ 10][−][3][⟨] _[p]_ [⟩] _,_ (4.4)

_B_ [2] _T_

where ⟨ _p_ ⟩ is the volume-averaged plasma pressure (in keV × 10 [19] m [−][3] ) and _BT_ is the
toroidal magnetic field on axis (in T).

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

![](images/tmp7a0ae_mb.pdf-10-4.png)

<!-- PAGE:12 -->

( _a_ ) ( _b_ )

FIGURE 5. SPARC and ITER (Mukhovatov _et al._ 2007; Shimada _et al._ 2007) operating points
plotted against various parameters from the ITER H-mode database DB4v5 (Thomsen and the
H-mode Database Working Group 2002). Database points are filtered to include only standard
aspect ratio tokamaks and to exclude those without necessary data for each plot. Twenty-five
JET discharges from the DB4v5 database that are near non-dimensional matches to the SPARC
operating point are highlighted as green diamonds. Modified from Greenwald _et al._ (2018) for
SPARC V2.

To be conservative, the electron density peaking is taken to be _ν_ ne = _ν_ ne [Angioni]        - 0 _._ 1, to
be more consistent with ICRH-heated, metal-walled tokamaks (Greenwald _et al._ 2007 _a_ ).
The ion density peaking is taken to be _ν_ ni = _ν_ ne [Angioni]       - 0 _._ 2, since the scaling from Angioni
_et al._ (2007) is for the electron density, and some of this may be due to impurity peaking
(Angioni _et al._ 2014). No central fuelling (pellets, beams, etc.) is considered. In the

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

![](images/tmp7a0ae_mb.pdf-11-2.png)

![](images/tmp7a0ae_mb.pdf-11-3.png)

![](images/tmp7a0ae_mb.pdf-11-9.png)

![](images/tmp7a0ae_mb.pdf-11-10.png)

![](images/tmp7a0ae_mb.pdf-11-11.png)

![](images/tmp7a0ae_mb.pdf-11-12.png)

<!-- PAGE:13 -->

Full-field H-mode Full-field L-mode 8 T H-mode

_B_ 0 12 _._ 2 12 _._ 2 8 T
_Ip_ 8 _._ 7 8 _._ 7 5 _._ 7 MA
_q_ [∗] Uckan 3 _._ 05 3 _._ 05 3 _._ 05
_ρ_ [∗] 0 _._ 0027 0 _._ 0031 0 _._ 0036
_ν_ eff 0 _._ 16 0 _._ 04 0 _._ 13
_ν_ [∗] 0 _._ 029 0 _._ 0073 0 _._ 024
_H_ 98 _y,_ 2 or _H_ 89 1 _._ 0 1 _._ 0 1 _._ 0
_τE_ 0 _._ 77 0 _._ 44 0 _._ 65 s
_P_ RF 11 _._ 1 24 _._ 1 9 _._ 9 MW
_P_ ohmic 1 _._ 7 1 _._ 1 1 _._ 1 MW
_Z_ eff 1 _._ 5 1 _._ 5 1 _._ 5
Main ion dilution 0 _._ 85 0 _._ 85 0 _._ 85
⟨ _Te_ ⟩ 7 _._ 3 9 _._ 7 5 _._ 6 keV
⟨ _Ti_ ⟩ 7 _._ 3 9 _._ 7 5 _._ 6 keV
⟨ _ne_ ⟩ 3 _._ 1 1 _._ 4 1 _._ 5 10 [20] m [−][3]

⟨ _ni_ ⟩ 2 _._ 7 1 _._ 2 1 _._ 3 10 [20] m [−][3]

_νTe_ 2 _._ 5 2 _._ 5 2 _._ 5
_ν_ ni 1 _._ 33 1 _._ 51 1 _._ 36
_fG_ 0 _._ 37 0 _._ 16 0 _._ 26
_β_ 0 _._ 012 0 _._ 007 0 _._ 010
_βN_ 1 _._ 0 0 _._ 6 0 _._ 8 m T MA [−][1]

_P_ sep _B_ 0 _/R_ 0 191 199 53 MW T m [−][1]

_P_ fusion 140 55 17 MW
_Q_ 11 _._ 0 2 _._ 2 1 _._ 6

TABLE 2. Performance projections for D-T plasmas in the SPARC tokamak based on the
empirical scaling analysis described in this work.

POPCON analysis, the electron and ion temperatures are assumed to be the same, with a
peaking factor of _νT_ = 2 _._ 5, which is consistent with high-performance discharges on JET
and ASDEX Upgrade (Angioni _et al._ 2007). Note that the temperature and density peaking
factors predicted empirically for the SPARC V2 full-performance H-mode discharge in
table 2 agree quite well with integrated modelling results based on physics-based models
for transport and heating (Rodriguez-Fernandez _et al._ 2020).
The plasma _Z_ eff is assumed to be 1.5 and the main ion (D-T) fraction is assumed
to be 0.85 (the main ion density is 85 % of the electron density), which is consistent
with relatively pure plasmas on present metal-walled machines (Romanelli & JET EFDA
Contributors 2013). All analysis performed here assumes a 50–50 deuterium–tritium mix
for the main ions. Radiated power is taken to be the sum of bremsstrahlung and impurity
radiation calculated with the average ion model (Jensen _et al._ 1977), assuming a 6 %
helium concentration, a tungsten concentration of approximately 1 _._ 5 × 10 [−][5] (consistent
with results from ASDEX Upgrade (Neu _et al._ 2005) and JET ILW (Neu _et al._ 2014))
and a lumped _Z_ = 8 impurity to satisfy quasi-neutrality. In the parameter space relevant
to high-performance SPARC operation, this calculation was also found to be roughly
equivalent to simply multiplying the calculated bremsstrahlung power by 2.25. Impurity
concentrations vary significantly on existing machines, and so introduce considerable
uncertainty when projecting to a new device. Boronization is planned as a possible
technique to mitigate high impurity levels in SPARC.

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

<!-- PAGE:14 -->

Heating power is a combination of ohmic power, ICRH and fusion alphas. Ohmic power
is calculated based on neoclassical resistivity, and the ICRH power coupled to the core
plasma required to attain a given temperature and density is an output of the calculation,
limited by the total available radio-frequency power. Ohmic power, though small
(∼1 MW), is also included as heating power in the fusion gain calculation.
Access to and maintenance of H-mode are evaluated based on the Martin scaling
(Martin & Takizuka 2008), corrected for the plasma isotope (Behn _et al._ 2014) and with
estimated core radiated power subtracted from the input power used to evaluate against
the threshold. The power used in this scaling is thus the sum of ohmic power, auxiliary
heating power and alpha power minus the radiated power. While the original scaling
was derived without subtracting radiated power, recent work suggests that maintaining
good H-mode confinement requires inclusion of this additional term (Hughes _et al._ 2011).
As such, this work is conservative compared to the original scaling. This analysis also
makes the conservative assumption that operation in H-mode can only be sustained above
this power threshold, despite a well-documented hysteresis in access power (Martin &
Takizuka 2008).
Using approximate kinetic profiles, the separatrix shaping parameters from table 1
translate to roughly _κ_ 95 ≈ _κa_ = 1 _._ 75 and _δ_ 95 ≈ 0 _._ 45 (these are the 95 % flux surface values,
as opposed to the separatrix shaping parameters given in table 1). Note that _δ_ 95 in particular
will vary considerably depending on the assumed or calculated kinetic profiles, and so
calculations based on this parameter are by nature approximate. These values are used to
calculate the achievable plasma current and the energy confinement time (since the _H_ 98 _,y_ 2
scaling uses the areal elongation _κa_ = _S/_ π _a_ [2], where _S_ is the plasma cross-sectional area
and _a_ is the plasma minor radius). The achievable elongation for SPARC was estimated
based on the performance of existing devices of similar aspect ratio, which is described
further in Sweeney _et al._ (2020). The vertical stability of this plasma was subsequently
confirmed based on time-dependent TSC runs (Jardin _et al._ 1986), which model realistic
vertical stability coils and passive conductors.
The achievable plasma current for a given set of machine parameters is calculated by
assuming _q_ [∗] = 3 _._ 05, where _q_ [∗] is calculated from Uckan & the ITER Physics Group (1990)
as

   5 _a_ 2 _B_ 0
_q_ [∗] Uckan [=]

- 1 + _κ_ 952 �1 + 2 _δ_ 95 [2] [−] [1] _[.]_ [2] _[δ]_ 95 [3] 

_._ (4.5)
2

_R_ 0 _Ip_

Note that this formula for _q_ [∗], which corresponds to _q_ 95 ≈ 3 _._ 4 on SPARC (where _q_ 95 is
the safety factor at the 95 % flux surface) (Rodriguez-Fernandez _et al._ 2020), is more
conservative than the definition of _q_ [∗] used in the ITER Physics Basis (ITER Physics Basis
Editors _et al._ 1999), which includes an additional correction factor for the machine aspect
ratio. Using the formula from the ITER Physics Basis gives _q_ [∗] ≈ 3 _._ 6 for SPARC.
The operating point is also constrained by the Greenwald density (Greenwald _et al._
1988) and by _β_ limits, though due to the large toroidal field in SPARC, neither of these two
constraints limit any of the scenarios shown in table 2. The large margin against densityand pressure-driven instabilities is one of the advantages of high magnetic field (Whyte
_et al._ 2016).
All three operating scenarios described here (H-mode, L-mode, reduced-field H-mode)
have the magnetic equilibrium shown in figure 2 (with small internal differences due to
differences in _β_, etc.), as calculated with the FreeGS Grad-Shafranov solver. [2]

[2See https://github.com/bendudson/freegs for information about the FreeGS code.](https://github.com/bendudson/freegs)

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

<!-- PAGE:15 -->

Using the methodology outlined here, the performance projections for the three
scenarios are as follows.

### 4.1 Full-performance H-mode discharge

Since the full-performance H-mode scenario is the most demanding on many of the
SPARC engineering systems, it has been the focus of the majority of the analysis to
date. With a plasma current of 8.7 MA and with _H_ 98 _,y_ 2 = 1, SPARC achieves _Q_ ≈ 11
and produces roughly 140 MW of fusion power. The operating space is represented in
a POPCON in figure 4 and further details of this operating point are given in table 2.
This scenario ends up operating right at the L–H threshold in order to optimize the fusion
gain (see above for how the threshold is calculated), though moving to higher density and
heating power would enable higher fusion power (fusion powers in excess of 250 MW
are achievable while maintaining _Q_ ≈ 10). Such operation would, however, likely exceed
allowable neutron heating of the toroidal field magnets. At full field, the ICRH power is
primarily absorbed in a helium-3 minority, with some additional absorption at the second
harmonic of tritium (Lin _et al._ 2020).
Even with significantly degraded confinement at _H_ 98 _,y_ 2 = 0 _._ 7 (two standard deviations
below the mean of the database), a full-field discharge is projected to achieve the primary
SPARC mission of _Q >_ 2. This margin allows one to, for example, run scenarios with
highly dissipative divertor solutions even if they lead to degradation of core confinement,
and still achieve the mission of _Q >_ 2. In addition, SPARC is projected to meet its _Q >_ 2
mission when performance is calculated using the other _H_ 98 _,y_ scalings in ITER Physics
Expert Group on Confinement and Transport _et al._ (1999), the various energy confinement
time scalings proposed in Verdoolaege _et al._ (2018) and the proposed _H_ 20 scaling in
Verdoolaege _et al._ (2020).
Note that the dependency of _Q_ on the volume-averaged density is sensitive to several
details of the POPCON modelling, in particular on the density peaking. If one assumes
constant density peaking (i.e. peaking that is independent of other parameters), then
moving to higher density generally improves the fusion gain. When one self-consistently
calculates the peaking (as is done in this paper), however, then moving to higher
volume-averaged density tends to increase total power, but decreases gain. Calculation
of the density peaking is one of the reasons (in addition to treatment of impurity radiation)
for small differences between the analysis shown in this paper and independent POPCON
analysis of SPARC in Rodriguez-Fernandez _et al._ (2020). The good agreement between
the independent analyses (both give _Q_ ≈ 11) indicates that the design point is robust to
these assumptions. Even with no density peaking (a completely flat density profile, which
is unrealistic), POPCON analysis indicates that SPARC should achieve _Q_ ≈ 4.
This discharge runs near the achievable elongation and just above _q_ [∗] = 3 (using the
conservative (Uckan & the ITER Physics Group 1990) definition), which is often seen as a
reasonable limit for the safety factor (Sweeney _et al._ 2020). Even in this regime, however,
SPARC runs well below known _β_ and density limits. The density, chosen to optimize gain
while remaining within the allowable total fusion power, sits at a Greenwald fraction of
only 0.37. The normalized _βN_ in this regime is roughly 1.0.
SPARC is being designed to withstand the divertor heat flux in this full-power discharge
for the full 10 s flattop with an attached, single-null plasma (even though double-null
operation is also planned) via strike point sweeping. Details of the divertor physics are
described in another paper in this series (Kuang _et al._ 2020). Empirical scalings for the
heat flux width are used to determine the divertor heat loads (Eich _et al._ 2013; Brunner
_et al._ 2018). SPARC may be able to attain higher powers for shorter time periods, though
the gain will likely be lower in these scenarios (partially due to decreased density peaking

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

<!-- PAGE:16 -->

at higher collisionalities). This scenario is limited from reaching higher gain due to the
L–H threshold power (as is seen in figure 4), though it may be possible to run at lower
input power and achieve higher gain due to the hysteresis observed between entering and
exiting H-mode (Martin & Takizuka 2008).
In addition to the time-independent equilibrium shown in figure 2, time-dependent
scenarios have been developed using TSC (Jardin _et al._ 1986). Plasma current and safety
factor time traces generated with TSC for the full-performance H-mode discharge are
shown in figure 3. These simulations ensure that the desired flattop plasma can be
achieved, starting from plasma initiation and progressing to the end of the discharge,
given the SPARC V2 central solenoid and poloidal field coil set. TSC simulates all of
the central solenoid modules and poloidal field coils, including the vertical stability coils.
It also includes passively conducting structures, such as the vacuum vessel and the vertical
stability plates. Lower current discharges are considerably less demanding on the central
solenoid and poloidal field coil set, since the majority of the central solenoid flux is
required to ramp the plasma to full current, and so this first scenario likely sets most of the
coil requirements for normal operation. Time-dependent transport simulations including
sawteeth and kinetic profile evolution are described in Rodriguez-Fernandez _et al._ (2020),
confirming that the plasma is well equilibrated a few seconds into the current flattop.
To put this discharge in context, compare its operational parameters to those from
discharges in the ITER confinement database DB4v5 (Thomsen and the H-mode Database
Working Group 2002). Figure 5 shows how this SPARC discharge (as well as the inductive
ITER reference discharge (Mukhovatov _et al._ 2007; Shimada _et al._ 2007)) compares
to other discharges in the database in terms of _H_ 98 _,y_ 2, _q_ 95, _βN_, _n/nG_, _ν_ [∗] (where _ν_ [∗] =
0 _._ 01⟨ _ne,_ 20⟩ _q_ 95 _RZ_ eff _(R/a)_ [3] _[/]_ [2] _/_ ⟨ _Ti,_ keV⟩ [2] ), _ρ_ [∗] (where _ρ_ [∗] = 4 _._ 57 × 10 [−][3] ⟨ _Ti,_ keV _M_ ⟩ [0] _[.]_ [5] _/(aBt)_ ) and
_τE_ . These database points were filtered to include only standard aspect ratio tokamaks and
to exclude those without necessary data for each plot. SPARC sits further from stability
limits than ITER in _q_ 95, _βN_ and _n/nG_ . It has very similar _ν_ [∗], and requires no extrapolation
in either _ρ_ [∗] or _τE_, unlike ITER.

Figure 5 highlights data from 25 JET discharges in the DB4v5 database that are near
non-dimensional matches to the SPARC operating point. Here _H_ 98 _,y_ 2, _q_ 95, _βN_, _n/nG_, _ν_ [∗] and
_τE_ are all very close matches, though SPARC has a somewhat smaller _ρ_ [∗] . In other words,
no new plasma physics is needed for this SPARC discharge (except for alpha physics),
as non-dimensionally near-identical discharges have already been run on JET. While the
plasma physics is largely governed by these non-dimensional parameters, however, fusion
power depends on absolute density and temperature, so SPARC’s fusion power and gain
will be considerably larger than those of the devices included in this database, including
JET.

### 4.2 Full-performance L-mode discharge

In addition to the full-field H-mode discharge, the performance of SPARC in L-mode
at full machine parameters has also been considered. Operation in L-mode avoids some
of the challenges associated with H-mode, such as edge localized modes and impurity
accumulation. It also presents the possibility of reducing the divertor heat flux challenge
by allowing for operation with a large fraction of the power radiated from the core
plasma while maintaining _H_ 89 ≈ 1 (Greenwald _et al._ 1997). Table 2 shows the projected
performance of a full-field and full-current L-mode discharge in SPARC. The fusion gain
in this scenario is projected to be _Q_ ≈ 2 _._ 2 with a fusion power of 55 MW, thus satisfying
the primary SPARC mission. This scenario is primarily limited in performance by the
available radio-frequency power and by the ability of the divertor to handle the heat
exhaust.

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

<!-- PAGE:17 -->

### 4.3 Reduced field and current H-mode discharge

In addition to full-field and full-current scenarios, performance at reduced field and current
has also been considered. Of particular interest has been performance at 2/3 of the toroidal
field (8 T), since the same ICRH frequency (120 MHz) that is resonant in the 12.2 T
discharge is resonant with a hydrogen minority at this reduced field. At 8 T, the majority
of the ICRH power is absorbed in the hydrogen minority, with some additional power
absorbed at the second harmonic of deuterium. Scenarios with fields on axis within 1 T or
so of either 8 or 12 T are of primary interest to SPARC as ICRH absorption will be best in
this range. See Lin _et al._ (2020) for more information about ICRH physics in SPARC.
This lower-field, lower-current scenario is likely to be an intermediate step on the way to
full-field operation, as it will demonstrate considerable fusion power while remaining far
away from nearly all machine limits. As shown in table 2, operation at _B_ 0 = 8 T and _q_ [∗] =
3 _._ 05 corresponds to a 5.7 MA plasma, and achieves _Q_ ≈ 1 _._ 6 with 17 MW of fusion power.
While this does not achieve the SPARC mission of _Q >_ 2, increasing the field to 8.6 T and
the current to 6.2 MA does achieve _Q_ = 2. At 8.6 T, the ICRH will heat slightly off-axis
(on the low-field side). The lower volume-averaged temperature of this discharge also
provides another data point in the study of alpha physics and the interaction of alphas with
MHD modes (Tolman _et al._ 2019). Finally, operation at this field provides valuable data on
the dependence of confinement on toroidal field, looking towards developing appropriate
projections to ARC.

## 5 Investigation of SPARC physics

In addition to the work described in § 4, a number of other aspects of the physics of
SPARC plasmas have been investigated in some detail. Each of these topics is detailed in
another article in this series, but a brief description is given here.
Since the design of ITER and the writing of the ITER Physics Basis (ITER Physics
Basis Editors _et al._ 1999) and the Progress in the ITER Physics Basis (Shimada _et al._
2007), considerable advancements have been made in physics-based modelling of tokamak
plasmas. High-fidelity models now exist for core turbulent transport, H-mode pedestals,
energetic particle heating as well as many other aspects of tokamak plasmas. These
advancements mean that one can now perform integrated modelling of many parts of
the plasma in order to project the performance of a machine that has not yet been built.
While SPARC parameters were initially chosen based on the empirical scalings used in
the ITER design, integrated modelling has been performed as part of the SPARC design
process and is described in Rodriguez-Fernandez _et al._ (2020). This modelling predicts a
peak performance of _Q_ ≈ 9 for the full-current, full-field H-mode in SPARC, which, given
the considerable uncertainties in both the empirical scalings and models used here, is in
remarkable agreement with the empirical prediction of _Q_ ≈ 11. Such agreement reduces
the risk that the SPARC operating regime is somehow qualitatively different from those
used to generate the empirical scaling laws and thus increases confidence in SPARC’s
performance projections.
Peak performance in SPARC will likely require operating in H-mode, so special
attention has been paid to H-mode accessibility and to the challenges that come with
H-mode operation, such as edge localized modes (Hughes _et al._ 2020). While H-mode
has been accessed in nearly all modern diverted tokamaks, the physics of the L–H
transition is still an area of active research and predictions of the power required to
transition have considerable uncertainty (Martin & Takizuka 2008; Behn _et al._ 2014;
Schmidtmayr _et al._ 2018). In addition, edge localized modes present a major challenge
in any high-power-density device, as they lead to considerable transient loading to the

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

<!-- PAGE:18 -->

divertor and other surfaces. Both of these phenomena, as well as others, including the
ability to maintain high-quality H-mode confinement and the implications of reduced
pedestal quality, are considered in greater detail in Hughes _et al._ (2020). It is shown in
Hughes _et al._ (2020) and Rodriguez-Fernandez _et al._ (2020) that SPARC is able to achieve
its mission of _Q >_ 2 even with a 50 % degradation in pedestal pressure compared to the
nominal prediction.
The high power density in SPARC V2 and other burning plasma devices means that
one of the most difficult challenges in the device is heat exhaust. As such, considerable
work has focused on the performance of the divertor and its ability to operate successfully
in a full-power D-T discharge (Kuang _et al._ 2020). The baseline design scenario for
SPARC V2 is to sweep attached divertor strike points (both inner and outer) in order
to spread the exhaust heat across the divertor target. Since strike point sweeping places
strict requirements on power supplies and other systems, it is important to consider this
operational scenario early in the machine design. Since the ability to balance a perfect
double-null is uncertain, the SPARC divertors are being conservatively designed to operate
in single-null. SPARC operation will represent an extrapolation in the empirical parallel
heat flux width scaling (λ _q_ ≈ 0 _._ 2 mm, with peak unmitigated parallel heat fluxes estimated
to be of the order of 10 GW m [−][2] ) (Eich _et al._ 2013; Brunner _et al._ 2018) and some recent
modelling (Chang _et al._ 2017; Xu _et al._ 2019) predicts considerably wider heat flux widths
in low- _ρ_ [∗] plasmas. For this reason, data from SPARC on the divertor heat flux width
scaling will be an important physics result and may help resolve the differences between
empirical scaling and modelling predictions. This conservative approach to design does
not preclude the exploration of detached divertor regimes, and SPARC will be able to test
predictions for the impurity fractions required to induce detachment (Goldston, Reinke
& Schwartz 2017; Reinke 2017). Two-dimensional fluid modelling work has also been
performed for SPARC to gauge the possibility of detachment. Divertor physics studies on
SPARC will inform the design and operation of ARC’s divertor, including the possibility
of testing an ‘advanced’ X-point target divertor configuration.
SPARC’s high field and current density place it in a somewhat unique operating space
compared to other high-performance tokamak regimes with regards to MHD (Sweeney
_et al._ 2020). While _β_ -driven instabilities are expected to play a significantly smaller
role than in many current devices, the very large plasma current density leads to special
concern around disruptions and the thermal and mechanical loads that these will place
on the device. Electromagnetic disruption loads have been calculated based on empirical
scalings and SPARC’s mechanical structures are being designed to withstand these loads.
Main chamber plasma-facing components are being designed to withstand anticipated
radiative heating during disruptions, including appropriate peaking factors. The effects
of disruptions specifically on the divertor are considered further in Kuang _et al._ (2020).
In addition, the generation and mitigation of runaway electrons in SPARC have been
considered, building on earlier work that analysed SPARC V0 (Fülöp _et al._ 2020).
The possibility of incorporating a passive non-axisymmetric coil in order to reduce the
likelihood of damage from a runaway electron beam is also under consideration (Boozer
2011).
The high field and high density in SPARC make ICRH the preferred source of auxiliary
heating. Since SPARC will rely exclusively on ICRH, considerable work has been put into
determining the efficacy of various ICRH operating scenarios and systems (Lin _et al._
2020). Depending on the operating field, either a hydrogen or helium-3 minority will
be the primary species into which power is deposited. Heating of fast alpha particles is
predicted to be small, and minority tail energies should not be problematic. The ICRH

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

<!-- PAGE:19 -->

power source, transmission and antenna systems have also been scoped out based on
existing equipment, such as that from Alcator C-Mod.
Finally, one of the most novel areas of SPARC physics will be the presence of large
populations of alpha particles (Scott _et al._ 2020). Care must be taken to ensure that
alphas will not damage the device, and detailed neoclassical and ripple loss simulations
have shown that first-wall heating from alpha losses from these mechanisms should be
modest. With the 0.3 % toroidal field ripple in SPARC V2, ripple-induced alpha losses
are projected to be less than 1 %. The possibility of interactions between alpha particles
and high-frequency MHD modes is an area of interest and initial examination of the
effect of high-field operation in general on Alfvén eigenmode linear stability has been
carried out (Tolman _et al._ 2019). This work suggests that the SPARC regime of alpha
physics is close to what has been predicted for ITER, since the ion temperatures are
similar. In addition to MHD interactions, SPARC should also be able to explore various
other aspects of alpha and burning plasma physics (especially if, as expected, regimes
with _Q_ ≈ 11 are accessible), including alpha stabilization of turbulence, the interaction
of alpha populations with sawteeth and the self-consistent plasma profiles that result
from dominant alpha heating. The self-consistent distribution of alphas in space and
energy in high-gain plasmas is a frontier research topic (National Academies of Sciences,
Engineering and Medicine 2019; American Physical Society Division of Plasma Physics
Community Planning Process 2020) and SPARC will expand upon earlier work from
TFTR (Strachan _et al._ 1997; Zweben _et al._ 1997; Hawryluk 1998) and JET (Keilhacker
1999).

## 6 Conclusions
SPARC is a compact, _Q >_ 2 tokamak and is the next step on the path to timely and
economical fusion energy. It is well into the conceptual design phase and is on track
to begin construction in 2021. As shown using the conservative physics methodology
outlined in this paper, SPARC has considerable margin to achieve its goal of _Q >_ 2,
and should be able to achieve a fusion gain of _Q_ ≈ 11 with nominal assumptions. The
nominal _Q_ ≈ 11 discharge is well within the burning plasma regime and likely provides an
opportunity to study various aspects of burning plasma physics. This high performance is
possible in a compact device due to the high magnetic fields enabled by HTS magnets. The
high field of SPARC allows for high current and high density, placing SPARC in a unique
operating regime where typical density and _β_ limits do not constrain high-performance
operation. The papers in this collection highlight analysis that has been done as part of
the design of SPARC and foreshadow some of the experimental results that SPARC will
produce.
Based on what is learned from the design and operation of SPARC, CFS plans to move
as rapidly as possible to the construction of a commercial power plant based on the ARC
concept. The design of ARC will combine the plasma physics knowledge gained from the
study of burning plasmas on SPARC, the engineering experience of building high-field
superconducting magnets and a spectrum of other research and development work in
other areas of fusion technology such as blankets and materials. The worldwide fusion
community has made significant progress towards a new clean energy source, but must
accelerate towards the final goal in order to successfully combat climate change.

Acknowledgements

This work was funded by Commonwealth Fusion Systems. Parts of this work were also
funded by CFS under MIT PSFC RPP005; under INFUSE grant 2702 awarded to CFS
(INFUSE is a DOE SC FES private–public partnership programme); by CFS through

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

<!-- PAGE:20 -->

ORNL Strategic Partnership Project no. NFE-19-07728; by the SPARC Fellowship Fund;
by the S. W. Ing (1953) Memorial Fund, a gift of Mimi and Frank Slaughter; by the
National Science Foundation Graduate Research Fellowship under grant no. 1122374; and
by the US Department of Energy, Office of Science, Office of Fusion Energy Sciences,
under Award Numbers DE-SC0014264, DE-SC0018287 and DE-AC02-09CH11466.

_Editor William Dorland thanks the referees for their advice in evaluating this article_ .

Declaration of interests

The authors report no conflict of interest.

## References

AMERICAN PHYSICAL SOCIETY DIVISION OF PLASMA PHYSICS COMMUNITY PLANNING PROCESS
2020 A community plan for fusion energy and discovery plasma sciences. _Tech. Rep._ American
Physical Society.
ANGIONI, C., FABLE, E., GREENWALD, M., MASLOV, M., PEETERS, A. G., TAKENAGA, H. &
WEISEN, H. 2009 Particle transport in tokamak plasmas, theory and experiment. _Plasma Phys._
_Control. Fusion_ 51 (12), 124017.
ANGIONI, C., MANTICA, P., PÜTTERICH, T., VALISA, M., BARUZZO, M., BELLI, E. A., BELO, P.,
CASSON, F. J., CHALLIS, C., DREWELOW, P., _et al._ 2014 Tungsten transport in JET H-mode
plasmas in hybrid scenario, experimental observations and modelling. _Nucl. Fusion_ 54 (8), 083028.
ANGIONI, C., WEISEN, H., KARDAUN, O. J. W. F., MASLOV, M., ZABOLOTSKY, A., FUCHS, C.,
GARZOTTI, L., GIROUD, C., KURZAN, B., MANTICA, P., _et al._ 2007 Scaling of density peaking
in H-mode plasmas based on a combined database of AUG and JET observations. _Nucl. Fusion_ 47
(9), 1326–1335.
BANGERTER, R., NAVRATIL, G. & SAUTHOFF, N. 2003 2002 fusion summer study report. _Tech. Rep._
Snowmass, CO.
BEHN, R., LABIT, B., DUVAL, B. P., KARPUSHOV, A., MARTIN, Y. & PORTE, L. 2014 Threshold power
for the transition into H-mode for H, D, and He plasmas in TCV. _Plasma Phys. Control. Fusion_ 57
(2), 025007.
BOOZER, A. H. 2011 Two beneficial non-axisymmetric perturbations to tokamaks. _Plasma Phys. Control._
_Fusion_ 53 (8), 084002.
BRUNNER, D. 2019 Overview of SPARC on the high-field path to fusion energy. In _61st Annual Meeting_
_of the APS Division of Plasma Physics_ .
BRUNNER, D., LABOMBARD, B., KUANG, A. Q. & TERRY, J. L. 2018 High-resolution heat flux width
measurements at reactor-level magnetic fields and observation of a unified width scaling across
confinement regimes in the Alcator C-Mod tokamak. _Nucl. Fusion_ 58 (9), 094002.
CHANG, C. S., KU, S., LOARTE, A., PARAIL, V., KÖCHL, F., ROMANELLI, M., MAINGI, R.,
AHN, J.-W., GRAY, T., HUGHES, J., _et al._ 2017 Gyrokinetic projection of the divertor heat-flux
width from present tokamaks to ITER. _Nucl. Fusion_ 57 (11), 116023.
COPPI, B., AIROLDI, A., BOMBARDA, F., CENACCHI, G., DETRAGIACHE, P., FERRO, C.,
MAGGIORA, R., SUGIYAMA, L. E. & VECCHI, G. 1999 Critical physics issues for ignition
experiments: ignitor. MIT RLE Report PTP 99/06.
COPPI, B., AIROLDI, A., BOMBARDA, F., CENACCHI, G., DETRAGIACHE, P. & SUGIYAMA, L. E. 2001
Optimal regimes for ignition and the Ignitor experiment. _Nucl. Fusion_ 41 (9), 1253–1257.
COSTLEY, A. E. 2016 On the fusion triple product and fusion power gain of tokamak pilot plants and
reactors. _Nucl. Fusion_ 56 (6), 066003.
CREELY, A. J., BRUNNER, D., GRANETZ, R., GREENWALD, M., HOWARD, N., HUTCHINSON, I.,
KESSEL, C., MUMGAARD, R., RODRIGUEZ-FERNANDEZ, P. & SORBOM, B. 2019 Scenario
development for SPARC. In _61st Annual Meeting of the APS Division of Plasma Physics_ .
EICH, T., LEONARD, A. W., PITTS, R. A., FUNDAMENSKI, W., GOLDSTON, R. J., GRAY, T. K.,
HERRMANN, A., KIRK, A., KALLENBACH, A., KARDAUN, O., _et al._ 2013 Scaling of the tokamak

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

<!-- PAGE:21 -->

near the scrape-off layer H-mode power width and implications for ITER. _Nucl. Fusion_ 53 (9),
093031.
FEDERICI, G., BACHMANN, C., BARUCCA, L., BIEL, W., BOCCACCINI, L., BROWN, R., BUSTREO, C.,
CIATTAGLIA, S., CISMONDI, F., COLEMAN, M., _et al._ 2018 DEMO design activity in Europe:
progress and updates. _Fusion Engng Des_ . 136, 729–741. Special Issue: Proceedings of the 13th
International Symposium on Fusion Nuclear Technology (ISFNT-13).
FERESIN, E. 2010 Fusion reactor aims to rival ITER. _Nature_ .
FRENCH, J. W., FEDOR, B. J., SHAW, L. E. & SABADO, M. M. 1983 Construction of the tokamak fusion
test reactor. _Nucl. Technol. Fusion_ 4 (2P2), 326–335.
FÜLÖP, T., HELANDER, P., VALLHAGEN, O., EMBREUS, O., HESSLOW, L., SVENSSON, P.,
CREELY, A. J., HOWARD, N. T. & RODRIGUEZ-FERNANDEZ, P. 2020 Effect of plasma elongation
on current dynamics during tokamak disruptions. _J. Plasma Phys_ . 86 (1), 474860101.
FURTH, H. P. & THE CIT PROJECT GROUP, 1987 Role of CIT in the US fusion program. _Tech. Rep._
PPPL–2480, DE88 003454. Princeton Plasma Physics Laboratory.
GOLDSTON, R. J. 1992 I. _Burning plasma experiment physics design description. Fusion Technology_ 21
(3P1), 1050–1055.
GOLDSTON, R. J., REINKE, M. L. & SCHWARTZ, J. A. 2017 A new scaling for divertor detachment.
_Plasma Phys. Control. Fusion_ 59 (5), 055015.
GREENWALD, M., ANGIONI, C., HUGHES, J. W., TERRY, J. & WEISEN, H. 2007 _a_ Density profile
peaking in low collisionality H-modes: comparison of Alcator C-Mod data to ASDEX upgrade/JET
scalings. _Nucl. Fusion_ 47 (9), L26–L29.
GREENWALD, M., BOIVIN, R. L., BOMBARDA, F., BONOLI, P. T., FIORE, C. L., GARNIER, D.,
GOETZ, J. A., GOLOVATO, S. N., GRAF, M. A., GRANETZ, R. S., _et al._ 1997 H-mode
confinement in Alcator C-Mod. _Nucl. Fusion_ 37 (6), 793–807.
GREENWALD, M., BRUNNER, D., CREELY, A. J., HOWARD, N. T., HUGHES, J. W., KUANG, A. Q.,
LIN, Y., RODRIGUEZ-FERNANDEZ, P., SCOTT, S. & WUKITCH, S. 2019 Parameter sensitivities
and physics optimization for SPARC. In _61st Annual Meeting of the APS Division of Plasma Physics_ .
GREENWALD, M., CALLIS, R., GATES, D., DORLAND, B., HARRIS, J., LINFORD, R., MAUEL, M.,
MCCARTHY, K., MEADE, D., NAJMABADI, F., _et al._ 2007 _b_ Priorities, gaps and opportunities:
towards a long-range strategic plan for magnetic fusion energy. _Tech. Rep._ Fusion Energy Sciences
Advisory Committee.
GREENWALD, M., TERRY, J. L., WOLFE, S. M., EJIMA, S., BELL, M. G., KAYE, S. M. &
NEILSON, G. H. 1988 A new look at density limits in tokamaks. _Nucl. Fusion_ 28 (12),
2199–2207.
GREENWALD, M., WHYTE, D., BONOLI, P., HARTWIG, Z., IRBY, J., LABOMBARD, B., MARMAR, E.,
MINERVINI, J., TAKAYASU, M., TERRY, J., _et al._ 2018 The high-field path to practical fusion
energy. PSFC Report RR-18-2.
HARTWIG, Z., VIEIRA, R., SORBOM, B., BADCOCK, R., BAJKO, M., BECK, W., CASTALDO, B.,
CRAIGHILL, C., DAVIES, M., ESTRADA, J., _et al._ 2020 VIPER: an industrially mature high-current
high temperature superconductor cable. _Supercond. Sci. Technol_ . (submitted).
HAWRYLUK, R. J. 1998 Results from deuterium-tritium tokamak confinement experiments. _Rev. Mod._
_Phys_ . 70, 537–587.
HAZELTINE, R., HILL, D., NEILSON, H., GREENFIELD, C., HUBBARD, A., MAINGI, R., MEIER, W.,
RAFFRAY, R., SARFF, J., ULRICKSON, M., _et al._ 2009 ReNeW report: research needs for
magnetic fusion energy sciences. _Tech. Rep._ US Department of Energy, Office of Fusion Energy
Sciences.
HOULBERG, W. A., ATTENBERGER, S. E. & HIVELY, L. M. 1982 Contour analysis of fusion reactor
plasma performance. _Nucl. Fusion_ 22 (7), 935–945.
HOWARD, N. T., RODRIGUEZ-FERNANDEZ, P., HOLLAND, C., GREENWALD, M., HUGHES, J. W.,
CREELY, A. J., WRIGHT, J. C. & WUKITCH, S. 2019 Investigation of core physics in the SPARC
tokamak. In _61st Annual Meeting of the APS Division of Plasma Physics_ .
HUGHES, J. W., HOWARD, N. T., GREENWALD, M. J., HUBBARD, A. E., MATHEWS, A.,
KUANG, A. Q., RODRIGUEZ-FERNANDEZ, P., WILKS, T. M., MORDIJCK, S., REKSOATMODJO,
R., _et al._ 2019 The edge pedestal on the SPARC tokamak. In _61st Annual Meeting of the APS Division_
_of Plasma Physics_ .

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

<!-- PAGE:22 -->

HUGHES, J. W., HOWARD, N. T., RODRIGUEZ-FERNANDEZ, P., KUANG, A. Q., TOLMAN, E. A.,
CREELY, A. J. & SNYDER, P. B. 2020 High confinement access and edge pedestal structure in
the SPARC tokamak. _J. Plasma Phys_ . (under review).
HUGHES, J. W., LOARTE, A., REINKE, M. L., TERRY, J. L., BRUNNER, D., GREENWALD, M.,
HUBBARD, A. E., LABOMBARD, B., LIPSCHULTZ, B., MA, Y., _et al._ 2011 Power requirements
for superior H-mode confinement on Alcator C-mod: experiments in support of ITER. _Nucl. Fusion_
51 (8), 083007.
HUGUET, M. 1993 The ITER magnet system – present status of design and R&D programme. In _15th_
_IEEE/NPSS Symposium. Fusion Engineering_, vol. 1, pp. 1–6.
HUTCHINSON, I. H. 1989 C-Mod: the next Alcator. In _IEEE Thirteenth Symposium on Fusion Engineering_,
vol. 1, pp. 13–18.
ITER PHYSICS BASIS EDITORS, ITER PHYSICS EXPERT GROUP CHAIRS AND CO-CHAIRS, ITER
JOINT CENTRAL TEAM AND PHYSICS INTEGRATION UNIT & ITER EDA 1999 Chapter 1:
overview and summary. _Nucl. Fusion_ 39 (12), 2137–2174.
ITER PHYSICS EXPERT GROUP ON CONFINEMENT AND TRANSPORT, ITER PHYSICS EXPERT GROUP

ON CONFINEMENT MODELING AND DATABASE & ITER PHYSICS BASIS EDITORS 1999
Chapter 2: plasma confinement and transport. _Nucl. Fusion_ 39 (12), 2175–2249.
JARDIN, S. C., POMPHREY, N. & DELUCIA, J. 1986 Dynamic modeling of transport and positional control
of tokamaks. _J. Comput. Phys_ . 66, 481–507.
JENSEN, R. V., POST, D. E., GRASBERGER, W. H., TARTER, C. B. & LOKKE, W. A. 1977 Calculations
of impurity radiation and its effects on tokamak experiments. _Nucl. Fusion_ 17 (6), 1187–1196.
KEILHACKER, M. 1999 JET deuterium:tritium results and their implications. _Phil. Trans. R. Soc._ A 357,
415–442.
KEILHACKER, M., GIBSON, A., GORMEZANO, C. & REBUT, P. H. 2001 The scientific success of JET.
_Nucl. Fusion_ 41 (12), 1925–1966.
KISHIMOTO, H., ISHIDA, S., KIKUCHI, M. & NINOMIYA, H. 2005 Advanced tokamak research on JT-60.
_Nucl. Fusion_ 45 (8), 986–1023.
KUANG, A. Q., BALLINGER, S., BRUNNER, D., CANIK, J., CREELY, A. J., GRAY, T.,
GREENWALD, M., HUGHES, J. W., IRBY, J., LABOMBARD, B., _et al._ 2020 Prediction and
mitigation of divertor heat fluxes in SPARC. _J. Plasma Phys_ . (under review).
KUANG, A. Q., BALLINGER, S., LABOMBARD, B., GREENWALD, M., TERRY, J. L., WUKITCH, S.,
UMANSKY, M. & BRUNNER, D. 2019 Developing solutions for GW/m [2] -level divertor heat fluxes
for a 10 second flat top discharge in SPARC. In _61st Annual Meeting of the APS Division of Plasma_
_Physics_ .
KUANG, A. Q., CAO, N. M., CREELY, A. J., DENNETT, C. A., HECLA, J., LABOMBARD, B.,
TINGUELY, R. A., TOLMAN, E. A., HOFFMAN, H., MAJOR, M., _et al._ 2018 Conceptual design
study for heat exhaust management in the ARC fusion pilot plant. _Fusion Engng Des_ . 137,
221–242.
LEE, G. S., KWON, M., DOH, C. J., HONG, B. G., KIM, K., CHO, M. H., NAMKUNG, W.,
CHANG, C. S., KIM, Y. C., KIM, J. Y., _et al._ 2001 Design and construction of the KSTAR
tokamak. _Nucl. Fusion_ 41 (10), 1515–1523.
LIN, Y., WRIGHT, J. C. & WUKITCH, S. J. 2020 ICRF on the SPARC tokamak. _J. Plasma Phys_ .
(under review).
LUXON, J. L. 2002 A design retrospective of the DIII-D tokamak. _Nucl. Fusion_ 42 (5), 614–633.
LUXON, J. L. 2005 A brief introduction to the DIII-D tokamak. _Fusion Sci. Technol_ . 48 (2), 828–833.
MAINGI, R., LUMSDAINE, A., BARISH, S., WHITE, A., CHACON, L., GOURLAY, S., HUMPHREYS, D.,
IZZO, V., ALLAIN, J.-P., RAPP, J., _et al._ 2018 Transformative enabling capabilities for efficient
advance toward fusion energy. _Tech. Rep._ Fusion Energy Sciences Advisory Committee.
MARTIN, Y. R., TAKIZUKA, T. & THE ITPA CDBM H-MODE THRESHOLD DATA GROUP 2008 Power
requirement for accessing the H-mode in ITER. _J. Phys.: Conf. Ser_ . 123, 012033.
MCDONALD, D. C., CORDEY, J. G., THOMSEN, K., KARDAUN, O. J. W. F., SNIPES, J. A.,
GREENWALD, M., SUGIYAMA, L., RYTER, F., KUS, A., STOBER, J., _et al._ 2007 Recent progress
on the development and analysis of the ITPA global H-mode confinement database. _Nucl. Fusion_
47, 147–174.

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

<!-- PAGE:23 -->

MEADE, D. M. 2002 _a_ [A comparison of unit costs for FIRE and ITER. Available at: https://fire.pppl.gov/](https://fire.pppl.gov/snow{_}ITERFIRE{_}cost.pdf)
[snow_ITERFIRE_cost.pdf.](https://fire.pppl.gov/snow{_}ITERFIRE{_}cost.pdf)
MEADE, D. M. 2002 _b_ FIRE, a next step option for magnetic fusion. _Fusion Engng Des_ . 63–64, 531–540.
MUKHOVATOV, V., SHIMADA, M., LACKNER, K., CAMPBELL, D. J., UCKAN, N. A., WESLEY, J. C.,
HENDER, T. C., LIPSCHULTZ, B., LOARTE, A., STAMBAUGH, R. D., _et al._ 2007 Chapter 9: ITER
contributions for DEMO plasma development. _Nucl. Fusion_ 47 (6), S404–S413.
NATIONAL ACADEMIES OF SCIENCES, ENGINEERING AND MEDICINE 2019 _Final Report of the_
_Committee on a Strategic Plan for U.S. Burning Plasma Research_ . The National Academies Press.
NEILSON, G. H. 1992 II. Device description and general physics requirements. _Fusion Technol_ . 21 (3P1),
1056–1075.
NEU, R. L., BREZINSEK, S., BEURSKENS, M., BOBKOV, V., DE VRIES, P., GIROUD, C., JOFFRIN, E.,
KALLENBACH, A., MATTHEWS, G. F., MAYORAL, M., _et al._ 2014 Experiences with tungsten
plasma facing components in ASDEX Upgrade and JET. _IEEE Trans. Plasma Sci_ . 42 (3),
552–562.
NEU, R., DUX, R., KALLENBACH, A., PÜTTERICH, T., BALDEN, M., FUCHS, J. C., HERRMANN,
A., MAGGI, C. F., MULLANE, M. O., PUGNO, R., _et al._ 2005 Tungsten: an option for divertor
and main chamber plasma facing components in future fusion devices. _Nucl. Fusion_ 45 (3),
209–218.
NEU, R., RIESCH, J., COENEN, J. W., BRINKMANN, J., CALVO, A., ELGETI, S., GARCÍA-ROSALES,
C., GREUNER, H., HOESCHEN, T., HOLZNER, G., _et al._ 2016 Advanced tungsten materials for
plasma-facing components of DEMO and fusion power plants. _Fusion Engng Des_ . 109–111,
1046–1052. Proceedings of the 12th International Symposium on Fusion Nuclear Technology-12
(ISFNT-12).
OLYNYK, G. M., HARTWIG, Z. S., WHYTE, D. G., BARNARD, H. S., BONOLI, P. T., BROMBERG, L.,
GARRETT, M. L., HAAKONSEN, C. B., MUMGAARD, R. T. & PODPALY, Y. A. 2012 Vulcan: a
steady-state tokamak for reactor-relevant plasma–material interaction science. _Fusion Engng Des_ .
87 (3), 224–233. Special Section on Vulcan Conceptual Design.
PARKER, R. R., BATEMAN, G., COLESTOCK, P. L., FURTH, H. P., GOLDSTON, R. J.,
HOULBERG, W. A., IGNAT, D., JARDIN, S., JOHNSON, J. L., KAYE, S., _et al._ 1988 Compact
ignition tokamak physics and engineering basis. In _IAEA Fusion Energy Conference Proceedings_,
p. 359. IAEA.
PARKER, R. R., GREENWALD, M., LUCKHARDT, S. C., MARMAR, E. S., PORKOLAB, M. & WOLFE,
S. M. 1985 Progress in tokamak research at MIT. _Nucl. Fusion_ 25 (9), 1127–1136.
REINKE, M. L. 2017 Heat flux mitigation by impurity seeding in high-field tokamaks. _Nucl. Fusion_ 57 (3),
034004.
RODRIGUEZ-FERNANDEZ, P., HOWARD, N. T., GREENWALD, M. J., CREELY, A. J., HUGHES, J.
W., WRIGHT, J. C., HOLLAND, C., LIN, Y., SCIORTINO, F. & THE SPARC TEAM 2020
Predictions of core plasma performance for the SPARC tokamak. _J. Plasma Phys_ [. 86. doi:10.1017/](doi:10.1017/S0022377820001075)
[S0022377820001075.](doi:10.1017/S0022377820001075)
RODRIGUEZ-FERNANDEZ, P., HOWARD, N. T., GREENWALD, M. J., HUGHES, J. W., CREELY, A. J.,
HOLLAND, C., WRIGHT, J. C. & WUKITCH, S. 2019 Physics-based integrated modeling and
exploration of fusion performance in SPARC plasmas. In _61st Annual Meeting of the APS Division_
_of Plasma Physics_ .
ROMANELLI, F. & JET EFDA CONTRIBUTORS 2013 Overview of the JET results with the ITER-like
wall. _Nucl. Fusion_ 53 (10), 104002.
SCHMIDTMAYR, M., HUGHES, J. W., RYTER, F., WOLFRUM, E., CAO, N., CREELY, A. J.,
HOWARD, N., HUBBARD, A. E., LIN, Y., REINKE, M. L., _et al._ 2018 Investigation of the critical
edge ion heat flux for L–H transitions in Alcator C-Mod and its dependence on BT. _Nucl. Fusion_ 58
(5), 056003.
SCHULTZ, J. H., ANTAYA, T., FENG, J., GUNG, C., MARTOVETSKY, N., MINERVINI, J. V.,
MICHAEL, P., RADOVINSKY, A. & TITUS, P. 2005 The ITER central solenoid. In _21st IEEE/NPS_
_Symposium on Fusion Engineering SOFE 05_, pp. 1–4.
SCOTT, S., HOWARD, N., RODRIGUEZ-FERNANDEZ, P. & TOLMAN, E. 2019 Projections of ripple-loss
of fast ions in SPARC. In _61st Annual Meeting of the APS Division of Plasma Physics_ .

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

<!-- PAGE:24 -->

SCOTT, S. D., KRAMER, G. J., SNICKER, A., VARJE, J., SÄRKIMÄKI, K., TOLMAN, E. A.,
RODRIGUEZ-FERNANDEZ, P. & WRIGHT, J. C. 2020 Fast ion physics in SPARC. _J. Plasma Phys_ .
[86. doi:10.1017/S0022377820001087.](doi:10.1017/S0022377820001087)
SHIMADA, M., CAMPBELL, D. J., MUKHOVATOV, V., FUJIWARA, M., KIRNEVA, N., LACKNER, K.,
NAGAMI, M., PUSTOVITOV, V. D., UCKAN, N., WESLEY, J., 2007 Chapter 1: overview and
summary. _Nucl. Fusion_ 47 (6), S1–S17.
SONG, Y. T., LI, J. G., WAN, Y. X., WAN, B. N., FU, P., GAO, X., XIAO, B. J., ZHAO, Y. P., HU, C. D.,
GAO, G., _et al._ 2013 EAST accomplishments/plans in support of fusion next-steps. In _2013 IEEE_
_25th Symposium on Fusion Engineering (SOFE)_, pp. 1–6.
SORBOM, B. N., BALL, J., PALMER, T. R., MANGIAROTTI, F. J., SIERCHIO, J. M., BONOLI, P.,
KASTEN, C., SUTHERLAND, D. A., BARNARD, H. S., HAAKONSEN, C. B., _et al._ 2015 ARC: a
compact, high-field, fusion nuclear science facility and demonstration power plant with demountable
magnets. _Fusion Engng Des_ . 100, 378–405.
STRACHAN, J. D., BATHA, S., BEER, M., BELL, M. G., BELL, R. E., BELOV, A., BERK, H.,
BERNABEI, S., BITTER, M., BREIZMAN, B., _et al._ 1997 TFTR DT experiments. _Plasma Phys._
_Control. Fusion_ 39 (12B), B103–B114.
STREIBL, B., LANG, P. T., LEUTERER, F., NOTERDAEME, J.-M. & STÄBLER, A. 2003 Chapter 2:
machine design, fueling, and heating in ASDEX upgrade. _Fusion Sci. Technol_ . 44 (3), 578–592.
SWEENEY, R., CREELY, A. J., DOODY, J., FÜLÖP, T., GARNIER, D. T., GRANETZ, R.,
GREENWALD, M., HESSLOW, L., IRBY, J., IZZO, V. A., _et al._ 2020 MHD stability and disruptions
in the SPARC tokamak. _J. Plasma Phys_ [. 86. doi:10.1017/S0022377820001129.](doi:10.1017/S0022377820001129)
TAKENAGA, H., TANAKA, K., MURAOKA, K., URANO, H., OYAMA, N., KAMADA, Y.,
YOKOYAMA, M., YAMADA, H., TOKUZAWA, T. & YAMADA, I. 2008 Comparisons of density
profiles in JT-60U tokamak and LHD helical plasmas with low collisionality. _Nucl. Fusion_ 48 (7),
075004.
THOME, R. J., SMITH, B. A. JR., Pillsbury, R. D., Olmstead, M. M., Bates, J., Vieira, R., Feng, J.,
Titus, P. & Myatt, R. L. 1991 Compact ignition tokamak (CIT) central solenoid design and R&D
for a “bucked” and for a “wedged” machine. _Fusion Technol_ . 19 (3P2A), 1059–1064.
THOMSEN, K. & THE H-MODE DATABASE WORKING GROUP 2002 The international global H-mode
confinement database: storage and distribution. _Fusion Engng Des_ . 60 (3), 347–352.
TINGUELY, R. A., SVENSSON, P., HOPPE, M., EMBREUS, O., FULOP, T., NEWTON, S., CREELY, A. J.,
SWEENEY, R. & GRANETZ, R. S. 2019 Runaway electrons in SPARC. In _61st Annual Meeting of_
_the APS Division of Plasma Physics_ .
TOLMAN, E. A., LOUREIRO, N. F., RODRIGUES, P., HUGHES, J. W. & MARMAR, E. S. 2019
Dependence of alpha-particle-driven Alfvén eigenmode linear stability on device magnetic field
strength and consequences for next-generation tokamaks. _Nucl. Fusion_ 59 (4), 046020.
UCKAN, N. A. & THE ITER PHYSICS GROUP 1990 _ITER physics design guidelines: 1989_ . IAEA.
VERDOOLAEGE, G., KAYE, S. M., ANGIONI, C., KARDAUN, O., MASLOV, M., ROMANELLI, M.,
RYTER, F. & THOMSEN, K. 2018 First analysis of the updated itpa global h-mode confinement
database. In _Proceedings of the 27th IAEA Fusion Energy Conference_, p. 8. International Atomic
Energy Agency.
VERDOOLAEGE, G., KAYE, S. M., ANGIONI, C., KARDAUN, O. J. W. F., MASLOV, M.,
ROMANELLI, M., RYTER, F. & THOMSEN, K. 2020 The updated ITPA global H-mode
confinement database: description and analysis. In _ITPA Transport & Confinement Topical Group_
_Meeting_ .
WAGNER, F., BECKER, G., BEHRINGER, K., CAMPBELL, D., EBERHAGEN, A., ENGELHARDT, W.,
FUSSMANN, G., GEHRE, O., GERNHARDT, J., GIERKE, G. V., _et al._ 1982 Regime of improved
confinement and high beta in neutral-beam-heated divertor discharges of the ASDEX tokamak.
_Phys. Rev. Lett_ . 49, 1408–1412.
WEIYUE, W., SONGTAO, W., JIE, Y., DAMING, G. & PEIDE, W. 2006 Assembly of the superconducting
tokamak EAST. _J. Korean Phys. Soc_ . 49 (9), 14.
WHYTE, D. G., MINERVINI, J., LABOMBARD, B., MARMAR, E., BROMBERG, L. & GREENWALD, M.
2016 Smaller and sooner: exploiting high magnetic fields from new superconductors for a more
attractive fusion energy development path. _J. Fusion Energy_ 35, 41–53.

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)

<!-- PAGE:25 -->

WRIGHT, J., LIN, Y., WUKITCH, S. & SELTZMAN, A. 2019 ICRF heating for SPARC. In _61st Annual_
_Meeting of the APS Division of Plasma Physics_ .
XU, X. Q., LI, N. M., LI, Z. Y., CHEN, B., XIA, T. Y., TANG, T. F., ZHU, B. & CHAN, V. S. 2019
Simulations of tokamak boundary plasma turbulence transport in setting the divertor heat flux width.
_Nucl. Fusion_ 59 (12), 126039.
YUSHMANOV, P. N., TAKIZUKA, T., RIEDEL, K. S., KARDAUN, O. J. W. F., CORDEY, J. G., KAYE,
S. M. & POST, D. E. 1990 Scalings for tokamak energy confinement. _Nucl. Fusion_ 30 (10),
1999–2006.
ZOHM, H. 2010 On the minimum size of DEMO. _Fusion Sci. Technol_ . 58 (2), 613–624.
ZWEBEN, S. J., ARUNASALAM, V, BATHA, S. H., BUDNY, R. V., BUSH, C. E., CAUFFMAN, S.,
CHANG, C. S., CHANG, Z., CHENG, C. Z., DARROW, D. S., _et al._ 1997 Alpha-particle physics in
the tokamak fusion test reactor DT experiment. _Plasma Phys. Control. Fusion_ 39 (5A), A275–A283.

[https://doi.org/10.1017/S0022377820001257 Published online by Cambridge University Press](https://doi.org/10.1017/S0022377820001257)


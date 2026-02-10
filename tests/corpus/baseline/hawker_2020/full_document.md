

<!-- PAGE:1 -->


Research

**Cite this article:** Hawker N. 2020 A simplified

economic model for inertial fusion. _Phil.Trans._

_R.Soc.A_ **378** : 20200053.

http://dx.doi.org/10.1098/rsta.2020.0053

Accepted: 10 June 2020

One contribution of 14 to a discussion meeting

issue ‘Prospects for high gain inertial fusion

energy (part 1)’.

**Subject Areas:**

energy, plasma physics

**Keywords:**

fusion, inertial fusion, LCOE, gain

**Author for correspondence:**

Nicholas Hawker

[e-mail: nicholas.hawker@firstlightfusion.com](mailto:nicholas.hawker@firstlightfusion.com)

Electronic supplementary material is available

[online at https://doi.org/10.6084/m9.figshare.](https://doi.org/10.6084/m9.figshare.c.5098451)

[c.5098451.](https://doi.org/10.6084/m9.figshare.c.5098451)

A simplified economic model
for inertial fusion

Nicholas Hawker

First Light Fusion Ltd., Unit 10 Oxford Industrial Park, Mead Road,

Yarnton, Oxfordshire, OX5 1QU

[NH, 0000-0003-0810-0631](http://orcid.org/0000-0003-0810-0631)

## Abstract

A simple model for the levelized cost of electricity
(LCOE) of an inertial fusion power plant is developed.
The model has 14 parameters. These have been
designed to be technology agnostic, such that the
model may be applied broadly to all variants of
inertial fusion. It is also designed to allow easy use
of proxies from existing technology. The variables
related most intimately to the physics challenges of
inertial fusion, such as gain and target cost, are treated
as parameters such that requirements can be found
without bringing complex physics into the model.
A Monte Carlo approach is taken to explore the
parameter space. The most important conclusion is
that a combination of high gain (greater than 500)
and high fusion energy yield per shot (greater than
5 GJ) together appear to unlock more cost competitive
designs than those in the existing literature. Designs
with LCOE as low as $25/MWh are found with
optimistic but not obviously unrealistic inputs.
This article is part of a discussion meeting issue
‘Prospects for high gain inertial fusion energy (part 1)’.

1. Introduction

Cost effective energy production using inertial fusion
depends on many factors but one of the most important
is the concept of ‘gain’. This can be defined in many
ways but it is common in the inertial fusion community
to talk in terms of ‘target gain’, which is the fusion
energy released divided by the energy input to the
target. In these terms, it is often stated that a gain of
30–100 is required for power production from inertial
fusion [1]. This conclusion comes from consideration
of the driver and thermodynamic efficiencies, and a

2020 The Authors. Published by the Royal Society under the terms of the
[Creative Commons Attribution License http://creativecommons.org/licenses/](http://creativecommons.org/licenses/by/4.0/)
[by/4.0/, which permits unrestricted use, provided the original author and](http://creativecommons.org/licenses/by/4.0/)
source are credited.

<!-- PAGE:2 -->

**Table1.** Acomparisonofindicativecostsofelectricalgenerationfordifferenttechnologiesinthe2030s.Alsoshownisawholesystem cost for managing the intermittency of renewable generation, and a cost for large-scale carbon capture and storage
(CCS).

~~LCOE ($/MWh)~~ ~~fexibility cost ($/MWh)~~ ~~CCS cost ($/MWh)~~
solar PV 35 +15 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
onshore wind 35 +15 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
offshore wind 50 +15 . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
coal 50 - +70
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
gas 80 - +70
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
nuclear 100 - . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

requirement for the recirculating power to be a small fraction of the total electrical power. Taken
literally, the conclusion on required gain is true; a gain in that range is necessary for power
production, but the analysis says nothing about cost. Fusion must be cost competitive in a market
of different energy technologies.

(a) The cost of electricity

## The cost of electricity

Cost comparisons of energy generation technologies are typically made using the levelized cost of
electricity (LCOE), which will be defined in equation (2.1). To understand the cost requirements
for fusion means projecting the expected costs of future energy generation technologies to the
time where a fusion power plant is expected to be built. Projections of this kind are not a precise
science and are subject to substantial judgement, but with that caveat there are several major
studies to draw on [2–4]. A summary of rough predicted values for the cost of electricity in the
2030s is given in table 1. These are indicative global averages; the actual cost depends strongly on
the local economy and geography, particularly for renewables.
Renewables are intermittent by nature and to achieve a very high fraction of electricity
generation requires a balancing of variability in the system. One estimate of the additional cost,
from a whole-system point of view, of balancing this variability is $15/MWh [5], although it
should be noted that this is not a fully zero-carbon system, requiring the use of gas peakers to
manage seasonal variation.
Based on only this information, the conclusion would be that solar and onshore wind are
the most cost competitive technologies and fusion would need to compete directly on price at a
$50/MWh level. This, however, does not account for an important aspect, which is the balance of
supply and demand. Electricity is expected to increase substantially as a fraction of total energy
use as sectors currently using hydrocarbons electrify [6,7]. The electrification of transport is an
example. Without a significant increase in the rate of deployment of renewables, it seems likely
that there will be a ‘clean power gap’. One study estimates the total generation from renewables
in the 2030s could reach 50% of demand [8]. This study is global in scope but in relation to the UK,
it does not account for the more recent commitment to net-zero, which would imply that the clean
power gap is even larger. Fusion must therefore compete with the other options for the remaining
market.
The technology choices available to fill that remaining market are dramatically different
depending on the weight that is placed on carbon intensiveness, with the choices most
constrained in net-zero policy scenarios. If reducing carbon intensity is not of concern, the
remaining electricity demand will be met with coal and gas. In a net-zero world, and based only
on the economics, this demand would be met with nuclear and the higher cost would be accepted.
If nuclear power is not acceptable to the public then the remaining options are limited. Large-scale

~~**2**~~

<!-- PAGE:3 -->

carbon capture and storage (CCS) is not a proven technology and it roughly doubles the cost of
generation, requiring the acceptance of an even higher cost.
Judging what constitutes a competitive price point for fusion is exactly that, a judgement. The
author is sceptical about public tolerance for a higher price for electricity and believes that fusion
must reach a price point of $100/MWh for the first plants, competing directly with nuclear, and
with a pathway for future plants to reach $60/MWh, displacing remaining gas generation. As will
be seen, the model presented in this paper suggests that reaching this goal is not only achievable
but that inertial fusion may indeed be able to compete directly with renewables on cost.

(b) Previous studies

## Previous studies

There have been several previous conceptual design studies of inertial fusion power plants

[9–15]. These prior works focus on singular design points rather than exploration of the parameter
space. The works cited include three different types of driver: lasers, heavy ion beams, and pulsed
power drivers. Within the laser driver literature there is, over time, a general move in a particular
direction, namely, to lower energy drivers and higher frequencies. This in turn leads to lower
gains (commensurate with lower driver energies) and a perceived need for very low target costs.
The challenges of high frequency are clear, but the benefits are less so, or rather, the reasons for
the choice of design point are less clear. Studies of pulsed power drivers focus on lower frequency
of operation [15], although this seems to be more out of necessity than design optimization; the
replacement of the final transmission line section being a challenging aspect of these designs. The
present work aims to complement these prior studies by providing a tool that makes the cost
impact of design choices such as higher frequency clearer.

2. Model

## Model
$$\text{LCOE} = \frac{\sum_{i=1}^{n} C_i / (1+d)^i}{\sum_{i=1}^{n} E_i / (1+d)^i}$$

          - _n_
_i_ =1 _[C][/]_ [(1][ +] _[ d]_ [)] _[i]_
LCOE = ~~�~~ _n_ [,] (2.1)
_i_ =1 _[E][i][/]_ [(1][ +] _[ d]_ [)] _[i]_

where _Ci_ and _Ei_ are the cost and the energy generated in the _i_ th year, respectively, and _d_ is the
discount rate or weighted average cost of capital. When calculated in this way, the LCOE is the
average price for which energy generated would need to be sold for the net present value of
the investment to be zero. That is, it is the price that would make the energy generating asset a
profitable investment.
Typical values for the discount rate depend on many things but a crucial aspect is whether
the project is privately funded or government-backed. Privately funded projects might have a
discount rate greater than 10%, whereas government borrowing costs can be as low as 2% [16,17].
LCOE is a simplified concept, the price of electricity is not a constant. In many geographies,
such as the UK, it is a time-varying quantity set through auction processes in a dynamic market. If
a generating asset is being built to address peak, high-price demand, a so-called ‘peaking plant’,
a more complex calculation of economic viability would be required.
To calculate the LCOE, we need models for cost and energy generated over time. To do this,
we will split the plants life into two phases, construction and operation. In this paper, we will take
the construction time to be 5 years and the operational lifetime to be 40 years.
The energy generated during construction is zero. The energy generated during operation can
be written as

_Ei_ = [(365][ ×][ 24][ ×][ 60][ ×][ 60)] _Peμa_, (2.2)

(10 [6] × 60 × 60)

~~**3**~~

<!-- PAGE:4 -->

**Table 2.** A list of the 14 independent parameters of the model.

~~parameter~~ ~~symbol~~ ~~units~~
availability _μa_              . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
blanket multiple _Eb_            . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
discount _d_            . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
driver cost constant _γ_ $/J
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
driver efficiency _μd_             . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
driver energy _Ed_ J
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
driver lifetime _Nd_ shots/year
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
frequency _f_ Hz
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
gain _G_           . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
O&M cost constant _ε_ $/kWe-yr
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
plant cost constant _α_ $/kWe
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
target cost constant _δ_ $/target
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
thermal efficiency _μth_            . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
yield cost constant _β_ $/GJ
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

where _Pe_ is the electrical power of the plant, _μa_ is the availability, and where the numerical factors
convert from power to energy per year in MWh. The availability, normally given as a percentage,
is the amount of energy produced compared with continuous operation at rated output. To
illustrate by example, for nuclear power availability is mainly set by scheduled downtime. If the
refuelling process takes six months and must be done after 3 years, the availability would be 86%.
For a fusion power plant, there is expected to be scheduled downtime for replacement of
components, but it should also be expected, particularly for the first plants, that unscheduled
downtime will be a major influence on availability. In this analysis, we will take availability as a
parameter; a more complex model could have a specific availability sub-model.
The cost model is given by

~~**4**~~

_Ci_ =

_Cp_ + _CY_ + _Cd_, _c_ on during construction, (2.3)
_Ct_ + _CO_ & _M_ + _Cd_, _op_ during operation

where _Cp_ is the plant cost, _CY_ is the yield cost, _Cd_,con and _Cd_, _op_ are the driver costs during
construction and operation, respectively, _Ct_ is the target cost and _CO_ & _M_ is the fixed operations
$$C_p = \alpha P e^{Y_c}$$

Wait, let me reconsider. Looking at the garbled text more carefully:

The equation numbered (2.4) shows `Cp = [α][P][e]` with context mentioning `Yc` (years for construction) and `α` (a constant describing plant cost).

Given the context of plant cost equations in engineering economics, this is likely a power relationship. A common form is:

$$C_p = \alpha P^e$$

where $C_p$ is the plant cost, $\alpha$ is a constant describing the plant cost, $P$ is a capacity or size parameter, and $e$ is a scaling exponent. This follows the standard power-law cost scaling relationship used in engineering economics.

$$C_p = \alpha P^e$$
It is common practice to describe these costs using $/kWe and in this model we will assume a
direct proportionally. This allows us to use proxies from other technologies to provide bounding
values. The plant cost is

_Cp_ = _[α][P][e]_ (2.4)

where _Yc_ is the number of years for construction and _α_ is a constant describing the plant cost in
$/kWe. Nuclear power plants cost around $6000/kWe, whereas gas power plants are closer to
$1000/kWe. It is reasonable to assume that the cost of a fusion power plant will be less than the
cost of a nuclear plant due to the substantially reduced risk profile, although this should not be

<!-- PAGE:5 -->

taken for granted as generally speaking regulations for fusion do not yet exist. Equally, it is not
reasonable to think that a fusion power plant would be less complex to build than a gas power
plant, which therefore gives us a lower bound. As a sense check we can put the capital costs from
the HYLIFE design [8] into these terms. Separating the driver cost and inflating to 2020 dollars
gives $3600/kWe.
Modelling the capital cost as proportional to electrical power only leads to a part of parameter
space where costs are minimized using very high fusion yield and low frequency, reducing plant
size, and therefore cost, while also reducing target cost. A second aspect of capital cost is therefore
added, which is proportional to the fusion energy per event, which here will be called the ‘yield
cost’. Essentially this represents the cost of the reaction vessel.
The engineering of a system for large yield but low electrical power, which is the parameter
space we’re trying to constrain by adding the yield cost, might not be ‘typical’. For example, large
energy release and low frequency may lead to a meaningful variation in the temperature of the
primary coolant over the shot cycle. This will potentially introduce a complexity in the primary
circuit, and possibly a compromise in efficiency. However, to the author, a system with this
characteristic does not seem inherently implausible, so long as the central chamber can reliably
absorb the energy release.
The yield cost is given by

_βEf_
_CY_ =, (2.5)

where _Ef_ is the fusion energy per shot and _β_ is a constant describing the cost in $/GJ. This cost
parameter can be bounded by recognizing that the primary coolant itself is, for both the First
Light and HYLIFE designs, the most expensive material in the reaction vessel. Both propose pure
lithium as the primary coolant. The bulk cost for high-purity lithium metal is roughly $100/kg. All
other options, such as FLiBe or enriched lithium, are likely to be more expensive. In comparison,
the price of steel is $1–5/kg.
A lower bound for the coolant mass can be found based on the mass required to absorb
the fusion energy without egregious temperature rise. Using the heat capacity of lithium and a
temperature rise of 400 C gives a cost of $70 k/GJ. An upper bound can be found from the HYLIFE
design [8], which has a total lithium inventory of 800 tonnes, giving a cost of $44 M/GJ. It should
be noted, however, that the $3600/MWe quoted above includes the lithium cost, i.e. there is a
double counting issue with these numbers. This is why the author thinks that the HYLIFE yield
cost can be reasonably thought of as an upper bound.
The driver cost appears in both construction and operation because the replacement of parts
is an important aspect in the cost of a fusion power plant. The lifetime of the driver itself is an
important consideration but there will also be replacement parts required in the reaction vessel
and perhaps elsewhere. In this simple model, these costs are all wrapped into a ‘replacement
driver’ cost, representing a requirement for continued capital expenditure.
The driver cost is often discussed in terms of the cost per Joule of energy delivered to target. In
this model, we will use the cost per Joule of energy in the bank. This allows the driver efficiency
to be separated from the cost more cleanly and reduces the range of values. The driver cost is
given by

_Cd_, _con_ = _[γ][ E][d]_ (2.6)

~~**5**~~

and

_Cd_, _op_ = _[γ][ E][d]_, (2.7)

_Ld_

where _Ed_ is the driver bank energy, _Ld_ is the driver lifetime in years and _γ_ is a constant describing
the driver cost in $/J. Some rough values for _γ_ can be found by looking at existing machines. The
NIF laser costs roughly $4bn and has a 422 MJ capacitor bank, giving a cost of $9.5/J. First Light’s
Machine Three has a bank energy of 2.5 MJ and cost $4.3 M, giving a cost of $1.7/J. It should be
$$L_d = \frac{N_d}{N_y}$$
cost further. A more complex driver cost model could include component level costs and lifetimes
specific to the technology being considered.
The driver lifetime in years is given by

_Ld_ = _[N][d]_, (2.8)

_Ny_

where _Nd_ is the lifetime of the driver expressed as a number of shots, and _Ny_ is the number of
shots per year. Expressing the driver lifetime in terms of number of shots allows an important
trade-off with frequency to be captured. The number of shots per year is

_Ny_ = (365 × 24 × 60 × 60) _f_ _μa_, (2.9)

where _f_ is the frequency of shots and where the availability also appears to account for downtime.
The target cost is given by
_Ct_ = _δNy_, (2.10)

where _δ_ is a constant describing the target cost in $/target. It should be noted that ‘target’ cost in
this context does not strictly mean the fusion target itself. All components that are consumed in
a shot must be accounted for, including, for example, the final transmission line section for the
Z-IFE approach [12].
Present inertial fusion targets are extremely expensive, but these are essentially bespoke, oneoff prototypes. Ultimately, in a mass manufacturing context, the target cost might reasonably
be expected to be proportional to the cost of the raw materials. A more complex model could
therefore have a schedule of target materials and a cost per kg for each, possibly with a multiplier
accounting for the cost of the manufacturing process itself. In this study, we will simply treat _δ_ as
a parameter with the aim of finding the requirements for target cost independent of any specific
design.
The operations and maintenance cost represents other general running costs, such as staff.
These costs are commonly described in terms of $/kWe-yr. Again, figures from gas and nuclear
can give us bounds, in this case $10–100/kWe-yr [18].

_CO_ & _M_ = _εPe_, (2.11)

where ε is O&M cost in $/kWe-yr.
This leaves us with only the electrical power, _Pe_, unaccounted for. This can be expressed as,

_Pe_ = _μthPth_                    - _Prc_, (2.12)

where _μth_ is the thermodynamic efficiency, _Pth_ is the thermal power and _Prc_ is the recirculating
power required to run the plant. The main contributor to this will be the driver, therefore,

_Prc_ = 2 _Edf_, (2.13)

where an arbitrary pre-factor of two has been applied, notionally motivated by the cooling
requirements being equal to the driver power itself. This is another area where a more complex
model could be developed. As examples, plants with a liquid metal first wall may have significant
pumping power, and plant concepts with replaceable transmission lines may need to account for
the energy cost of reforming the transmission lines for each shot.
The thermal power itself, _Pth_, can be written as

_Pth_ = _EbP_ fus, (2.14)

where _Eb_ is the energy multiple in the blanket or primary coolant and _P_ fus is the fusion power.
The energy multiple comes from the reaction between the fusion neutrons and lithium, which
regardless of any energy multiple must be used to produce tritium. The reaction with [6] Li is
exothermic, but the reaction with [7] Li is endothermic. This means that the overall sum can be endoor exothermic depending on the approach used. A reasonable range for this value is between 0.6
and 1.4.

~~**6**~~

<!-- PAGE:7 -->

Finally, the fusion power is given by

_Pfus_ = _GEtf_, (2.15)

where _G_ is the target gain and _Et_ is the target energy, or more specifically the energy incident on
the target, which is given by
_Et_ = _μdEd_, (2.16)

where _μd_ is the driver efficiency. Describing the model in these terms allows addition of gain
curves specific to individual target design concepts. Later we will add two different gain curves
and assess the impact on the available parameter space for power plant design. The first is the
spherical, isobaric hot spot limiting gain curve [1]

~~**7**~~

�0.3
, (2.17)

_G_ = 6000 _μc_

_μcEd_

_A_

where _μc_ = _Efuel_ / _Et_ is the coupling efficiency (where _Efuel_ is the final energy in the fuel), and _A_
is the isentrope parameter. In this equation, the driver energy, _Ed_, is in MJ. This model considers
ignition of preassembled fuel and finds there to be an absolute maximum gain as a function of
$$\frac{3}{4\pi} e^{\mu c E d} \rho r$$

Wait, let me reconsider the garbled text more carefully. The subscripts and superscripts suggest a specific structure. Let me re-parse this.

Looking at the garbled text again:

- `3` over `4π` suggests a fraction `\frac{3}{4\pi}`
- `ρ` with `[3]` superscript
- `e` with `[μ][c][E][d]` as superscript/subscript markers
- `ρr` at the end

The most likely equation from this garbled extraction is:

$$\frac{3}{4\pi} \frac{\rho^3}{e^{\mu c E d}} \rho r$$

Hmm, without seeing the actual PDF image (I don't see an attached image in your message), I'm working only from the garbled text. Could you share the PDF page image so I can give you the exact LaTeX? 

Based on the most common physics/math formula matching this pattern, this likely represents:

$$\frac{3}{4\pi} e^{\mu_c E_d} \rho_r^{3}$$

If you can share the image, I can provide the precise conversion.

_ρr_ =

3 _ρ_ [3]
4 _π_ _e_ _[μ][c][E][d]_

_ρr_
_θ_ = (2.19)
_ρr_ + 70

and _G_ = 6.75 _e_ 14 × _[θμ]_ _V_ [2] _[c]_ [,] (2.20)

where _ρr_ is the fuel areal density, _ρ_ is the fuel mass density, _e_ is the fuel internal energy density,
_θ_ is the burn fraction and _V_ is the implosion velocity. The scaling of areal density with driver
energy had to be reconstructed from the values given in the reference. Essentially this means
finding the value for _ρ_ [3] / _e_ . This has been done using the hydrodynamic equivalence concept
discussed in the reference. That is, the implosion velocity, final fuel internal energy density and
final fuel mass density were all assumed to remain constant as the driver energy increases. That is,
the fuel mass increases but all intrinsic properties remain the same. This process was followed for
a coupling efficiency of 10% and an implosion velocity of 400 km s [−][1], meaning that the numerical
factor in equation (2.18) is only valid for these values.
In adding these gain curves to the model, we have removed gain as a free parameter but added
further new parameters describing fundamental aspects of target physics. We will initially work
with the gain as a free parameter with the aim, much like target cost, of understanding what is
required without reference to any specific approach.

3. Results and discussion

(a) Correlation analysis

## Results and discussion

To explore the properties of the model a Monte Carlo approach was taken. There are 14 parameters
of interest, which are listed in table 3. The table also shows the ranges used for each of the
individual values, which were sampled uniformly in linear or log space as indicated. Ten million
samples were used. Some combinations give rise to designs that are clearly unfeasible, for
example, having extremely high fusion yield. The results were filtered such that the electrical
power is less than 2 GWe, the LCOE is less than $200/MWh, the initial capital expenditure is less
than $10bn, and the fusion energy is less than 25 GJ.
### Correlation analysis

To compare the relative importance of the different parameters the Pearson correlation
coefficient was calculated between each of the input parameters individually and the LCOE. The

<!-- PAGE:8 -->

**Table 3.** A list of the parameters in the model, the ranges used for a Monte Carlo sample over all parameters, whether the
particular parameter is sampled uniformly in linear or log space, and the resulting Pearson correlation coefficient between the
individual parameter of interest and the LCOE.

~~input parameter~~ ~~range~~ ~~linear or log space~~ ~~Pearson correlation coefcient~~
discount 2–12% linear +0.247
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
plant cost $1000–6000/kWe linear +0.210
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
target cost $1–100/target log +0.186
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
gain 10–1000 log −0.164
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
driver lifetime 10 [6] –10 [9] shots log −0.134
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
availability 50–100% linear −0.127
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
driver cost $2–10/J linear +0.075
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
driver efficiency 5–30% linear −0.063
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
O&M cost $10–100/kWe-yr linear +0.050
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
$$\rho = \frac{\text{cov}(A, B)}{\sigma_A \sigma_B}$$
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
yield cost $500 k–50 M/GJ log +0.026
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .
target energy 0.5–50 MJ linear +0.011
. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .

Pearson correlation coefficient is given by

_ρ_ = _[co][v]_ [(] _[A]_ [,] _[ B]_ [)] (3.1)

_σAσB_

where _cov_ ( _A_, _B_ ) is the covariance between variables _A_ and _B_, and _σ A_ and _σ B_ are the standard
deviations of _A_ and _B_, respectively. The value of the correlation coefficient is between −1 and +1,
indicating perfect negative and positive correlations, respectively.
Values for the Pearson correlation are given in the final column of table 3. The results do not
indicate a dominant correlation with any parameter, but there are some that have a larger impact
than others. A purely financial aspect, the discount rate, has the strongest influence on LCOE.
This should not come as a surprise for the reader familiar with costs in the nuclear sector, where
the difference between China and Europe, for example, is in large part explained by the different
cost of capital.
The plant cost features next. The plant cost depends on the engineering of the wider balance of
plant. Its importance underlines the importance of a regulatory regime appropriate to the specific
risks and challenges of fusion.
The next two aspects relate to the target, the target cost and the gain. The results show a greater
correlation between target cost and LCOE than gain, which suggests it is more important to have
a cheaper target than higher gain. The difference between the coefficients is not large, however.
After these is a grouping of four parameters relating to the driver, with the driver lifetime and
availability stronger influences than the raw driver cost itself. This implies that reliable operation
is the most important aspect for the driver.
The remaining parameters do not have a strong influence. The most surprising finding here
might be the very weak influence of yield cost. This does, however, agree with more detailed
proprietary studies conducted by First Light, which found a weak dependence between details of
the reaction vessel and LCOE.
The weak dependence on frequency appears to contradict some more detailed studies, such
as HiPER, which proposes 10 Hz operation [14]. This needs deeper investigation and shows the

~~**8**~~

<!-- PAGE:9 -->

200

150

100

50

0
1 10
target cost ($/target)

~~**9**~~

![](images/Hawker---2020---A-simplified-economic-model-for-inertial-fusion.pdf-8-0.png)

10 [2]

**Figure 1.** LCOE versus target cost. All six cost parameters are sampled over the ranges indicated in table 3, with 10 k samples
used. The results show that once target cost is less than roughly $10 the impact of further cost reduction is not large.

limits of the analysis here; in some cases, it is not enough to understand the global dependence.
In the following section, individual dependences will be explored but before moving on, we can
also look at correlations between LCOE and other output variables.
The model shows an ‘economy of scale’, with larger plants found to correlate with lower
LCOE. The Pearson correlation coefficient between electrical power and LCOE is −0.233, the
second-strongest correlation found. This needs exploration because the plant cost is linear with
electrical power. To explain this dependence, we need to look at the recirculating power as a
fraction of the total. The correlation between this and LCOE is +0.171, which confirms the instinct
that the recirculating power must be a small fraction of the total.

(b) Dependence on individual parameters

### Dependence on individual parameters

In the following, unless otherwise stated, the default values are: availability = 70%;
driver lifetime = 50 M shots, which at 0.2 Hz is about 8 years; thermal efficiency = 40%;
discount rate = 8%; plant cost = $3 k/kWe; driver cost = $5/J; target cost = $10/target, yield
cost = $5 M/GJ; O&M cost = $30/kWe-yr; target energy = 10 MJ; frequency = 0.2 Hz; gain = 500;
driver efficiency = 10%; and blanket multiple = 1.2.
First, we will examine the parameters relating to cost. Detailed analysis of the discount,
plant cost and driver cost did not reveal anything particularly surprising other than confirming
expectations from the generally weak correlation with any individual parameter. Even if one of
these values is at the top of the range there are still design points with LCOE less than $80/MWh
achievable.

Figure 1 shows the dependence of LCOE on target cost. There is clearly a nonlinear relationship
where, essentially, if the target cost is large it begins to dominate the costs overall. Broadly
speaking it seems that there is a threshold below which the target cost has been reduced enough
and after which there is limited benefit for further improvement, and that that threshold is
roughly $10/target.
Exploration of the yield cost did not reveal anything to change the conclusion from the general
correlation analysis, which is that it does not play a large role. To put this in context, for the default
design point here, the fusion yield is 5 GJ per event. At the upper end of the range, this means
that the reaction vessel alone costs $250 M. However, the plant cost is $1.3bn and the driver cost
is $500 M in this case, which explains the insensitivity.
Moving onto parameters relating more to engineering and physics, the dependence on driver
lifetime is as expected, with a longer lifespan naturally being better. It is interesting to note,

<!-- PAGE:10 -->

200

150

100

50

0

~~**10**~~

![](images/Hawker---2020---A-simplified-economic-model-for-inertial-fusion.pdf-9-0.png)

200 400 600
gain

800 1000

**Figure 2.** LCOEversusgain.Gain,driverenergy,frequencyanddriverefficiencyarebeingsampledovertherangesindicatedin
table 3. The points are coloured by electrical power as indicated in the legend. In order to fill out the less common parameter
space,whicharethesmallerplantsizes,100 ksampleswererequired.Theresultsweretruncatedtoshow500pointspercategory.
The dependence of LCOE on both gain and electrical power can be seen. (Online version in colour.)

however, that like target cost, there seems to be a threshold beyond which further improvement
delivers marginal benefit. For the default parameters here this is about 5 years, which is roughly
30 M shots.
LCOE as a function of gain is shown in figure 2, with a stratification by electrical power. This
shows that the gain needs to be above a certain level to reach a cost competitive design; for the
default design here, greater than roughly 400. The required gain depends on the cost parameters,
however. If values near the bottom of the range are accessible, competitive LCOE numbers exist
even with gain less than 100.
The figure also shows two things about plant size. First, that smaller plants require higher
gain, which might seem counterintuitive. Second, the dependence of LCOE on the plant size can
be seen, although a wide range of values had to be selected to make the effect clearly visible.
Perhaps the most surprising conclusion from this plot is that designs smaller than 50 MWe can
potentially be viable.

Figure 3 shows LCOE versus frequency, where the results have been stratified according to the
fusion energy per shot. With no restriction on yield, there is an optimum frequency. On the left,
the driver and/or reaction vessel increase in cost. On the right the limit on electrical power, in
this case 2 GWe, clips the parameter space. If the yield is constant and the frequency increases, the
power must increase. With no limit on power output there is no optimum frequency, with faster
being universally better. Returning to the correlation analysis without the electrical power and
capital expense limits confirms this, with the new correlation coefficient being −0.110.
Looking at the different yield categories seems to explain why existing ICF designs have high
electrical power and high frequency. As the yield decreases, the optimum frequency increases,
and with a yield of 1 GJ or less the optimum is at the cut-off for electrical power. This suggests
that the energy per event has a profound, although indirect, influence on the optimal design
point for ICF. Higher yield enables lower LCOE through reduced target cost and reduced plant
cost, while high gain ensures that recirculating power is minimized.

(c) Addition of gain curves

### Addition of gain curves

The first gain curve [1], the limiting gain curve for a spherical, isobaric hot spot fuel configuration,
given in equation (2.17), replaces gain as an independent parameter with two new physics
parameters: _μc_, the coupling efficiency, and _A_, the isentrope parameter. These were set to 10%

<!-- PAGE:11 -->

200

150

100

50

![](images/Hawker---2020---A-simplified-economic-model-for-inertial-fusion.pdf-10-0.png)

~~**11**~~

0
10 [–2] 10 [–1] 1 10

frequency (Hz)

**Figure 3.** LCOE versus frequency, coloured by fusion energy per shot. The sampling is as in figure 2, with the low yield designs
the less common in this case. An optimum frequency can be seen, but the location of this depends on the fusion yield, with
lower yield designs having an optimum at higher frequency. (Online version in colour.)

and 3, respectively. In the Monte Carlo approach used, the gain was randomly set to a value
between 1 and the limiting gain, where that limiting gain was commensurate with the randomly
selected driver energy used for that calculation. The results showed little change, indicating that
this fuel configuration is fundamentally able to deliver enough gain to reach cost competitiveness.
The second gain curve [19], given in equations (2.18–2.20), is much more restrictive in terms
of absolute gain attainable, reaching a maximum of approximately 250 for the driver energies
considered here. This gain curve adds the fuel mass density, _ρ_, the fuel internal energy, _e_, the
implosion velocity, _V_, and the coupling efficiency, _μc_, as independent parameters. The same
approach to sampling is used as for the first gain curve, i.e. between a gain of one and the value
specified by the gain curve.
The results are shown in figure 4. In this case the impact is more pronounced; the limit on
gain removes the lowest cost designs, which need gains greater than approximately 400. The
smaller plant sizes are affected more than the larger ones by this restriction. The degree of
compromise also depends on the actual cost levels, which in figure 4 remain at the defaults.
Broader exploration of the results shows low-cost design points remain even with the more
stringent limit on gain.

(d) Minimum cost design point

### Minimum cost design point

We will now return to the scan over all parameters but with the intention of understanding the
lowest cost design points. Figure 5 shows a histogram of all calculated values for LCOE and
appears to show the possibility of very low-cost configurations.
An example configuration for which the model finds an LCOE of $24.6/MWh is:
availability = 80%; driver lifetime = 40 M shots; thermal efficiency = 50%; discount rate = 4%;
plant cost = $1.5 k/kWe; driver cost = $3/J; target cost = $2/target, yield cost = $5 M/GJ;
O&M cost = $20/kWe-yr; target energy = 5 MJ; frequency = 0.05 Hz; gain = 1000 and driver
efficiency = 20%. This results in a thermal power of 300 MWth and electrical power 147.5 MWe.
The dominant cost is the initial capital expenditure, where the plant cost is $220 M, the driver
cost is $75 M, and the yield cost is $25 M. The driver cost is low because of the low target energy
and high efficiency. Whether a system able to meet the frequency and lifetime requirements could
really be built for this cost is very uncertain.
The other question is about the plant costs. Costs for combined-cycle gas power plants, where a
Rankine cycle and the associated space and infrastructure is required, can be less than $1000/kWe;

<!-- PAGE:12 -->

200

150

100

50

0

~~**12**~~

![](images/Hawker---2020---A-simplified-economic-model-for-inertial-fusion.pdf-11-0.png)

50 100 150 200
gain

250 300

**Figure 4.** LCOE versus gain, where the gain is not an independent parameter but has been calculated using a gain curve from

[19]. Driver energy, frequency and driver efficiency are being sampled over the ranges indicated in table 3. Note that the _x_ -axis
is truncated at a gain of 300. With this gain curve there is a cost optimum very close to the ultimate gain limit specified by the
gain curve. 500 k samples were used. (Online version in colour.)

20 000

17 500

15 000

12 500

10 000

5000

0

0 25 50 75 100 125 150 175 200
LCOE ($/MWh)

**Figure 5.** A histogram of the LCOE from the sample over all parameters. The scan shows that very low-cost designs, less than
$25/MWh, may be possible.

however, this number is based on a 700 MWe plant [14]. From a physics point of view, gain of 1000
is very high. The limiting gain curve of Atzeni and Meyer-ter-Vehn [1] shows it is possible to reach
this level, but gain of 1000 is certainly larger than typically discussed.
Clearly, design points of this type are worth further exploration, but the author urges caution.
It is the role of a simple model to indicate interesting parts of parameter space, but much more
detailed study is required to substantiate the findings.

4. Conclusion

## Conclusion

The aim of this work was to build a simple model for LCOE of an inertial fusion power plant. The
core physics has been described in a technology agnostic manner that allows broad application
across different inertial fusion approaches. The model for the wider system has been built to
maximize the use of proxies from existing technology, allowing a comparative approach. The

![](images/Hawker---2020---A-simplified-economic-model-for-inertial-fusion.pdf-11-1.png)

<!-- PAGE:13 -->

model seems to capture important trade-offs in the design and allows cost competitive design
points to be rapidly identified and explored.
A Monte Carlo approach and correlation analysis revealed that no single parameter is strongly
dominant. The discount rate, plant cost and target cost were found to be the most important
aspects globally, but detailed analysis revealed complex trends in some areas, more so than can
be captured in a single correlation coefficient.
One such area was the target cost, which was found to decrease in importance below a cost
threshold of roughly $10/target. Another is the required gain. This work opened with the oftcited requirement for a gain greater than 30–100 for power production for ICF [1]. The present
model extends this analysis to include the question of cost competitiveness and finds that LCOE
always benefits from higher gain. There is, however, a rough threshold beyond which further
increases in gain only delivers marginal benefit. For the mid-range default parameters used in
this study, this gain threshold is around 400. It should be noted, though, that constraining gain to
a maximum of approximately 250 still led to competitive designs, although the lowest cost points
were closed off.
Perhaps the most complex aspect identified was in the analysis of LCOE versus frequency.
This highlighted a complex relationship between optimal frequency and the fusion energy per
shot and illustrates what is, in the author’s mind, the most important conclusion of this work.
As the amount of energy per shot increases, the optimum frequency decreases. Not only does
this reduce one of the main engineering challenges of inertial fusion, it also appears to unlock a
fundamentally lower LCOE. Moreover, this type of design point does not seem to be confined
to very large plant sizes. A potential design was identified at approximately 150 MWe scale. In
this case, the engineering challenges of the wider plant are reduced due to the small size, the
engineering challenges in the centre of the plant are reduced by the low frequency, the financing
challenge is reduced again through the small size and commensurate lower initial capital cost,
and the LCOE is also very attractive.
There are of course compromises. The engineering challenge of designing a reaction vessel
to accept multi-GJ yields must be solved, and the physics challenge of high gain must also be
addressed. The design point also relies on a cheap and efficient driver design.
Regarding future study, the properties of the present model have by no means been
exhaustively explored. It is also easily extensible through the addition of more detailed submodels, for example a more detailed cost and lifetime model of a prospective driver technology,
or gain curves capturing relevant physics in a more detailed manner than those included here.
The model would also be able to facilitate like-for-like comparison of different approaches by
providing a common basis.
To conclude, there remains much to be understood about the ultimate potential of inertial
fusion to deliver cost competitive electricity, but the results presented here show that it has the
potential to be a very attractive option.

## Acknowledgements and References

Data accessibility. The source code for the work is included in the electronic supplementary material.
Competing interests. The author notes that he has a financial interest in First Light Fusion Ltd.
Funding. I received no funding for this study.
Acknowledgements. The author would like to thank Dave Chapman and Tom Clayson for reviewing the
manuscript, and Dave Chapman and David Bryon for helpful conversations whilst building the model.

References

1. Atzeni S, Meyer-ter-Vehn J. 2004 _The physics of inertial fusion: beam plasma interaction,_
_hydrodynamics, hot dense matter_ . Oxford, UK: Clarendon Press.
2. IRENA. 2019 Renewable Power Generation Costs in 2018, International Renewable Energy
Agency, Abu Dhabi.
[3. Lazard: Lazard’s Levelised Cost of Energy Analysis – Version 12. [internet]. 2018 See https://](https://www.lazard.com/media/450784/lazards-levelized-cost-of-energy-version-120-vfinal.pdf)
[www.lazard.com/media/450784/lazards-levelized-cost-of-energy-version-120-vfinal.pdf.](https://www.lazard.com/media/450784/lazards-levelized-cost-of-energy-version-120-vfinal.pdf)

~~**13**~~

<!-- PAGE:14 -->

4. Ram M, Child M, Aghahosseini A, Bogdanov D, Poleva A, Breyer C. 2017 Comparing
electricity production costs of renewables to fossil and nuclear power plants in G20
[countries. See https://www.greenpeace.de/sites/www.greenpeace.de/files/publications/](https://www.greenpeace.de/sites/www.greenpeace.de/files/publications/20170705_greenpeace_studie_comparing_electricity_costs_engl.pdf)
[20170705_greenpeace_studie_comparing_electricity_costs_engl.pdf.](https://www.greenpeace.de/sites/www.greenpeace.de/files/publications/20170705_greenpeace_studie_comparing_electricity_costs_engl.pdf)
5. Energy Transitions Commission. 2017 Low-cost, low-carbon power systems: how to develop
[competitive renewable-based power systems through flexibility. See http://www.energy-](http://www.energy-transitions.org/sites/default/files/Low-cost-low-carbon-power-systems.pdf)
[transitions.org/sites/default/files/Low-cost-low-carbon-power-systems.pdf.](http://www.energy-transitions.org/sites/default/files/Low-cost-low-carbon-power-systems.pdf)
[6. Shell. SKY SCENARIO. 2018 [internet]. See https://www.shell.com/energy-and-innovation/](https://www.shell.com/energy-and-innovation/the-energy-future/scenarios/shell-scenario-sky.html)
[the-energy-future/scenarios/shell-scenario-sky.html.](https://www.shell.com/energy-and-innovation/the-energy-future/scenarios/shell-scenario-sky.html)
[7. Energy Transitions Commission. Mission possible. [internet]. 2018 See http://www.energy-](http://www.energy-transitions.org/sites/default/files/ETC_MissionPossible_FullReport.pdf)
[transitions.org/sites/default/files/ETC_MissionPossible_FullReport.pdf.](http://www.energy-transitions.org/sites/default/files/ETC_MissionPossible_FullReport.pdf)
8. SystemIQ. 2019 Electrification and decarbonisation: the role of fusion in achieving a zero[carbon power grid. [internet]. See https://www.systemiq.earth/insights/electrification-and-](https://www.systemiq.earth/insights/electrification-and-decarbonisation/)
[decarbonisation/.](https://www.systemiq.earth/insights/electrification-and-decarbonisation/)
9. Blink JA, Hogam WJ, Hovingh J, Meier ER, Pitts JH. 1985 The high-yield lithium-injection
fusion-energy (HYLIFE) Reactor, UCRL-53559.
10. Moir RW _et al._ 1994 HYLIFE-II: a molten-salt inertial fusion energy power plant design—final
report. _Fusion Technol._ **25**, 5–25.
11. Meier WR, Bieri RL, Monsler MJ, Hendricks CD, Laybourne P, Shillito KR. 1992 OSIRIS
and SOMBRERO inertial fusion power plant designs Volume 1 Executive Summary and
Overview.
12. Anderson M _et al._ 2006 Z-inertial fusion energy: power plant final report FY 2006.
(10.2172/901970)
13. Dunne M _et al._ 2011 Timely delivery of laser inertial fusion energy (LIFE). _Fusion Science and_
_Technology_ **60** [, 19–27. (doi:10.13182/FST10-316)](http://dx.doi.org/10.13182/FST10-316)
14. HiPER project team. 2013 HiPER preparatory phase study.
15. Olson C _et al._ 2005 Development path for Z-pinch IFE. _Fusion Science and Technology._ **47**, 633–
[640. (doi:10.13182/FST05-A757)](http://dx.doi.org/10.13182/FST05-A757)
16. Steffen B. 2020 Estimating the cost of capital for renewable energy projects. _Energy Economics._
**88** [, 104783. (doi:10.1016/j.eneco.2020.104783)](http://dx.doi.org/10.1016/j.eneco.2020.104783)
[17. Office for Budget Responsibility. Discount rates. [internet]. 2011 See https://obr.uk/box/](https://obr.uk/box/discount-rates/)
[discount-rates/.](https://obr.uk/box/discount-rates/)
18. US Energy Information Administration. 2016 Capital cost estimates for utility scale electricity
generating plants.
19. Betti. 2011 Tutorial on the physics of inertial confinement fusion for energy applications. In
_3rd Meeting of the NAS panel on Inertial Fusion Energy Systems, Albuquerque, NM, March 29–_
_April 1_ .

~~**14**~~


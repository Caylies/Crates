# Overview

**Crates** is a Ballsdex package for crates, also referred to as *packs*. Crates may be opened, traded, and rewarded through time. Opening a crate rewards the user will a set amount of countryballs.

## The Problem

Packs are one of the most highly requested Ballsdex packages. However, the ecosystem for packages centered around packs is scarce. The packages that do exist for packs often contain unsafe features, unmaintained code, and heavy customizability constraints.

## Philosophy

Crates aims to be a configurable, minimalistic, and a straightfoward package. Internally, code readability and safety is highly valued.

Design choices for Crates follow three core rules:

* **Identity and control is important:** Configuration allows an application to have a stronger identity and gives the user more control.
* **Minimalism over complexity:** The package aims to be minimalistic. The user should never have to go through tedious tasks to get Crates into a state they're pleased with.
* **Documentation everywhere:** Documentation is an important aspect of a package. The user should be provided a clean, readable, and simplistic guide for inquiries on the motivation behind the package, what the package aims to solve, and its design.

### Non-Goals

* Crates does not aim to support legacy Ballsdex versions.

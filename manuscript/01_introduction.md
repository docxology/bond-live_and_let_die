# Introduction

*Live and Let Die* ({{LALD_YEAR}}) follows James Bond to the fictional Caribbean
island of San Monique, where the villain Kananga — governor by day, narcotics
baron by night — runs a poppy-to-market operation and protects his enterprise
with voodoo-coded radio traffic and a mangrove-and-crocodile coastline. This
package turns that milieu into three deterministic computation problems, each
the kind an intelligence analyst would actually run before an operation:

1. **Supply-graph analytics.** Model the narcotics chain as a capacity-constrained
   flow network and answer operational questions: what is the cheapest route to
   market, how much volume can move, and which single transit asset — if
   seized — costs the enemy the most? The answer sharpens the targeting case
   against a specific bottleneck.
2. **Coded-communiqué deciphering.** The voodoo "symbol substitution" is a
   monoalphabetic keyword cipher. Recover the substitution table and decrypt the
   intercepted message; a frequency-attack solver provides an unkeyed
   best-effort fallback.
3. **Island ops planning.** San Monique is a terrain graph of mangrove, swamp,
   open coast, and a crocodile channel. Plan the lowest-cost infiltration route
   while tracking how much of it crosses crocodile water.

Across the three modules the mission lifecycle of the BOND-API protocol
({{LALD_MISSION_PHASES}}) is exercised: a brief declares the objectives, recon
surveys the ground truth, planning schedules the analytical steps, execution
computes every result, and debriefing distils actionable lessons with full
provenance (fixed seed, canonical input hash).

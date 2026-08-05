# Introduction

*Live and Let Die* ({{LALD_YEAR}}) follows James Bond to the fictional Caribbean
island of San Monique, where the villain Kananga — governor by day, narcotics
baron by night — runs a poppy-to-market operation and protects his enterprise
with voodoo-coded radio traffic and a mangrove-and-crocodile coastline. This
package turns that milieu into {{LALD_MODULE_COUNT}} deterministic computation
problems — one pure domain module each — of the kind an intelligence analyst
would actually run before an operation:

1. **Supply-graph analytics.** Model the narcotics chain as a capacity-constrained
   flow network and answer operational questions: what is the cheapest route to
   market, how much volume can move, and which single transit asset — if
   seized — costs the enemy the most? The answer sharpens the targeting case
   against a specific bottleneck.
2. **Budgeted network interdiction.** One bottleneck is a target; a *strike
   plan* is a campaign. Given a fixed budget of legs that can be severed in one
   coordinated operation, choose the set that costs the enemy the most
   throughput — and bound the heuristic's quality with an exact optimum.
3. **Coded-communiqué deciphering.** The voodoo "symbol substitution" is a
   monoalphabetic keyword cipher. Recover the substitution table and decrypt the
   intercepted message; a frequency-attack solver provides an unkeyed
   best-effort fallback.
4. **Drum-code signalling.** The cult's drums are a channel, not set dressing.
   Encode and decode messages as Morse-timed rhythm on a per-beat grid, and
   reduce an intercepted transmission to a comparable traffic signature.
5. **Market-flow economics.** Volume is only half the operation; the other half
   is money. Propagate price and purity from the farm gate to the street to
   establish who actually captures the value — and therefore where interdiction
   bites.
6. **Island ops planning.** San Monique is a terrain graph of mangrove, swamp,
   open coast, and a crocodile channel. Plan the lowest-cost infiltration route
   while tracking how much of it crosses crocodile water.

Across all {{LALD_MODULE_COUNT}} modules the mission lifecycle of the BOND-API protocol
({{LALD_MISSION_PHASES}}) is exercised: a brief declares the
{{LALD_NUM_OBJECTIVES}} mission objectives, recon surveys the ground truth,
planning schedules the analytical steps, execution computes every result, and
debriefing distils actionable lessons with full provenance (fixed seed
{{LALD_SEED}}, canonical input hash). The same analysers are exposed as
{{LALD_GADGET_COUNT}} named gadgets so a coordinator can invoke any one of them
directly, without running the full mission.

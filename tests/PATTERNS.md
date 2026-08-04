# PATTERNS — tests

Real-data testing patterns used across this suite:

- **Known-value assertions**: lock deterministic outputs (e.g. route cost 41,
  4 crocodile cells, bottleneck airfield, ciphertext `HBKBKDB INTS TEN SKBHN AFTN`).
- **Round-trip identity**: `decipher(encipher(x, key), key) == x`;
  `from_json(to_json(outcome)) == outcome`.
- **Guard / error branches**: invalid node/edge, out-of-bounds cell, unknown
  source, unreachable goal, malformed config — asserted with `pytest.raises`.
- **Live cross-reference gate**: scan `manuscript/[0-9]*.md` and require every
  `{{TOKEN}}` to exist in `generate_variables()`.
- **Subprocess smoke**: run thin CLIs with `sys.executable` and `cwd=package_root`;
  assert exit code 0 and artifacts under `output/`.

Determinism: no RNG, no mock framework; every expected value is stable.

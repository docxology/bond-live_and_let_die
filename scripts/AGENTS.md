# AGENTS.md — scripts

Thin orchestrators only. Pattern: bootstrap `src/` onto `sys.path`, import the
relevant `live_and_let_die` module, delegate with (at most) trivial argv
shaping, `raise SystemExit(main())`. Add `# noqa: E402` on the sys.path
bootstrap import lines. No business logic here.

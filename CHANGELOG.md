# Changelog

All notable changes to this project will be documented in this file.

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/).

## [0.2.0] - 2026-05-24

The revival. The March scaffold tried to be eight things at once; this
release picks one (run agents over tasks, print a leaderboard) and ships
it as a real, working package.

### Added
- `Task`, `Agent` protocol, `FunctionAgent` adapter
- `Arena` runner that pairs every agent with every task
- `Leaderboard` aggregator with ASCII and JSON rendering
- Four built-in scorers: `exact_match`, `contains`, `keyword`, `regex`
- Three bundled fake agents and three bundled tasks for offline demos
- CLI: `agent-eval-arena demo` and `agent-eval-arena run --tasks ...`
- 61 tests covering scorers, arena execution, error capture,
  leaderboard ordering, CLI loading, bundled demo
- MIT license

### Changed
- License changed from proprietary "Officethree Technologies"
  placeholder to MIT.
- Package layout switched to `src/agent_eval_arena/` so the import path
  is `from agent_eval_arena import ...` instead of the old `from src
  import ...`.

### Removed
- ELO rating system stub (was a class with no implementation).
- FastAPI app and `/process`, `/batch`, `/history` routes (none of it
  did anything related to evaluation).
- `AgentEvalArena`, `EvalArena`, `Arena`, `EloSystem`, `Evaluator`,
  `Judges`, `Matchmaker`, `Reporter`, `Scenarios`, `LLM` stub modules.
  Each was a copy of the same template with renamed methods.
- `Health`, `requirements.txt`, `Dockerfile`, `docker-compose.yml`,
  `config.example.yaml`, `CONTRIBUTING.md`. None had a reason to exist
  in this scope.
- Roughly 1,000 lines of generated stub source and broken examples.

## [0.1.0] - 2026-03-18

Initial scaffold. Generated stub code that did not do what the README
said. See the 0.2.0 "Removed" section for what was in this release.

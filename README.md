# agent-eval-arena

A small, dependency-free arena that runs agents over a set of tasks
and prints a leaderboard.

[![tests](https://img.shields.io/badge/tests-61_passing-brightgreen)](./tests)
[![python](https://img.shields.io/badge/python-3.10%2B-blue)](./pyproject.toml)
[![license](https://img.shields.io/badge/license-MIT-blue)](./LICENSE)

## What it does

You define some tasks, you wire up some agents, you call `Arena.run()`,
and you get back ranked rows like this:

```
#  agent        total  mean  done  lat_ms  errs
-  -----------  -----  ----  ----  ------  ----
1  strong_fake  3.00   1.00  3/3   0.0     0
2  medium_fake  2.00   0.67  3/3   0.0     0
3  weak_fake    0.00   0.00  3/3   0.0     0
```

That is the entire product. There is no ELO system, no FastAPI server,
no LLM SDK glue, no judge model. Those things have been cut on purpose,
see the `CHANGELOG.md` entry for v0.2.0.

## What works

- `Task` carries a prompt, an optional expected answer, and a scorer
- `Agent` protocol; any callable with `name` and `run(task)` qualifies
- `FunctionAgent` adapter wraps a plain callable
- Four built-in scorers: `exact_match`, `contains`, `keyword`, `regex`
- `Arena.run()` produces a `Leaderboard` with per-agent rows
- CLI: `agent-eval-arena demo` and `agent-eval-arena run --tasks tasks.json`
- 3 bundled fake agents and 3 bundled tasks so the demo runs offline
- 61 tests, zero runtime dependencies

## What does not work (yet)

- No real LLM agents bundled. You bring those yourself and wrap them
  with `FunctionAgent`. There is no opinion about which SDK to use.
- No concurrency. Runs are single-threaded by design; if you need
  parallel agents wrap the calls in your own `concurrent.futures`.
- No persistent storage. The arena returns an `ArenaResult` you can
  serialize yourself with `result.to_dict()`.

## Install

From source:

```bash
git clone https://github.com/MukundaKatta/agent-eval-arena
cd agent-eval-arena
pip install -e ".[dev]"
```

## 30-second demo

```bash
agent-eval-arena demo
```

or in Python:

```python
from agent_eval_arena import Arena, FunctionAgent, Task, exact_match_scorer

tasks = [
    Task(
        task_id="capital_france",
        prompt="What is the capital of France?",
        expected="Paris",
        scorer=exact_match_scorer(),
    ),
]

agents = [
    FunctionAgent("greedy", lambda t: "Paris"),
    FunctionAgent("wrong", lambda t: "Berlin"),
]

result = Arena(agents=agents, tasks=tasks).run()
print(result.leaderboard.render_ascii())
```

## Wrap your own agent

```python
from anthropic import Anthropic

client = Anthropic()

def claude_agent(task):
    msg = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=128,
        messages=[{"role": "user", "content": task.prompt}],
    )
    return msg.content[0].text

agent = FunctionAgent("claude", claude_agent)
```

Same shape for OpenAI, Gemini, local models, regex baselines. The arena
does not care.

## Tasks from JSON

`agent-eval-arena run --tasks examples/tasks.sample.json` accepts the
shape shown in that file:

```json
[
  {
    "task_id": "capital_france",
    "prompt": "What is the capital of France?",
    "scorer": "exact",
    "expected": "Paris"
  }
]
```

Valid `scorer` values: `exact`, `contains`, `keyword`, `regex`.

## Test

```bash
pytest -v
```

## Related work

- [evalharness](https://github.com/MukundaKatta/evalharness): a larger
  sibling repo aimed at prompt, agent, and RAG-pipeline red-teaming
  plus CI testing. If you want a heavier harness with regression
  flows, look there. If you just want to print a leaderboard, this
  arena is the smaller surface.
- [`@mukundakatta/agentsnap`](https://www.npmjs.com/package/@mukundakatta/agentsnap):
  snapshot tests for agent traces (npm).
- `agenttrace-foundry` (in progress): Foundry-specific reasoning agent
  QA harness; this arena is the model-agnostic generic version.

## License

MIT

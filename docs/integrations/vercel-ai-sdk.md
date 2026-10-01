# AI SDK

[`@trustabl/ai-sdk`](https://www.npmjs.com/package/@trustabl/ai-sdk) exposes
Trustabl as a tool an [AI SDK](https://ai-sdk.dev) agent can call
mid-conversation. The agent asks for a scan, gets back what is wrong with the
repository, and can act on it in the same turn.

```sh
npm install @trustabl/ai-sdk
```

## Use with agent

```ts
import { generateText } from 'ai';
import { scanRepo } from '@trustabl/ai-sdk';

const { text } = await generateText({
  model: 'openai/gpt-5.1',
  prompt: 'Scan https://github.com/google/adk-python and summarise the three worst issues.',
  tools: { scanRepo: scanRepo() },
});

console.log(text);
```

The tool takes one argument, `path`, which is either a local directory or a
GitHub repository URL. A URL is shallow-cloned to a temporary directory and
removed when the scan exits, the same as [`trustabl scan`](../quick-start.md).

## What the model receives

A full scan of a large repository exceeds six megabytes of JSON — more than a
model can read, and more than most context windows hold. The tool returns a
summary instead.

| Field | What it holds |
|---|---|
| `sdks`, `languages` | What the repository uses, from production code only |
| `inventory` | Counts of tools, agents, subagents, skills, MCP servers |
| `score` | Overall readiness, 0 to 1 |
| `findingCount`, `bySeverity` | Every finding, counted — including those not returned |
| `findings` | Rule id, severity, title, file, line, suggested fix |
| `truncated` | `true` when findings were left out |
| `engineVersion` | The scanner release that produced the result |

`truncated` matters. Without it a model reads a capped list as the complete
picture and tells the user a repository is cleaner than it is.

The tool description instructs the model to read the inventory first. If the
tool and agent counts look wrong, the scan was pointed at the wrong place and
the findings are not worth reporting yet — the same discipline the
[CLI report](../output-formats.md) expects of a human reader.

## Options

```ts
scanRepo({
  minSeverity: 'medium',   // 'critical' | 'high' | 'medium' | 'low' | 'info'
  maxFindings: 25,
  timeoutSeconds: 300,
})
```

Findings in test paths — `tests/`, `testdata/`, `test_*.py`, `*.spec.ts` and
the rest — are excluded whatever their severity. Sample agent code vendored as
a fixture is not what the agent is being asked about.

## How the scanner is obtained

The package ships no binary. On first use it downloads the pinned Trustabl
release for the host platform, verifies it against that release's
`checksums.txt`, and caches it under `~/.cache/trustabl-ai-sdk`. Nothing is
executed before the checksum matches.

The pinned release is recorded in the package's own `package.json`, separate
from the package version, so a fix to the tool is not published as a new
scanner.

| Variable | Effect |
|---|---|
| `TRUSTABL_BIN` | Use this binary and skip the download entirely |
| `TRUSTABL_CACHE_DIR` | Where the downloaded binary is cached |

Binaries cover macOS, Linux and Windows on x64 and arm64. Windows on ARM uses
the x64 build, which runs under emulation.

## Privacy

The scan runs on the machine running your agent. There is no hosted scanner,
no account, and your source is never uploaded. The only network calls are
fetching the scanner on first use and fetching the rule pack at scan time.

## Compatibility

Verified against AI SDK `5.0.271`, `6.0.299` and `7.0.126`.

## Source

[`trustabl/ai-sdk-tool`](https://github.com/trustabl/ai-sdk-tool) — Apache-2.0.

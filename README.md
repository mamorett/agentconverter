# Agent Configuration Converter

A Python package for converting agent configuration files between **Gemini**, **OpenCode**, **Qwen**, **Kilo**, **Nanobot**, **Hermes**, and **LiteLLM ConfigMap** formats.

## Table of Contents

- [Overview](#overview)
- [Supported Formats](#supported-formats)
- [Requirements](#requirements)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Command Line Options](#command-line-options)
- [Usage Examples](#usage-examples)
- [Conversion Matrix](#conversion-matrix)
- [Format Specifications](#format-specifications)
- [Nanobot, Hermes & ConfigMap Details](#nanobot--hermes--configmap-details)
- [Package Structure](#package-structure)
- [Troubleshooting](#troubleshooting)

---

## Overview

This package converts configuration files between seven popular agent frameworks:

| Format | File Example | Primary Use |
|--------|--------------|-------------|
| **Gemini** | `gemini_settings.json` | Gemini AI agent configurations |
| **OpenCode** | `opencode.json` | OpenCode.ai configurations |
| **Qwen** | `settings.json` | Qwen Code configurations |
| **Kilo** | `kilo.json` | Kilo (OpenCode variant with permissions) |
| **Nanobot** | `nanobot_config.json` | Nanobot agent configurations |
| **Hermes** | `hermes_config.yaml` | Hermes agent configurations |
| **ConfigMap** | `config.yaml` | LiteLLM Kubernetes ConfigMap (models only) |

The converter supports:
- **Full file conversion** - Convert entire configuration files
- **Section-specific conversion** - Convert only MCP servers or models
- **Item-specific conversion** - Convert a single MCP server or model
- **Auto-detection** - Automatically detect source format
- **Diff mode** - Compare two files to find missing items

> **Note:** Nanobot, Hermes, and ConfigMap conversions are **one-way only** (from other formats → Nanobot/Hermes/ConfigMap). Conversions from these formats to other formats are not supported.

---

## Supported Formats

### MCP Servers Conversion

All formats support MCP (Model Context Protocol) servers with the following mappings:

| Format | MCP Location | Command Format | Environment |
|--------|--------------|----------------|-------------|
| **Gemini** | `mcpServers` | `command` (string) + `args` (array) | `env` (object) |
| **OpenCode** | `mcp` | `command` (array, combined) | `environment` (object) |
| **Qwen** | `mcpServers` | `command` (string) + `args` (array) | `env` (object) |
| **Kilo** | `mcp` | `command` (array, combined) | `environment` (object) |
| **Nanobot** | `tools.mcpServers` | `command` (string) + `args` (array) | `env` (object) |
| **Hermes** | `tools.mcpServers` | List of server names only | N/A |

### Models Conversion

| Format | Models Location | Notes |
|--------|-----------------|-------|
| **Gemini** | *(none)* | No models section |
| **OpenCode** | `provider.<name>.models` | Nested under providers |
| **Qwen** | `modelProviders.<provider>[]` | Array per provider |
| **Kilo** | `provider.<name>.models` | Same as OpenCode |
| **Nanobot** | `providers` + `agents.defaults` | Simplified provider config |
| **Hermes** | `model.default` + `provider` | Single default model |

---

## Requirements

- **Python 3.10+** (uses type hints with `str | None` syntax)
- No external dependencies (uses only Python standard library)

---

## Installation

1. **Clone or copy the repository:**

```bash
cd /gorgon/ia/agentconverter
```

2. **Make the script executable (optional):**

```bash
chmod +x agent_converter.py
```

3. **Verify Python version:**

```bash
python3 --version  # Should show Python 3.10 or higher
```

### Running as a Module

You can also run the package as a Python module:

```bash
python3 -m agent_converter -i input.json -t qwen
```

---

## Quick Start

### Basic Full Conversion

```bash
# Convert Gemini to Qwen
python3 agent_converter.py -i gemini_settings.json -o output.json -t qwen

# Convert OpenCode to Nanobot
python3 agent_converter.py -i opencode.json -o nanobot_output.json -t nanobot

# Convert Qwen to Hermes
python3 agent_converter.py -i settings.json -o hermes_output.json -t hermes -s qwen
```

The source format is auto-detected by default. Use `-s` to specify explicitly.

### One-Way Conversions (to Nanobot/Hermes)

```bash
# Any format → Nanobot (MCP + models)
python3 agent_converter.py -i opencode.json -t nanobot --stdout

# Any format → Hermes (MCP + models)
python3 agent_converter.py -i settings.json -t hermes --stdout -s qwen
```

---

## Command Line Options

```
usage: agent_converter.py [-h] -i INPUT -o OUTPUT -t {gemini,opencode,qwen,kilo,nanobot,hermes}
                          [-s {gemini,opencode,qwen,kilo,nanobot,hermes,auto}]
                          [--section {mcp,models}] [--mcp MCP] [--model MODEL] [--stdout]

Options:
  -i, --input INPUT       Input configuration file path (required)
  -o, --output OUTPUT     Output file path (optional - defaults to stdout)
  -t, --target TARGET     Target format: gemini, opencode, qwen, kilo, nanobot, or hermes
  -s, --source SOURCE     Source format: auto-detect or explicitly specify
  --section SECTION       Convert only a specific section: mcp or models
  --mcp MCP               Convert only a specific MCP server by name
  --model MODEL           Convert only models matching this model ID
  --stdout                Output to stdout (default behavior)
  --target-input FILE     For diff mode: second input file to compare against
  --diff                  Enable diff mode: compare source with target file
  -h, --help              Show help message
```

### Diff Mode

When `--diff` is used with `--target-input`, the script compares two files of the same format and **outputs the full missing sections** (MCP servers and/or models) that exist in the source but not in the target.

**Output is to stdout by default** - use `-o` to write to a file.

> **Note:** Diff mode is not supported for Nanobot and Hermes as they are one-way target formats only.

---

## Usage Examples

### 1. Full File Conversion

#### Auto-detect source format
```bash
python3 agent_converter.py -i gemini_settings.json -o qwen_output.json -t qwen
```

#### Explicitly specify source format
```bash
python3 agent_converter.py -i config.json -o output.json -t opencode -s qwen
```

#### Convert to Nanobot
```bash
python3 agent_converter.py -i opencode.json -o nanobot_config.json -t nanobot
```

#### Convert to Hermes
```bash
python3 agent_converter.py -i settings.json -o hermes_config.json -t hermes -s qwen
```

### 2. MCP-Only Conversion

Convert only the MCP servers section:
```bash
python3 agent_converter.py -i gemini_settings.json -o mcp_only.json -t opencode --section mcp
```

Convert MCP to Nanobot:
```bash
python3 agent_converter.py -i opencode.json -o nanobot_mcp.json -t nanobot --section mcp
```

Convert MCP to Hermes:
```bash
python3 agent_converter.py -i settings.json -o hermes_mcp.json -t hermes --section mcp -s qwen
```

### 3. Single MCP Server Conversion

Convert only a specific MCP server:
```bash
# Convert only the 'terraform' server from Gemini to Qwen
python3 agent_converter.py -i gemini_settings.json -o terraform.json -t qwen --mcp terraform

# Convert only 'mcp-camsnap' from OpenCode to Nanobot
python3 agent_converter.py -i opencode.json -o nanobot_camsnap.json -t nanobot --mcp mcp-camsnap
```

### 4. Single Model Conversion

Convert only models matching a specific ID:
```bash
# Convert only 'qwen3:14b' model from OpenCode to Qwen
python3 agent_converter.py -i opencode.json -o qwen3_model.json -t qwen --model qwen3:14b

# Convert models containing 'ollama' from Qwen to Hermes
python3 agent_converter.py -i settings.json -o hermes_ollama.json -t hermes -s qwen --model ollama

# Convert models to LiteLLM ConfigMap (YAML output)
python3 agent_converter.py -i opencode.json -o config.yaml -t configmappo --section models
```

### 5. Output to stdout

```bash
# Output conversion result to stdout
python3 agent_converter.py -i gemini_settings.json -t nanobot --stdout
```

### 6. Diff Mode - Compare Two Files

Compare two files of the same format to find and output missing MCP servers or models:

```bash
# Compare two OpenCode files (outputs to stdout)
python3 agent_converter.py -i opencode.json --target-input opencode_backup.json --diff

# Compare two Qwen files and save to file
python3 agent_converter.py -i settings.json --target-input settings_old.json --diff -o missing.json -s qwen
```

**Output format:** JSON containing the full missing sections in the source format.

**Empty output (`{}`)** means all source items exist in the target.

> **Note:** Gemini format has no models section, so only MCP servers will be compared for Gemini files.

### 7. Batch Conversion Examples

Convert all common format combinations:

```bash
# Gemini → Qwen
python3 agent_converter.py -i gemini_settings.json -o to_qwen.json -t qwen

# Gemini → Nanobot
python3 agent_converter.py -i gemini_settings.json -o to_nanobot.json -t nanobot

# OpenCode → Hermes
python3 agent_converter.py -i opencode.json -o to_hermes.json -t hermes

# Qwen → Nanobot
python3 agent_converter.py -i settings.json -o to_nanobot.json -t nanobot -s qwen

# Kilo → Nanobot
python3 agent_converter.py -i kilo.json -o to_nanobot.json -t nanobot -s kilo
```

---

## Conversion Matrix

### MCP Server Conversions (All Supported)

| From → To | Gemini | OpenCode | Qwen | Kilo | Nanobot | Hermes |
|-----------|--------|----------|------|------|---------|--------|
| **Gemini** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **OpenCode** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Qwen** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Kilo** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Nanobot** | ✗ | ✗ | ✗ | ✗ | - | - |
| **Hermes** | ✗ | ✗ | ✗ | ✗ | - | - |

> **✓** = Supported conversion
> **✗** = Not supported (one-way target only)
> **-** = Same format (no conversion needed)

### Model Conversions

| From → To | Gemini | OpenCode | Qwen | Kilo | Nanobot | Hermes |
|-----------|--------|----------|------|------|---------|--------|
| **Gemini** | N/A | ✓ (empty) | ✓ (empty) | ✓ (empty) | ✓ (empty) | ✓ (empty) |
| **OpenCode** | ✓ (empty) | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Qwen** | ✓ (empty) | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Kilo** | ✓ (empty) | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Nanobot** | ✗ | ✗ | ✗ | ✗ | - | - |
| **Hermes** | ✗ | ✗ | ✗ | ✗ | - | - |

> **Note:**
> - Gemini format does not have a models section. Conversions to Gemini for models will produce empty results.
> - Nanobot and Hermes are **one-way target formats only** - you cannot convert FROM them to other formats.

---

## Format Specifications

### Gemini Format (`gemini_settings.json`)

```json
{
  "mcpServers": {
    "server-name": {
      "command": "/path/to/command",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR": "value"
      }
    }
  },
  "security": {
    "auth": {
      "selectedType": "oauth-personal"
    }
  },
  "ui": {
    "theme": "ANSI"
  },
  "general": {
    "sessionRetention": {
      "enabled": true,
      "maxAge": "30d"
    }
  }
}
```

**Key characteristics:**
- MCP servers use `command` (string) + `args` (array)
- Environment variables in `env` object
- No models section
- Server names can have `_disabled` suffix

### OpenCode Format (`opencode.json`)

```json
{
  "$schema": "https://opencode.ai/config.json",
  "autoupdate": true,
  "mcp": {
    "server-name": {
      "command": ["/path/to/command", "arg1", "arg2"],
      "type": "local",
      "environment": {
        "ENV_VAR": "value"
      }
    }
  },
  "provider": {
    "provider-name": {
      "name": "Provider Display Name",
      "npm": "@ai-sdk/openai-compatible",
      "options": {
        "baseURL": "http://localhost:11434/v1"
      },
      "models": {
        "model-id": {
          "name": "Model Display Name",
          "modalities": {
            "input": ["text", "image"],
            "output": ["text"]
          }
        }
      }
    }
  }
}
```

**Key characteristics:**
- MCP uses `command` as array (command + args combined)
- Environment in `environment` object
- Models nested under `provider.<name>.models`
- Uses `baseURL` (camelCase)

### Qwen Format (`settings.json`)

```json
{
  "$version": 3,
  "env": {
    "API_KEY_NAME": "default-value"
  },
  "mcpServers": {
    "server-name": {
      "command": "/path/to/command",
      "args": ["arg1", "arg2"],
      "env": {
        "ENV_VAR": "value"
      }
    }
  },
  "modelProviders": {
    "openai": [
      {
        "id": "model-id",
        "name": "Model Display Name",
        "envKey": "API_KEY_NAME",
        "baseUrl": "http://localhost:11434/v1",
        "generationConfig": {
          "modalities": {
            "image": true
          }
        }
      }
    ]
  },
  "model": {
    "name": "selected-model-id"
  },
  "security": {
    "auth": {
      "selectedType": "openai"
    }
  }
}
```

**Key characteristics:**
- MCP uses `command` (string) + `args` (array)
- Global `env` section for API keys
- Models as array under `modelProviders.<provider>`
- Uses `baseUrl` (camelCase)
- Image modalities as boolean in `generationConfig`

### Kilo Format (`kilo.json`)

Kilo format is **identical to OpenCode** but includes a `permission` section:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "autoupdate": true,
  "permission": {
    "bash": "allow"
  },
  "mcp": { ... },
  "provider": { ... }
}
```

### Nanobot Format (`nanobot_config.json`)

```json
{
  "agents": {
    "defaults": {
      "workspace": "~/.nanobot/workspace",
      "model": "provider/default",
      "maxTokens": 110000,
      "temperature": 0.7,
      "maxToolIterations": 20,
      "memoryWindow": 50
    }
  },
  "providers": {
    "provider-name": {
      "apiKey": "",
      "apiBase": "http://localhost:11434/v1",
      "extraHeaders": null
    }
  },
  "tools": {
    "mcpServers": {
      "server-name": {
        "command": "/path/to/command",
        "args": ["arg1", "arg2"],
        "env": {
          "ENV_VAR": "value"
        }
      }
    }
  },
  "gateway": {
    "host": "0.0.0.0",
    "port": 18790
  }
}
```

**Conversion output includes:**
- `tools.mcpServers` - MCP servers from source
- `providers` - Simplified provider configuration (apiKey, apiBase, extraHeaders)
- `agents.defaults` - Default agent settings with first provider as model

> **Note:** API keys are set to empty strings - you must fill them in manually.

### Hermes Format (`hermes_config.yaml`)

```yaml
model:
  default: provider/model-id
provider: provider-name
toolsets:
  - all
agent:
  max_turns: 60
  verbose: false
  reasoning_effort: medium
tools:
  mcpServers:
    - server-name-1
    - server-name-2
```

**Conversion output includes:**
- `tools.mcpServers` - List of MCP server names (not full config)
- `model.default` - First available model from source
- `provider` - Provider name
- `toolsets` - Set to `["all"]`
- `agent` - Default agent settings

> **Note:** Hermes MCP format is a simple list of server names, not full server configurations.

---

## Nanobot & Hermes Details

### One-Way Conversion

Nanobot and Hermes are **target-only formats**. You can convert FROM any format TO Nanobot or Hermes, but NOT the reverse.

**Supported conversions:**
- Gemini → Nanobot ✓
- Gemini → Hermes ✓
- OpenCode → Nanobot ✓
- OpenCode → Hermes ✓
- Qwen → Nanobot ✓
- Qwen → Hermes ✓
- Kilo → Nanobot ✓
- Kilo → Hermes ✓

**Not supported:**
- Nanobot → Any format ✗
- Hermes → Any format ✗

### MCP Conversion Differences

| Feature | Nanobot | Hermes |
|---------|---------|--------|
| Format | Full server config (command, args, env) | Simple list of server names |
| Environment | Preserved | Not applicable |
| Use case | Direct config migration | Enable/disable server list |

### Model Conversion Differences

| Feature | Nanobot | Hermes |
|---------|---------|--------|
| Format | `providers` dict + `agents.defaults` | `model.default` + `provider` string |
| Multiple providers | All preserved | First model used as default |
| API keys | Empty placeholders | Not included |

---

## Package Structure

The code is organized as a modular Python package:

```
agent_converter/
├── __init__.py              # Package initialization
├── __main__.py              # Entry point for `python -m agent_converter`
├── cli.py                   # CLI argument parsing and main entry point
├── conversion_orchestrator.py  # Main conversion logic
├── diff.py                  # Diff comparison functions
├── format_detection.py      # Format detection utilities
├── utils.py                 # File I/O and helper functions
├── mcp_converters/          # MCP format converters
│   ├── __init__.py
│   ├── gemini.py
│   ├── opencode.py
│   ├── qwen.py
│   ├── kilo.py
│   ├── nanobot.py
│   └── hermes.py
└── model_converters/        # Model format converters
    ├── __init__.py
    ├── gemini.py
    ├── opencode.py
    ├── qwen.py
    ├── kilo.py
    ├── nanobot.py
    └── hermes.py
```

Each format has its own converter module, making it easy to:
- Add support for new formats
- Test individual converters
- Maintain format-specific logic

---

## Troubleshooting

### Common Issues

#### "Could not detect source format"
**Solution:** Use `-s` to explicitly specify the source format:
```bash
python3 agent_converter.py -i config.json -o output.json -t nanobot -s opencode
```

#### "Input file not found"
**Solution:** Verify the input file path is correct:
```bash
ls -la gemini_settings.json
```

#### Empty output for models conversion to Gemini
**Expected behavior:** Gemini format has no models section. This is normal.

#### MCP servers missing in output
**Check:** Ensure the source file has the correct structure. Use `--section mcp` if needed.

#### "Unknown target format"
**Solution:** Ensure you're using a valid target: `gemini`, `opencode`, `qwen`, `kilo`, `nanobot`, or `hermes`.

### Debug Tips

1. **Check detected format:**
```bash
python3 agent_converter.py -i config.json -t qwen 2>&1 | grep "Detected"
```

2. **Preview conversion to stdout:**
```bash
python3 agent_converter.py -i config.json -t nanobot --stdout | head -50
```

3. **Convert specific items to verify:**
```bash
python3 agent_converter.py -i config.json -t hermes --mcp terraform --stdout
```

---

## Examples: Real-World Conversions

### Example 1: Migrating from Gemini to Nanobot

```bash
# Full conversion
python3 agent_converter.py -i ~/.gemini/gemini_settings.json -o ~/.nanobot/config.json -t nanobot

# Verify the output
cat ~/.nanobot/config.json
```

### Example 2: Extracting Only MCP Servers for Hermes

```bash
# Get only MCP servers from OpenCode in Hermes format
python3 agent_converter.py -i opencode.json -o hermes_mcp.json -t hermes --section mcp
```

### Example 3: Creating a Minimal Nanobot Config

```bash
# Convert only specific servers
python3 agent_converter.py -i gemini_settings.json -o minimal_nanobot.json -t nanobot --mcp terraform
```

### Example 4: Converting Qwen Models to Hermes

```bash
# Extract models from Qwen config for Hermes
python3 agent_converter.py -i settings.json -o hermes_models.json -t hermes --section models -s qwen
```

---

## License

This script is provided as-is for converting between agent configuration formats.

---

## Author

Created for converting between Gemini, OpenCode, Qwen, Kilo, Nanobot, and Hermes agent configurations.

"""
Command-line interface for the agent configuration converter.
"""

import argparse
import json
import sys
from typing import Any

from .format_detection import detect_format
from .conversion_orchestrator import convert_full_file, convert_section_only
from .diff import compute_mcp_diff_full, compute_model_diff_full
from .utils import load_json_file

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class FriendlyArgumentParser(argparse.ArgumentParser):
    """Custom ArgumentParser that shows full help when errors occur."""
    def error(self, message):
        sys.stderr.write(f"Error: {message}\n\n")
        self.print_help()
        sys.exit(2)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments with clear and structured help."""
    parser = FriendlyArgumentParser(
        description="Convert agent configuration files between different formats (Gemini, OpenCode, Qwen, Kilo, Nanobot, Hermes, ConfigMap, Vibe).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Modes of Operation:
  1. Conversion Mode:
     Convert configuration file from one format to another.
     Example:
       python3 agent_converter.py --input gemini_settings.json --target vibe --output config.toml

  2. Filtered Conversion Mode:
     Convert only specific parts (e.g. only MCP servers or specific models).
     Example:
       python3 agent_converter.py --input opencode.json --target qwen --section mcp
       python3 agent_converter.py --input settings.json --target hermes --model ollama

  3. Diff Mode:
     Compare two files of the same format and output the missing items (source vs target-input).
     Example:
       python3 agent_converter.py --input file1.json --target-input file2.json --diff
"""
    )

    # Custom groups for better layout
    required = parser.add_argument_group("Required Arguments")
    required.add_argument(
        "-i", "--input",
        required=True,
        metavar="PATH",
        help="Path to the input configuration file"
    )

    conversion = parser.add_argument_group("Conversion Options")
    conversion.add_argument(
        "-t", "--target",
        metavar="FORMAT",
        choices=["gemini", "opencode", "qwen", "kilo", "nanobot", "hermes", "configmappo", "vibe"],
        help="Target format to convert into. Supported: gemini, opencode, qwen, kilo, nanobot, hermes, configmappo, vibe"
    )
    conversion.add_argument(
        "-s", "--source",
        metavar="FORMAT",
        default="auto",
        choices=["gemini", "opencode", "qwen", "kilo", "nanobot", "hermes", "configmappo", "auto"],
        help="Source format. If set to 'auto' (default), the tool automatically detects the input format"
    )

    filtering = parser.add_argument_group("Filtering / Partial Conversion Options")
    filtering.add_argument(
        "--section",
        metavar="SECTION",
        choices=["mcp", "models"],
        help="Convert only a specific section: 'mcp' or 'models'"
    )
    filtering.add_argument(
        "--mcp",
        metavar="NAME",
        help="Convert only a specific MCP server by its name"
    )
    filtering.add_argument(
        "--model",
        metavar="ID",
        help="Convert only models matching this model ID"
    )

    output = parser.add_argument_group("Output Options")
    output.add_argument(
        "-o", "--output",
        metavar="PATH",
        help="Path to write the output file. If omitted, prints to stdout"
    )
    output.add_argument(
        "--stdout",
        action="store_true",
        help="Force printing output to stdout even if --output is specified"
    )

    diff = parser.add_argument_group("Diff / Comparison Options")
    diff.add_argument(
        "--diff",
        action="store_true",
        help="Enable diff mode to find items missing in --target-input compared to --input"
    )
    diff.add_argument(
        "--target-input",
        metavar="PATH",
        help="The second configuration file to compare against (used only in --diff mode)"
    )

    # Show help and exit if no arguments are provided
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    return parser.parse_args()


def run_diff_mode(args: argparse.Namespace) -> int:
    """Run diff mode - compare source with target file."""
    if not args.target_input:
        print("Error: --diff requires --target-input to specify the comparison file", file=sys.stderr)
        return 1
    
    # Load input file
    try:
        data = load_json_file(args.input)
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        return 1
    
    # Load target file
    try:
        target_data = load_json_file(args.target_input)
    except FileNotFoundError:
        print(f"Error: Target input file not found: {args.target_input}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in target input file: {e}", file=sys.stderr)
        return 1
    
    # Detect formats
    source_format = args.source if args.source != "auto" else detect_format(data)
    if source_format == "unknown":
        print("Error: Could not detect source format. Use -s to specify explicitly.", file=sys.stderr)
        return 1
    
    target_file_format = detect_format(target_data)
    if target_file_format == "unknown":
        print("Error: Could not detect target file format.", file=sys.stderr)
        return 1
    
    # Compute diffs - get full missing sections
    mcp_missing = compute_mcp_diff_full(data, target_data, source_format, target_file_format)
    model_missing = compute_model_diff_full(data, target_data, source_format, target_file_format)
    
    # Build output based on source format
    if source_format == "gemini":
        result = {}
        if mcp_missing:
            result["mcpServers"] = mcp_missing
    elif source_format == "opencode":
        result = {}
        if mcp_missing:
            result["mcp"] = mcp_missing
        if model_missing:
            # Reconstruct provider structure with only missing models
            result["provider"] = {}
            for provider_name, models_dict in model_missing.items():
                result["provider"][provider_name] = {"models": models_dict}
    elif source_format == "kilo":
        result = {}
        if mcp_missing:
            result["mcp"] = mcp_missing
        if model_missing:
            # Reconstruct provider structure with only missing models
            result["provider"] = {}
            for provider_name, models_dict in model_missing.items():
                result["provider"][provider_name] = {"models": models_dict}
    elif source_format == "qwen":
        result = {}
        if mcp_missing:
            result["mcpServers"] = mcp_missing
        if model_missing:
            result["modelProviders"] = model_missing
    
    # Output result
    output_json = json.dumps(result, indent=2)
    
    # Default to stdout, write to file only if -o is specified
    if args.stdout or not args.output:
        print(output_json)
    else:
        try:
            with open(args.output, "w") as f:
                f.write(output_json)
            print(f"Diff output written to: {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            return 1
    
    return 0


def run_conversion_mode(args: argparse.Namespace) -> int:
    """Run conversion mode - convert file from source to target format."""
    # Require -t/--target for conversion mode
    if not args.target:
        print("Error: -t/--target is required for conversion mode", file=sys.stderr)
        return 1
    
    # Load input file
    try:
        data = load_json_file(args.input)
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
        return 1
    
    target_format = args.target
    
    # Detect or use specified source format
    source_format = args.source
    if source_format == "auto":
        source_format = detect_format(data)
        if source_format == "unknown":
            print("Error: Could not detect source format. Use -s to specify explicitly.", file=sys.stderr)
            return 1
        print(f"Detected source format: {source_format}", file=sys.stderr)
    
    # Perform conversion
    try:
        if args.section or args.mcp or args.model:
            # Section-specific conversion
            if args.mcp:
                args.section = "mcp"
            if args.model:
                args.section = "models"
            
            result = convert_section_only(
                data, source_format, target_format,
                args.section,
                args.mcp or args.model
            )
        else:
            # Full file conversion
            result = convert_full_file(data, source_format, target_format)
    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        return 1

    # Output result
    # Hermes and ConfigMap formats use YAML, vibe uses TOML, others use JSON
    if target_format == "vibe":
        output_json = result
    elif target_format in ["hermes", "configmappo"]:
        if YAML_AVAILABLE:
            # For configmappo, result is already a YAML string
            if target_format == "configmappo" and isinstance(result, str):
                output_json = result
            else:
                output_json = yaml.dump(result, default_flow_style=False, sort_keys=False, allow_unicode=True)
        else:
            print("Warning: PyYAML not installed, falling back to JSON output", file=sys.stderr)
            output_json = json.dumps(result, indent=2)
    else:
        output_json = json.dumps(result, indent=2)

    # Default to stdout, write to file only if -o is specified
    if args.stdout or not args.output:
        print(output_json)
    else:
        try:
            # For Hermes, ConfigMap, and Vibe, write string directly instead of using save_json_file
            if target_format in ["hermes", "configmappo", "vibe"]:
                with open(args.output, "w") as f:
                    f.write(output_json)
            else:
                from .utils import save_json_file
                save_json_file(result, args.output)
            print(f"Conversion complete. Output written to: {args.output}", file=sys.stderr)
        except Exception as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            return 1

    return 0


def main() -> int:
    """Main entry point."""
    args = parse_args()
    
    # Diff mode
    if args.diff:
        return run_diff_mode(args)
    
    # Conversion mode
    return run_conversion_mode(args)

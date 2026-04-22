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


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert agent configuration between Gemini, OpenCode, Qwen, and Kilo formats.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Convert full file:
    %(prog)s -i gemini_settings.json -o output.json -t qwen

  Convert only MCP section:
    %(prog)s -i gemini_settings.json -o output.json -t opencode --section mcp

  Convert specific MCP server:
    %(prog)s -i gemini_settings.json -o output.json -t qwen --mcp github

  Convert specific model:
    %(prog)s -i opencode.json -o output.json -t qwen --model qwen3:14b

  Auto-detect source format:
    %(prog)s -i config.json -o output.json -t gemini

  Specify source format explicitly:
    %(prog)s -i config.json -o output.json -t qwen -s opencode

  Diff mode - compare two files of same format:
    %(prog)s -i file1.json --target-input file2.json --diff -s qwen -o diff_report.txt

  Diff mode with auto-detection:
    %(prog)s -i opencode.json --target-input opencode_backup.json --diff
        """
    )
    
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Input configuration file path"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output file path (optional - defaults to stdout)"
    )
    
    parser.add_argument(
        "-t", "--target",
        choices=["gemini", "opencode", "qwen", "kilo", "nanobot", "hermes"],
        help="Target format (required unless using --diff)"
    )
    
    parser.add_argument(
        "-s", "--source",
        choices=["gemini", "opencode", "qwen", "kilo", "nanobot", "hermes", "auto"],
        default="auto",
        help="Source format (default: auto-detect)"
    )
    
    parser.add_argument(
        "--section",
        choices=["mcp", "models"],
        help="Convert only a specific section (mcp or models)"
    )
    
    parser.add_argument(
        "--mcp",
        help="Convert only a specific MCP server by name"
    )
    
    parser.add_argument(
        "--model",
        help="Convert only models matching this model ID"
    )
    
    parser.add_argument(
        "--stdout",
        action="store_true",
        help="Output to stdout instead of file"
    )
    
    parser.add_argument(
        "--target-input",
        help="For diff mode: second input file to compare against (source vs target)"
    )
    
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Diff mode: compare source with target input file (when formats are the same)"
    )
    
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
    output_json = json.dumps(result, indent=2)
    
    # Default to stdout, write to file only if -o is specified
    if args.stdout or not args.output:
        print(output_json)
    else:
        try:
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

"""Command-line interface for TOON format conversion."""
import sys
import json
import argparse
from pathlib import Path
from typing import Optional

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False

try:
    from .kaggle import (
        is_kaggle_slug,
        download_dataset,
        find_best_csv,
        csv_to_records,
        parse_croissant,
        croissant_to_summary,
    )
    KAGGLE_AVAILABLE = True
except ImportError:
    KAGGLE_AVAILABLE = False

from . import encode, decode


def count_tokens(text: str) -> Optional[int]:
    """
    Count tokens in text using tiktoken (o200k_base encoding).
    
    Args:
        text: Text to count tokens in
        
    Returns:
        Token count or None if tiktoken not available
    """
    if not TIKTOKEN_AVAILABLE:
        return None
    
    try:
        encoding = tiktoken.get_encoding("o200k_base")
        return len(encoding.encode(text))
    except Exception:
        return None


def detect_mode(input_path: Optional[str], force_encode: bool, force_decode: bool) -> str:
    """
    Detect conversion mode from file extension or flags.
    
    Args:
        input_path: Input file path
        force_encode: Force encode mode
        force_decode: Force decode mode
        
    Returns:
        'encode' or 'decode'
    """
    if force_encode:
        return 'encode'
    if force_decode:
        return 'decode'
    
    if input_path and input_path != '-':
        path = Path(input_path)
        ext = path.suffix.lower()
        if ext == '.json':
            return 'encode'
        elif ext == '.toon':
            return 'decode'
    
    # Default to encode
    return 'encode'


def read_input(input_path: Optional[str]) -> str:
    """
    Read input from file or stdin.
    
    Args:
        input_path: Input file path or '-' for stdin
        
    Returns:
        Input content
    """
    if not input_path or input_path == '-':
        return sys.stdin.read()
    
    with open(input_path, 'r', encoding='utf-8') as f:
        return f.read()


def write_output(content: str, output_path: Optional[str]) -> None:
    """
    Write output to file or stdout.
    
    Args:
        content: Content to write
        output_path: Output file path or None for stdout
    """
    if not output_path:
        print(content)
    else:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='TOON (Token-Oriented Object Notation) - Convert between JSON and TOON formats',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Encode JSON file to TOON
  toon input.json -o output.toon

  # Decode TOON file to JSON
  toon input.toon -o output.json

  # Pipe JSON and encode to TOON
  echo '{"key": "value"}' | toon -e

  # Force decode mode with custom delimiter
  toon input.txt -d --delimiter tab

  # Show token statistics
  toon input.json --stats

  # Download Kaggle dataset and convert to TOON
  toon username/dataset-name --kaggle --stats

  # Select specific file from Kaggle dataset
  toon username/dataset-name --kaggle --file data.csv

  # Parse Croissant metadata to see dataset schema
  toon metadata.json --croissant
        """
    )
    
    parser.add_argument(
        'input',
        nargs='?',
        help='Input file path (or "-" for stdin, default: stdin)'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: stdout)'
    )
    parser.add_argument(
        '-e', '--encode',
        action='store_true',
        help='Force encode mode (JSON to TOON)'
    )
    parser.add_argument(
        '-d', '--decode',
        action='store_true',
        help='Force decode mode (TOON to JSON)'
    )
    parser.add_argument(
        '--delimiter',
        choices=['comma', 'tab', 'pipe'],
        default='comma',
        help='Array delimiter (default: comma)'
    )
    parser.add_argument(
        '--indent',
        type=int,
        default=2,
        help='Indentation size (default: 2)'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show token statistics'
    )
    parser.add_argument(
        '--no-strict',
        action='store_true',
        help='Disable strict validation (decode only)'
    )
    parser.add_argument(
        '--key-folding',
        choices=['off', 'safe'],
        default='off',
        help='Key folding mode (encode only, default: off)'
    )
    parser.add_argument(
        '--flatten-depth',
        type=int,
        help='Maximum key folding depth (encode only)'
    )
    parser.add_argument(
        '--expand-paths',
        choices=['off', 'safe'],
        default='off',
        help='Path expansion mode (decode only, default: off)'
    )
    parser.add_argument(
        '--kaggle',
        action='store_true',
        help='Treat input as Kaggle dataset slug (e.g., username/dataset-name)'
    )
    parser.add_argument(
        '--croissant',
        action='store_true',
        help='Parse input as Croissant (ML Commons) metadata and show schema'
    )
    parser.add_argument(
        '--file', '-f',
        dest='select_file',
        help='Select specific file from Kaggle dataset (use with --kaggle)'
    )

    args = parser.parse_args()
    
    # Validate arguments
    if args.encode and args.decode:
        parser.error('Cannot specify both --encode and --decode')

    # Handle Kaggle dataset download
    if args.kaggle or (KAGGLE_AVAILABLE and args.input and is_kaggle_slug(args.input)):
        if not KAGGLE_AVAILABLE:
            print('Error: Kaggle support requires the kaggle package. '
                  'Install with: pip install kaggle', file=sys.stderr)
            return 1

        try:
            print(f'Downloading Kaggle dataset: {args.input}', file=sys.stderr)
            files = download_dataset(args.input)

            # Find the target file
            if args.select_file:
                target = next(
                    (f for f in files if args.select_file in f.name),
                    None
                )
                if not target:
                    print(f'Error: No file matching "{args.select_file}" in dataset',
                          file=sys.stderr)
                    print(f'Available files: {[f.name for f in files]}', file=sys.stderr)
                    return 1
            else:
                target = find_best_csv(files)
                if not target:
                    # Try JSON files
                    json_files = [f for f in files if f.suffix.lower() == '.json']
                    target = json_files[0] if json_files else None

                if not target:
                    print('Error: No CSV or JSON files found in dataset', file=sys.stderr)
                    return 1

            print(f'Using: {target.name}', file=sys.stderr)

            # Read and convert
            content = target.read_text(encoding='utf-8', errors='replace')

            if target.suffix.lower() == '.csv':
                data = csv_to_records(content)
            else:
                data = json.loads(content)

            # Encode to TOON
            options = {
                'delimiter': args.delimiter,
                'indent': args.indent,
                'key_folding': args.key_folding,
            }
            if args.flatten_depth is not None:
                options['flatten_depth'] = args.flatten_depth

            output_content = encode(data, options)
            input_content = json.dumps(data)  # For stats comparison

            # Show statistics if requested
            if args.stats:
                input_tokens = count_tokens(input_content)
                output_tokens = count_tokens(output_content)

                print(f'Input (JSON):  {len(input_content)} bytes', file=sys.stderr)
                print(f'Output (TOON): {len(output_content)} bytes', file=sys.stderr)
                if len(input_content) > 0:
                    print(f'Size reduction: {(1 - len(output_content) / len(input_content)) * 100:.1f}%',
                          file=sys.stderr)

                if input_tokens is not None and output_tokens is not None:
                    print(f'Input tokens:  {input_tokens}', file=sys.stderr)
                    print(f'Output tokens: {output_tokens}', file=sys.stderr)
                    print(f'Token reduction: {(1 - output_tokens / input_tokens) * 100:.1f}%',
                          file=sys.stderr)
                else:
                    print('(Install tiktoken for token statistics)', file=sys.stderr)

                print('---', file=sys.stderr)

            write_output(output_content, args.output)
            return 0

        except Exception as e:
            print(f'Error: {e}', file=sys.stderr)
            return 1

    # Handle Croissant metadata parsing
    if args.croissant:
        if not KAGGLE_AVAILABLE:
            print('Error: Croissant support requires the kaggle module.', file=sys.stderr)
            return 1

        try:
            input_content = read_input(args.input)
            metadata = json.loads(input_content)
            info = parse_croissant(metadata)
            output_content = croissant_to_summary(info)

            print(f'Dataset: {info["name"]}', file=sys.stderr)
            print(f'Files: {[f["name"] for f in info["files"]]}', file=sys.stderr)

            write_output(output_content, args.output)
            return 0

        except Exception as e:
            print(f'Error parsing Croissant metadata: {e}', file=sys.stderr)
            return 1

    try:
        # Read input
        input_content = read_input(args.input)
        
        # Detect mode
        mode = detect_mode(args.input, args.encode, args.decode)
        
        # Convert
        if mode == 'encode':
            # Parse JSON
            data = json.loads(input_content)
            
            # Encode to TOON
            options = {
                'delimiter': args.delimiter,
                'indent': args.indent,
                'key_folding': args.key_folding,
            }
            if args.flatten_depth is not None:
                options['flatten_depth'] = args.flatten_depth
            
            output_content = encode(data, options)
            
            # Show statistics if requested
            if args.stats:
                input_tokens = count_tokens(input_content)
                output_tokens = count_tokens(output_content)
                
                print(f'Input (JSON):  {len(input_content)} bytes', file=sys.stderr)
                print(f'Output (TOON): {len(output_content)} bytes', file=sys.stderr)
                print(f'Size reduction: {(1 - len(output_content) / len(input_content)) * 100:.1f}%', file=sys.stderr)
                
                if input_tokens is not None and output_tokens is not None:
                    print(f'Input tokens:  {input_tokens}', file=sys.stderr)
                    print(f'Output tokens: {output_tokens}', file=sys.stderr)
                    print(f'Token reduction: {(1 - output_tokens / input_tokens) * 100:.1f}%', file=sys.stderr)
                else:
                    print('(Install tiktoken for token statistics)', file=sys.stderr)
                
                print('---', file=sys.stderr)
        
        else:  # decode
            # Decode TOON
            options = {
                'strict': not args.no_strict,
                'expand_paths': args.expand_paths,
                'default_delimiter': args.delimiter,
            }
            
            data = decode(input_content, options)
            
            # Convert to JSON
            output_content = json.dumps(data, indent=2, ensure_ascii=False)
            
            # Show statistics if requested
            if args.stats:
                input_tokens = count_tokens(input_content)
                output_tokens = count_tokens(output_content)
                
                print(f'Input (TOON): {len(input_content)} bytes', file=sys.stderr)
                print(f'Output (JSON): {len(output_content)} bytes', file=sys.stderr)
                print(f'Size increase: {(len(output_content) / len(input_content) - 1) * 100:.1f}%', file=sys.stderr)
                
                if input_tokens is not None and output_tokens is not None:
                    print(f'Input tokens:  {input_tokens}', file=sys.stderr)
                    print(f'Output tokens: {output_tokens}', file=sys.stderr)
                    print(f'Token increase: {(output_tokens / input_tokens - 1) * 100:.1f}%', file=sys.stderr)
                else:
                    print('(Install tiktoken for token statistics)', file=sys.stderr)
                
                print('---', file=sys.stderr)
        
        # Write output
        write_output(output_content, args.output)
        
        return 0
    
    except json.JSONDecodeError as e:
        print(f'Error parsing JSON: {e}', file=sys.stderr)
        return 1
    except FileNotFoundError as e:
        print(f'Error: {e}', file=sys.stderr)
        return 1
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""
DU Improved - Disk Usage Improved
A more versatile version of the 'du' command that displays disk usage statistics
with customizable bar graphs and human-readable sizes.
"""

import subprocess
import argparse
import sys
import os

def call_du_sub(target_directory):
    """
    Calls the 'du -d 1' command on the target directory and returns a list of strings.
    :param target_directory: Path to the directory.
    :return: List of strings representing du output.
    """
    try:
        process = subprocess.Popen(
            ['du', '-d', '1', target_directory],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,  # Suppress permission denied errors
            text=True
        )
        stdout, _ = process.communicate()
        return [line.strip() for line in stdout.split('\n') if line.strip()]
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

def percent_to_graph(percent, total_chars):
    """
    Converts a percentage into a graphical bar.
    :param percent: Percentage (0-100).
    :param total_chars: Total length of the bar.
    :return: Graphical bar as a string.
    """
    if not (0 <= percent <= 100):
        raise ValueError("Percent must be between 0 and 100.")
    filled_length = round((percent / 100) * total_chars)
    return '=' * filled_length + ' ' * (total_chars - filled_length)

def create_dir_dict(du_output):
    """
    Creates a dictionary from the du output.
    :param du_output: List of strings from 'du -d 1'.
    :return: Dictionary with directory names as keys and sizes in KB as values.
    """
    dir_dict = {}
    for line in du_output:
        parts = line.split('\t')
        if len(parts) == 2:
            size, directory = parts
            dir_dict[directory] = int(size)
    return dir_dict

def parse_command_args():
    """
    Parses command-line arguments.
    :return: Parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="DU Improved -- See Disk Usage Report with bar charts",
        epilog="Copyright 202X"
    )
    parser.add_argument(
        "target", nargs="?", default=".", 
        help="The directory to scan."
    )
    parser.add_argument(
        "-H", "--human-readable", action="store_true",
        help="Print sizes in human-readable format (e.g., 1K, 23M, 2G)."
    )
    parser.add_argument(
        "-l", "--length", type=int, default=20,
        help="Specify the length of the graph. Default is 20."
    )
    return parser.parse_args()

def human_readable(size_kb):
    """
    Converts size in KB to human-readable format.
    :param size_kb: Size in kilobytes.
    :return: Human-readable string.
    """
    size_bytes = size_kb * 1024
    for unit in ['B', 'K', 'M', 'G', 'T']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} P"

def main():
    args = parse_command_args()
    
    if not os.path.isdir(args.target):
        print(f"Error: {args.target} is not a valid directory", file=sys.stderr)
        sys.exit(1)
    
    du_output = call_du_sub(args.target)
    dir_dict = create_dir_dict(du_output)
    
    if not dir_dict:
        print("No subdirectories found.", file=sys.stderr)
        sys.exit(0)
    
    # Get total size (removing the target directory itself)
    total_size = dir_dict.pop(args.target, 0)
    
    # Sort by size (descending)
    sorted_dirs = sorted(
        dir_dict.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    # Print results
    for directory, size in sorted_dirs:
        percent = (size / total_size) * 100 if total_size > 0 else 0
        bar = percent_to_graph(percent, args.length)
        size_str = human_readable(size) if args.human_readable else f"{size}K"
        print(f"{percent:>3.0f} % [{bar}] {size_str:>8}  {directory}")
    
    # Print total
    total_str = human_readable(total_size) if args.human_readable else f"{total_size}K"
    print(f"Total: {total_str}   {args.target}")

if __name__ == "__main__":
    main()
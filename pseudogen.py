#!/usr/bin/env python3

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

def read_source_file(file_path):
    """Read the contents of the source file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

def generate_pseudocode(source_code, api_key):
    """Generate pseudocode using OpenAI's GPT model."""
    if not api_key:
        print("Error: OpenAI API key not found. Please set it in .env file.", 
              file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", 
                 "content": "You are a helpful assistant that converts source "
                           "code into clear, readable pseudocode."},
                {"role": "user", 
                 "content": f"Convert the following code into pseudocode. Use "
                           f"clear, concise language and maintain the logical "
                           f"structure:\n\n{source_code}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating pseudocode: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(
        description='Generate pseudocode from source code using LLM'
    )
    parser.add_argument('source_file', type=str, 
                       help='Path to the source code file')
    parser.add_argument('--output', '-o', type=str,
                       help='Output file path (optional, defaults to stdout)')
    args = parser.parse_args()

    # Get API key from environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    
    # Read source file
    source_code = read_source_file(args.source_file)
    
    # Generate pseudocode
    pseudocode = generate_pseudocode(source_code, api_key)
    
    # Output results
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(pseudocode)
        except Exception as e:
            print(f"Error writing to output file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(pseudocode)

if __name__ == '__main__':
    main() 
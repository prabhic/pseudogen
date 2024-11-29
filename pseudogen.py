#!/usr/bin/env python3

import argparse
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import requests
import tiktoken
import logging
from typing import List

# Set up logging configuration
def setup_logging(level: str) -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )

# Load environment variables from .env file
load_dotenv()

# Available models
AVAILABLE_MODELS = {
    "gpt-3.5-turbo-1106": "GPT-3.5 Turbo (Latest) - Fast and cost-effective",
    "gpt-4-1106-preview": "GPT-4 Turbo (Latest) - Most capable and up-to-date model",
    "gpt-4": "GPT-4 (Standard) - Highly capable model with 8k context",
    "gpt-4-32k": "GPT-4 32k - Extended context version of GPT-4",
    "gpt-4o": "GPT-4o - Optimized version of GPT-4",
    "o1-mini": "O1 Mini - Lightweight model for quick tasks",
    "o1-preview": "O1 Preview - Preview version of the O1 model"
}

MAX_TOKENS = 4096  # Define a reasonable token threshold


ABSTRACTION_LEVELS = {
    0: {
        "system_message": (
            "You are a system architect specialized in high-level software design. "
            "Your role is to analyze code and identify the fundamental architectural patterns and components. "
            "Follow these guidelines:\n"
            "1. Identify only the 2-3 most essential components/classes that form the core architecture\n"
            "2. Focus on system-level interactions and dependencies between these components\n"
            "3. Use architectural pattern terminology where applicable (e.g., Client-Server, MVC, Pub-Sub)\n"
            "4. Describe component responsibilities at a system level\n"
            "5. Highlight key architectural decisions and their implications\n"
            "6. Omit all implementation details, method names, and specific code elements\n\n"
            "Your output should help stakeholders understand the system's fundamental building blocks "
            "and their relationships without any technical implementation details."
        ),
        "user_message": (
            "Analyze this code from a system architecture perspective. Provide:\n"
            "1. The 2-3 most fundamental components that form the core architecture\n"
            "2. Their primary responsibilities at a system level\n"
            "3. Key interactions between these components\n"
            "4. The overall architectural pattern (if identifiable)\n\n"
            "Code to analyze:\n\n{chunk}"
        )
    },
    1: {
        "system_message": (
            "You are a software designer focused on creating high-level structural representations of code. "
            "Your role is to translate implementation code into clear, high-level pseudocode that emphasizes "
            "system structure and component relationships. Follow these guidelines:\n"
            "1. Focus on class/module level design and their relationships\n"
            "2. Include only public interfaces and primary service boundaries\n"
            "3. Use clear, consistent naming that reflects component purposes\n"
            "4. Show inheritance, composition, and other key relationships\n"
            "5. Exclude private methods, properties, and implementation specifics\n"
            "6. Use standard design pattern terminology where applicable\n\n"
            "Your pseudocode should help developers understand the system's structure and component "
            "interactions without diving into implementation details."
        ),
        "user_message": (
            "Create a high-level structural pseudocode representation of this code. Include:\n"
            "1. Main classes/modules and their primary purposes\n"
            "2. Public interfaces and service boundaries\n"
            "3. Key relationships between components\n"
            "4. Any significant design patterns used\n\n"
            "Exclude all implementation details and private members.\n\n"
            "Code to convert:\n\n{chunk}"
        )
    },
    2: {
        "system_message": (
            "You are a technical lead focused on explaining main program flows and behaviors. "
            "Your role is to create mid-level pseudocode that captures essential logic patterns "
            "and data transformations. Follow these guidelines:\n"
            "1. Show primary algorithms and key method behaviors\n"
            "2. Include core logic flows and data transformations\n"
            "3. Use standard algorithmic terminology (iterate, transform, aggregate, etc.)\n"
            "4. Summarize complex operations without implementation details\n"
            "5. Show important state changes and condition handling\n"
            "6. Maintain logical structure while abstracting specific code\n\n"
            "Your pseudocode should help developers understand how the system works without "
            "getting lost in implementation specifics."
        ),
        "user_message": (
            "Create flow-oriented pseudocode that shows how this code works. Include:\n"
            "1. Primary algorithms and their key steps\n"
            "2. Important data transformations and state changes\n"
            "3. Main control flows and condition handling\n"
            "4. Critical business logic patterns\n\n"
            "Summarize complex operations without implementation details.\n\n"
            "Code to convert:\n\n{chunk}"
        )
    },
    3: {
        "system_message": (
            "You are a developer creating detailed pseudocode that closely mirrors implementation code. "
            "Your role is to translate code into clear, comprehensive pseudocode that maintains full "
            "logical fidelity. Follow these guidelines:\n"
            "1. Include all significant classes, methods, and their implementations\n"
            "2. Show detailed logic flows, algorithms, and control structures\n"
            "3. Represent data workflows and state transformations\n"
            "4. Include error handling and edge cases\n"
            "5. Use consistent pseudocode conventions for clarity\n"
            "6. Maintain the original code's logical structure and relationships\n\n"
            "Your pseudocode should provide enough detail for developers to fully understand "
            "the implementation while being more readable than source code."
        ),
        "user_message": (
            "Create detailed pseudocode that thoroughly represents this implementation. Include:\n"
            "1. All important classes, methods, and their logic\n"
            "2. Complete algorithms and control structures\n"
            "3. Data workflows and state management\n"
            "4. Error handling and edge cases\n"
            "5. Key variable interactions and transformations\n\n"
            "Use clear, consistent pseudocode syntax.\n\n"
            "Code to convert:\n\n{chunk}"
        )
    }
}



def read_source_file(file_path: str) -> str:
    """Read the contents of the source file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logging.error(f"Error reading file {file_path}: {e}")
        sys.exit(1)


def count_tokens(text: str, model: str = "gpt-3.5-turbo-1106") -> int:
    """Count the number of tokens in the text for a given model."""
    try:
        encoding = tiktoken.encoding_for_model(model)
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception as e:
        logging.error(f"Error counting tokens: {e}")
        sys.exit(1)


def split_source_code(source_code: str, model: str = "gpt-3.5-turbo-1106") -> List[str]:
    """Split source code into chunks that fit within the token limit."""
    encoding = tiktoken.encoding_for_model(model)
    tokens = encoding.encode(source_code)
    
    # Split tokens into chunks
    chunks = []
    for i in range(0, len(tokens), MAX_TOKENS):
        chunk_tokens = tokens[i:i + MAX_TOKENS]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
    
    return chunks


def generate_pseudocode(source_code: str, api_key: str, model: str = "gpt-3.5-turbo-1106", abstract_level: int = 1) -> str:
    """Generate pseudocode using OpenAI's GPT model."""
    if not api_key:
        logging.error("OpenAI API key not found. Please set it in .env file.")
        sys.exit(1)

    if model not in AVAILABLE_MODELS:
        logging.error(f"Invalid model '{model}'. Available models:")
        for m, desc in AVAILABLE_MODELS.items():
            logging.error(f"  - {m}: {desc}")
        sys.exit(1)

    # Count tokens
    token_count = count_tokens(source_code, model)
    logging.info(f"Token count for the input: {token_count}")

    # Split source code if it exceeds the token limit
    if token_count > MAX_TOKENS:
        logging.info("Source code exceeds token limit, splitting into chunks...")
        source_chunks = split_source_code(source_code, model)
    else:
        source_chunks = [source_code]

    client = OpenAI(api_key=api_key)
    pseudocode_chunks = []

    for i, chunk in enumerate(source_chunks):
        logging.info(f"Processing chunk {i + 1} of {len(source_chunks)}")
        try:
            if abstract_level in ABSTRACTION_LEVELS:
                system_message = ABSTRACTION_LEVELS[abstract_level]["system_message"]
                user_message = ABSTRACTION_LEVELS[abstract_level]["user_message"].format(chunk=chunk)
            else:
                system_message = (
                    "You are a helpful assistant that converts source code into clear, "
                    "readable pseudocode. Your pseudocode should be language-agnostic "
                    "and as concise as possible."
                )
                user_message = (
                    f"Convert the following code into pseudocode. Use clear, concise "
                    f"language and maintain the logical structure:\n\n{chunk}"
                )

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1
            )
            pseudocode_chunks.append(response.choices[0].message.content)
        except Exception as e:
            logging.error(f"Error generating pseudocode: {e}")
            sys.exit(1)

    logging.info("Pseudocode generation completed.")
    return "\n\n".join(pseudocode_chunks)


def list_available_models() -> None:
    """Print available models and their descriptions."""
    print("\nAvailable models:")
    for model, description in AVAILABLE_MODELS.items():
        print(f"  - {model}: {description}")


def fetch_source_from_url(url: str) -> str:
    """Fetch the contents of the source file from a URL."""
    logging.info(f"Fetching source code from URL: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching file from URL: {e}")
        sys.exit(1)


def main() -> None:
    setup_logging('INFO')  # Default log level
    
    parser = argparse.ArgumentParser(
        description='Generate pseudocode from source code using LLM'
    )
    parser.add_argument('source_files', type=str, nargs='+',
                        help='Path to the source code file(s) or URL(s)')
    parser.add_argument('--output', '-o', type=str,
                        help='Output file path (optional, defaults to stdout)')
    parser.add_argument('--model', '-m', type=str,
                        default="gpt-3.5-turbo-1106",
                        help='Model to use for generation (use --list-models to see options)')
    parser.add_argument('--list-models', action='store_true',
                        help='List available models and exit')
    parser.add_argument('--abstractlevel', '-a', type=int, choices=[0, 1, 2, 3], default=1,
                        help='Level of abstraction for pseudocode: 0 (summary) to 3 (detailed)')
    parser.add_argument('--loglevel', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='INFO',
                        help='Set the logging level')
    args = parser.parse_args()

    if args.loglevel:
        logging.getLogger().setLevel(getattr(logging, args.loglevel.upper(), logging.INFO))

    if args.list_models:
        list_available_models()
        sys.exit(0)

    if not args.source_files:
        parser.error("source_file is required unless --list-models is used")

    # Get API key from environment variable
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        logging.error("OpenAI API key not found. Please set it in .env file.")
        sys.exit(1)
    
    all_pseudocodes = []
    
    for source_file in args.source_files:
        # Determine if the source_file is a URL or a local file path
        if source_file.startswith('http://') or source_file.startswith('https://'):
            source_code = fetch_source_from_url(source_file)
        else:
            source_code = read_source_file(source_file)
        
        # Generate pseudocode
        pseudocode = generate_pseudocode(source_code, api_key, args.model, args.abstractlevel)
        all_pseudocodes.append(pseudocode)
    
    # Combine all pseudocodes
    final_pseudocode = "\n\n".join(all_pseudocodes)
    
    # Output results
    if args.output:
        try:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(final_pseudocode)
            logging.info(f"Pseudocode written to {args.output}")
        except Exception as e:
            logging.error(f"Error writing to output file: {e}")
            sys.exit(1)
    else:
        print(final_pseudocode)


if __name__ == '__main__':
    main() 
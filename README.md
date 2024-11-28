# Pseudocode Generator

A command-line tool that converts source code into pseudocode using OpenAI's GPT models.

## Requirements
- Python 3.6+
- OpenAI API key

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Set up your environment variables:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_actual_api_key_here
     ```

## Usage

Basic usage (uses GPT-3.5 Turbo by default):
```bash
python pseudogen.py path/to/source/file.py
```

Read source from URL:
```bash
python pseudogen.py https://raw.githubusercontent.com/user/repo/main/file.py
```

Save output to a file:
```bash
python pseudogen.py path/to/source/file.py -o output.txt
```

Use a specific model:
```bash
python pseudogen.py path/to/source/file.py --model gpt-4-1106-preview
```

List available models:
```bash
python pseudogen.py --list-models
```

## Arguments
- `source`: Path to the source code file or URL (required)
- `--output`, `-o`: Output file path (optional, defaults to stdout)
- `--model`, `-m`: Model to use for generation (optional, defaults to gpt-3.5-turbo-1106)
- `--list-models`: List available models and exit

## Available Models
- `gpt-3.5-turbo-1106`: Latest GPT-3.5 Turbo - Fast and cost-effective (default)
- `gpt-4-1106-preview`: Latest GPT-4 Turbo - Most capable and up-to-date model
- `gpt-4`: Standard GPT-4 - Highly capable model with 8k context
- `gpt-4-32k`: GPT-4 32k - Extended context version of GPT-4

## Examples

Convert Python code using GPT-4 Turbo:
```bash
python pseudogen.py example.py --model gpt-4-1106-preview
```

Convert code from GitHub using GPT-3.5 Turbo:
```bash
python pseudogen.py https://raw.githubusercontent.com/user/repo/main/script.py -m gpt-3.5-turbo-1106
```

Save pseudocode to a file using GPT-3.5 Turbo:
```bash
python pseudogen.py example.py -m gpt-3.5-turbo-1106 -o pseudocode.txt
```
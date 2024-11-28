# Pseudocode Generator

A command-line tool that converts source code into pseudocode using OpenAI's GPT model.

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

Basic usage:
```bash
python pseudogen.py path/to/source/file.py
```

Save output to a file:
```bash
python pseudogen.py path/to/source/file.py -o output.txt
```

## Arguments
- `source_file`: Path to the source code file (required)
- `--output`, `-o`: Output file path (optional, defaults to stdout)
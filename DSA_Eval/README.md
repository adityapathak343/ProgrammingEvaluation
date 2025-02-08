# DSA Assignment Grader

Automated grading system for Data Structures and Algorithms (DSA) assignments using OpenAI's GPT-4 model. The system evaluates student code submissions based on defined rubrics and generates detailed feedback reports.

## Core Features

- Automated evaluation of code submissions
- Detailed feedback with strengths and weaknesses
- Point-based scoring system
- Batch processing support
- YAML-based configuration and output

## Setup

1. Install dependencies:
```bash
pip install openai pyyaml
```

2. Set up OpenAI API key and add to the script.
```bash
 #replace  api_key = "your_api_key"
```

## Directory Structure

```
project_root/
├── dsa_rubric.yaml      # Grading rubric configuration
├── PROBLEM_DIR/         # Directory containing problem and submissions
    ├── question.txt     # Problem description
    ├── _language1/      # Language-specific submissions
    │   ├── submission1.txt
    │   └── submission2.txt
    └── _language2/
        └── submission1.txt
```

## Rubric Configuration

Use the `dsa_rubric.yaml` file with your grading criteria by keeping it in the same folder as the script


## Usage

### Basic Command

```bash
python dsa.py <problem_directory> [use_test_case_ratio]
```

Examples:
```bash
# Grade without test cases
python dsa.py assignments/week1

# Grade with test case results
python dsa.py assignments/week1 1
```

### Output Format

The grader generates a YAML report for each submission:

```yaml
timestamp: "2025-02-02T14:30:00"
total_score: 8
max_score: 12
percentage: 66.67
categories:
  logical_correctness:
    score: 3
    feedback:
      strengths:
        - points: 2
          comment: "Core algorithm implementation is correct."
      weaknesses:
        - points: 2
          comment: "Edge case handling is incomplete."
```

## How It Works

1. **Input Processing**:
   - Reads problem description from question.txt
   - Processes student submissions from language-specific directories
   - Optionally accepts test case results

2. **Evaluation Process**:
   - Uses GPT-4 to analyze code against rubric criteria
   - Generates structured feedback with point allocations
   - Considers test case performance if provided

3. **Feedback Generation**:
   - Provides category-wise scoring
   - Lists specific strengths and weaknesses
   - Includes point breakdown for each feedback item
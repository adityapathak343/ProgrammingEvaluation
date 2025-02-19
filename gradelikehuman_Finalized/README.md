# Automated Programming Assignment Grading Pipeline

This system implements a three-stage pipeline for automated programming assignment grading:
1. Rubric Generation
2. Grading
3. Re-evaluation

## Prerequisites

1. Python 3.8+
2. Required packages:
   ```bash
   pip install openai pandas pyyaml python-dotenv
   ```

3. OpenAI API key in `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Basic Usage

### Full Pipeline

Run all three stages in sequence:
```bash
python main.py \
  --problem-number 1 \
  --synth-v3-path synth-v3 \
  --stages rubric grade reeval
```

### Individual Stages

#### 1. Rubric Generation Only

```bash
python main.py \
  --problem-number 1 \
  --synth-v3-path synth-v3 \
  --stages rubric \
  --sampling-method distribution \
  --sample-size 5 \
  --max-epochs 3
```

Alternative sampling method:
```bash
python main.py \
  --problem-number 1 \
  --synth-v3-path synth-v3 \
  --stages rubric \
  --sampling-method random
```

#### 2. Grading Only

```bash
python main.py \
  --problem-number 1 \
  --synth-v3-path synth-v3 \
  --stages grade \
  --existing-rubric output/rubrics/problem1_rubric_[timestamp].yaml \
  --grading-strategy batch \
  --batch-size 3
```

Different grading strategies:
```bash
# One-shot grading
python main.py \
  --problem-number 1 \
  --synth-v3-path synth-v3 \
  --stages grade \
  --grading-strategy one-shot \
  --existing-rubric output/rubrics/problem1_rubric_[timestamp].yaml

# Self-reflection grading
python main.py \
  --problem-number 1 \
  --synth-v3-path synth-v3 \
  --stages grade \
  --grading-strategy self-reflection \
  --existing-rubric output/rubrics/problem1_rubric_[timestamp].yaml
```

#### 3. Re-evaluation Only

```bash
python main.py \
  --problem-number 1 \
  --synth-v3-path synth-v3 \
  --stages reeval \
  --existing-rubric output/rubrics/problem1_rubric_[timestamp].yaml \
  --existing-grades output/grades/grades_problem1_[timestamp].csv \
  --reeval-group-size 3 \
  --reeval-iterations 2
```

## Advanced Configurations

### Combined Stage Execution

Run rubric generation and grading:
```bash
python main.py \
  --problem-number 1 \
  --synth-v3-path synth-v3 \
  --stages rubric grade \
  --sampling-method distribution \
  --grading-strategy batch
```

Run grading and re-evaluation:
```bash
python main.py \
  --problem-number 1 \
  --synth-v3-path synth-v3 \
  --stages grade reeval \
  --existing-rubric output/rubrics/problem1_rubric_[timestamp].yaml \
  --grading-strategy batch \
  --reeval-group-size 3
```

### Model Selection

Use different OpenAI models:
```bash
python main.py \
  --problem-number 1 \
  --synth-v3-path synth-v3 \
  --model gpt-4o-mini \  # or gpt-3.5-turbo
  --stages rubric grade reeval
```

### Output Directory Structure

```
output/
├── rubrics/
│   └── problem1_rubric_[timestamp].yaml
├── grades/
│   └── grades_problem1_[timestamp].csv
└── reeval/
    └── reeval_grades_problem1_[timestamp].csv
```

## Full Pipeline with All Options

Here's an example running the complete pipeline with all options specified:

```bash
python main.py \
  --problem-number 1 \
  --synth-v3-path synth-v3 \
  --stages rubric grade reeval \
  --sampling-method distribution \
  --sample-size 5 \
  --max-epochs 5 \
  --grading-strategy batch \
  --batch-size 3 \
  --reeval-group-size 3 \
  --reeval-iterations 2 \
  --model gpt-4o-mini \
  --output-dir outputs
```

## Common Issues and Solutions

1. **Missing OpenAI API Key**
   - Ensure your `.env` file contains a valid API key
   - Check that python-dotenv is installed

2. **File Not Found Errors**
   - Verify the synth-v3 directory path is correct
   - Check that problem files exist in the expected locations

3. **Invalid Timestamps**
   - When using `--existing-rubric` or `--existing-grades`, make sure to use the correct timestamp from your output files

## Output Files

1. Rubric files include:
   - Criteria and point allocations
   - Detailed descriptions for each score level
   - Total points possible

2. Grade files include:
   - Problem identifiers (e.g., problem1_solution, problem1-0pt)
   - Expected scores for each solution

3. Re-evaluation files include:
   - Adjusted scores after group comparison
   - Final calibrated grades

Note: Replace `[timestamp]` in file paths with the actual timestamp of your generated files (format: YYYYMMDD_HHMMSS).
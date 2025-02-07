#!/bin/bash

# Pipeline script for Grade Like a Human system
# Runs rubric redesign, evaluation, and re-evaluation in sequence

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default configuration
CONFIG_FILE="config.yaml"
DATA_DIR="data"
QUESTION_ID="q1"
SAMPLING_METHOD="distribution"
SAMPLE_SIZE=10
ITERATIONS=3
BATCH_SIZE=10
REGROUP_ROUNDS=2
PROMPT_STRATEGY="batching"

# Get the absolute path to the project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Add the project root to PYTHONPATH
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH}"
export OPENAI_API_KEY="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"
# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" >&2
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

# Function to check if previous command succeeded
check_status() {
    if [ $? -ne 0 ]; then
        error "$1"
        exit 1
    fi
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        --data-dir)
            DATA_DIR="$2"
            shift 2
            ;;
        --question-id)
            QUESTION_ID="$2"
            shift 2
            ;;
        --sampling)
            SAMPLING_METHOD="$2"
            shift 2
            ;;
        --sample-size)
            SAMPLE_SIZE="$2"
            shift 2
            ;;
        --iterations)
            ITERATIONS="$2"
            shift 2
            ;;
        --batch-size)
            BATCH_SIZE="$2"
            shift 2
            ;;
        --regroup-rounds)
            REGROUP_ROUNDS="$2"
            shift 2
            ;;
        --prompt-strategy)
            PROMPT_STRATEGY="$2"
            shift 2
            ;;
        *)
            error "Unknown parameter: $1"
            exit 1
            ;;
    esac
done

# Setup paths
QUESTION_FILE="${DATA_DIR}/questions/${QUESTION_ID}.txt"
INITIAL_RUBRIC="${DATA_DIR}/rubrics/${QUESTION_ID}_original.txt"
IMPROVED_RUBRIC="${DATA_DIR}/rubrics/${QUESTION_ID}_improved.txt"
SUBMISSIONS_FILE="${DATA_DIR}/submissions/${QUESTION_ID}.csv"
EVAL_RESULTS="${DATA_DIR}/results/${QUESTION_ID}_evaluations.json"
FINAL_RESULTS="${DATA_DIR}/results/${QUESTION_ID}_final.json"

# Check if required files exist
for file in "$QUESTION_FILE" "$INITIAL_RUBRIC" "$SUBMISSIONS_FILE"; do
    if [ ! -f "$file" ]; then
        error "Required file not found: $file"
        exit 1
    fi
done

# Create output directories if they don't exist
mkdir -p "${DATA_DIR}/rubrics" "${DATA_DIR}/results"

# Start pipeline
log "Starting Grade Like a Human pipeline for question ${QUESTION_ID}"
log "Using configuration file: ${CONFIG_FILE}"

# Step 1: Redesign rubric
log "Step 1/3: Redesigning rubric"
python scripts/redesign_rubric.py \
    --question "$QUESTION_FILE" \
    --initial-rubric "$INITIAL_RUBRIC" \
    --submissions "$SUBMISSIONS_FILE" \
    --output "$IMPROVED_RUBRIC" \
    --config "$CONFIG_FILE" \
    --sampling "$SAMPLING_METHOD" \
    --sample-size "$SAMPLE_SIZE" \
    --iterations "$ITERATIONS" \
    --verbose

check_status "Rubric redesign failed"
log "Rubric redesign completed. Improved rubric saved to: $IMPROVED_RUBRIC"

# Step 2: Evaluate submissions
log "Step 2/3: Evaluating submissions with improved rubric"
python scripts/evaluate.py \
    --question "$QUESTION_FILE" \
    --rubric "$IMPROVED_RUBRIC" \
    --submissions "$SUBMISSIONS_FILE" \
    --output "$EVAL_RESULTS" \
    --config "$CONFIG_FILE" \
    --prompt-strategy "$PROMPT_STRATEGY" \
    --batch-size "$BATCH_SIZE" \
    --calculate-metrics \
    --verbose

check_status "Evaluation failed"
log "Evaluation completed. Results saved to: $EVAL_RESULTS"

# Step 3: Re-evaluate results
log "Step 3/3: Re-evaluating grading results"
python scripts/re_evaluate.py \
    --question "$QUESTION_FILE" \
    --rubric "$IMPROVED_RUBRIC" \
    --evaluations "$EVAL_RESULTS" \
    --output "$FINAL_RESULTS" \
    --config "$CONFIG_FILE" \
    --batch-size "$BATCH_SIZE" \
    --regroup-rounds "$REGROUP_ROUNDS" \
    --calculate-metrics \
    --verbose

check_status "Re-evaluation failed"
log "Re-evaluation completed. Final results saved to: $FINAL_RESULTS"

# Pipeline completion
log "Pipeline completed successfully"
log "Generated files:"
log "  - Improved rubric: $IMPROVED_RUBRIC"
log "  - Evaluation results: $EVAL_RESULTS"
log "  - Final results: $FINAL_RESULTS"

# Optional: Print summary from final results
if [ -f "$FINAL_RESULTS" ]; then
    echo -e "\n${GREEN}Summary:${NC}"
    python -c "
import json
with open('$FINAL_RESULTS', 'r') as f:
    data = json.load(f)
    stats = data['statistics']
    print(f'Total submissions: {stats.get(\"total_submissions\", 0)}')
    print(f'Anomalies found: {stats.get(\"anomalies_found\", 0)}')
    print(f'Grades revised: {stats.get(\"grades_revised\", 0)}')
    if 'comparison_metrics' in data:
        metrics = data['comparison_metrics']['comparison_metrics']
        print(f'MAE: {metrics.get(\"mae\", 0):.3f}')
        print(f'RMSE: {metrics.get(\"rmse\", 0):.3f}')
"
fi
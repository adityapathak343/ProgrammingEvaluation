grade_like_human/
│
├── src/
│   ├── __init__.py
│   ├── rubric_designer.py      # Rubric generation and improvement
│   ├── evaluator.py           # Main grading evaluation logic
│   ├── re_evaluator.py        # Re-evaluation and review logic
│   ├── utils.py               # Shared utilities and helpers
│   └── config.py              # Configuration and settings
│
├── prompts/
│   ├── rubric_prompts.json    # Prompts for rubric generation
│   ├── eval_prompts.json      # Prompts for evaluation
│   └── reeval_prompts.json    # Prompts for re-evaluation
│
├── data/
│   ├── questions/             # Question files
│   ├── rubrics/              # Rubric files (original and improved)
│   └── submissions/          # Student submissions
│
├── scripts/
│   ├── redesign_rubric.py    # Script to run rubric redesign
│   ├── evaluate.py           # Script to run evaluation
│   └── re_evaluate.py        # Script to run re-evaluation
│
├── requirements.txt
└── README.md
# src/config.py

"""
Configuration management for the grading system.
Handles settings, paths, and model configurations.
"""

import os
from pathlib import Path
from typing import Dict, Any
import yaml

class Config:
    """Configuration manager for the grading system."""
    
    DEFAULT_CONFIG = {
        'model': {
            'name': 'gpt-4o-mini',
            'temperature': 0,
            'max_tokens': 2000
        },
        'paths': {
            'data_dir': 'data',
            'questions_dir': 'data/questions',
            'rubrics_dir': 'data/rubrics',
            'submissions_dir': 'data/submissions',
            'results_dir': 'data/results',
            'prompts_dir': 'prompts'
        },
        'sampling': {
            'default_size': 10,
            'n_strata': 5
        },
        'evaluation': {
            'batch_size': 10,
            'regroup_rounds': 2,
            'score_tolerance': 0.1
        },
        'logging': {
            'level': 'INFO',
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'prompts': {
        'grading': '''
            Please grade the following student submission according to this rubric:
            
            Submission:
            {submission}
            
            Rubric:
            {rubric}
            
            Provide a detailed evaluation and final score.
        ''',
        'rubric_generation': '''
            # Add your default rubric generation prompt here
        '''
    }
    }
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration, optionally from file.
        
        Args:
            config_path: Path to YAML configuration file
        """
        self.config = self.DEFAULT_CONFIG.copy()
        
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                custom_config = yaml.safe_load(f)
                self._update_recursive(self.config, custom_config)
                
        # Create required directories
        self._create_directories()

    def _update_recursive(self, base: Dict, update: Dict) -> None:
        """Recursively update nested dictionary."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict):
                self._update_recursive(base[key], value)
            else:
                base[key] = value

    def _create_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        for path in self.config['paths'].values():
            Path(path).mkdir(parents=True, exist_ok=True)

    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration."""
        return self.config['model']

    def get_path(self, key: str) -> Path:
        """Get path from configuration."""
        if key not in self.config['paths']:
            raise KeyError(f"Unknown path key: {key}")
        return Path(self.config['paths'][key])

    def get_sampling_config(self) -> Dict[str, Any]:
        """Get sampling configuration."""
        return self.config['sampling']

    def get_evaluation_config(self) -> Dict[str, Any]:
        """Get evaluation configuration."""
        return self.config['evaluation']

    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.config['logging']

    def save(self, path: str) -> None:
        """Save current configuration to file."""
        with open(path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    def get_prompts(self) -> Dict[str, str]:
        """Get prompts configuration."""
        return self.config.get('prompts', {})
    @staticmethod
    def load(path: str) -> 'Config':
        """Load configuration from file."""
        return Config(config_path=path)
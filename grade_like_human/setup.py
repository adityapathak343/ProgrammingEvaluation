from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="grade_like_human",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requirements,
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "redesign-rubric=scripts.redesign_rubric:main",
            "evaluate=scripts.evaluate:main",
            "re-evaluate=scripts.re_evaluate:main",
        ],
    },
)
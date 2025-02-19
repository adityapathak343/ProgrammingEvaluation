# codev.py
from openai import OpenAI
import json
import os
import statistics
from typing import List, Dict, Any
from pathlib import Path
import time

class CodEv:
    def __init__(self, api_key: str):
        """Initialize CodEv with OpenAI API key."""
        self.client = OpenAI(api_key=api_key)
        
    def get_single_evaluation(self, code: str) -> Dict[str, Any]:
        """Get a single evaluation from the model."""
        try:
            prompt = """You are evaluating a Java code submission for a Cricket Analytics System.
            Provide your evaluation in VALID JSON format only.
            
          

            You are required to implement functionalities for a Cricket Analytics application. 
            The provided template code for this application contains multiple classes and methods related to cricket players, 
            their roles, team information, and various data-handling operations. Your tasks involve implementing several methods, 
            each responsible for performing specific actions like reading data from a file, writing data back, updating player 
            statistics, and filtering data.
            
Tasks and Methods to be Implemented:
1. RunsComparator: compare Method [2 marks] Write code for comparing runs scored by two players in descending order. Return a negative value if the first player has more runs, a positive value if the second player has more runs, or zero if they have the same number of runs.
2. CricketDataHandler: readPlayersFromFile Method [9 marks] Write code for reading player data from the input CSV file and creating a list of Player objects.
● Step 1: Create an empty list to store player details. [1 mark]
● Step 2: Open the specified file for reading data. [1 mark]
● Step 3: Ignore the first line since it contains the column names. [1 mark]
● Step 4: Read each line one by one until reaching the end of the file. [1 mark]
● Step 5: Split the line into different pieces of information. [1 mark]
● Step 6: Create a new player using this information. [1 mark]
● Step 7: Add the new player to the list. [1 mark]
● Step 8: Close the file after reading all data. [1 mark]
● Step 9: Return the complete list of players. [1 mark]
3. CricketDataHandler: writePlayersToFile Method [4 marks] Write code to write the updated list of players back to the output CSV file. The format of the output file should be the same as that of the input file.
● Step 1: Prepare to write data into the specified file. [1 mark]
● Step 2: Write the column names as the first line of the file. [1 mark]
● Step 3: For each player in the list, convert their details to the desired format. [1 mark]
● Step 4: Write each player's information to the file. [1 mark]
4. CricketDataHandler: updatePlayerStats Method [5 marks] Implement the method to update a player's stats (runs and wickets).
● Step 1: Go through each player in the list. [1 mark]
● Step 2: Check if the current player's name matches the given name. [1 mark]
● Step 3: If it matches, update the player's runs with the new value. Updated value will be the sum of the old runs and the argument runs. For example, if a player had 100 runs and the runs argument (to this method) is 50, their new total should be 150 runs. [1 mark]
● Step 4: Similarly, update the player's wickets with the new value. Updated value will be the sum of the old wickets and the argument wickets. For example, if they had 10 wickets and the wickets argument (to this method) is 2, their new total should be 12 wickets[1 mark]
● Step 5: If no player matches the given name, throw an IllegalArgumentException. [1 mark]
5. CricketDataHandler: calculateTeamAverageRuns Method [5 marks] Write code to calculate the average runs scored by players of a specific team.
● Step 1: Filter players belonging to the specified team. [2 marks]
● Step 2: If no players for this team exist, throw an IllegalArgumentException exception. [1 mark]
● Step 3: Calculate the total runs scored by all players from this team. [1 mark]
● Step 4: Compute and return the average runs scored. [1 mark]
6. TeamFilter: filter Method [5 marks] Write code to filter players by their team.
● Step 1: Create an empty list for players matching the criteria. [1 mark]
● Step 2: Go through each player in the players list. [1 mark]
● Step 3: If the player's team matches the given name, add them to the list. [2 marks]
● Step 4: Return the list containing all matching players. [1 mark]
7. AllRounderStatsFilter: filter Method [5 marks] Write code to filter all-rounder players which satisfy the provided criteria (i.e. filter those all-rounders who have runs and wickets greater than or equal to the runs and wickets specified in the criteria respectively).
● Step 1: Create an empty list for players matching the criteria. [1 mark]
● Step 2: Go through each player in the list. [1 mark]
● Step 3: If the player is an all-rounder and meets the given criteria for both runs and wickets, add them to the list. [2 marks]
● Step 4: Return the list containing all matching players. [1 mark]
            Student Code:
            ```java
            {code}
            ```

            Respond ONLY with a JSON object in this exact format:
            {{
                "function_scores": {{
                    "compare": {{"score": 0, "max_score": 2, "feedback": "feedback here"}},
                    "readPlayersFromFile": {{"score": 0, "max_score": 9, "feedback": "feedback here"}},
                    "writePlayersToFile": {{"score": 0, "max_score": 4, "feedback": "feedback here"}},
                    "updatePlayerStats": {{"score": 0, "max_score": 5, "feedback": "feedback here"}},
                    "calculateTeamAverageRuns": {{"score": 0, "max_score": 5, "feedback": "feedback here"}},
                    "teamFilter": {{"score": 0, "max_score": 5, "feedback": "feedback here"}},
                    "allRounderFilter": {{"score": 0, "max_score": 5, "feedback": "feedback here"}}
                }},
                "total_score": 0,
                "overall_feedback": "overall feedback here"
            }}"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a code evaluator that ONLY responds with valid JSON. No other text or explanation."
                    },
                    {
                        "role": "user",
                        "content": prompt.format(code=code)
                    }
                ],
                temperature=0.1
            )

            response_text = response.choices[0].message.content.strip()
            return json.loads(response_text)

        except Exception as e:
            print(f"Error in single evaluation: {str(e)}")
            return None

    def evaluate_submission(self, code: str, model_solution: str, ensemble_size: int = 5) -> Dict[str, Any]:
        """Evaluate a single submission using ensemble approach."""
        print(f"\nStarting ensemble evaluation with {ensemble_size} models...")
        
        evaluations = []
        for i in range(ensemble_size):
            print(f"Running evaluation {i+1}/{ensemble_size}...")
            result = self.get_single_evaluation(code)
            if result:
                evaluations.append(result)

        if not evaluations:
            print("All evaluation attempts failed")
            return None

        # Ensemble processing
        try:
            # Get all scores for each function
            function_scores = {
                func_name: [eval['function_scores'][func_name]['score'] 
                           for eval in evaluations]
                for func_name in evaluations[0]['function_scores'].keys()
            }

            # Calculate mode scores for each function
            final_scores = {
                func_name: statistics.mode(scores)
                for func_name, scores in function_scores.items()
            }

            # Get total scores
            total_scores = [eval['total_score'] for eval in evaluations]
            final_total = statistics.mode(total_scores)

            # Select the evaluation whose total score is closest to the final total
            best_eval_index = min(range(len(evaluations)), 
                                key=lambda i: abs(evaluations[i]['total_score'] - final_total))
            best_evaluation = evaluations[best_eval_index]

            # Create final result with mode scores and feedback from best evaluation
            final_result = {
                "function_scores": {
                    func_name: {
                        "score": final_scores[func_name],
                        "max_score": best_evaluation['function_scores'][func_name]['max_score'],
                        "feedback": best_evaluation['function_scores'][func_name]['feedback']
                    }
                    for func_name in final_scores.keys()
                },
                "total_score": final_total,
                "overall_feedback": best_evaluation['overall_feedback'],
                "ensemble_statistics": {
                    "evaluations_count": len(evaluations),
                    "score_variance": {
                        func_name: statistics.variance(scores) if len(scores) > 1 else 0
                        for func_name, scores in function_scores.items()
                    },
                    "total_score_variance": statistics.variance(total_scores) if len(total_scores) > 1 else 0
                }
            }

            print(f"Ensemble evaluation complete. Final score: {final_total}")
            return final_result

        except Exception as e:
            print(f"Error in ensemble processing: {str(e)}")
            return None
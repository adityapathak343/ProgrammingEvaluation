import pandas as pd


class OOPdatasetloader:
    def load_submission_file(self, file_path):
        """
        Loads the content of a .java file given its path.

        Args:
            file_path: The path to the .java file.

        Returns:
            The content of the .java file as a string.
            Returns None if the file cannot be opened.
        """
        with open(file_path, 'r') as file:
            return file.read()

    def solution_loader(self, filepath="OOPS_dataset_v1/cleaned_oops.xlsx"):
        df = pd.read_excel(filepath)  # Use pd.read_excel for excel files
        solutions = {}
        for id in df["Folder Name"]:
            java_file_path = f"OOPS_dataset_v1/solutions/{id}/p1.java"
            eval_score = df[df['Folder Name'] == id]['Part1 Total'].values[0]
            try:
                solutions[id] = [self.load_submission_file(java_file_path),eval_score]
            except FileNotFoundError:
                solutions[id] = ["No Solution Provided",eval_score]
        return solutions
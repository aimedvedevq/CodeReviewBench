EXACT_MATCH_PROMPT = """
reference: {reference}
hypothesis: {hypothesis}

"""

SYSTEM_PROMPT = """
You will be provided with a code diff snippet and two comments from the code describing an issue.
Your task is to determine whether both comments describe the same problem.
If both comments describe the same problem and propose the same solution, answer: correct.
If the comments describe different problems and solutions, answer: wrong.
Write your answer as correct or wrong, without quotes or any other extra characters.

If it is correct, return "correct".
If it is incorrect, return "wrong".
"""
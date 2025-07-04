import re
from typing import List, Dict


def parse_predictions(predictions: List[str]) -> List[List[str]]:
    parsed_predictions = []
    for prediction in predictions:
        # Handle None predictions
        if prediction is None:
            print(f"Warning: Found None prediction, skipping...")
            parsed_predictions.append([])
            continue

        # Convert to string if not already
        if not isinstance(prediction, str):
            prediction = str(prediction)

        # Combine both Russian and English comment patterns
        # Russian: Комментарий 1: ...
        # English: Comment 1: ...
        comment_pattern = re.compile(
            r'(?:Комментарий|Comment)\s*\d+:\s*(.*?)(?=(?:Комментарий|Comment)\s*\d+:|$)',
            re.DOTALL | re.IGNORECASE
        )
        comments = comment_pattern.findall(prediction)
        comments = [comment.strip() for comment in comments if comment.strip()]
        # If no structured comments were captured, fall back to the full output
        if not comments:
            fallback = prediction.strip()
            if fallback:
                parsed_predictions.append([fallback])
            else:
                parsed_predictions.append([])
        else:
            parsed_predictions.append(comments[:10])
    return parsed_predictions
import json
import random

# Function to read questions from a JSON file
def read_questions(category):
    filename = f'test-questions/de_{category.lower()}_questions.json'
    with open(filename, 'r') as file:
        questions = json.load(file)
    return questions

def question_list(ques_num=5,categories=['concept']):
    
    # List to store selected questions
    selected_questions = set()
    
    # Select one question from each category
    for category in categories:
        questions = read_questions(category)
        if questions:
            selected_questions.add(random.choice(questions[category]))
    
    # Select additional questions randomly if needed to reach a total of 7 questions
    remaining_questions = ques_num - len(selected_questions)
    if remaining_questions > 0:
        for _ in range(remaining_questions):
            category = random.choice(categories)
            questions = read_questions(category)
            if questions:
                selected_questions.add(random.choice(questions[category]))
        
    return list(selected_questions)

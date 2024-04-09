import json
import time
import random
import os

DEFAULT_TIME_PER_Q = 3
time_limit = int(input(f'Enter how many seconds you want for each answer (Default is: {DEFAULT_TIME_PER_Q}s): '))


def LoadQuestionsFromFile(JSONPath):
    try:
        with open(JSONPath, 'r') as file:
            qs = json.load(file)
            return qs
    except FileNotFoundError:
        print(f"File not found at {str(JSONPath)}")
        return []


def SaveQuizState(state):
    with open('quiz_state.json', 'w') as file:
        json.dump(state, file)


def LoadQuizState():
    try:
        with open('quiz_state.json', 'r') as file:
            state = json.load(file)
            return state
    except FileNotFoundError:
        return None


def AskQuestions(quests, time_limit=DEFAULT_TIME_PER_Q, difficulty='easy'):
    score = 0
    total_answered = 0  
    totalQs = min(5, len(quests))  

    state = LoadQuizState()
    answered_questions = []
    current_question = 1 
    if state:
        current_question = state.get('current_question', 1)
        score = state.get('score', 0)
        total_answered = state.get('total_answered', 0)
        time_limit = state.get('time_limit', DEFAULT_TIME_PER_Q)
        answered_questions = state.get('answered_questions', [])
        difficulty = state.get('difficulty', 'easy')

    remaining_questions = [
        item for item in quests if item['question'] not in answered_questions and item['difficulty'] == difficulty
    ]
    random.shuffle(remaining_questions)
    remaining_questions = remaining_questions[:totalQs] 

    for i, item in enumerate(remaining_questions, start=current_question):
        ResetQuizState()

        print(f'{i}. {item["question"]}\n')

        if item['type'] == 'multiple_choice':
            for index, choice in enumerate(item['choices'], start=1):
                print(f'{index}. {choice}')
                if choice == item['correctAnswer']:
                    correctAnsI = index
            print("\n")

        elif item['type'] == 'true_false':
            print("1. True")
            print("2. False")
            correctAnsI = 1 if item['correctAnswer'] == 'True' else 2

        elif item['type'] == 'fill_in_the_blank':
            user_answer = input("Enter your answer: ").strip().lower()
            correct_answer = item['correctAnswer'].lower()
            correctAnsI = 1 if user_answer == correct_answer else 0
            if correctAnsI == 1:
                print("Correct!")
                score += 1
            else:
                print("Wrong :(")
            total_answered += 1  
            print(f'Current score: {score}/{total_answered}')

        start_time = time.time()
        validInput = False
        while not validInput:
            elapsed_time = time.time() - start_time
            if elapsed_time > time_limit:
                print("Time's up!")
                if correctAnsI is not None:  
                    print("Wrong :(")
                break

            if item['type'] != 'fill_in_the_blank':
                try:
                    userPick = int(input("Enter your choice (As a number in front of the choice you want): "))
                    elapsed_time = time.time() - start_time
                    if elapsed_time > time_limit:
                        print("Time's up!")
                        print(f'Current score: {score}/{total_answered}')
                        if correctAnsI is not None:
                            print("Wrong :(")
                        break
                    elif userPick >= 1 and userPick <= len(item['choices']):
                        validInput = True
                        total_answered += 1  
                        if correctAnsI is not None and correctAnsI == userPick:
                            print("Correct!")
                            score += 1
                        elif correctAnsI is None: 
                            print("Correct!")
                            score += 1
                        else:
                            print("Wrong :(")
                        print(f'Current score: {score}/{total_answered}')
                    else:
                        print("Invalid input! Please provide input as specified.")
                except ValueError:
                    print("Invalid input! Please provide input as specified.")
            else:
                validInput = True

        print("\n")
        answered_questions.append(item['question'])
        state = {'current_question': i + 1, 'score': score, 'total_answered': total_answered,
                 'time_limit': time_limit, 'answered_questions': answered_questions, 'difficulty': difficulty}
        SaveQuizState(state)

        if i + 1 <= 5:
            choice = input("Do you want to stop the quiz and save the current state? (y/n): ")
            if choice.lower() == 'y':
                break

    if i + 1 == totalQs:
        ResetQuizState()

    return score, total_answered  


def GenerateReport(score, totalQs):
    print(f"Total correct: {score}/{totalQs}")
    print(f"Percentage: {score * 100 / totalQs}%")


def ValidateQuestions(FilePath):
    try:
        quests = LoadQuestionsFromFile(FilePath)
        for qs in quests:
            if (
                str(qs['question'])
                and ('choices' in qs or qs['type'] == 'fill_in_the_blank')
                and ('choices' not in qs or (len(qs['choices']) >= 4 and len(qs['correctAnswer']) == 1))
                and 'type' in qs
                and 'difficulty' in qs
            ):
                continue
            else:
                return False
        return True
    except json.JSONDecodeError:
        return False


def ResetQuizState():
    if os.path.exists('quiz_state.json'):
        os.remove('quiz_state.json')


FilePath = "questions.json"

while True:
    questions = LoadQuestionsFromFile(FilePath)

    difficulty = input("Choose difficulty level (easy/hard): ")
    score, total_answered = AskQuestions(questions, time_limit, difficulty)
    GenerateReport(score, total_answered)

    choice = input("Do you want to start a new quiz? (y/n): ")
    if choice.lower() != 'y':
        break
    else:
        ResetQuizState()

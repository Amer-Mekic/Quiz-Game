const readlineSync = require('readline-sync');
const fs = require('fs');

const DEFAULT_TIME_PER_Q = 3;

function loadQuestionsFromFile(filePath) {
    try {
        const fileData = fs.readFileSync(filePath);
        const questions = JSON.parse(fileData);
        return questions;
    } catch (error) {
        console.log(`Error reading file: ${error.message}`);
        return [];
    }
}

function saveQuizState(state) {
    try {
        const stateJson = JSON.stringify(state);
        fs.writeFileSync('quiz_state.json', stateJson);
    } catch (error) {
        console.log(`Error saving state: ${error.message}`);
    }
}

function loadQuizState() {
    try {
        const fileData = fs.readFileSync('quiz_state.json');
        const state = JSON.parse(fileData);
        return state;
    } catch (error) {
        return null;
    }
}

function askQuestions(questions, timeLimit = DEFAULT_TIME_PER_Q, difficulty = 'easy') {
    let score = 0;
    const totalQs = Math.min(5, questions.length); 

    let state = loadQuizState();
    let answeredQuestions = state ? state.answeredQuestions : [];
    let currentQuestion = state ? state.currentQuestion : 0;

    for (let i = currentQuestion; i < Math.min(currentQuestion + 5, questions.length); i++) {
        const item = questions[i];

        console.log(`${i + 1}. ${item.question}\n`);

        let correctAnsI = null; 
        if (item.choices) {
            item.choices.forEach((choice, index) => {
                console.log(`${index + 1}. ${choice}`);
                if (choice === item.correctAnswer) {
                    correctAnsI = index + 1;
                }
                console.log('\n');
            });
        } else {
            console.log("No choices available for this question.");
        }

        const start_time = new Date();
        const userPick = readlineSync.questionInt('Enter your choice (As a number in front of the choice you want): ', {
            limit: [1, item.choices ? item.choices.length : 1],
            limitMessage: 'Invalid input! Please provide input as specified.',
            timeout: timeLimit * 1000,
            timeoutMessage: "Time's up!",
        });
        const elapsed_time = new Date() - start_time;

        if (elapsed_time >= timeLimit * 1000) {
            console.log("Time's up!");
            continue; 
        }

        if (userPick === correctAnsI) {
            console.log('Correct!');
            score++;
        } else {
            console.log('Wrong :(');
        }

        console.log(`Current score: ${score}/${totalQs}\n`);

        answeredQuestions.push(item.question);
        state = {
            currentQuestion: i + 1,
            score,
            timeLimit,
            answeredQuestions,
            difficulty,
            start_time,
        };
        saveQuizState(state);

        if (i + 1 >= totalQs) {
            console.log(`Total correct: ${score}/${totalQs}`);
            console.log(`Percentage: ${(score * 100) / totalQs}%`);
            break;
        }

        const choice = readlineSync.keyInYNStrict('Do you want to stop the quiz and save the current state?');
        if (choice) {
            console.log(`Total correct: ${score}/${totalQs}`);
            console.log(`Percentage: ${(score * 100) / totalQs}%`);
            break;
        }
    }

    saveQuizState(null);
}

const filePath = 'questions.json';
const questions = loadQuestionsFromFile(filePath);
const difficulty = readlineSync.question('Choose difficulty level (easy/hard): ').toLowerCase();
const timeLimit = readlineSync.questionInt('Enter how many seconds you want for each answer (Default is: 3s): ') || DEFAULT_TIME_PER_Q;
askQuestions(questions, timeLimit, difficulty);

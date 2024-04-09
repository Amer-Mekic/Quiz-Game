using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading;
using Newtonsoft.Json;

public class Question
{
    public string question { get; set; }
    public List<string>? choices { get; set; }
    public string? correctAnswer { get; set; }
}

public class QuizState
{
    public int CurrentQuestion { get; set; }
    public int Score { get; set; }
    public List<string> AnsweredQuestions { get; set; } = new List<string>();
}

class Program
{
    static void Main()
    {
        string JSONPath = "questions.json";
        var questions = LoadQuestionsFromFile(JSONPath);

        if (questions != null)
        {
            AskQuestions(questions);
        }
    }

    static List<Question> LoadQuestionsFromFile(string JSONPath)
    {
        try
        {
            string data = File.ReadAllText(JSONPath);
            return JsonConvert.DeserializeObject<List<Question>>(data) ?? new List<Question>();
        }
        catch (Exception)
        {
            Console.WriteLine("Error occurred in loading questions.");
            return new List<Question>();
        }
    }

    static void AskQuestions(List<Question> questions)
    {
        int score = 0;
        int totalQuests = questions.Count;

        Console.WriteLine("Enter how many seconds you want for each question (default is 3s): ");
        string timeLimitInput = Console.ReadLine();
        int timeLimit = string.IsNullOrEmpty(timeLimitInput) ? 3 : int.Parse(timeLimitInput);

        QuizState state = LoadQuizState();
        if (state == null)
        {
            state = new QuizState();
        }

        List<string> answeredQuestions = state.AnsweredQuestions;
        int currentQuestion = state.CurrentQuestion;

        List<Question> remainingQuestions = questions
            .Where(q => !answeredQuestions.Contains(q.question))
            .OrderBy(_ => Guid.NewGuid()) 
            .ToList();

        foreach (var question in remainingQuestions.Skip(currentQuestion))
        {
            Console.WriteLine($"{question.question}");
            Console.WriteLine();

            Timer timer = new Timer(_ =>
            {
                Console.WriteLine("Time's up!");
                Console.WriteLine($"Current Score: {score}/{totalQuests}");
            }, null, timeLimit * 1000, Timeout.Infinite);

            if (question.choices == null)
            {
                Console.Write("Please enter your answer: ");
                string inputFITB = Console.ReadLine();

                timer.Change(Timeout.Infinite, Timeout.Infinite); 

                if (question.correctAnswer.ToLower().Equals(inputFITB.ToLower()))
                {
                    Console.WriteLine($"Correct!");
                    score++;
                    Console.WriteLine($"Current Score: {score}/{totalQuests}");
                }
                else
                {
                    Console.WriteLine($"Wrong!");
                    Console.WriteLine($"Current Score: {score}/{totalQuests}");
                }
            }
            else
            {
                for (int j = 0; j < question.choices.Count; j++)
                {
                    Console.WriteLine($"{j + 1}. {question.choices[j]}");
                }

                Console.WriteLine();

                Console.Write("Please enter the number of your answer: ");
                var input = Console.ReadLine();
                int answerIndex;

                timer.Change(Timeout.Infinite, Timeout.Infinite); 

                if (int.TryParse(input, out answerIndex) && answerIndex >= 1 && answerIndex <= question.choices.Count)
                {
                    if (question.choices[answerIndex - 1] == question.correctAnswer)
                    {
                        Console.WriteLine("Correct!");
                        score++;
                        Console.WriteLine($"Current Score: {score}/{totalQuests}");
                    }
                    else
                    {
                        Console.WriteLine($"Wrong!");
                        Console.WriteLine($"Current Score: {score}/{totalQuests}");
                    }
                }
                else
                {
                    Console.WriteLine("Invalid input. Please enter a number between 1 and the number of choices.");
                }
                Console.WriteLine();
            }

            answeredQuestions.Add(question.question);
            state = new QuizState
            {
                CurrentQuestion = currentQuestion + 1,
                Score = score,
                AnsweredQuestions = answeredQuestions
            };
            SaveQuizState(state);

            Console.WriteLine("Do you want to quit and save progress? (y/n)");
            string quitInput = Console.ReadLine();
            if (quitInput.ToLower() == "y")
            {
                break;
            }
        }

        Console.WriteLine($"Total correct: {score}");
        Console.WriteLine($"Percentage: {(score * 100.0) / totalQuests}%");

        SaveQuizState(null);
    }

    static void SaveQuizState(QuizState state)
    {
        try
        {
            string stateJson = JsonConvert.SerializeObject(state);
            File.WriteAllText("quiz_state.json", stateJson);
        }
        catch (Exception e)
        {
            Console.WriteLine($"Error saving state: {e.Message}");
        }
    }

    static QuizState LoadQuizState()
    {
        try
        {
            string fileData = File.ReadAllText("quiz_state.json");
            QuizState state = JsonConvert.DeserializeObject<QuizState>(fileData);
            return state;
        }
        catch (Exception)
        {
            return null;
        }
    }
}

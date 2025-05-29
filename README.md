# The Quiz Whiz 
<h3>AI Application that allows users to generate quizzes based on uploaded PDF's.</h3>

<img src="../res/chat.gif" alt="Demonstration" />

## Features
<ol>
  <h3><li>Allows Users to Choose Question Type</li></h3>
  It allows the users to choose the question type using checkboxes and select one or more types from Multiple Choice, True/False, and Short Answer. The Checkboxes are shown using:
  <pre><code>question_types = gr.CheckboxGroup(
choices=["Multiple Choice", "True/False", "Short Answer"],
label="Select Question Types")</code></pre>
And actually put to action(using them in the quiz) using this line in the system prompt:
  <pre><code>"Generate different types of questions including multiple-choice, true/false, short answer, and essay."</code></pre>
And also shown using this line in the <code>chat_with_ai</code> function with this code:
  <pre><code>selected_types = ", ".join(question_types) if question_types else "any"</code></pre>

  <h3><li>Allows Users to Choose Question Number</li></h3>
  It also allows the users to choose the number of questions using a slider and select from 1 - 50.
  The slider is shown in the website using:
  <pre><code><mark>num_questions</mark> = gr.Slider(minimum=1, maximum=50, step=1, value=10, label="Number of Questions")</code></pre>
It is implemented using this line in the <code>chat_with_ai</code> function in the message area with this code:
  <pre><code>message = f"Generate a quiz with <mark>{num_questions}</mark> questions. Question types: {selected_types}. Difficulty levels: {difficulties}"</code></pre>

  <h3><li>Allows Users to Choose Difficulty Level</li></h3>
  Allows the users to choose the difficulty level of questions using Gradio's Radio option, which is a button that only allows you to select one option, and select from Easy, Medium, or Hard.
  The radio is shown in the website using:
  <pre><code>difficulty_levels = gr.Radio(
    choices=["Easy", "Medium", "Hard"],
    label="Select Difficulty Level"
)</code></pre>
It is declared using this line in the <code>chat_with_ai</code> function with this code:
  <pre><code>difficulties = ", ".join(difficulty_levels) if difficulty_levels else "any"</code></pre>
</ol>

## How to Get Started
> **Step 1:** Download the <code>main.py</code> and the two other pictures(logo.jpeg, favicon.ico).  
If you are using VS Code, make sure to put the pictures into the Explorer. If you are using another editor, write the file path in the code.

> **Step 2:** Paste your OpenAI API key in the <code>"YOUR_API_KEY"</code> area.

> **Step 3:** <code>pip install</code> required dependencies.
<pre><code>pip install openai</code></pre>
<pre><code>pip install llama-index</code></pre>
<pre><code>pip install gradio</code></pre>
<pre><code>pip install fpdf</code></pre>

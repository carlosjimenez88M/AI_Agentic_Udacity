### Chaining Prompts with Python


Implementing a Prompt Chain in Python
At its core, prompt chaining is simply about managing strings and making sequential API calls. We're going to build a complete prompt chain from scratch using basic Python to show you how it works.

Our Goal: We'll implement the "Data Analysis Script Generation" use case. Our agent will create a Python script that reads a CSV, calculates an average, and writes the result to a new file.

Step 1: Generate the Outline
First, we need the AI to create a high-level plan. We'll give it the role of a programming assistant and ask it for a step-by-step outline.


```python
# --- Setup (assumes get_completion function is defined) ---
# from openai import OpenAI
# client = OpenAI(...)
# def get_completion(prompt):
#     

# --- Step 1: Generate the Outline ---

# The first prompt in our chain
prompt_step1 = """
You are a helpful programming assistant.

I need a Python script to read a CSV file named 'input_data.csv',
calculate the average of a column named 'value', and write the
average to a new file named 'output.txt'.

Please provide a simple, step-by-step outline for this script.
"""

print("--- Calling AI for Step 1: Outline Generation ---")
outline_response = get_completion(prompt_step1)

print("\n--- AI-Generated Outline ---")
print(outline_response)
```

Likely Output from Step 1:

```python
--- AI-Generated Outline ---
Here is a step-by-step outline for your script:
1. Import the necessary libraries (csv).
2. Open and read the 'input_data.csv' file.
3. Extract the 'value' column and convert the values to numbers.
4. Calculate the average of the values.
5. Create and open a new file called 'output.txt'.
6. Write the calculated average to 'output.txt'.
```

### Step 2: Generate the Code from the Outline
Now for the key step in prompt chaining. We will take the outline_response from the previous step and programmatically insert it into our next prompt.

```python
# --- Step 2: Generate the Code ---


# The second prompt, which USES the output from the first
prompt_step2 = f"""
You are a helpful programming assistant.

Based on the following outline, please write the complete Python code for the script.
Ensure you use standard libraries and include comments.

Outline:
---
{outline_response}
---
"""

print("\n--- Calling AI for Step 2: Code Generation ---")
code_response = get_completion(prompt_step2)

print("\n--- AI-Generated Python Code ---")
print(code_response)

```

Likely Output from Step 2:

```python
# --- AI-Generated Python Code ---
import csv

def analyze_data():
    """
    Reads data from input_data.csv, calculates the average of the 'value' column,
    and writes the result to output.txt.
    """
    values = []
    # 1 & 2. Read the CSV file and extract values
    try:
        with open('input_data.csv', mode='r') as infile:
            reader = csv.DictReader(infile)
            for row in reader:
                # 3. Convert to number
                values.append(float(row['value']))
    except FileNotFoundError:
        print("Error: input_data.csv not found.")
        return

    # 4. Calculate the average
    if values:
        average = sum(values) / len(values)
    else:
        average = 0

    # 5 & 6. Write the result to the output file
    with open('output.txt', mode='w') as outfile:
        outfile.write(f"The average is: {average}")

    print("Analysis complete. Check output.txt for the result.")

# Run the analysis
analyze_data()
```



### Step 3: The "Gate Check"

Our chain worked! But what if the AI had made a syntax error? A reliable system needs validation. We can create a "gate check" using Python's built-in ast (Abstract Syntax Tree) library to check the code's syntax without running it.


```python
import ast

def check_python_syntax(code):
    """Checks for syntax errors in a string of Python code."""
    try:
        ast.parse(code)
        return True, "No syntax errors found."
    except SyntaxError as e:
        return False, f"Syntax Error: {e}"

# Run our gate check on the generated code
is_valid, message = check_python_syntax(code_response)

print(f"\n--- Gate Check Result ---")
print(f"Code is valid: {is_valid}")
print(message)

```

If is_valid were False, we would proceed to an optional third step in our chain: asking the AI to fix its own mistake by feeding the code and the error message back to it.

This demonstration shows the core logic of prompt chaining:

Break a task into steps.
Use the output of one prompt as the input for the next.
Add programmatic checks ("gate checks") between steps to ensure reliability.



Pydantic: Creating Structured Data for AI Agents
As we start to build more complex, multi-step agents, we run into a fundamental challenge. The natural output of a Large Language Model is just a string of text. While this is great for conversation, it's not ideal for building reliable applications.

Imagine you ask an AI to extract a user's name and order number from an email. It might respond with:

"The user is Alex and their order is #8675309."
"Alex's order number is 8675309."
"Order: 8675309, Name: Alex"
All of these are correct, but their inconsistent structure makes them very difficult for another program to use. If a downstream system is expecting a specific format, these variations will cause it to break.

To build agents, we need to control and standardize their output. The most common way to do this is to instruct the LLM to respond in a structured format like JSON. This is where a powerful Python library called Pydantic(opens in a new tab) becomes useful.

What is a Pydantic Model?
Think of a Pydantic model as a blueprint or schema for your data. It's a simple Python class where you define the exact "shape" of the data you expect. You define each field you want, its data type (like str, int, bool), and whether it's required or optional.

Pydantic then does two magical things for us:

Data Validation: It automatically validates incoming data (like the JSON from an LLM) against your model. If the data is malformed, has the wrong data types, or is missing a required field, Pydantic will raise a clear error. This makes it perfect for creating the gate checks in our prompt chains.
Data Parsing: If the data is valid, Pydantic parses it into a clean, accessible Python object. You can then access the data with standard dot notation (e.g., my_object.user_id), making your code cleaner and less error-prone.
How to Create a Pydantic Model: An Example
Creating a Pydantic model is straightforward. You create a class that inherits from BaseModel. Let's create a model for a simple user profile.

```python
# First, we import the necessary components from the Pydantic library
from pydantic import BaseModel, Field
from typing import Optional

# Now, we define our model as a Python class
class UserProfile(BaseModel):
    """A model to hold structured information about a user."""

    # This is a required field of type integer.
    # The `Field` function lets us add a description.
    user_id: int = Field(..., description="The unique identifier for the user.")

    # This is a required field of type string.
    username: str = Field(..., description="The user's public username.")

    # This is a required boolean field.
    is_active: bool = Field(..., description="Whether the user's account is currently active.")

    # This is an optional field. If it's not present, its value will be None.
    email: Optional[str] = Field(None, description="The user's email address, if available.")

```

In our agentic workflows, we will use these models in two key ways:

In the Prompt: We can provide the model's schema (its field names and descriptions) as context in our prompt to the LLM. This tells the LLM exactly what JSON structure we expect it to generate.
In the Gate Check: We use the same Pydantic model in our Python code to parse and validate the LLM's JSON response, ensuring it followed our instructions before we pass its output to the next step in a chain.
By using Pydantic, we make our agent's communication much more reliable and predictable.
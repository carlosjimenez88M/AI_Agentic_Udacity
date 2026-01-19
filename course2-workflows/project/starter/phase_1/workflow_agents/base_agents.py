# Import the OpenAI class for interfacing with OpenAI's API
# This provides access to chat completions, embeddings, and other AI capabilities
from openai import OpenAI
import numpy as np
import pandas as pd
import re
import csv
import uuid
from datetime import datetime

# DirectPromptAgent class definition
# EDUCATIONAL NOTE: This is the simplest agent pattern - a baseline for comparison with more sophisticated approaches.
# It demonstrates basic LLM prompting without any augmentation, persona, or knowledge injection.
# WHY THIS WORKS: The LLM uses only its pre-trained knowledge to respond, making it useful for general queries
# but potentially unreliable for domain-specific or factual questions where hallucination is a concern.
class DirectPromptAgent:
    """
    A basic agent that sends prompts directly to the LLM without any augmentation.
    This serves as a baseline to compare against more sophisticated agent patterns.
    """

    def __init__(self, openai_api_key):
        """
        Initialize the DirectPromptAgent.

        Parameters:
        openai_api_key (str): API key for accessing OpenAI services
        """
        # Store the API key as an instance attribute for use in the respond method
        self.openai_api_key = openai_api_key

    def respond(self, prompt):
        """
        Generate a response using the OpenAI API with no system prompt or augmentation.

        Parameters:
        prompt (str): The user's input query

        Returns:
        str: The LLM's response based solely on the user prompt
        """
        # Create OpenAI client using the stored API key
        client = OpenAI(api_key=self.openai_api_key)

        # Call the chat completions API with gpt-3.5-turbo
        # IMPORTANT: Note that we only pass the user message - no system prompt
        # This means the LLM has no specific instructions about how to behave
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using GPT-3.5 for cost-effectiveness
            messages=[
                {"role": "user", "content": prompt}  # Only the user's prompt, no system context
            ],
            temperature=0  # Temperature=0 for deterministic, consistent responses
        )

        # Extract and return only the text content from the response object
        # The response structure is: response.choices[0].message.content
        return response.choices[0].message.content
        
# AugmentedPromptAgent class definition
# EDUCATIONAL NOTE: This agent demonstrates persona-based behavior modification through system prompts.
# WHY THIS MATTERS: Personas shape how the LLM interprets and responds to queries by establishing
# a specific role, expertise level, and communication style. This is crucial for creating specialized agents.
# CONTEXT ISOLATION: The "forget previous context" instruction ensures each interaction is independent,
# preventing cross-contamination between unrelated queries in a conversation.
class AugmentedPromptAgent:
    """
    An agent that uses a system-level persona to modify LLM behavior and response style.
    The persona establishes the agent's role, expertise, and communication approach.
    """

    def __init__(self, openai_api_key, persona):
        """
        Initialize the AugmentedPromptAgent with API credentials and a persona.

        Parameters:
        openai_api_key (str): API key for accessing OpenAI services
        persona (str): A description of the agent's role and expertise (e.g., "You are a Product Manager...")
        """
        # Store the persona that defines this agent's behavioral characteristics
        self.persona = persona
        # Store the API key for OpenAI authentication
        self.openai_api_key = openai_api_key

    def respond(self, input_text):
        """
        Generate a response using the OpenAI API with persona-based system prompt.

        Parameters:
        input_text (str): The user's input query

        Returns:
        str: The LLM's response influenced by the defined persona
        """
        # Create OpenAI client using the stored API key
        client = OpenAI(api_key=self.openai_api_key)

        # CHAIN OF THOUGHT ENHANCEMENT: The system prompt instructs the LLM to:
        # 1. Assume the specified persona role
        # 2. Forget any previous context (ensuring clean state)
        # 3. Respond according to the persona's expertise and style
        system_prompt = f"{self.persona} Forget all previous context and respond to this query as this persona."

        # Call the OpenAI API with both system and user messages
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},  # Persona instruction at system level
                {"role": "user", "content": input_text}  # User's actual query
            ],
            temperature=0  # Deterministic responses for consistency
        )

        # Extract and return only the text content from the response
        return response.choices[0].message.content

# KnowledgeAugmentedPromptAgent class definition
# EDUCATIONAL NOTE: This agent demonstrates knowledge grounding - a critical technique for preventing hallucination.
# WHY THIS WORKS: By injecting specific domain knowledge into the system prompt and instructing the LLM to
# use ONLY that knowledge, we ensure responses are factually grounded in provided information rather than
# the model's potentially outdated or incorrect pre-trained knowledge.
# KEY BENEFIT: This approach is ideal for domain-specific applications where accuracy is paramount
# (e.g., product documentation, technical support, compliance-sensitive contexts).
class KnowledgeAugmentedPromptAgent:
    """
    An agent that combines persona with domain-specific knowledge to generate grounded responses.
    This prevents hallucination by constraining the LLM to use only provided knowledge.
    """

    def __init__(self, openai_api_key, persona, knowledge):
        """
        Initialize the KnowledgeAugmentedPromptAgent with credentials, persona, and knowledge base.

        Parameters:
        openai_api_key (str): API key for accessing OpenAI services
        persona (str): A description of the agent's role and expertise
        knowledge (str): Domain-specific information the agent should use exclusively for responses
        """
        # Store the persona that defines behavioral characteristics
        self.persona = persona
        # Store the knowledge base that constrains and grounds responses
        self.knowledge = knowledge
        # Store the API key for OpenAI authentication
        self.openai_api_key = openai_api_key

    def respond(self, input_text):
        """
        Generate a response using the OpenAI API, grounded in provided knowledge.

        Parameters:
        input_text (str): The user's input query

        Returns:
        str: The LLM's response based exclusively on the provided knowledge
        """
        # Create OpenAI client using the stored API key
        client = OpenAI(api_key=self.openai_api_key)

        # CHAIN OF THOUGHT ENHANCEMENT: The system prompt implements a structured reasoning process:
        # 1. Read the question carefully
        # 2. Search the provided knowledge for relevant information
        # 3. Think step-by-step about how to answer using ONLY that knowledge
        # 4. Structure the answer clearly and cite the knowledge
        # 5. Do NOT use the model's own pre-trained knowledge
        system_prompt = (
            f"You are a {self.persona} knowledge-based assistant. Forget all previous context.\n\n"
            f"IMPORTANT: Use only the following knowledge to answer, do not use your own knowledge:\n\n"
            f"{self.knowledge}\n\n"
            f"INSTRUCTIONS:\n"
            f"- Read the question carefully\n"
            f"- Search the knowledge above for relevant information\n"
            f"- Think step-by-step about how to answer using ONLY the provided knowledge\n"
            f"- Structure your answer clearly\n"
            f"- Answer the prompt based on this knowledge, not your own."
        )

        # Call the OpenAI API with knowledge-grounded system prompt and user query
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},  # Knowledge-grounded instructions
                {"role": "user", "content": input_text}  # User's query
            ],
            temperature=0  # Deterministic for consistency
        )

        # Extract and return only the text content from the response
        return response.choices[0].message.content

# RAGKnowledgePromptAgent class definition
class RAGKnowledgePromptAgent:
    """
    An agent that uses Retrieval-Augmented Generation (RAG) to find knowledge from a large corpus
    and leverages embeddings to respond to prompts based solely on retrieved information.
    """

    def __init__(self, openai_api_key, persona, chunk_size=2000, chunk_overlap=100):
        """
        Initializes the RAGKnowledgePromptAgent with API credentials and configuration settings.

        Parameters:
        openai_api_key (str): API key for accessing OpenAI.
        persona (str): Persona description for the agent.
        chunk_size (int): The size of text chunks for embedding. Defaults to 2000.
        chunk_overlap (int): Overlap between consecutive chunks. Defaults to 100.
        """
        self.persona = persona
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.openai_api_key = openai_api_key
        self.unique_filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.csv"

    def get_embedding(self, text):
        """
        Fetches the embedding vector for given text using OpenAI's embedding API.

        Parameters:
        text (str): Text to embed.

        Returns:
        list: The embedding vector.
        """
        client = OpenAI(base_url="https://openai.vocareum.com/v1", api_key=self.openai_api_key)
        response = client.embeddings.create(
            model="text-embedding-3-large",
            input=text,
            encoding_format="float"
        )
        return response.data[0].embedding

    def calculate_similarity(self, vector_one, vector_two):
        """
        Calculates cosine similarity between two vectors.

        Parameters:
        vector_one (list): First embedding vector.
        vector_two (list): Second embedding vector.

        Returns:
        float: Cosine similarity between vectors.
        """
        vec1, vec2 = np.array(vector_one), np.array(vector_two)
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    def chunk_text(self, text):
        """
        Splits text into manageable chunks, attempting natural breaks.

        Parameters:
        text (str): Text to split into chunks.

        Returns:
        list: List of dictionaries containing chunk metadata.
        """
        separator = "\n"
        text = re.sub(r'\s+', ' ', text).strip()

        if len(text) <= self.chunk_size:
            return [{"chunk_id": 0, "text": text, "chunk_size": len(text)}]

        chunks, start, chunk_id = [], 0, 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            if separator in text[start:end]:
                end = start + text[start:end].rindex(separator) + len(separator)

            chunks.append({
                "chunk_id": chunk_id,
                "text": text[start:end],
                "chunk_size": end - start,
                "start_char": start,
                "end_char": end
            })

            start = end - self.chunk_overlap
            chunk_id += 1

        with open(f"chunks-{self.unique_filename}", 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["text", "chunk_size"])
            writer.writeheader()
            for chunk in chunks:
                writer.writerow({k: chunk[k] for k in ["text", "chunk_size"]})

        return chunks

    def calculate_embeddings(self):
        """
        Calculates embeddings for each chunk and stores them in a CSV file.

        Returns:
        DataFrame: DataFrame containing text chunks and their embeddings.
        """
        df = pd.read_csv(f"chunks-{self.unique_filename}", encoding='utf-8')
        df['embeddings'] = df['text'].apply(self.get_embedding)
        df.to_csv(f"embeddings-{self.unique_filename}", encoding='utf-8', index=False)
        return df

    def find_prompt_in_knowledge(self, prompt):
        """
        Finds and responds to a prompt based on similarity with embedded knowledge.

        Parameters:
        prompt (str): User input prompt.

        Returns:
        str: Response derived from the most similar chunk in knowledge.
        """
        prompt_embedding = self.get_embedding(prompt)
        df = pd.read_csv(f"embeddings-{self.unique_filename}", encoding='utf-8')
        df['embeddings'] = df['embeddings'].apply(lambda x: np.array(eval(x)))
        df['similarity'] = df['embeddings'].apply(lambda emb: self.calculate_similarity(prompt_embedding, emb))

        best_chunk = df.loc[df['similarity'].idxmax(), 'text']

        client = OpenAI(base_url="https://openai.vocareum.com/v1", api_key=self.openai_api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You are {self.persona}, a knowledge-based assistant. Forget previous context."},
                {"role": "user", "content": f"Answer based only on this information: {best_chunk}. Prompt: {prompt}"}
            ],
            temperature=0
        )

        return response.choices[0].message.content

# EvaluationAgent class definition
# EDUCATIONAL NOTE: This agent implements the "Evaluator-Optimizer Pattern" - a powerful technique for
# iterative refinement and quality assurance in AI systems.
# WHY THIS WORKS: By separating generation (worker agent) from evaluation (this agent), we create a
# feedback loop that progressively improves output quality through multiple iterations.
# THIS IS A FORM OF "SELF-CRITIQUE": The system evaluates its own outputs against defined criteria
# and generates specific correction instructions, mimicking human review processes.
# KEY BENEFIT: This pattern dramatically improves output quality for structured tasks where specific
# criteria must be met (e.g., format requirements, completeness checks, style guidelines).
class EvaluationAgent:
    """
    An agent that implements iterative refinement through generate-evaluate-correct cycles.
    It manages a worker agent and validates outputs against defined criteria.
    """

    def __init__(self, openai_api_key, persona, evaluation_criteria, worker_agent, max_interactions):
        """
        Initialize the EvaluationAgent with credentials, persona, criteria, and worker agent.

        Parameters:
        openai_api_key (str): API key for accessing OpenAI services
        persona (str): The evaluator's role description
        evaluation_criteria (str): Specific criteria that responses must meet
        worker_agent: The agent whose outputs will be evaluated (must have a respond() method)
        max_interactions (int): Maximum number of refinement iterations before accepting current output
        """
        # Store all initialization parameters as instance attributes
        self.openai_api_key = openai_api_key
        self.persona = persona
        self.evaluation_criteria = evaluation_criteria
        self.worker_agent = worker_agent
        self.max_interactions = max_interactions

    def evaluate(self, initial_prompt):
        """
        Execute the iterative refinement loop: generate → evaluate → refine → repeat.

        WORKFLOW:
        1. Worker agent generates initial response
        2. Evaluator checks response against criteria
        3. If approved → return final response
        4. If not approved → generate correction instructions
        5. Worker agent refines based on feedback
        6. Repeat until approved or max iterations reached

        Parameters:
        initial_prompt (str): The original user query to process

        Returns:
        dict: Contains 'final_response', 'evaluation', and 'iterations'
        """
        # Create OpenAI client for evaluation and correction generation
        client = OpenAI(api_key=self.openai_api_key)
        prompt_to_evaluate = initial_prompt

        # ITERATIVE REFINEMENT LOOP: Up to max_interactions attempts
        for i in range(self.max_interactions):
            print(f"\n--- Interaction {i+1} ---")

            # STEP 1: GENERATION - Worker agent produces a response
            print(" Step 1: Worker agent generates a response to the prompt")
            print(f"Prompt:\n{prompt_to_evaluate}")
            response_from_worker = self.worker_agent.respond(prompt_to_evaluate)
            print(f"Worker Agent Response:\n{response_from_worker}")

            # STEP 2: EVALUATION - Check response against criteria
            print(" Step 2: Evaluator agent judges the response")
            # CHAIN OF THOUGHT ENHANCEMENT: Evaluator thinks step-by-step about each criterion
            eval_prompt = (
                f"Think step-by-step: Compare each part of the following answer against the criteria.\n\n"
                f"Answer: {response_from_worker}\n\n"
                f"Criteria: {self.evaluation_criteria}\n\n"
                f"Check if ALL criteria are met. Identify specific issues if any.\n"
                f"Respond with 'Yes' or 'No' at the start, followed by the reason why it does or doesn't meet the criteria."
            )
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": self.persona},
                    {"role": "user", "content": eval_prompt}
                ],
                temperature=0
            )
            evaluation = response.choices[0].message.content.strip()
            print(f"Evaluator Agent Evaluation:\n{evaluation}")

            # STEP 3: APPROVAL CHECK - Does response meet criteria?
            print(" Step 3: Check if evaluation is positive")
            if evaluation.lower().startswith("yes"):
                print("✅ Final solution accepted.")
                # Return successful result with final response and metadata
                return {
                    "final_response": response_from_worker,
                    "evaluation": evaluation,
                    "iterations": i + 1
                }
            else:
                # STEP 4: CORRECTION GENERATION - Create specific fix instructions
                print(" Step 4: Generate instructions to correct the response")
                # CHAIN OF THOUGHT ENHANCEMENT: Think about problems → identify fixes → provide concrete steps
                instruction_prompt = (
                    f"Identify the problems in the evaluation below, think about how to fix them, "
                    f"and provide concrete, actionable steps to correct the issues.\n\n"
                    f"Evaluation: {evaluation}"
                )
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": self.persona},
                        {"role": "user", "content": instruction_prompt}
                    ],
                    temperature=0
                )
                instructions = response.choices[0].message.content.strip()
                print(f"Instructions to fix:\n{instructions}")

                # STEP 5: FEEDBACK LOOP - Construct refinement prompt for worker agent
                print(" Step 5: Send feedback to worker agent for refinement")
                prompt_to_evaluate = (
                    f"The original prompt was: {initial_prompt}\n"
                    f"The response to that prompt was: {response_from_worker}\n"
                    f"It has been evaluated as incorrect.\n"
                    f"Make only these corrections, do not alter content validity: {instructions}"
                )

        # If max iterations reached without approval, return best attempt with warning
        print(f"\n⚠️ Max iterations ({self.max_interactions}) reached without full approval.")
        return {
            "final_response": response_from_worker,
            "evaluation": evaluation,
            "iterations": self.max_interactions
        }

# RoutingAgent class definition
# EDUCATIONAL NOTE: This agent demonstrates semantic routing using embeddings - a powerful alternative
# to traditional keyword-based or rule-based routing.
# WHY THIS WORKS: Embeddings capture the *meaning* of text in high-dimensional vector space, allowing
# the system to understand semantic similarity rather than relying on exact keyword matches.
# SUPERIORITY OVER KEYWORD MATCHING: This approach handles synonyms, paraphrasing, and context naturally.
# For example, "create user stories" and "define personas" would route similarly despite different words.
# KEY TECHNIQUE: Cosine similarity measures the angle between embedding vectors, providing a score
# of how closely two pieces of text align in meaning (0=unrelated, 1=identical meaning).
class RoutingAgent():
    """
    An agent that uses semantic similarity (via embeddings) to route queries to specialized agents.
    This enables intelligent dispatching based on meaning rather than keywords.
    """

    def __init__(self, openai_api_key, agents):
        """
        Initialize the RoutingAgent with credentials and a list of agent configurations.

        Parameters:
        openai_api_key (str): API key for accessing OpenAI services
        agents (list): List of agent dictionaries, each containing:
            - 'name': Agent identifier
            - 'description': Semantic description of agent's expertise/purpose
            - 'func': Function to execute when this agent is selected
        """
        # Store API key for authentication
        self.openai_api_key = openai_api_key
        # Store the list of available agents with their descriptions and functions
        self.agents = agents

    def get_embedding(self, text):
        """
        Calculate the embedding vector for given text using OpenAI's embedding model.

        TECHNICAL NOTE: text-embedding-3-large produces 3072-dimensional vectors that
        capture semantic meaning. Similar texts produce similar vectors.

        Parameters:
        text (str): Text to convert into an embedding vector

        Returns:
        list: The embedding vector (3072 dimensions)
        """
        # Create OpenAI client
        client = OpenAI(api_key=self.openai_api_key)

        # Call the embeddings API to convert text into a vector representation
        response = client.embeddings.create(
            model="text-embedding-3-large",  # High-quality embedding model
            input=text,
            encoding_format="float"
        )

        # Extract and return the embedding vector from the response
        embedding = response.data[0].embedding
        return embedding

    def route(self, user_input):
        """
        Route a user query to the most appropriate agent based on semantic similarity.

        ALGORITHM:
        1. Compute embedding of user input
        2. Compute embeddings of all agent descriptions
        3. Calculate cosine similarity between input and each agent description
        4. Select agent with highest similarity score
        5. Execute that agent's function with the input

        Parameters:
        user_input (str): The user's query/request to route

        Returns:
        The result from executing the best-matched agent's function
        """
        # STEP 1: Compute the embedding of the user's input query
        input_emb = self.get_embedding(user_input)

        # Initialize tracking variables for best agent selection
        best_agent = None
        best_score = -1  # Cosine similarity ranges from -1 to 1

        # STEP 2-4: Evaluate each agent's suitability
        print("\n[Routing Agent] Evaluating agent matches...")
        for agent in self.agents:
            # Compute the embedding of this agent's description
            agent_emb = self.get_embedding(agent["description"])

            # Handle edge case where embedding generation fails
            if agent_emb is None:
                continue

            # COSINE SIMILARITY: Measures semantic alignment between query and agent expertise
            # Formula: dot(A,B) / (||A|| * ||B||)
            # Result ranges from -1 (opposite) to 1 (identical meaning)
            similarity = np.dot(input_emb, agent_emb) / (np.linalg.norm(input_emb) * np.linalg.norm(agent_emb))

            # EDUCATIONAL TRANSPARENCY: Show similarity scores for all agents
            print(f"  - {agent['name']}: {similarity:.3f}")

            # STEP 5: Track the best-matching agent
            if similarity > best_score:
                best_score = similarity
                best_agent = agent

        # Error handling: No suitable agent found
        if best_agent is None:
            return "Sorry, no suitable agent could be selected."

        # Log the routing decision for transparency
        print(f"\n[Router] ✓ Selected: {best_agent['name']} (similarity score: {best_score:.3f})")

        # Execute the selected agent's function with the user input
        return best_agent["func"](user_input)

# ActionPlanningAgent class definition
# EDUCATIONAL NOTE: This agent demonstrates workflow decomposition - breaking down high-level goals
# into sequential, actionable steps using domain knowledge.
# WHY THIS WORKS: By providing the agent with a knowledge hierarchy (e.g., Stories → Features → Tasks),
# it can reason about the logical sequence of steps required to achieve a complex objective.
# KEY PATTERN: This implements "goal-oriented decomposition" where the LLM uses structured knowledge
# to identify the intermediate stages between the current state and the desired end state.
# REAL-WORLD APPLICATION: This pattern is used in task planning, project management, workflow automation,
# and any domain where complex processes need to be broken into manageable steps.
class ActionPlanningAgent:
    """
    An agent that decomposes high-level requests into sequential workflow steps using domain knowledge.
    This enables automatic workflow orchestration based on goal analysis.
    """

    def __init__(self, openai_api_key, knowledge):
        """
        Initialize the ActionPlanningAgent with credentials and domain knowledge.

        Parameters:
        openai_api_key (str): API key for accessing OpenAI services
        knowledge (str): Domain-specific knowledge about workflow structures, hierarchies, and processes
        """
        # Store API key for authentication
        self.openai_api_key = openai_api_key
        # Store knowledge that defines the workflow hierarchy and available steps
        self.knowledge = knowledge

    def extract_steps_from_prompt(self, prompt):
        """
        Analyze a high-level request and extract the sequential steps needed to accomplish it.

        CHAIN OF THOUGHT ENHANCEMENT: The system prompt guides the LLM through structured reasoning:
        1. Analyze the request to identify the end goal
        2. Consult the knowledge hierarchy to understand available workflow stages
        3. Determine which stages are required to reach the goal
        4. List only the steps that exist in the knowledge base
        5. Return steps in logical execution order

        Parameters:
        prompt (str): A high-level request or goal (e.g., "What would the development tasks be?")

        Returns:
        list: Sequential list of workflow steps extracted from the prompt
        """
        # STEP 1: Create OpenAI client
        client = OpenAI(api_key=self.openai_api_key)

        # STEP 2: Construct system prompt with COT reasoning instructions
        # This prompt combines:
        # - Role definition (action planning agent)
        # - Task instruction (extract steps from user prompt)
        # - Knowledge grounding (use only provided knowledge)
        # - COT reasoning (analyze step-by-step, consult hierarchy, determine stages)
        system_prompt = (
            f"You are an action planning agent. Using your knowledge, you extract from the user prompt "
            f"the steps requested to complete the action the user is asking for.\n\n"
            f"REASONING PROCESS:\n"
            f"1. Analyze the request step-by-step to identify the end goal\n"
            f"2. Consult the knowledge hierarchy below to understand the workflow structure\n"
            f"3. Determine which stages are required to achieve the goal\n"
            f"4. List only the steps that exist in your knowledge\n"
            f"5. Return the steps in logical execution order\n\n"
            f"You return the steps as a list. Only return the steps in your knowledge. "
            f"Forget any previous context.\n\n"
            f"This is your knowledge:\n{self.knowledge}"
        )

        # STEP 3: Call OpenAI API with action planning instructions
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0  # Deterministic for consistent workflow planning
        )

        # STEP 4: Extract the response text from the API response
        response_text = response.choices[0].message.content

        # STEP 5: Clean and format the extracted steps
        # Split on newlines to get individual steps
        raw_steps = response_text.split("\n")

        # Filter out empty lines and clean up whitespace
        # Remove any step numbering or bullet points (e.g., "1. ", "- ", etc.)
        steps = []
        for step in raw_steps:
            # Strip whitespace
            cleaned_step = step.strip()
            # Skip empty lines
            if not cleaned_step:
                continue
            # Remove common list prefixes (numbers, bullets, dashes)
            # This regex handles formats like "1. ", "1) ", "- ", "* ", etc.
            import re
            cleaned_step = re.sub(r'^[\d\.\)\-\*\s]+', '', cleaned_step)
            # Only add non-empty steps
            if cleaned_step:
                steps.append(cleaned_step)

        return steps
import os
import asyncio
import logging
from typing import List, Optional
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# --- 1. CONFIGURACIÓN DE ENTORNO Y OBSERVABILIDAD ---
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("CulinaryOrchestrator")

# --- 2. DEFINICIÓN DE CONTRATOS DE DATOS (PYDANTIC) ---

# Salida del CHEF (Generator)
# Incluimos 'thought_process' para forzar el Chain of Thought antes del resultado final.
class NutritionalInfo(BaseModel):
    calories_per_serving: int
    protein_grams: float
    is_gluten_free: bool
    is_vegan: bool

class ChefRecipe(BaseModel):
    thought_process: str = Field(description="Step-by-step reasoning on how you selected ingredients to meet constraints.")
    dish_name: str
    ingredients: List[str]
    instructions: List[str]
    nutrition: NutritionalInfo

# Salida del AUDITOR (Evaluator)
class AuditResult(BaseModel):
    is_approved: bool = Field(description="True only if ALL constraints are strictly met.")
    feedback: str = Field(description="Specific feedback on what failed (e.g., 'Protein is only 10g, needed 15g').")
    score: int = Field(description="Quality score from 1-10.")

# --- 3. AGENTE GENERADOR (OPTIMIZER - THE CHEF) ---
class AsyncRecipeChef:
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def create_recipe(self, request_data: dict, feedback: Optional[str] = None) -> ChefRecipe:
        constraints = "\n".join([f"- {c}" for c in request_data['constraints']])
        base_dish = request_data['base_dish']
        
        system_msg = (
            "You are a Molecular Gastronomy Chef specializing in dietary restrictions. "
            "You must solve complex nutritional puzzles. "
            "First, THINK step-by-step in the 'thought_process' field about how to substitute ingredients "
            "to meet the constraints (especially protein vs calories). Then generate the recipe."
        )

        user_prompt = f"""
        Create a recipe for: {base_dish}
        
        STRICT CONSTRAINTS:
        {constraints}
        """

        # Inyección de Feedback (El núcleo del patrón Optimizer)
        if feedback:
            logger.info("👨‍🍳 Chef is revising the recipe based on feedback...")
            user_prompt += f"\n\n🚨 CRITICAL FEEDBACK FROM PREVIOUS ATTEMPT:\n{feedback}\n\nFIX THESE ISSUES IMMEDIATELY."

        response = await self.client.beta.chat.completions.parse(
            model="gpt-4o", # Necesario para Structured Outputs
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_prompt}
            ],
            response_format=ChefRecipe,
            temperature=0.7 
        )
        return response.choices[0].message.parsed

# --- 4. AGENTE EVALUADOR (VALIDATOR - THE AUDITOR) ---
class AsyncNutritionalAuditor:
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def audit_recipe(self, recipe: ChefRecipe, original_constraints: List[str]) -> AuditResult:
        logger.info("📋 Auditing recipe against constraints...")
        
        constraints_str = "\n".join(original_constraints)
        
        system_msg = (
            "You are a strict Nutritional Auditor. "
            "Your job is to verify if a recipe MATHEMATICALLY matches the requirements. "
            "Do not trust the Chef's claims blindly; analyze the ingredients list for hidden allergens (like coconut derivatives)."
        )

        # Le pasamos al auditor la receta estructurada JSON para que la analice
        user_prompt = f"""
        AUDIT THIS RECIPE:
        Name: {recipe.dish_name}
        Ingredients: {recipe.ingredients}
        Chef's Stated Nutrition: {recipe.nutrition}
        
        AGAINST THESE CONSTRAINTS:
        {constraints_str}
        
        Task:
        1. Check if ingredients violate 'vegan', 'gluten-free' or 'no coconut'.
        2. Check if the protein/calorie math seems plausible for these ingredients.
        """

        response = await self.client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_prompt}
            ],
            response_format=AuditResult,
            temperature=0.0 # Determinismo máximo para el juez
        )
        return response.choices[0].message.parsed

# --- 5. ORQUESTADOR (WORKFLOW LOOP) ---
async def run_recipe_workflow(request_data: dict, max_retries: int = 5):
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    chef = AsyncRecipeChef(client)
    auditor = AsyncNutritionalAuditor(client)

    feedback = None
    
    print(f"\n🥘 STARTING WORKFLOW FOR: {request_data['base_dish'].upper()}\n")

    for i in range(max_retries):
        logger.info(f"--- Iteration {i+1}/{max_retries} ---")
        
        # 1. GENERAR (Con CoT implícito en el modelo Pydantic)
        recipe_draft = await chef.create_recipe(request_data, feedback)
        
        # Mostrar el "Chain of Thought" del Chef (Observabilidad)
        print(f"\n💭 Chef's Reasoning (Iter {i+1}): {recipe_draft.thought_process[:200]}...")
        print(f"   Dish Proposed: {recipe_draft.dish_name}")
        
        # 2. EVALUAR
        audit_result = await auditor.audit_recipe(recipe_draft, request_data['constraints'])
        
        # 3. VERIFICAR (Stopping Condition)
        if audit_result.is_approved:
            logger.info(f"✅ Recipe APPROVED. Score: {audit_result.score}/10")
            return recipe_draft
        
        # 4. LOOP DE FEEDBACK
        logger.warning(f"❌ Recipe REJECTED. Reason: {audit_result.feedback}")
        feedback = audit_result.feedback

    logger.error("💀 Max retries reached. The Chef could not satisfy the Auditor.")
    return None

# --- EJECUCIÓN ---
if __name__ == "__main__":
    # Solicitud compleja: Difícil balancear bajas calorías con alta proteína siendo vegano
    RECIPE_REQUEST = {
        "base_dish": "creamy pasta",
        "constraints": [
            "gluten-free",
            "vegan",
            "strictly under 450 calories per serving", # Restricción dura
            "high protein (>20g per serving)",        # Restricción dura
            "no coconut milk",                        # Trampa común para 'creamy vegan'
            "no cashew nuts"                          # Otra trampa común calórica
        ]
    }

    final_recipe = asyncio.run(run_recipe_workflow(RECIPE_REQUEST))
    
    if final_recipe:
        print("\n" + "="*40)
        print(f"🌟 FINAL APPROVED RECIPE: {final_recipe.dish_name}")
        print("="*40)
        print(f"📝 Ingredients: {final_recipe.ingredients}")
        print(f"📊 Nutrition: {final_recipe.nutrition}")
        print(f"🍳 Instructions: {len(final_recipe.instructions)} steps")
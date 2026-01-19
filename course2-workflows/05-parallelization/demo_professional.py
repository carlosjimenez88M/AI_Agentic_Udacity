import os
import asyncio
import logging
from typing import List, Dict
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# 1. OBSERVABILIDAD: Configuración de Logging profesional
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("Orchestrator")

load_dotenv()

# 2. CLIENTE ASÍNCRONO: Fundamental para High-Throughput
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 3. CONTRATOS DE DATOS (PYDANTIC): Estructura estricta de entrada/salida
class AgentOutput(BaseModel):
    agent_name: str
    content: str

class AgentConfig(BaseModel):
    name: str
    system_prompt: str
    temperature: float = 0.2

# Configuración de los agentes (Separación de Datos y Lógica)
AGENTS_CONFIG = [
    AgentConfig(
        name="Policy Expert",
        system_prompt="You are a policy expert in global energy policy and climate regulations."
    ),
    AgentConfig(
        name="Tech Expert",
        system_prompt="You are an expert in renewable energy, smart grids, and storage."
    ),
    AgentConfig(
        name="Market Analyst",
        system_prompt="You are an energy market analyst focused on investment and pricing."
    )
]

# 4. LÓGICA DEL AGENTE GENÉRICO + RESILIENCIA
class AsyncAgent:
    def __init__(self, config: AgentConfig):
        self.config = config

    # Decorador @retry: Maneja fallos transitorios automáticamente
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def process(self, user_prompt: str) -> AgentOutput:
        logger.info(f"Starting task for: {self.config.name}")
        
        try:
            # await: Cede el control al Event Loop mientras espera la respuesta (Non-blocking)
            response = await client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": self.config.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config.temperature
            )
            content = response.choices[0].message.content
            logger.info(f"Finished task for: {self.config.name}")
            
            return AgentOutput(agent_name=self.config.name, content=content)
            
        except Exception as e:
            logger.error(f"Error in {self.config.name}: {str(e)}")
            raise # Re-lanzar para que 'tenacity' capture y reintente

# 5. ORQUESTADOR (FAN-OUT / FAN-IN)
async def orchestrator(user_prompt: str):
    logger.info(f"Orchestrating parallel request: {user_prompt}")
    
    # Instanciar agentes
    agents = [AsyncAgent(cfg) for cfg in AGENTS_CONFIG]
    
    # --- FAN-OUT (Scatter) ---
    # asyncio.gather dispara todas las corutinas simultáneamente.
    # return_exceptions=True evita que un fallo en un agente mate todo el proceso.
    tasks = [agent.process(user_prompt) for agent in agents]
    results: List[AgentOutput | Exception] = await asyncio.gather(*tasks, return_exceptions=True)

    # Filtrado de errores (Graceful Degradation)
    valid_outputs = []
    for result in results:
        if isinstance(result, AgentOutput):
            valid_outputs.append(result)
        else:
            logger.error(f"Task failed with error: {result}")

    if not valid_outputs:
        return "System Error: All agents failed."

    # --- FAN-IN (Gather/Reduce) ---
    summary = await summarize_results(user_prompt, valid_outputs)
    return summary

async def summarize_results(user_prompt: str, outputs: List[AgentOutput]) -> str:
    # Construcción dinámica del contexto
    context_str = "\n\n".join([f"--- {out.agent_name} ---\n{out.content}" for out in outputs])
    
    final_prompt = (
        f"User Query: {user_prompt}\n\n"
        f"Expert Analyses:\n{context_str}\n\n"
        "Synthesize these insights into a strategic executive summary."
    )
    
    logger.info("Generating final summary...")
    response = await client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Chief Strategy Officer."},
            {"role": "user", "content": final_prompt}
        ]
    )
    return response.choices[0].message.content

# Punto de entrada Async
if __name__ == "__main__":
    prompt = "What are current trends shaping the future of the energy industry? response in spanish"
    
    # run() maneja el ciclo de vida del Event Loop
    final_result = asyncio.run(orchestrator(prompt))
    
    print("\n=== EXECUTIVE SUMMARY ===\n")
    print(final_result)
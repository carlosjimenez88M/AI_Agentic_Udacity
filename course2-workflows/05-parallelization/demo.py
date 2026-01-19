import os
from openai import OpenAI
from dotenv import load_dotenv

# Librería estándar para concurrencia en Python.
# CLAVE: Python usa un Global Interpreter Lock (GIL), pero para llamadas de red (I/O bound)
# como APIs, 'threading' es efectivo porque el GIL se libera mientras espera la respuesta HTTP.
import threading # correr los agentes en hilos o estados separados 

# Carga de variables de entorno (.env) para no hardcodear la API Key (Seguridad básica).
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"))

# EXPLICACIÓN: Estado Compartido (Shared State).
# Este diccionario actuará como la memoria colectiva donde cada hilo escribirá su resultado.
# En Python, las operaciones de escritura en diccionarios son atómicas (thread-safe) para
# asignaciones simples, por lo que no necesitamos un 'Lock' explícito en este caso simple.
agent_outputs = {}

# El prompt del usuario que activará toda la cadena.
user_prompt = "What are current trends shaping the future of the energy industry?"
print(f"Using parallel agents to answer prompt: {user_prompt}")

# --- DEFINICIÓN DE AGENTES ESPECIALISTAS ---

class PolicyAgent:
    def run(self, prompt):
        print(f"Policy Agent resolving prompt: {prompt}")
        # Llamada bloqueante a la API.
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                # SYSTEM PROMPT: Aquí definimos la "Persona".
                # Esto restringe el espacio latente del modelo para que solo conteste
                # desde la perspectiva de regulaciones y política.
                {"role": "system", "content": "You are a policy expert in global energy policy and climate regulations."},
                {"role": "user", "content": prompt}
            ],
            # Temperatura 0.7: Balance entre determinismo y creatividad.
            temperature=0.7
        )
        # SIDE-EFFECT: El agente no retorna el valor, lo inyecta en el diccionario global
        # usando una clave única ("policy") para evitar colisiones con otros hilos.
        agent_outputs["policy"] = response.choices[0].message.content

class TechnologyAgent:
    def run(self, prompt):
        print(f"Technology Agent resolving prompt: {prompt}")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                # SYSTEM PROMPT: Especialización en tecnología (Smart grids, storage).
                {"role": "system", "content": "You are an expert in renewable energy, smart grids, and energy storage technologies."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        # Escribe en su propia clave ("tech").
        agent_outputs["tech"] = response.choices[0].message.content

class MarketAgent:
    def run(self, prompt):
        print(f"Market Agent resolving prompt: {prompt}")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                # SYSTEM PROMPT: Especialización en finanzas y mercado.
                {"role": "system", "content": "You are an energy market analyst focused on global investment, pricing, and demand trends."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        # Escribe en su propia clave ("market").
        agent_outputs["market"] = response.choices[0].message.content

# --- AGENTE AGREGADOR (REDUCER) ---

class SummaryAgent:
    def run(self, prompt, inputs):
        # PROMPT ENGINEERING (Context Injection):
        # Aquí construimos dinámicamente el prompt final.
        # Concatenamos la pregunta original + las respuestas de los 3 agentes anteriores.
        # Esto se conoce como patrón "Map-Reduce" aplicado a LLMs.
        combined_prompt = (
            f"The user asked: '{prompt}'\n\n"
            f"Here are the expert responses:\n"
            f"- Policy Expert: {inputs['policy']}\n\n" # Recupera del dict compartido
            f"- Technology Expert: {inputs['tech']}\n\n"
            f"- Market Expert: {inputs['market']}\n\n"
            "Please summarize the combined insights into a single clear and concise response."
        )
        print(f"Summary Agent resolving prompt: {combined_prompt}")

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                # El rol aquí es de síntesis, no de generación de nueva información.
                {"role": "system", "content": "You are an energy strategist skilled at synthesizing expert insights."},
                {"role": "user", "content": combined_prompt}
            ],
            temperature=0.7
        )
        # Este agente SÍ retorna el valor directamente (flujo sincrónico final).
        return response.choices[0].message.content

# --- ORQUESTACIÓN (MAIN LOOP) ---

def main():
    # 1. Instanciación de objetos.
    policy_agent = PolicyAgent()
    tech_agent = TechnologyAgent()
    market_agent = MarketAgent()
    summary_agent = SummaryAgent()

    # 2. Creación de Hilos (Threads) - FASE "FAN-OUT"
    # Preparamos los hilos apuntando a la función .run de cada agente.
    # Pasamos los argumentos necesarios (la tupla args).
    threads = [
        threading.Thread(target=policy_agent.run, args=(user_prompt,)),
        threading.Thread(target=tech_agent.run, args=(user_prompt,)),
        threading.Thread(target=market_agent.run, args=(user_prompt,))
    ]

    # 3. Ejecución Paralela
    # Iniciamos todos los hilos. En este punto, se hacen 3 llamadas a OpenAI simultáneamente.
    for t in threads:
        t.start()

    # 4. Sincronización (Barrier)
    # .join() bloquea el hilo principal (main) hasta que el hilo 't' termine.
    # Esto asegura que no avancemos al resumen hasta que los 3 agentes hayan escrito en 'agent_outputs'.
    for t in threads:
        t.join()

    # 5. Agregación - FASE "FAN-IN"
    # Una vez que los hilos murieron (terminaron), el diccionario 'agent_outputs' está lleno.
    # Llamamos al agente de resumen de manera secuencial.
    final_summary = summary_agent.run(user_prompt, agent_outputs)

    print("\n=== FINAL SUMMARY ===\n")
    print(final_summary)

if __name__ == "__main__":
    main()
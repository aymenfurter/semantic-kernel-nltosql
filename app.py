import gradio as gr
import semantic_kernel as sk
import asyncio
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from semantic_kernel.planning import SequentialPlanner
from dotenv import load_dotenv
import os
from plugins.QueryDb import queryDb as plugin

# Get ROOT_DIR
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Take environment variables from .env.
load_dotenv(ROOT_DIR + '/.env', override=True)

async def create_plan(planner, input):
    return await planner.create_plan(goal=input)

async def invoke_plan(sequential_plan):
    return await sequential_plan.invoke()

async def process_query(nlp_input):
    kernel = sk.Kernel()

    # Get AOAI settings from .env
    deployment, api_key, endpoint = sk.azure_openai_settings_from_dot_env()
    azure_text_service = AzureChatCompletion(deployment_name=deployment, endpoint=endpoint, api_key=api_key)
    kernel.add_text_completion_service("azure_text_completion", azure_text_service)

    # Import NLP to SQL Plugin
    plugins_directory = "plugins"
    kernel.import_semantic_plugin_from_directory(plugins_directory, "nlpToSqlPlugin")
    kernel.import_plugin(plugin.QueryDbPlugin(os.getenv("CONNECTION_STRING")), plugin_name="QueryDbPlugin")
    
    planner = SequentialPlanner(kernel)

    # Create a plan with the NLP input
    ask = f"Create a SQL query according to the following request: {nlp_input} and query the database to get the result."
    plan = await create_plan(planner, ask)
    
    # Invoke the plan and get the result
    result = await invoke_plan(plan)
    
    response = f'User ASK: {nlp_input}\nResponse: {result}\n'
    
    for index, step in enumerate(plan._steps):
        response += f"Step: {index}\nDescription: {step.description}\nFunction: {step.plugin_name}.{step._function.name}\n"
        if len(step._outputs) > 0:
            output_str = result[step._outputs[0]].replace("\n", "\n  ")
            response += f"  Output:\n{output_str}\n\n"
    
    return response

def query_database(nlp_input):
    return asyncio.run(process_query(nlp_input))

with gr.Blocks() as demo:
    gr.Markdown("# Chat with your SQL")
    gr.Markdown("Enter your natural language query below:")
    
    with gr.Row():
        input_text = gr.Textbox(label="Enter Query")
        output_text = gr.Textbox(label="Output", lines=10)

    query_button = gr.Button("Submit Query")
    query_button.click(fn=query_database, inputs=input_text, outputs=output_text)

if __name__ == "__main__":
    demo.launch()

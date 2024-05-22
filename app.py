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
    
    debug_info = f'**User ASK:** {nlp_input}\n\n**Response:** {result}\n\n'
    
    for index, step in enumerate(plan._steps):
        debug_info += f"**Step {index}:**\n- **Description:** {step.description}\n- **Function:** {step.plugin_name}.{step._function.name}\n"
        if len(step._outputs) > 0:
            output_str = result[step._outputs[0]].replace("\n", "\n  ")
            if "Message ->" in output_str:
                output_str = output_str.split("Message ->")[1]
            debug_info += f"  - **Output:**\n```\n{output_str}\n```\n\n"
    
    # Extract and return the output of step 3
    step3_output = next(step for step in plan._steps if step.description.startswith("Write a friendly response"))._outputs[0]
    final_output = result[step3_output]
    if "Message ->" in final_output:
        final_output = final_output.split("Message ->")[1].strip()
    return final_output, debug_info

def query_database(nlp_input):
    return asyncio.run(process_query(nlp_input))

def populate_textbox(selected_input):
    return selected_input

with gr.Blocks() as demo:
    gr.Markdown("# Chat with your SQL")
    gr.Markdown("Enter your natural language query below or select a suggested query:")
    
    with gr.Row():
        input_text = gr.Textbox(label="Enter Query")
        suggested_queries = gr.Dropdown(
            choices=[
                "I want to know how many transactions in the last 3 months",
                "Give me the name of the best seller in terms of sales volume in the whole period",
                "Which product has the highest sales volume in the last month"
            ],
            label="Suggested Queries"
        )
        suggested_queries.change(fn=populate_textbox, inputs=suggested_queries, outputs=input_text)
    
    output_text = gr.Textbox(label="Output", lines=5, interactive=False)
    debug_output = gr.Textbox(label="Debug Information", lines=20, interactive=False)

    query_button = gr.Button("Submit Query")

    # Connect the query button to the functions
    query_button.click(fn=query_database, inputs=input_text, outputs=[output_text, debug_output])

if __name__ == "__main__":
    demo.launch()

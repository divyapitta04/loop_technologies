import json
import pandas as pd
import requests
from typing import Any
import logging
import sys
from src.analytics import (
    get_total_trades,
    get_total_holdings,
    get_yearly_fund_performance,
    get_all_funds,
    get_fund_comparison,
    get_fund_stats_by_type,
    get_top_holdings
)



handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s"))
root_logger = logging.getLogger()
root_logger.handlers = []
root_logger.addHandler(handler)
# root_logger.setLevel(logging.DEBUG)
root_logger.setLevel(logging.INFO)
logger = logging.getLogger(__name__)


# Ollama endpoint (runs locally)
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral"

def check_ollama_running() -> bool:
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        return response.status_code == 200
    except:
        return False

# Load data
trades_df = pd.read_csv("data/trades.csv")
holdings_df = pd.read_csv("data/holdings.csv")

def execute_function(function_name: str, **kwargs) -> Any:
    """Execute the appropriate function"""
    if function_name == "get_total_trades":
        return get_total_trades(trades_df, fund=kwargs.get("fund"))
    elif function_name == "get_total_holdings":
        return get_total_holdings(holdings_df, fund=kwargs.get("fund"))
    elif function_name == "get_yearly_fund_performance":
        result = get_yearly_fund_performance(holdings_df)
        return result.to_dict(orient='records') if result is not None else None
    elif function_name == "get_all_funds":
        return get_all_funds(holdings_df)
    elif function_name == "get_fund_comparison":
        result = get_fund_comparison(holdings_df)
        return result.to_dict(orient='records') if result is not None else None
    elif function_name == "get_fund_stats_by_type":
        result = get_fund_stats_by_type(holdings_df, fund=kwargs.get("fund"))
        return result.to_dict(orient='records') if result is not None else None
    elif function_name == "get_top_holdings":
        result = get_top_holdings(holdings_df, fund=kwargs.get("fund"), limit=kwargs.get("limit", 10))
        return result.to_dict(orient='records') if result is not None else None
    return {"error": f"Unknown function: {function_name}"}

def query_ollama(prompt: str) -> str:
    """Query Ollama locally"""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        if response.status_code == 200:
            return response.json()["response"]
        else:
            return "Error: Could not get response from Ollama"
    except requests.exceptions.ConnectionError:
        return "Error: Ollama is not running. Please start Ollama first."
    except Exception as e:
        return f"Error: {str(e)}"

def is_data_empty(data: Any) -> bool:
    """Check if returned data is empty or None"""
    if data is None:
        return True
    if isinstance(data, dict) and "error" in data:
        return True
    if isinstance(data, list) and len(data) == 0:
        return True
    if isinstance(data, pd.DataFrame) and data.empty:
        return True
    return False

def get_chatbot_response(user_query: str, trades_df_arg: pd.DataFrame, holdings_df_arg: pd.DataFrame) -> str:
    """Get chatbot response using local LLM"""

     # Check if Ollama is running
    if not check_ollama_running():
        return "❌ Error: Ollama is not running!\n\nTo fix this:\n1. Install Ollama from https://ollama.ai\n2. Run: ollama pull mistral\n3. Run: ollama serve\n4. Try again"
    
    
    # Build context about available functions
    functions_context = """You have access to these functions, you are supposed to invoke the most relevant one(s) based on the user's question, from the user's query understand the fund or holding being referred to (if any) and pass it as parameter.
    1. get_total_trades(fund=None) - Get total trades count
    2. get_total_holdings(fund=None) - Get total holdings count
    3. get_yearly_fund_performance() - Get yearly P&L by fund
    4. get_all_funds() - List all available funds
    5. get_fund_comparison() - Compare all funds
    6. get_fund_stats_by_type(fund=None) - Get holdings by security type
    7. get_top_holdings(fund=None, limit=10) - Get top holdings
    
    When user asks a question, respond ONLY with:
    FUNCTION: function_name(param1=value1, param2=value2)
    Do not include any other text."""
    
    prompt = f"""{functions_context}
        User Question: {user_query}

        Determine which function(s) to call and respond with the function call."""
    
    print("Prompt to Ollama for function call determination:")
    
    # Get function recommendation from LLM
    function_call_response = query_ollama(prompt)
    print(f"Ollama Response:\n{function_call_response}\n")
    
    # Check if Ollama is running
    if "Error" in function_call_response:
        return function_call_response
    
    # Parse and execute function
    if "FUNCTION:" in function_call_response:
        func_str = function_call_response.split("FUNCTION:")[1].strip().split('\n')[0]
        try:
            # Extract function name and parameters
            func_name = func_str.split('(')[0].strip()
            
            # Parse parameters from the string
            params_str = func_str[func_str.index('(') + 1:func_str.rindex(')')]
            params = {}
            
            if params_str.strip():
                for param in params_str.split(','):
                    if '=' in param:
                        key, value = param.split('=')
                        key = key.strip()
                        value = value.strip().strip('"\'')
                        # Convert string numbers to int
                        try:
                            value = int(value)
                        except ValueError:
                            pass
                        params[key] = value

            logger.info(f"Executing function: {func_name} with params: {params}")
            # Execute the function
            result = execute_function(func_name, **params)
            
            # Check if result is empty
            if is_data_empty(result):
                return "Sorry, I cannot find the answer to your question in the database."
            
            # Get final response with results — instruct LLM to not hallucinate and to format human-friendly text
            final_prompt = f"""You are a concise fund analytics assistant.
                You will be given structured data (JSON-like) and a user question. Produce a short, factual, human-readable answer that only uses information present in the data. Do NOT add or invent any details. If fields are missing, say exactly: "No additional details available." 
                Formatting rules:
                - For a list of items: give a one-sentence summary and state the total count.
                - For tables: give a short summary (top 3 rows if applicable) and the overall aggregate if relevant.
                - Do not output JSON or code blocks — plain text only.
                User question: {user_query}

                Data (structured): {json.dumps(result, default=str)}
                Respond now with a concise, factual answer."""
            
            final_response = query_ollama(final_prompt)
            return final_response
            
        except Exception as e:
            return f"Sorry, I cannot find the answer to your question in the database."
    
    return "Sorry, I cannot find the answer to your question in the database."


def run_console_chatbot(user_query: str, trades_df_arg: pd.DataFrame, holdings_df_arg: pd.DataFrame) -> str:     
    print("=" * 60)
    print("🤖 Welcome to Fund Analytics Chatbot!")
    print("=" * 60)
    print("\nChecking Ollama connection...")
    
    if not check_ollama_running():
        print("❌ Ollama is not running!")
        print("\nTo start Ollama:")
        print("  1. Install from https://ollama.ai")
        print("  2. Run: ollama pull mistral")
        print("  3. Run: ollama serve")
        exit(1)
    
    logger.info("✅ Ollama is running!\n")
    try:
        response = get_chatbot_response(user_query, trades_df_arg, holdings_df_arg)
    except Exception as e:
        logger.error("Error in run_console_chatbot: %s", e)
        response = ""
    return response
        
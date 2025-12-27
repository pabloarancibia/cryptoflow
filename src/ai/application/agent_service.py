from src.ai.domain.ports import ILLMProvider, ITradingTool
from src.ai.domain.models import AgentResponse
import json

class TraderAgent:
    def __init__(self, llm_provider: ILLMProvider, trading_tool: ITradingTool):
        self.llm_provider = llm_provider
        self.trading_tool = trading_tool

    def run(self, user_input: str) -> AgentResponse:
        print(f"Agent: Processing '{user_input}'...")
        
        # 1. Intent Classification / Tool Selection via LLM
        prompt = f"""You are a trading agent. Analyze the user request.
Available tools:
- execute_trade(symbol, side, quantity)

User Request: {user_input}

If the user wants to trade, output a JSON object with keys: "tool", "symbol", "side", "quantity".
Example: {{"tool": "execute_trade", "symbol": "BTC", "side": "buy", "quantity": 0.5}}

If no trade is requested, output a JSON object with key "message".
Example: {{"message": "I can only help with trading."}}

Output ONLY JSON.
"""
        response_text = self.llm_provider.generate_text(prompt)
        
        # Clean up response (sometimes LLMs add markdown code blocks)
        clean_text = response_text.replace("```json", "").replace("```", "").strip()
        
        try:
            decision = json.loads(clean_text)
            
            if "tool" in decision and decision["tool"] == "execute_trade":
                symbol = decision.get("symbol")
                side = decision.get("side")
                qty = float(decision.get("quantity", 0))
                
                print(f"Agent: Decided to trade {side} {qty} {symbol}")
                result = self.trading_tool.execute(symbol, side, qty)
                
                return AgentResponse(
                    response_text=f"Executed trade: {result}",
                    tool_used="execute_trade",
                    tool_result=result
                )
            else:
                return AgentResponse(response_text=decision.get("message", response_text))
                
        except Exception as e:
            return AgentResponse(response_text=f"Error processing request: {e}\nLLM Output: {response_text}")

from src.ai.domain.ports import ILLMProvider, ITradingTool
from src.ai.domain.models import AgentResponse, ToolCall
from src.ai.application.tools.definitions import execute_trade_def

class TraderAgent:
    def __init__(self, llm_provider: ILLMProvider, trading_tool: ITradingTool):
        self.llm_provider = llm_provider
        self.trading_tool = trading_tool

    def run(self, user_input: str) -> AgentResponse:
        print(f"Agent: Processing '{user_input}'...")
        
        system_instruction = "You are a trading agent. You can execute trades using the available tools. If the user request is not about trading, simply reply."
        
        # Call LLM with tools
        response = self.llm_provider.generate_with_tools(
            prompt=user_input,
            tools=[execute_trade_def],
            system_instruction=system_instruction
        )
        
        if isinstance(response, ToolCall):
            if response.name == "execute_trade":
                args = response.arguments
                symbol = args.get("symbol")
                side = args.get("side")
                qty = float(args.get("quantity", 0))
                
                print(f"Agent: Decided to trade {side} {qty} {symbol}")
                result = self.trading_tool.execute(symbol, side, qty)
                
                return AgentResponse(
                    response_text=f"Executed trade: {result}",
                    tool_used="execute_trade",
                    tool_result=result
                )
        
        # Fallback to text response (or if unknown tool)
        # Convert response to string just in case, though it should be str if not ToolCall
        return AgentResponse(response_text=str(response))

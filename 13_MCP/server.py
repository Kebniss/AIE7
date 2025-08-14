from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
import os
from dice_roller import DiceRoller
import random
import string


load_dotenv()


mcp = FastMCP("mcp-server")
client = TavilyClient(os.getenv("TAVILY_API_KEY"))


@mcp.tool()
def web_search(query: str) -> str:
   """Search the web for information about the given query"""
   search_results = client.get_search_context(query=query)
   return search_results


@mcp.tool()
def roll_dice(notation: str, num_rolls: int = 1) -> str:
   """Roll the dice with the given notation"""
   roller = DiceRoller(notation, num_rolls)
   return str(roller)


@mcp.tool()
def generate_password(length: int = 12, include_symbols: bool = True, include_numbers: bool = True) -> str:
   """Generate a random password with specified length and character types"""
   characters = string.ascii_letters  # Always include letters
  
   if include_numbers:
       characters += string.digits
  
   if include_symbols:
       characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
  
   password = ''.join(random.choice(characters) for _ in range(length))
   return f"Generated password: {password}"


if __name__ == "__main__":
   mcp.run(transport="stdio")
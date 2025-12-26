from pydantic_ai import RunContext, Tool
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class BankingData:
    data: Dict[str, Any]

def get_banking_field(ctx: RunContext[BankingData], field_path: str) -> str:
    """
    Retrieve a specific field value from the extracted banking data using dot notation.
    
    Args:
        ctx: The context containing the banking data.
        field_path: The path to the field, e.g., 'customer.identity.borrowerName' or 'loan.mortgage.loanAmount'.
    
    Returns:
        The value of the field if found, or a descriptive message if not found.
    """
    data = ctx.deps.data
    keys = field_path.split('.')
    current = data
    
    try:
        for key in keys:
            if isinstance(current, dict):
                current = current.get(key)
            else:
                return f"Field path '{field_path}' not found. Stopped at '{key}'."
            
            if current is None:
                return f"Field '{field_path}' is null or not present."
        
        return str(current)
    except Exception as e:
        return f"Error retrieving field '{field_path}': {str(e)}"

# Define the tool object explicitly if needed for manual registration, 
# though PydanticAI usually uses the function directly decorated or passed to Agent.
# We will pass the function `get_banking_field` to the Agent constructor.

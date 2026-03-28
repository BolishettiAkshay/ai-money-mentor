from .base_agent import BaseAgent

class BudgetAgent(BaseAgent):
    def __init__(self):
        super().__init__("Budget Agent", "Analyzes affordability")

    def run(self, input_data):
        savings = input_data.get("savings", 0)
        expense = input_data.get("expense", 0)

        if savings >= expense:
            return {
                "status": "affordable",
                "message": "You can afford this purchase."
            }
        else:
            return {
                "status": "not_affordable",
                "message": "This purchase is risky based on your savings."
            }
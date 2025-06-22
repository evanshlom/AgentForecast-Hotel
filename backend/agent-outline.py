# ========== IMPORTS ==========
import os
from datetime import datetime, timedelta
import anthropic
import json
import re

# ========== MAIN FORECAST AGENT CLASS ==========
class ForecastAgent:
    def __init__(self):
        # Initialize Anthropic client with API key from environment
        self.client = anthropic.Client(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        # Keep conversation history for context (future enhancement)
        self.conversation_history = []
    
    # ========== DATE PARSING UTILITIES ==========
    
    def get_next_monday(self):
        """Helper to find next Monday"""
        today = datetime.now().date()
        # Calculate days until Monday (0 = Monday, 6 = Sunday)
        days_ahead = 0 - today.weekday()
        # If today is Monday or later, get next Monday
        if days_ahead <= 0:
            days_ahead += 7
        return today + timedelta(days_ahead)
    
    def parse_date_reference(self, date_str, base_date=None):
        """Parse natural language date references"""
        # Default to today if no base date provided
        if not base_date:
            base_date = datetime.now().date()
        
        date_str = date_str.lower()
        
        # ===== Common Date Patterns =====
        if "tomorrow" in date_str:
            return base_date + timedelta(days=1)
        elif "next week" in date_str or "next monday" in date_str:
            return self.get_next_monday()
        elif "this weekend" in date_str:
            # Weekend = Saturday (day 5)
            days_until_saturday = (5 - base_date.weekday()) % 7
            if days_until_saturday == 0:
                days_until_saturday = 7
            return base_date + timedelta(days=days_until_saturday)
        elif "fight night" in date_str or "fight weekend" in date_str:
            # UFC/Boxing typically on Saturday
            days_until_saturday = (5 - base_date.weekday()) % 7
            if days_until_saturday == 0:
                days_until_saturday = 7
            return base_date + timedelta(days=days_until_saturday)
        
        # Default to tomorrow if pattern not recognized
        return base_date + timedelta(days=1)
    
    # ========== MAIN MESSAGE PROCESSING ==========
    
    def process_message(self, message, current_forecast=None):
        """Process user message and return adjustments with detailed explanation"""
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        
        # ===== CONSTRUCT PROMPT FOR CLAUDE =====
        prompt = f"""You are an AI assistant for Wynn Resort Las Vegas operations forecasting. 
    Analyze the user's message about hotel operations and provide recommendations.

    User message: "{message}"
    Today's date: {datetime.now().date()}
    Forecast period: Next 168 hours (7 days)

    Parse the user's intent for modifications to:
    - rooms (occupancy percentage)
    - cleaning (staff needed)  
    - security (staff needed)

    Examples:
    - "Big UFC fight this Saturday" → Increase rooms to 95%, security +40%, cleaning +25%
    - "Convention Monday morning" → Cleaning +30% (10am-2pm), rooms 85%+
    - "Pool party season starting" → Cleaning +50% afternoons, security +20%

    Return ONLY valid JSON in this format:
    {{
        "response": "Natural language explanation of the changes and reasoning",
        "modifications": [
            {{
                "material": "rooms|cleaning|security",
                "type": "percentage|absolute|set",
                "value": number,
                "start_date": "YYYY-MM-DD",
                "end_date": "YYYY-MM-DD",
                "reason": "brief operational reason"
            }}
        ]
    }}

    If no modifications needed, return empty modifications array."""

        try:
            # ===== CALL CLAUDE API =====
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            # ===== EXTRACT AND PARSE JSON RESPONSE =====
            text = response.content[0].text
            # Find JSON object in response (greedy match to get full object)
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            
            if json_match:
                result = json.loads(json_match.group())
                
                # ===== PROCESS MODIFICATIONS =====
                for mod in result.get('modifications', []):
                    # Convert 'material' to 'metric' for compatibility with frontend
                    if 'material' in mod:
                        mod['metric'] = mod.pop('material')
                    
                    # Convert date strings to date objects
                    if 'start_date' in mod:
                        mod['start_date'] = datetime.strptime(mod['start_date'], '%Y-%m-%d').date()
                    if 'end_date' in mod:
                        mod['end_date'] = datetime.strptime(mod['end_date'], '%Y-%m-%d').date()
                
                # Add assistant response to history
                self.conversation_history.append({"role": "assistant", "content": result['response']})
                return result
            
        except Exception as e:
            print(f"Agent error: {e}")
        
        # ===== FALLBACK RESPONSE =====
        # Return safe default if anything goes wrong
        fallback = {
            "response": "I understand you're asking about resort operations. Could you be more specific about what changes you'd like to make to the forecast?",
            "modifications": []
        }
        self.conversation_history.append({"role": "assistant", "content": fallback['response']})
        return fallback

# ========== INTERACTIVE DEMO FUNCTION ==========
# This section only runs when file is executed directly
# In production, other code will import ForecastAgent class

def demo_agent():
    """Interactive chat with the agent"""
    # ===== CHECK API KEY =====
    if not os.environ.get('ANTHROPIC_API_KEY'):
        print("Error: ANTHROPIC_API_KEY not set!")
        print("Please run: export ANTHROPIC_API_KEY='your-key-here'")
        return
    
    # Create agent instance
    agent = ForecastAgent()
    
    # ===== WELCOME MESSAGE =====
    print("Wynn Resort Forecast Agent - Interactive Demo")
    print("=" * 60)
    print("Chat with the agent about resort operations.")
    print("Examples: 'Big UFC fight this Saturday', 'Convention next Monday'")
    print("Type 'quit' to exit\n")
    
    # ===== INTERACTIVE CHAT LOOP =====
    while True:
        try:
            # Get user input
            message = input("You: ").strip()
            
            # Check for exit commands
            if message.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            # Skip empty messages
            if not message:
                continue
            
            # Process message through agent
            result = agent.process_message(message)
            print(f"\nAgent: {result['response']}")
            
            # ===== DISPLAY MODIFICATIONS IF ANY =====
            if result['modifications']:
                print("\nPlanned Adjustments:")
                for mod in result['modifications']:
                    print(f"  - {mod['metric']}: {mod['type']} by {mod['value']}")
                    print(f"    Period: {mod['start_date']} to {mod['end_date']}")
                    # Optional time range field
                    if 'time_range' in mod:
                        print(f"    Hours: {mod['time_range']}")
                    print(f"    Reason: {mod['reason']}")
            
            print()  # Extra line for readability
            
        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

# ========== ENTRY POINT ==========
# Only run demo when script is executed directly
# When imported as module, only ForecastAgent class is available
if __name__ == "__main__":
    demo_agent()
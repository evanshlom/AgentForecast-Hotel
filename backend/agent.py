import os
from datetime import datetime, timedelta
import anthropic
import json
import re

class ForecastAgent:
    def __init__(self):
        self.client = anthropic.Client(api_key=os.environ.get('ANTHROPIC_API_KEY'))
        self.conversation_history = []
    
    def get_next_monday(self):
        """Helper to find next Monday"""
        today = datetime.now().date()
        days_ahead = 0 - today.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return today + timedelta(days_ahead)
    
    def parse_date_reference(self, date_str, base_date=None):
        """Parse natural language date references"""
        if not base_date:
            base_date = datetime.now().date()
        
        date_str = date_str.lower()
        
        if "tomorrow" in date_str:
            return base_date + timedelta(days=1)
        elif "next week" in date_str or "next monday" in date_str:
            return self.get_next_monday()
        elif "this weekend" in date_str:
            days_until_saturday = (5 - base_date.weekday()) % 7
            if days_until_saturday == 0:
                days_until_saturday = 7
            return base_date + timedelta(days=days_until_saturday)
        elif "fight night" in date_str or "fight weekend" in date_str:
            # Typically Saturday
            days_until_saturday = (5 - base_date.weekday()) % 7
            if days_until_saturday == 0:
                days_until_saturday = 7
            return base_date + timedelta(days=days_until_saturday)
        
        # Default to tomorrow
        return base_date + timedelta(days=1)
    
    def process_message(self, message, current_forecast=None):
        """Process user message and return adjustments with detailed explanation"""
        self.conversation_history.append({"role": "user", "content": message})
        
        prompt = f"""You are an AI assistant for Wynn Resort Las Vegas operations forecasting. 
Analyze the user's message about hotel operations and provide detailed recommendations for:
- rooms (occupancy percentage)
- cleaning (staff needed)
- security (staff needed)

User message: "{message}"
Today's date: {datetime.now().date()}
Current time: {datetime.now().strftime('%H:%M')}
Forecast period: Next 168 hours (7 days)

IMPORTANT: Always provide a detailed explanation of WHY you're making these changes, showing your understanding of Vegas resort operations.

Extract modifications and return JSON:
{{
    "response": "Detailed explanation of the operational impact and why these specific changes make sense",
    "modifications": [
        {{
            "material": "rooms|cleaning|security",
            "type": "percentage|absolute|set",
            "value": number,
            "start_date": "YYYY-MM-DD",
            "end_date": "YYYY-MM-DD",
            "time_range": "HH:MM-HH:MM",
            "reason": "specific operational reason"
        }}
    ]
}}

Vegas-specific considerations:
- UFC/Boxing events: Rooms 95-100%, security +40% (crowd control), cleaning +25% (quick turnovers)
- Conventions: Cleaning +30% mornings (10am-2pm for group checkouts), rooms 85%+
- Pool parties: Cleaning +50% afternoons, security +20% (alcohol-related incidents)
- Major shows: Security +15% evenings (9pm-1am), moderate room increase
- Construction/Strip closures: Rooms -10% (access issues)
- Holidays: Everything increases, especially security

Hourly patterns to consider:
- Check-in rush: 3-6 PM (cleaning preparing rooms)
- Check-out rush: 10 AM-12 PM (cleaning heavy load)
- Casino peaks: 10 PM-3 AM (security focus)
- Pool hours: 10 AM-6 PM (cleaning/security)

Be specific about time ranges and explain the business reasoning."""

        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            text = response.content[0].text
            
            # Find JSON in response
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                result = json.loads(json_match.group())
                
                # Convert material to metric for compatibility
                for mod in result.get('modifications', []):
                    if 'material' in mod:
                        mod['metric'] = mod.pop('material')
                    
                    # Parse dates if they're strings
                    if isinstance(mod.get('start_date'), str):
                        # Handle datetime format
                        if ' ' in mod['start_date']:
                            mod['start_date'] = datetime.strptime(mod['start_date'], '%Y-%m-%d %H:%M')
                        else:
                            mod['start_date'] = datetime.strptime(mod['start_date'], '%Y-%m-%d').date()
                    
                    if isinstance(mod.get('end_date'), str):
                        if ' ' in mod['end_date']:
                            mod['end_date'] = datetime.strptime(mod['end_date'], '%Y-%m-%d %H:%M')
                        else:
                            mod['end_date'] = datetime.strptime(mod['end_date'], '%Y-%m-%d').date()
                
                self.conversation_history.append({"role": "assistant", "content": result['response']})
                return result
            
        except Exception as e:
            print(f"Agent error: {e}")
        
        # Fallback response
        fallback = {
            "response": "I understand you're asking about resort operations. Could you be more specific about what changes you'd like to make to the forecast?",
            "modifications": []
        }
        self.conversation_history.append({"role": "assistant", "content": fallback['response']})
        return fallback

# Demo function for standalone testing
def demo_agent():
    """Test the agent with example messages"""
    agent = ForecastAgent()
    
    # Test messages
    test_messages = [
        "There's a big UFC fight happening this Saturday night",
        "We have a tech convention checking in Monday morning",
        "Pool party season is starting this weekend"
    ]
    
    for message in test_messages:
        print(f"\n{'='*60}")
        print(f"User: {message}")
        result = agent.process_message(message)
        print(f"\nAgent: {result['response']}")
        
        if result['modifications']:
            print("\nPlanned Adjustments:")
            for mod in result['modifications']:
                print(f"  - {mod['metric']}: {mod['type']} by {mod['value']}")
                print(f"    Period: {mod['start_date']} to {mod['end_date']}")
                if 'time_range' in mod:
                    print(f"    Hours: {mod['time_range']}")
                print(f"    Reason: {mod['reason']}")

if __name__ == "__main__":
    demo_agent()
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# Initialize Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash')


def get_stock_prediction(symbol, current_price, change_percent):
    """
    Get AI-based stock prediction and insights using Gemini API

    Returns:
    {
        "summary": str,
        "trend": str (Bullish/Bearish/Neutral),
        "risk": str (Low/Medium/High),
        "recommendation": str (Buy/Hold/Sell),
        "reasoning": str
    }
    """
    try:
        prompt = f"""
You are a stock market analyst. Provide a brief analysis for the stock: {symbol}

Current Price: ₹{current_price}
Today's Change: {change_percent}%

Please provide:
1. A 2-sentence summary about this stock
2. Short-term trend prediction (Bullish/Bearish/Neutral)
3. Risk level (Low/Medium/High)
4. Recommendation (Buy/Hold/Sell) with 1-sentence reasoning

IMPORTANT: This is for educational purposes only, not financial advice.

Format your response exactly as:
SUMMARY: [your 2-sentence summary]
TREND: [Bullish/Bearish/Neutral]
RISK: [Low/Medium/High]
RECOMMENDATION: [Buy/Hold/Sell]
REASONING: [your 1-sentence reasoning]
"""

        response = model.generate_content(prompt)
        text = response.text.strip()

        # Parse the response
        result = {
            "summary": "",
            "trend": "",
            "risk": "",
            "recommendation": "",
            "reasoning": ""
        }

        for line in text.split('\n'):
            line = line.strip()
            if line.startswith("SUMMARY:"):
                result["summary"] = line.replace("SUMMARY:", "").strip()
            elif line.startswith("TREND:"):
                result["trend"] = line.replace("TREND:", "").strip()
            elif line.startswith("RISK:"):
                result["risk"] = line.replace("RISK:", "").strip()
            elif line.startswith("RECOMMENDATION:"):
                result["recommendation"] = line.replace("RECOMMENDATION:", "").strip()
            elif line.startswith("REASONING:"):
                result["reasoning"] = line.replace("REASONING:", "").strip()

        return result

    except Exception as e:
        print(f"Gemini API error: {e}")
        return {
            "summary": "AI prediction currently unavailable.",
            "trend": "N/A",
            "risk": "N/A",
            "recommendation": "N/A",
            "reasoning": "Unable to fetch AI insights at this time."
        }


def get_portfolio_insights(total_invested, current_value, total_profit, profit_percent):
    """
    Get AI insights about overall portfolio performance
    """
    try:
        prompt = f"""
You are a portfolio analyst. Analyze this investment portfolio:

Total Invested: ₹{total_invested:,.2f}
Current Value: ₹{current_value:,.2f}
Total Profit/Loss: ₹{total_profit:,.2f}
Return: {profit_percent:.2f}%

Provide:
1. A 2-sentence performance assessment
2. Risk assessment (Low/Medium/High)
3. One actionable suggestion

Format as:
ASSESSMENT: [your assessment]
RISK: [Low/Medium/High]
SUGGESTION: [your suggestion]
"""

        response = model.generate_content(prompt)
        text = response.text.strip()

        result = {
            "assessment": "",
            "risk": "",
            "suggestion": ""
        }

        for line in text.split('\n'):
            line = line.strip()
            if line.startswith("ASSESSMENT:"):
                result["assessment"] = line.replace("ASSESSMENT:", "").strip()
            elif line.startswith("RISK:"):
                result["risk"] = line.replace("RISK:", "").strip()
            elif line.startswith("SUGGESTION:"):
                result["suggestion"] = line.replace("SUGGESTION:", "").strip()

        return result

    except Exception as e:
        print(f"Gemini API error: {e}")
        return {
            "assessment": "AI insights currently unavailable.",
            "risk": "N/A",
            "suggestion": "Please try again later."
        }

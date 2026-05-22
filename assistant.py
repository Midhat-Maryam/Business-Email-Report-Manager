from openai import OpenAI
import os
import json
import re
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def calculate(expression):
    try:
        expression = expression.lower()

        expression = expression.replace("what's", "")
        expression = expression.replace("calculate", "")
        expression = expression.replace("of", "*")
        expression = expression.replace("percent", "%")
        expression = expression.replace("?", "").strip()

        match = re.search(r"(\d+)%\s*\*\s*(\d+)", expression)
        if match:
            percent = float(match.group(1))
            number = float(match.group(2))
            return json.dumps({"result": (percent / 100) * number})

        result = eval(expression, {"__builtins__": {}}, {})
        return json.dumps({"result": result})

    except Exception as e:
        return json.dumps({"error": str(e)})


def web_search(query):
    mock_results = {
        "market trends": "Tech sector showing 15% growth in Q1 2026",
        "industry news": "AI adoption increasing across all sectors",
        "best practices": "Email best practices: personalization, clear CTAs",
        "competitor": "Main competitors expanding to new markets"
    }

    query_lower = query.lower()

    for key in mock_results:
        if key in query_lower:
            return json.dumps({"results": mock_results[key]})

    return json.dumps({"results": f"Information about {query}"})



def analyze_data(data_string, operation):
    try:
        data = json.loads(data_string)

        if isinstance(data, list):
            values = [float(x) for x in data]
        elif isinstance(data, dict):
            values = [float(v) for v in data.values()]
        else:
            return json.dumps({"error": "Invalid data format"})

        if operation == "sum":
            result = sum(values)
        elif operation == "average":
            result = sum(values) / len(values)
        elif operation == "max":
            result = max(values)
        elif operation == "min":
            result = min(values)
        else:
            return json.dumps({"error": "Unknown operation"})

        return json.dumps({
            "result": result,
            "count": len(values)
        })

    except Exception as e:
        return json.dumps({"error": str(e)})

def format_report(report_type, data, period):
    template = {
        "sales": {
            "sections": [
                "Executive Summary",
                "Key Metrics",
                "Analysis",
                "Recommendations"
            ],
            "header": f"{period} Sales Performance Report"
        },
        "quarterly": {
            "sections": [
                "Overview",
                "Financial Highlights",
                "Operational Updates",
                "Next Steps"
            ],
            "header": f"{period} Quarterly Report"
        }
    }

    report_template = template.get(report_type, template["sales"])

    return json.dumps({
        "header": report_template["header"],
        "sections": report_template["sections"],
        "timestamp": datetime.now().strftime("%B %d, %Y")
    })


class BusinessAssistant:

    # ---------------- EMAIL WRITER ----------------
    def write_email(self, purpose, recipient, tone, research_topic=None):

        research = ""

        if research_topic:
            research = json.loads(web_search(research_topic))["results"]

        prompt = f"""
        Write a professional business email.

        Purpose: {purpose}
        Recipient: {recipient}
        Tone: {tone}
        Research: {research}

        Include subject, greeting, body (3-5 paragraphs), closing.
        """

        return client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content


    # ---------------- REPORT GENERATOR ----------------
    def generate_report(self, report_type, data, period):

        data_json = json.dumps(data)

        total = json.loads(analyze_data(data_json, "sum"))["result"]
        avg = json.loads(analyze_data(data_json, "average"))["result"]

        prompt = f"""
        Create a business report.

        Type: {report_type}
        Period: {period}
        Data: {data}

        Total: {total}
        Average: {avg}

        Include:
        Executive Summary
        Key Metrics
        Analysis
        Recommendations
        """

        return client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content


    # ---------------- MEETING SUMMARIZER ----------------
    def summarize_meeting(self, notes, date):

        prompt = f"""
        Summarize meeting:

        Date: {date}
        Notes: {notes}

        Include:
        Summary
        Key Points
        Decisions
        Action Items
        """

        return client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content


    # ---------------- DATA ANALYZER ----------------
    def analyze_business_data(self, query, data):

        data_json = json.dumps(data)
        stats = json.loads(analyze_data(data_json, "average"))

        if "error" in stats:
            stats = {"result": 0, "count": 0}

        prompt = f"""
        Query: {query}
        Data: {data}
        Stats: {stats}

        Explain insights, trends, and recommendations.
        """

        return client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content


    # ---------------- CLIENT COMMUNICATION ----------------
    def draft_client_communication(self, comm_type, client_name, context, tone):

        prompt = f"""
        Write a {comm_type} for {client_name}.

        Context: {context}
        Tone: {tone}

        Include greeting, body, CTA, closing.
        """

        return client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}]
        ).choices[0].message.content


    def process_request(self, request):

        req = request.lower()

        if "email" in req:
            return self.write_email(
                purpose=request,
                recipient="team",
                tone="professional"
            )

        elif "%" in req or "what's" in req:
            return calculate(req)

        elif "report" in req:
            return self.generate_report(
                report_type="sales",
                data={"Jan": 50000, "Feb": 60000, "Mar": 70000},
                period="Q1 2026"
            )

        elif "meeting" in req:
            return self.summarize_meeting(
                notes=request,
                date="May 22, 2026"
            )

        elif "average" in req or "revenue" in req:
            return self.analyze_business_data(
                query=request,
                data=[50000, 60000, 70000]
            )

        elif "market" in req or "industry" in req:
            return web_search(request)

        else:
            return "Request not recognized."

if __name__ == "__main__":

    assistant = BusinessAssistant()

    tests = [
        "Write an email to my team about Q2 results",
        "What's 25% of 160?",
        "Show me market trends",
        "What's average revenue?",
        "Summarize meeting notes from today"
    ]

    for test in tests:
        result = assistant.process_request(test)
        print("\n💬 Response:\n", result)
        print("=" * 60)
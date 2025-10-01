import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_grok_recommendations():
    api_key = os.environ['GROK_API_KEY']
    
    prompt = """Search X and the web thoroughly for the best fantasy football waiver wire 
pickups for the coming week of the 2025 NFL season. 

CRITICAL: Verify all player schedules, matchups, and injury reports before making recommendations. 
Double-check that the teams and opponents you mention are actually playing each other in the 
upcoming weeks. Do not hallucinate matchups.

Focus your X search on:
- Fantasy experts and analysts (e.g., @FantasyPros, @TheFFExperts, @YahooFantasy, 
  @ScottBarrettDFB, @JJZachariason)
- Recent tweets from beat reporters about player usage, injuries, and opportunities
- Fantasy community discussion about sleepers and breakout candidates
- Injury news that creates opportunities for backup players

Also search the web for:
- Latest waiver wire articles from FantasyPros, ESPN, Yahoo, The Athletic, CBS Sports
- VERIFIED NFL schedules and matchups for the next 2-3 weeks
- Player news, snap counts, and target share from last week
- Upcoming matchups and defensive rankings

Provide me with TOP 5 PICKUPS FOR EACH POSITION:
- 5 QBs
- 5 RBs
- 5 WRs
- 5 TEs
- 5 Kickers (K)
- 5 Defenses (D/ST)

For each player include:
- Ownership percentage (if available)
- Why they're valuable (injury replacement, favorable schedule, usage trending up, etc.)
- VERIFIED next 2-3 weeks opponent schedule with actual matchups

At the end, tell me which ONE player should be my #1 waiver priority overall.

Format your response for a PLAIN TEXT EMAIL - do not use markdown symbols like ###, **, or -. 
Instead use:
- ALL CAPS for section headers
- Blank lines between sections
- Simple dashes or numbers for lists

Prioritize players available in most leagues (under 50% rostered). Be accurate and verify all 
information before including it."""

    response = requests.post(
        'https://api.x.ai/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        },
        json={
            'messages': [{'role': 'user', 'content': prompt}],
            'model': 'grok-4',  # Using the flagship model
            'stream': False,
            'temperature': 0,  # Lower temperature for more factual responses
            'search_parameters': {
                'mode': 'on',
                'sources': [
                    {'type': 'x'},
                    {'type': 'web'},
                    {'type': 'news'}
                ],
                'return_citations': True,
                'max_search_results': 25  # Increased for more comprehensive search
            }
        }
    )
    
    print("API Response Status:", response.status_code)
    
    if response.status_code != 200:
        print("API Response:", response.text)
        raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    response_data = response.json()
    
    if 'error' in response_data:
        raise Exception(f"Grok API Error: {response_data['error']}")
    
    content = response_data['choices'][0]['message']['content']
    
    # Add citations if available
    if 'citations' in response_data:
        content += "\n\n" + "="*50 + "\nSOURCES:\n" + "="*50 + "\n"
        content += "\n".join(response_data['citations'])
    
    return content

def send_email(message):
    sender_email = os.environ['SENDER_EMAIL']
    sender_password = os.environ['EMAIL_PASSWORD']
    recipient = os.environ['RECIPIENT_EMAIL']
    
    msg = MIMEMultipart()
    msg['Subject'] = '🏈 Waiver Wire Pickups - This Week'
    msg['From'] = sender_email
    msg['To'] = recipient
    
    msg.attach(MIMEText(message, 'plain'))
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

if __name__ == '__main__':
    print("Getting recommendations from Grok-4 with Live Search...")
    recommendations = get_grok_recommendations()
    print("Sending email...")
    send_email(recommendations)
    print("✅ Email sent successfully!")
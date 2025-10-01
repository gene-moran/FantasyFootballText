import os
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_grok_recommendations():
    api_key = os.environ['GROK_API_KEY']
    
    prompt = """Search X and the web thoroughly for the best fantasy football waiver wire 
pickups for the coming week of the 2024 NFL season. 

Focus your X search on:
- Fantasy experts and analysts (e.g., @FantasyPros, @TheFFExperts, @YahooFantasy, 
  @ScottBarrettDFB, @JJZachariason)
- Recent tweets from beat reporters about player usage, injuries, and opportunities
- Fantasy community discussion about sleepers and breakout candidates
- Injury news that creates opportunities for backup players

Also search the web for:
- Latest waiver wire articles from FantasyPros, ESPN, Yahoo, The Athletic, CBS Sports
- Player news, snap counts, and target share from last week
- Upcoming matchups and defensive rankings

Provide me with:
1. TOP 5 WAIVER PICKUPS broken down by position (QB, RB, WR, TE)
2. Ownership percentage for each player (if available)
3. Why they're valuable (injury replacement, favorable schedule, usage trending up, etc.)
4. Which one should be my #1 priority

Format it concisely so I can quickly decide who to target. Prioritize players 
available in most leagues (under 50% rostered). Focus on this week's value and 
the next 2-3 weeks of schedule."""

    response = requests.post(
        'https://api.x.ai/v1/chat/completions',
        headers={
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        },
        json={
            'messages': [{'role': 'user', 'content': prompt}],
            'model': 'grok-beta',
            'stream': False,
            'temperature': 0
        }
    )
    
    return response.json()['choices'][0]['message']['content']

def send_email(message):
    sender_email = os.environ['SENDER_EMAIL']
    sender_password = os.environ['EMAIL_PASSWORD']
    recipient = os.environ['RECIPIENT_EMAIL']
    
    msg = MIMEMultipart()
    msg['Subject'] = '🏈 Waiver Wire Pickups - This Week'
    msg['From'] = sender_email
    msg['To'] = recipient
    
    # Add message as plain text
    msg.attach(MIMEText(message, 'plain'))
    
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

if __name__ == '__main__':
    print("Getting recommendations from Grok...")
    recommendations = get_grok_recommendations()
    print("Sending email...")
    send_email(recommendations)
    print("✅ Email sent successfully!")
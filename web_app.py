#!/usr/bin/env python3
from flask import Flask, jsonify, request
import os
import math
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

app = Flask(__name__)

class Calculator:
    @staticmethod
    def calculate(expression):
        try:
            math_functions = {
                'abs': abs, 'round': round, 'sqrt': math.sqrt, 'sin': math.sin, 'cos': math.cos,
                'tan': math.tan, 'log': math.log, 'exp': math.exp, 'pi': math.pi
            }
            result = eval(expression.replace(" ", ""), {"__builtins__": {}}, math_functions)
            return {"status": "success", "result": str(result)}
        except Exception as e:
            return {"status": "error", "result": str(e)}

class WebSearch:
    @staticmethod
    def search(query):
        try:
            response = requests.get("https://api.duckduckgo.com/", 
                params={'q': query, 'format': 'json', 'no_html': 1}, timeout=5)
            data = response.json()
            results = []
            if data.get('AbstractText'):
                results.append({'title': data.get('Heading', 'Result'), 
                              'text': data['AbstractText'][:300], 
                              'url': data.get('AbstractURL', '#')})
            return {"status": "success", "results": results if results else [{"title": "No results", "text": "Try another search", "url": "#"}]}
        except Exception as e:
            return {"status": "error", "message": str(e)}

class CodeExecutor:
    @staticmethod
    def execute(code):
        try:
            import io
            from contextlib import redirect_stdout
            safe_funcs = {'print': print, 'len': len, 'range': range, 'sum': sum, 'max': max, 
                         'min': min, 'str': str, 'int': int, 'float': float, 'list': list}
            output = io.StringIO()
            with redirect_stdout(output):
                exec(code, {"__builtins__": {}}, safe_funcs)
            return {"status": "success", "output": output.getvalue() or "Code executed"}
        except Exception as e:
            return {"status": "error", "output": str(e)}

class AIChat:
    @staticmethod
    def get_response(message):
        try:
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                return {"status": "error", "message": "No API key"}
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(model="claude-3-5-sonnet-20241022", max_tokens=1000,
                messages=[{"role": "user", "content": message}])
            return {"status": "success", "response": response.content[0].text}
        except Exception as e:
            return {"status": "error", "message": str(e)}

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width"><title>AI Chatbot</title>
<style>*{margin:0;padding:0;box-sizing:border-box}:root{--primary:#0066ff;--dark:#0a0e27;--light:#f0f4ff;--gray:#8892b0}
body{font-family:Segoe UI,sans-serif;background:linear-gradient(135deg,#050812,var(--dark));color:var(--light);min-height:100vh}
.container{display:flex;height:100vh}.sidebar{width:280px;background:rgba(10,14,39,.95);border-right:1px solid rgba(0,102,255,.2);padding:20px;overflow-y:auto}
.logo{font-size:24px;font-weight:bold;margin-bottom:30px;background:linear-gradient(135deg,var(--primary),#00d4ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.commands{display:flex;flex-direction:column;gap:12px}.command-btn{padding:12px 16px;background:rgba(0,102,255,.1);border:1px solid rgba(0,102,255,.3);color:var(--light);border-radius:8px;cursor:pointer;font-size:14px}
.command-btn:hover{background:rgba(0,102,255,.2)}.command-btn.active{background:var(--primary);border-color:var(--primary)}.main{flex:1;display:flex;flex-direction:column}
.header{padding:20px;border-bottom:1px solid rgba(0,102,255,.2);display:flex;justify-content:space-between}.messages{flex:1;overflow-y:auto;padding:20px;display:flex;flex-direction:column;gap:16px}
.message{display:flex;gap:12px;animation:slideIn .3s}.message.user{justify-content:flex-end}.message-content{max-width:70%;padding:12px 16px;border-radius:12px;word-wrap:break-word;font-size:14px}
.message.bot .message-content{background:rgba(0,102,255,.1);border:1px solid rgba(0,102,255,.3)}.message.user .message-content{background:linear-gradient(135deg,var(--primary),#00d4ff)}
.input-area{padding:20px;border-top:1px solid rgba(0,102,255,.2)}.input-tabs{display:flex;gap:8px;margin-bottom:12px;border-bottom:1px solid rgba(0,102,255,.2)}
.tab-btn{padding:8px 16px;background:transparent;border:none;color:var(--gray);cursor:pointer;border-bottom:2px solid transparent;font-size:13px}
.tab-btn.active{color:var(--primary);border-bottom-color:var(--primary)}.input-fields{display:none}.input-fields.active{display:flex;gap:12px}
input,textarea{flex:1;padding:12px 16px;background:rgba(0,102,255,.05);border:1px solid rgba(0,102,255,.3);color:var(--light);border-radius:8px;font-family:inherit;font-size:14px}
button{padding:12px 24px;background:linear-gradient(135deg,var(--primary),#00d4ff);color:white;border:none;border-radius:8px;cursor:pointer;font-weight:600;min-width:120px}
@keyframes slideIn{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
</style></head><body><div class="container"><div class="sidebar"><div class="logo">🤖 ChatBot</div><div class="commands">
<button class="command-btn active" onclick="setMode('chat')">💬 Chat</button><button class="command-btn" onclick="setMode('search')">🔍 Search</button>
<button class="command-btn" onclick="setMode('math')">🧮 Math</button><button class="command-btn" onclick="setMode('code')">💻 Code</button></div></div>
<div class="main"><div class="header"><div>AI Chatbot</div><div style="font-size:12px;color:var(--gray)">🟢 Online</div></div>
<div class="messages" id="messages"><div style="text-align:center;color:var(--gray)"><h2>Welcome!</h2><p>Choose a feature</p></div></div>
<div class="input-area"><div class="input-tabs"><button class="tab-btn active" onclick="switchTab('chat')">Chat</button>
<button class="tab-btn" onclick="switchTab('search')">Search</button><button class="tab-btn" onclick="switchTab('math')">Math</button>
<button class="tab-btn" onclick="switchTab('code')">Code</button></div>
<div id="chat" class="input-fields active"><input id="chatInput" placeholder="Type message..." onkeypress="if(event.key=='Enter')sendChat()"><button onclick="sendChat()">Send</button></div>
<div id="search" class="input-fields"><input id="searchInput" placeholder="Search web..." onkeypress="if(event.key=='Enter')sendSearch()"><button onclick="sendSearch()">Search</button></div>
<div id="math" class="input-fields"><input id="mathInput" placeholder="e.g., 2+2, sqrt(16)..." onkeypress="if(event.key=='Enter')sendMath()"><button onclick="sendMath()">Calculate</button></div>
<div id="code" class="input-fields"><textarea id="codeInput" placeholder="Python code..." rows="4" onkeypress="if(event.key=='Enter'&&event.ctrlKey)sendCode()"></textarea><button onclick="sendCode()">Execute</button></div>
</div></div></div>
<script>const msg=document.getElementById('messages');let mode='chat';function setMode(m){mode=m;document.querySelectorAll('.command-btn').forEach(b=>b.classList.remove('active'));event.target.classList.add('active')}
function switchTab(t){document.querySelectorAll('.input-fields').forEach(f=>f.classList.remove('active'));document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));document.getElementById(t).classList.add('active');event.target.classList.add('active')}
function addMessage(text,type='bot'){if(msg.children[0].textContent.includes('Welcome'))msg.innerHTML='';const m=document.createElement('div');m.className=`message ${type}`;m.innerHTML=`<div class="message-content">${text}</div>`;msg.appendChild(m);msg.scrollTop=msg.scrollHeight}
async function sendChat(){const input=document.getElementById('chatInput');const text=input.value.trim();if(!text)return;addMessage(text,'user');input.value='';const res=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:text})});const data=await res.json();addMessage(data.response||data.message,'bot')}
async function sendSearch(){const input=document.getElementById('searchInput');const text=input.value.trim();if(!text)return;addMessage(text,'user');input.value='';const res=await fetch('/api/search',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({query:text})});const data=await res.json();const results=data.results.map(r=>`<b>${r.title}</b>: ${r.text}`).join('<br>');addMessage(results,'bot')}
async function sendMath(){const input=document.getElementById('mathInput');const text=input.value.trim();if(!text)return;addMessage(text,'user');input.value='';const res=await fetch('/api/math',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({expression:text})});const data=await res.json();addMessage(`Result: ${data.result}`,'bot')}
async function sendCode(){const input=document.getElementById('codeInput');const text=input.value.trim();if(!text)return;addMessage(text,'user');input.value='';const res=await fetch('/api/code',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code:text})});const data=await res.json();addMessage(data.output,'bot')}
</script></body></html>'''

@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.json
    return jsonify(AIChat.get_response(data.get('message', '')))

@app.route('/api/search', methods=['POST'])
def api_search():
    data = request.json
    return jsonify(WebSearch.search(data.get('query', '')))

@app.route('/api/math', methods=['POST'])
def api_math():
    data = request.json
    return jsonify(Calculator.calculate(data.get('expression', '')))

@app.route('/api/code', methods=['POST'])
def api_code():
    data = request.json
    return jsonify(CodeExecutor.execute(data.get('code', '')))

if __name__ == '__main__':
    print("🚀 AI Chatbot Server Starting...")
    print("📍 Visit: http://localhost:8000")
    print("Press Ctrl+C to stop\n")
    app.run(host='0.0.0.0', port=8000, debug=True)
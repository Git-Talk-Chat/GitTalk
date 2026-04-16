from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app import supabase
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

auth_bp = Blueprint("auth", __name__)

@auth_bp.route('/login')
def login():
    # O Supabase gera a URL de autorização do GitHub
    res = supabase.auth.sign_in_with_oauth({
        "provider": "github",
        "options": {
            "scopes": "repo read:user",
            "redirect_to": "https://jubilant-palm-tree-97qgwv9q4qj43p654-5000.app.github.dev/callback"
        }
    })
    return redirect(res.url)

@auth_bp.route('/callback')
def callback():
    # 1. Capturamos o código que o GitHub enviou na URL
    code = request.args.get('code')
    
    if not code:
        return redirect(url_for('auth.login'))

    try:
        # 2. Trocamos o código pela sessão diretamente no Servidor (Python)
        # Isso ignora qualquer problema de JS no navegador
        res = supabase.auth.exchange_code_for_session({
            "auth_code": code
        })
        
        if res.session:
            session.permanent = True
            # Guardamos os dados essenciais na sessão do Flask
            session['user'] = {
                "id": res.user.id,
                "email": res.user.email,
                "user_metadata": res.user.user_metadata
            }
            session['access_token'] = res.session.provider_token or res.session.access_token
            
            # 3. Redireciona direto para a Home (common.index)
            return redirect(url_for('common.index'))
            
    except Exception as e:
        print(f"Erro na troca de código: {e}")
        
    return "Falha na autenticação. Por favor, tente novamente.", 400

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

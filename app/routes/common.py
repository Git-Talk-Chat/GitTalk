import requests
from flask import Blueprint, render_template, session, redirect, url_for
from .auth import login_required

common_bp = Blueprint("common", __name__)

@common_bp.route('/')
@login_required
def index():
    # Página de chats recentes (carregados via localStorage no frontend)
    return render_template('index.html', user=session['user'])


@common_bp.route('/users')
@login_required
def users():
    return render_template('users.html', user=session['user'])


@common_bp.route('/chat/<path:repo_name>')
@login_required
def chat_room(repo_name):
    # Passamos o repo_name para o template para sabermos em qual "sala" estamos
    return render_template('chat.html', repo_name=repo_name, user=session['user'])


@common_bp.route('/dm/<username>')
@login_required
def direct_message(username):
    # DM com outro usuário
    token = session.get('access_token')
    headers = {'Authorization': f'token {token}'}
    
    # Verifica se o usuário existe
    try:
        user_res = requests.get(f'https://api.github.com/users/{username}', headers=headers)
        if user_res.status_code == 200:
            recipient_data = user_res.json()
            return render_template('dm.html', 
                                   recipient=recipient_data,
                                   recipient_username=username,
                                   user=session['user'])
        else:
            return redirect('/')
    except Exception as e:
        print(f"Erro ao carregar DM: {e}")
        return redirect('/')


@common_bp.route('/profile/<username>')
@login_required
def profile(username):
    token = session.get('access_token')
    headers = {'Authorization': f'token {token}'}
    
    # 1. Dados Básicos do Utilizador
    user_res = requests.get(f'https://api.github.com/users/{username}', headers=headers)
    user_data = user_res.json()
    
    # 2. Repositórios (para calcular linguagens e popularidade)
    repos_res = requests.get(f'https://api.github.com/users/{username}/repos?sort=updated&per_page=100', headers=headers)
    repos_data = repos_res.json()
    
    # 3. Lógica simples para calcular linguagens mais usadas
    languages = {}
    total_stars = 0
    for repo in repos_data:
        lang = repo.get('language')
        if lang:
            languages[lang] = languages.get(lang, 0) + 1
        total_stars += repo.get('stargazers_count', 0)
        
    # Ordenar linguagens por frequência
    top_languages = sorted(languages.items(), key=lambda x: x[1], reverse=True)[:5]
    
    return render_template('profile.html', 
                           dev=user_data, 
                           repos=repos_data, # Mostrar todos os repositórios
                           languages=top_languages,
                           total_stars=total_stars)


@common_bp.route('/followers/<username>')
@login_required
def followers(username):
    token = session.get('access_token')
    headers = {'Authorization': f'token {token}'}
    
    try:
        # Buscar informações do usuário
        user_res = requests.get(f'https://api.github.com/users/{username}', headers=headers)
        user_data = user_res.json()
        
        # Buscar followers
        followers_res = requests.get(f'https://api.github.com/users/{username}/followers?per_page=30', headers=headers)
        followers_data = followers_res.json() if followers_res.status_code == 200 else []
        
        return render_template('followers.html', 
                               user=user_data,
                               followers=followers_data)
    except Exception as e:
        print(f"Erro ao carregar followers: {e}")
        return redirect('/')


@common_bp.route('/following/<username>')
@login_required
def following(username):
    token = session.get('access_token')
    headers = {'Authorization': f'token {token}'}
    
    try:
        # Buscar informações do usuário
        user_res = requests.get(f'https://api.github.com/users/{username}', headers=headers)
        user_data = user_res.json()
        
        # Buscar following
        following_res = requests.get(f'https://api.github.com/users/{username}/following?per_page=30', headers=headers)
        following_data = following_res.json() if following_res.status_code == 200 else []
        
        return render_template('following.html', 
                               user=user_data,
                               following=following_data)
    except Exception as e:
        print(f"Erro ao carregar following: {e}")
        return redirect('/')


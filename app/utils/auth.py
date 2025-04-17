from flask import session, redirect, url_for

def check_role(required_role):
    if 'role' not in session or session['role'] != required_role:
        return redirect(url_for('main.index'))  # 跳转回首页
    return None  # 如果角色匹配，继续执行

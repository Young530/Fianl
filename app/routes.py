from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models import db, User, Course, Module, Chapter, Section, Video, Comment, Progress ,Question ,QuestionSubmission
from flask_login import login_required ,current_user ,login_user
from werkzeug.security import generate_password_hash

from app.utils.auth import check_role  # 导入权限检查函数

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # 查询数据库，查找该用户
        user = User.query.filter_by(username=username).first()

        if user and user.password == password:  # 密码匹配
            login_user(user)  # 使用 Flask-Login 提供的 login_user 方法来登录用户
            session['role'] = user.role  # 保存用户角色信息到 session

            # 获取登录前的目标页面
            next_page = request.args.get('next')  # 获取 next 参数（即用户尝试访问的页面）

            if next_page:  # 如果存在 next 参数，跳转到目标页面
                return redirect(next_page)
            else:
                # 默认跳转到角色相关的首页
                if user.role == 'student':
                    return redirect(url_for('main.student_dashboard'))  # 学生首页
                elif user.role == 'teacher':
                    return redirect(url_for('main.teacher_dashboard'))  # 老师首页
                elif user.role == 'admin':
                    return redirect(url_for('main.admin_dashboard'))  # 管理员首页
        else:
            flash('用户名或密码错误！', 'danger')

    return render_template('login.html')

#########学生
@bp.route('/student_dashboard')
@login_required
def student_dashboard():
    if 'role' not in session or session['role'] != 'student':
        # 加提示
        return redirect(url_for('main.index'))  # 权限控制：不是管理员跳转回首页
    return render_template('student_dashboard.html')  # 学生功能页面


@bp.route('/course_learning/<int:course_id>/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
def course_learning(course_id, chapter_id):
    course = Course.query.get_or_404(course_id)
    chapter = Chapter.query.get_or_404(chapter_id)

    # 获取该章节下的题目
    questions = Question.query.filter_by(chapter_id=chapter.id).all()

    # 获取该章节下的小节
    sections = Section.query.filter_by(chapter_id=chapter.id).all()

    # 获取视频资源
    videos = Video.query.filter_by(section_id=sections[0].id).all() if sections else []

    # 获取该章节的所有评论
    comments = Comment.query.filter_by(section_id=sections[0].id).all() if sections else []

    # 检查该章节是否完成
    chapter_progress = Progress.query.filter_by(user_id=current_user.id, chapter_id=chapter.id).first()
    chapter_completed = chapter_progress is not None and chapter_progress.progress_percent == 100

    if request.method == 'POST':
        # 提交评论
        comment_content = request.form.get('comment')
        if comment_content:
            new_comment = Comment(content=comment_content, user_id=current_user.id, section_id=sections[0].id)
            db.session.add(new_comment)
            db.session.commit()
            flash('评论已提交！', 'success')

        # 提交题目答案
        question_answers = request.form.getlist('question_answer')
        for i, answer in enumerate(question_answers):
            question_submission = QuestionSubmission(
                question_id=questions[i].id,
                answer_text=answer,
                user_id=current_user.id
            )
            db.session.add(question_submission)
        db.session.commit()

        # 更新章节学习进度
        progress = Progress.query.filter_by(user_id=current_user.id, chapter_id=chapter.id).first()
        if progress:
            progress.progress_percent = 100  # 假设章节完成后进度为100
        else:
            progress = Progress(user_id=current_user.id, chapter_id=chapter.id, progress_percent=100)
            db.session.add(progress)
        db.session.commit()

        flash('进度已更新！', 'success')

    return render_template(
        'course_learning.html',
        course=course,
        chapter=chapter,
        questions=questions,
        chapter_completed=chapter_completed,
        videos=videos,
        comments=comments,
        sections=sections
    )




@bp.route('/exercise')
@login_required
def exercise():
    # 显示题目演练功能
    return render_template('exercise.html')

@bp.route('/learning_report')
@login_required
def learning_report():
    # 显示学习报告
    return render_template('learning_report.html')

#########老师
@bp.route('/teacher_dashboard')
def teacher_dashboard():
    if 'role' not in session or session['role'] != 'teacher':
        return redirect(url_for('main.index'))  # 权限控制：不是老师跳转回首页
    return render_template('teacher_dashboard.html')  # 老师功能页面

@bp.route('/exercise_management')
@login_required
def exercise_management():
    # 显示题目管理功能
    return render_template('exercise_management.html')

@bp.route('/question_management')
@login_required
def question_management():
    # 显示提问管理功能
    return render_template('question_management.html')

@bp.route('/teacher_course_management', endpoint='teacher_course_management')
@login_required
def teacher_course_management():
    # 权限控制：老师只能查看自己教授的课程
    if current_user.role != 'teacher':
        flash('没有权限访问该页面', 'danger')
        return redirect(url_for('main.index'))

    courses = Course.query.filter_by(teacher_id=current_user.id).all()  # 老师查看自己教授的课程
    return render_template('course_management.html', courses=courses)

#########管理员

@bp.route('/admin_dashboard')
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        #加提示
        return redirect(url_for('main.index'))  # 权限控制：不是管理员跳转回首页
    return render_template('admin_dashboard.html')  # 管理员功能页面

@bp.route('/student_management')
@login_required
def student_management():
    if current_user.role != 'admin':
        flash('没有权限访问该页面', 'danger')
        return redirect(url_for('main.index'))

    students = User.query.filter_by(role='student').all()  # 查询所有学生
    return render_template('student_management.html', students=students)


@bp.route('/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if current_user.role != 'admin':
        flash('没有权限访问该页面', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # 确保密码和确认密码一致
        if password != confirm_password:
            flash('密码和确认密码不一致！', 'danger')
            return render_template('add_student.html')

        # 创建新学生账号
        new_student = User(username=username, email=email, password=generate_password_hash(password), role='student')

        # 验证用户名或邮箱是否已存在
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('该用户名或邮箱已经存在！', 'danger')
            return render_template('add_student.html')

        db.session.add(new_student)
        db.session.commit()

        flash('新学生账号已创建！', 'success')
        return redirect(url_for('main.student_management'))

    return render_template('add_student.html')

# 编辑学生信息：管理员可以编辑学生的信息
@bp.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
@login_required
def edit_student(student_id):
    student = User.query.get_or_404(student_id)

    # 权限控制：只有管理员才能修改学生信息
    if current_user.role != 'admin':
        flash('没有权限访问该页面', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # 获取提交的表单数据
        student.username = request.form['username']
        student.email = request.form['email']

        new_password = request.form['password']
        if new_password:
            # 如果密码字段不为空，更新密码（加密密码）
            student.password = generate_password_hash(new_password)

        db.session.commit()  # 保存更改到数据库

        flash('学生信息已更新！', 'success')
        return redirect(url_for('main.student_management'))  # 提交后返回学生管理页面

    return render_template('edit_student.html', student=student)  # 渲染编辑页面

# 删除学生：管理员可以删除学生
@bp.route('/delete_student/<int:student_id>', methods=['POST'])
@login_required
def delete_student(student_id):
    student = User.query.get_or_404(student_id)

    if current_user.role != 'admin':
        flash('没有权限访问该页面', 'danger')
        return redirect(url_for('main.index'))

    db.session.delete(student)
    db.session.commit()

    flash('学生账号已删除！', 'success')
    return redirect(url_for('main.student_management'))


@bp.route('/teacher_management')
@login_required
def teacher_management():
    if current_user.role != 'admin':
        flash('没有权限访问该页面', 'danger')
        return redirect(url_for('main.index'))

    teachers = User.query.filter_by(role='teacher').all()  # 查询所有老师
    return render_template('teacher_management.html', teachers=teachers)


# 添加新老师页面：管理员可以创建新老师
@bp.route('/add_teacher', methods=['GET', 'POST'])
@login_required
def add_teacher():
    if current_user.role != 'admin':
        flash('没有权限访问该页面', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # 确保密码和确认密码一致
        if password != confirm_password:
            flash('密码和确认密码不一致！', 'danger')
            return render_template('add_teacher.html')

        # 创建新老师账号
        new_teacher = User(username=username, email=email, password=generate_password_hash(password), role='teacher')

        # 验证用户名或邮箱是否已存在
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash('该用户名或邮箱已经存在！', 'danger')
            return render_template('add_teacher.html')

        db.session.add(new_teacher)
        db.session.commit()

        flash('新老师账号已创建！', 'success')
        return redirect(url_for('main.teacher_management'))

    return render_template('add_teacher.html')


# 编辑老师信息：管理员可以编辑老师的用户名、邮箱和密码
@bp.route('/edit_teacher/<int:teacher_id>', methods=['GET', 'POST'])
@login_required
def edit_teacher(teacher_id):
    teacher = User.query.get_or_404(teacher_id)

    if current_user.role != 'admin':
        flash('没有权限访问该页面', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        teacher.username = request.form['username']
        teacher.email = request.form['email']

        new_password = request.form['password']
        if new_password:
            teacher.password = generate_password_hash(new_password)  # 更新密码

        db.session.commit()

        flash('老师信息已更新！', 'success')
        return redirect(url_for('main.teacher_management'))  # 提交后返回老师管理页面

    return render_template('edit_teacher.html', teacher=teacher)


# 删除老师：管理员可以删除老师账号
@bp.route('/delete_teacher/<int:teacher_id>', methods=['POST'])
@login_required
def delete_teacher(teacher_id):
    teacher = User.query.get_or_404(teacher_id)

    if current_user.role != 'admin':
        flash('没有权限访问该页面', 'danger')
        return redirect(url_for('main.index'))

    db.session.delete(teacher)
    db.session.commit()

    flash('老师账号已删除！', 'success')
    return redirect(url_for('main.teacher_management'))

@bp.route('/student_progress')
@login_required
def student_progress():
    # 显示学生学习进度与学习报告
    return render_template('student_progress.html')


@bp.route('/course_management', endpoint='admin_course_management')
@login_required
def course_management():
    # 权限控制：管理员可以管理所有课程
    if current_user.role != 'admin':
        flash('没有权限访问该页面', 'danger')
        return redirect(url_for('main.index'))

    courses = Course.query.all()  # 管理员查看所有课程
    return render_template('course_management.html', courses=courses)



#########课程管理页面

@bp.route('/course_management')
@login_required
def course_management():
    if current_user.role == 'admin':
        courses = Course.query.all()  # 管理员查看所有课程
    elif current_user.role == 'teacher':
        courses = Course.query.filter_by(teacher_id=current_user.id).all()  # 老师查看自己教授的课程
    else:
        flash('没有权限访问该页面', 'danger')
        return redirect(url_for('main.index'))

    return render_template('course_management.html', courses=courses)

@bp.route('/edit_course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)

    # 权限检查，确保管理员或课程的老师才能编辑
    if current_user.role != 'admin' and current_user.id != course.teacher_id:
        flash('没有权限编辑该课程', 'danger')
        return redirect(url_for('main.course_management'))

    if request.method == 'POST':
        course.name = request.form['name']
        course.description = request.form['description']
        db.session.commit()

        flash('课程已更新！', 'success')
        return redirect(url_for('main.course_management'))

    return render_template('edit_course.html', course=course)

@bp.route('/delete_course/<int:course_id>', methods=['POST'])
@login_required
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)

    # 权限检查，确保管理员或课程的老师才能删除
    if current_user.role != 'admin' and current_user.id != course.teacher_id:
        flash('没有权限删除该课程', 'danger')
        return redirect(url_for('main.course_management'))

    db.session.delete(course)
    db.session.commit()

    flash('课程已删除！', 'success')
    return redirect(url_for('main.course_management'))

#########模块管理页面
@bp.route('/module_management/<int:course_id>', methods=['GET', 'POST'])
@login_required
def module_management(course_id):
    course = Course.query.get_or_404(course_id)
    if current_user.role != 'admin' and current_user.id != course.teacher_id:
        flash('没有权限访问该页面', 'danger')
        return redirect(url_for('main.course_management'))

    if request.method == 'POST':
        module_name = request.form['name']
        new_module = Module(name=module_name, course_id=course.id)
        db.session.add(new_module)
        db.session.commit()

        flash('模块已添加！', 'success')
        return redirect(url_for('main.module_management', course_id=course.id))

    modules = Module.query.filter_by(course_id=course.id).all()
    return render_template('module_management.html', course=course, modules=modules)


#########章节管理页面
@bp.route('/chapter_management/<int:module_id>', methods=['GET', 'POST'])
@login_required
def chapter_management(module_id):
    module = Module.query.get_or_404(module_id)
    if current_user.role != 'admin' and current_user.id != module.course.teacher_id:
        flash('没有权限访问该页面', 'danger')
        return redirect(url_for('main.module_management', course_id=module.course.id))

    if request.method == 'POST':
        chapter_name = request.form['name']
        new_chapter = Chapter(name=chapter_name, module_id=module.id)
        db.session.add(new_chapter)
        db.session.commit()

        flash('章节已添加！', 'success')
        return redirect(url_for('main.chapter_management', module_id=module.id))

    chapters = Chapter.query.filter_by(module_id=module.id).all()
    return render_template('chapter_management.html', module=module, chapters=chapters)


# 小节管理页面
@bp.route('/section_management/<int:chapter_id>', methods=['GET', 'POST'])
@login_required
def section_management(chapter_id):
    chapter = Chapter.query.get_or_404(chapter_id)
    if current_user.role != 'admin' and current_user.id != chapter.module.course.teacher_id:
        flash('没有权限访问该页面', 'danger')
        return redirect(url_for('main.chapter_management', module_id=chapter.module.id))

    if request.method == 'POST':
        section_name = request.form['name']
        new_section = Section(name=section_name, chapter_id=chapter.id)
        db.session.add(new_section)
        db.session.commit()

        flash('小节已添加！', 'success')
        return redirect(url_for('main.section_management', chapter_id=chapter.id))

    sections = Section.query.filter_by(chapter_id=chapter.id).all()
    return render_template('section_management.html', chapter=chapter, sections=sections)
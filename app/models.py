from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()


# 用户模型
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)  # 添加邮箱字段
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 角色：学生、老师、管理员

    # 这里通过 backref 自动为用户添加 courses 属性（用户教授的课程）
    # 这与后面的课程-模块等模型不会冲突
    courses = db.relationship('Course', backref='teacher', lazy=True)
    progress = db.relationship('Progress', back_populates='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


# 课程模型
class Course(db.Model):
    __tablename__ = 'course'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(250), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 课程所属老师

    # 与 Module 的关联使用 back_populates 显式双向绑定
    modules = db.relationship('Module', back_populates='course', lazy=True)
    # 用于记录学生的学习进度
    progress = db.relationship('Progress', back_populates='course')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'teacher_id': self.teacher_id
        }

    def __repr__(self):
        return f'<Course {self.name}>'


# 模块模型
class Module(db.Model):
    __tablename__ = 'module'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    description = db.Column(db.String(255))

    # 显式设置与 Course 的双向关系
    course = db.relationship('Course', back_populates='modules')
    # 与 Chapter 的关联使用显式双向绑定
    chapters = db.relationship('Chapter', back_populates='module', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'course_id': self.course_id,
            'description': self.description
        }

    def __repr__(self):
        return f'<Module {self.name}>'


# 章节模型
class Chapter(db.Model):
    __tablename__ = 'chapter'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)

    # 显式设置与 Module 的双向关系
    module = db.relationship('Module', back_populates='chapters')
    # 与 Section 的关联
    sections = db.relationship('Section', back_populates='chapter', lazy=True)
    # 每个章节有多个题目
    questions = db.relationship('Question', back_populates='chapter', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'module_id': self.module_id,
        }

    def __repr__(self):
        return f'<Chapter {self.name}>'


# 小节模型
class Section(db.Model):
    __tablename__ = 'section'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)

    # 显式设置与 Chapter 的双向关系
    chapter = db.relationship('Chapter', back_populates='sections')

    # 显式设置与 Video 的双向关系
    videos = db.relationship('Video', back_populates='section', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'chapter_id': self.chapter_id,
        }

    def __repr__(self):
        return f'<Section {self.name}>'


# 视频模型
# 视频模型
class Video(db.Model):
    __tablename__ = 'video'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)  # 视频资源的URL
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)

    # 与 Section 的关联
    section = db.relationship('Section', back_populates='videos')

    def __repr__(self):
        return f'<Video {self.title}>'

# 评论模型
class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    # 与 User 和 Section 的关联
    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    section = db.relationship('Section', backref=db.backref('comments', lazy=True))

    def __repr__(self):
        return f'<Comment by {self.user.username}>'


# 题目模型
class Question(db.Model):
    __tablename__ = 'question'

    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=False)  # 题目属于某一章节

    chapter = db.relationship('Chapter', back_populates='questions')

    def __repr__(self):
        return f'<Question {self.question_text}>'


# 题目提交模型
class QuestionSubmission(db.Model):
    __tablename__ = 'question_submission'

    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    answer_text = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 提问者

    question = db.relationship('Question', backref=db.backref('submissions', lazy=True))
    user = db.relationship('User', backref=db.backref('question_submissions', lazy=True))

    def __repr__(self):
        return f'<QuestionSubmission {self.question_id}>'


# 学习进度模型
class Progress(db.Model):
    __tablename__ = 'progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 学生
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)  # 课程
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=True)  # 模块
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'), nullable=True)  # 章节
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=True)  # 小节
    progress_percent = db.Column(db.Float, nullable=False, default=0)  # 进度百分比

    user = db.relationship('User', back_populates='progress')
    course = db.relationship('Course', back_populates='progress')
    module = db.relationship('Module', backref=db.backref('progress', lazy=True))
    chapter = db.relationship('Chapter', backref=db.backref('progress', lazy=True))
    section = db.relationship('Section', backref=db.backref('progress', lazy=True))

    def __repr__(self):
        return f'<Progress for {self.user.username} in {self.course.name}>'

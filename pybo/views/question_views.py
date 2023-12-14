from datetime import datetime
import boto3
import json
from flask import Blueprint, render_template, request, url_for, g, flash
from werkzeug.utils import redirect

from pybo import db
from pybo.forms import QuestionForm, AnswerForm
from pybo.models import Question, Answer, User
from pybo.views.auth_views import login_required

bp = Blueprint('question', __name__, url_prefix='/question')

sqs = boto3.client('sqs')
sqs_queue_url = "https://sqs.us-east-1.amazonaws.com/447079561480/team3q.fifo"
@bp.route('/list/')
def _list():
    page = request.args.get('page', type=int, default=1)
    kw = request.args.get('kw', type=str, default='')
    question_list = Question.query.order_by(Question.create_date.desc())
    if kw:
        search = '%%{}%%'.format(kw)
        sub_query = db.session.query(Answer.question_id, Answer.content, User.username) \
            .join(User, Answer.user_id == User.id).subquery()
        question_list = question_list \
            .join(User) \
            .outerjoin(sub_query, sub_query.c.question_id == Question.id) \
            .filter(Question.subject.ilike(search) |  # 질문 제목
                    Question.content.ilike(search) |  # 질문 내용
                    User.username.ilike(search) |  # 질문 작성자
                    sub_query.c.content.ilike(search) |  # 답변 내용
                    sub_query.c.username.ilike(search)  # 답변 작성자
                    ) \
            .distinct()
    question_list = question_list.paginate(page, per_page=10)
    return render_template('question/question_list.html', question_list=question_list, page=page, kw=kw)


@bp.route('/detail/<int:question_id>/')
def detail(question_id):
    form = AnswerForm()
    question = Question.query.get_or_404(question_id)
    return render_template('question/question_detail.html', question=question, form=form)


@bp.route('/create/', methods=('GET', 'POST'))
@login_required
def create():
    
    return render_template('question/question_form.html')

@bp.route('/reserve_tickets', methods=['POST'])
def reserve_tickets():
    # 웹 페이지에서 POST 요청으로 받은 정보 추출
    event_type = request.form.get('event_type')
    
    # Convert string datetime to Python datetime object
    event_time_str = request.form.get('event_time')
    event_time = datetime.strptime(event_time_str, '%Y-%m-%dT%H:%M')

    ticket_count = request.form.get('ticket_count')
    reservation_status = request.form.get('reservation_status')
    userid = g.user.uid
    
    # 필요한 정보를 JSON 형태로 구성
    message_body = {
        'event_type': event_type,
        'event_time': event_time.strftime('%Y-%m-%d %H:%M:%S'),  # Convert datetime to string
        'ticket_count': ticket_count,
        'reservation_status': reservation_status,
        'uid': userid
    }

    # JSON을 SQS 메시지로 변환
    message = json.dumps(message_body)

    # SQS에 메시지 전송
    response = sqs.send_message(
        QueueUrl=sqs_queue_url,
        MessageBody=message
    )

    return redirect(url_for('main.index'))


@bp.route('/modify/<int:question_id>', methods=('GET', 'POST'))
@login_required
def modify(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('수정권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    if request.method == 'POST':  # POST 요청
        form = QuestionForm()
        if form.validate_on_submit():
            form.populate_obj(question)
            question.modify_date = datetime.now()  # 수정일시 저장
            db.session.commit()
            return redirect(url_for('question.detail', question_id=question_id))
    else:  # GET 요청
        form = QuestionForm(obj=question)
    return render_template('question/question_form.html', form=form)


@bp.route('/delete/<int:question_id>')
@login_required
def delete(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user != question.user:
        flash('삭제권한이 없습니다')
        return redirect(url_for('question.detail', question_id=question_id))
    db.session.delete(question)
    db.session.commit()
    return redirect(url_for('question._list'))


@bp.route('/vote/<int:question_id>/')
@login_required
def vote(question_id):
    question = Question.query.get_or_404(question_id)
    if g.user == question.user:
        flash('본인이 작성한 글은 추천할수 없습니다')
    else:
        question.voter.append(g.user)
        db.session.commit()
    return redirect(url_for('question.detail', question_id=question_id))

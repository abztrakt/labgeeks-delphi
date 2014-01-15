from labgeeks_delphi.models import *
from labgeeks_delphi.forms import *
from labgeeks_sybil.models import Tag
from django.shortcuts import render_to_response
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.core.context_processors import csrf
from django.utils.html import strip_tags


def view_question(request, q_id):
    can_answer = False
    can_select_answer = False
    try:
        question = Question.objects.get(id=q_id)
    except Question.DoesNotExist:
        return render_to_response('no_question.html', {"request": request, 'urlhack': True, 'bad_form': False, })
    if question.times_viewed is None:
        ''' This is just in case we have a null times_viewed (as it is allowed
        by the model) '''
        question.times_viewed = 0
    question.times_viewed = question.times_viewed + 1
    try:
        answers = Answer.objects.filter(question=question).exclude(is_best=True)
        try:
            best_answers = Answer.objects.filter(question=question, is_best=True)
        except Answer.DoesNotExist:
            best_answers = None
    except Answer.DoesNotExist:
        answers = None
        best_answers = None
    if request.user.has_perm('delphi.can_answer'):
        can_answer = True
    if request.user.has_perm('delphi.can_select_answer'):
        can_select_answer = True
    args = {
        'question': question.question,
        'more_info': question.more_info,
        'best_answer': best_answers,
        'answers': answers,
        'date': question.date,
        'author': question.user,
        'request': request,
        'question_id': q_id,
        'can_answer': can_answer,
        'tags': question.tags.all(),
        'can_select_answer': can_select_answer,
    }
    return render_to_response('view_question.html', args)


@login_required
def create_question(request):
    c = {}
    c.update(csrf(request))
    if request.method == 'POST':
        form = CreateQuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.question = strip_tags(question.question)
            question.more_info = strip_tags(question.more_info)
            question.user = request.user
            question.date = datetime.now().date()
            question.save()
            tags = request.POST.getlist('tags')
            for tag in tags:
                if tag != '':
                    tag_tuple = Tag.objects.get_or_create(name=tag)
                    question.tags.add(tag_tuple[0])
            question.save()
            return HttpResponseRedirect('/delphi/' + str(question.id) + '/')
        else:
            return render_to_response('no_question.html', {'request': request, 'urlhack': False, 'bad_form': True, })
    else:
        form = CreateQuestionForm()
        form_fields = []
        for field in form.visible_fields():
            field_info = {
                'help_text': field.help_text,
                'label_tag': field.label_tag,
                'field': field,
            }
            form_fields.append(field_info)
        args = {
            'form_fields': form_fields,
            'tags': Tag.objects.all(),
            'user': request.user,
            'request': request,
        }
        return render_to_response('create_question.html', args, context_instance=RequestContext(request))


def delphi_home(request):
    requested_tags = request.GET.getlist('tag')
    QUESTIONS = []
    tags = Tag.objects.all()
    if requested_tags:
        for tag in requested_tags:
            tag_object = Tag.objects.get(name=tag)
            tagged_qs = Question.objects.filter(tags=tag_object)
            for tagged_q in tagged_qs:
                if tagged_q not in QUESTIONS:
                    QUESTIONS.append(tagged_q)
    else:
        try:
            QUESTIONS = Question.objects.all()
        except:
            QUESTIONS = None
    questions = []
    for QUESTION in QUESTIONS:
        question = {
            'question': QUESTION.question,
            'id': QUESTION.id,
            'preview': QUESTION.more_info[:200],
        }
        questions.append(question)
    can_add_question = request.user.has_perm('labgeeks_delphi.add_question')
    return render_to_response('delphi.html', {'tags': tags, 'requested_tags': requested_tags, 'questions': questions, 'request': request, 'can_add_question': can_add_question, })


def answer_question(request, q_id):
    if not request.user.has_perm('labgeeks_delphi.can_answer'):
        return render_to_response('403.html', {'request': request,})
    try:
        question = Question.objects.get(id=q_id)
    except Question.DoesNotExist:
        return render_to_response('no_question.html', {"request": request, 'urlhack': True, 'bad_form': False, })
    c = {}
    c.update(csrf(request))
    if request.method == 'POST':
        form = CreateAnswerForm(request.POST)
        if form.is_valid():
            answer = form.save()
            answer.answer = strip_tags(answer.answer)
            answer.user = request.user
            answer.date = datetime.now().date()
            answer.question = question
            answer.save()
        if question.times_viewed is None:
            ''' This is just in case we have a null times_viewed (as it is allowed
            by the model) '''
            question.times_viewed = 0
        else:
            ''' We count times_viewed backwards one because the page was viewed
            to get here in the normal flow, and will be viewed again, but it should
            only be counted once'''
            question.times_viewed = question.times_viewed - 1
        return HttpResponseRedirect('/delphi/' + str(question.id) + '/')
    else:
        form = CreateAnswerForm()
        form_fields = []
        for field in form.visible_fields():
            field_info = {
                'help_text': field.help_text,
                'label_tag': field.label_tag,
                'field': field,
            }
            form_fields.append(field_info)
        args = {
            'question': question.question,
            'more_info': question.more_info,
            'asker': question.user,
            'date': question.date,
            'form_fields': form_fields,
            'user': request.user,
            'request': request,
        }
        return render_to_response('create_answer.html', args, context_instance=RequestContext(request))


def select_answer(request, q_id):
    if not request.user.has_perm('labgeeks_delphi.can_select_answer'):
        return render_to_response('403.html', {'request': request})
    if request.method == 'GET':
        answer_ids = request.GET.getlist('id')
        try:
            question = Question.objects.get(id=q_id)
            try:
                best_answer = Answer.objects.filter(question=question, is_best=True)
                for answer in best_answer:
                    answer.is_best = False
                    answer.save()
            except Answer.DoesNotExist:
                best_answer = None
            try:
                for pk in answer_ids:
                    new_best_answer = Answer.objects.filter(question=question).get(id=pk)
                    new_best_answer.is_best = True
                    new_best_answer.save()
            except Answer.DoesNotExist:
                return render_to_response('no_question.html', {"request": request, 'urlhack': True, 'bad_form': False, })
        except Question.DoesNotExist:
            return render_to_response('no_question.html', {'request': request, 'urlhack': True, 'bad_form': False, })
    if question.times_viewed is None:
        question.times_viewed = 0
    else:
        ''' We count times_viewed backwards one because the page was viewed
        to get here in the normal flow, and will be viewed again, but it should
        only be counted once'''
        question.times_viewed = question.times_viewed - 1
    return HttpResponseRedirect('/delphi/' + str(q_id) + '/')

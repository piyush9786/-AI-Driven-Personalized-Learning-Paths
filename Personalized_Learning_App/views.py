import os
import json
import uuid
import numpy as np
import requests
from dotenv import load_dotenv
from xhtml2pdf import pisa
from datetime import timedelta
from django.core.cache import cache
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.timezone import now
from django.utils.decorators import method_decorator
from django.template.loader import get_template
from django.db.models import Count, Avg, Prefetch
from django.contrib.admin.views.decorators import staff_member_required
from .models import Test, TestSubmission, ContactMessage, CourseProgress, StudyRoom, Message, UserNote
from .forms import RegistrationForm, StudyRoomForm
from .utils import is_user_online
from .prompts import SYSTEM_PROMPT_TEMPLATE


load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "deepseek/deepseek-r1:free"

# ── Ollama config ──────────────────────────────────────────────────────────────
OLLAMA_URL = "http://host.docker.internal:11434/api/generate"
OLLAMA_MODEL = "llama3.2"


def ollama_generate(prompt):
    """Call local Ollama LLM. Falls back to OpenRouter if Ollama is unavailable."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=60
        )
        if response.status_code == 200:
            return response.json().get("response", "").strip()
    except Exception:
        pass

    # Fallback to OpenRouter
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }
    resp = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"].strip()
    return "Error: Could not generate response."


# ── ML Helper Functions ────────────────────────────────────────────────────────

def predict_performance(scores):
    """
    Input : list of past quiz scores (0–100)
    Output: 'At Risk' or 'On Track'
    """
    if not scores:
        return "Not enough data"
    avg = np.mean(scores)
    trend = scores[-1] - scores[0] if len(scores) > 1 else 0
    if avg < 50 or (avg < 65 and trend < 0):
        return "At Risk"
    return "On Track"


def recommend_course(course_progress_dict):
    """
    Input : {course_name: completion_percentage}
    Output: name of the course to focus on next
    """
    if not course_progress_dict:
        return "Python"
    return min(course_progress_dict, key=course_progress_dict.get)


def get_difficulty(user, topic):
    """
    Determine quiz difficulty based on past scores for that topic.
    Returns 'easy', 'medium', or 'hard'.
    """
    submissions = TestSubmission.objects.filter(
        user=user,
        test__topic__iexact=topic
    ).exclude(score=None).order_by('-submitted_at')[:3]

    if not submissions:
        return "easy"

    avg = sum(s.score for s in submissions) / len(submissions)
    if avg >= 80:
        return "hard"
    elif avg >= 50:
        return "medium"
    return "easy"


# ── Courses dict ───────────────────────────────────────────────────────────────

COURSES = {
    'Python': 'python_course',
    'C++': 'cpp_course',
    'Java': 'java_course',
    'DBMS': 'dbms_course',
    'OS': 'os_course',
    'Networking': 'cn_course',
    'Devops': 'devops_course'
}

TOTAL_SECTIONS = 5


# ── Auth Views ─────────────────────────────────────────────────────────────────

def register(request):
    attempted = False
    if request.method == 'POST':
        attempted = True
        form = RegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                User.objects.create_user(username=username, email=email, password=password)
                return redirect('login_view')
            except Exception:
                messages.error(request, "Something went wrong while creating your account.")
                return redirect('register')
        else:
            errors = form.non_field_errors()
            messages.error(request, errors[0] if errors else "Please check your input and try again.")
            return redirect('register')
    else:
        form = RegistrationForm()
    return render(request, 'auth/register.html', {'form': form, 'attempted': attempted})


def login_view(request):
    attempted = False
    if request.method == "POST":
        attempted = True
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user:
            if user.is_staff:
                messages.error(request, "Admin users must log in through the admin panel.")
            else:
                login(request, user)
                return redirect('user_dashboard')
        else:
            list(messages.get_messages(request))
            messages.error(request, "Invalid username or password.")
    return render(request, 'auth/login.html', {'attempted': attempted})


def admin_login_view(request):
    attempted = False
    if request.method == "POST":
        attempted = True
        user = authenticate(
            request,
            username=request.POST['username'],
            password=request.POST['password']
        )
        if user and user.is_staff:
            login(request, user)
            return redirect('admin_dash')
        else:
            messages.error(request, "Invalid admin credentials.")
    return render(request, 'auth/admin_login.html', {'attempted': attempted})


def user_logout(request):
    logout(request)
    return redirect('index')


def admin_logout(request):
    logout(request)
    return redirect('index')


# ── Landing Page Views ─────────────────────────────────────────────────────────

def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def contact(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        if name and email and message:
            ContactMessage.objects.create(name=name, email=email, message=message)
            messages.success(request, "Your message has been submitted successfully.")
        else:
            messages.error(request, "Please fill in all the fields.")
    return render(request, 'contact.html')


def ai_analysis(request):
    return render(request, 'ai_analysis.html')


def view_subjects(request):
    return render(request, 'view_subjects.html')


def thirdcard(request):
    return render(request, "thirdcard.html")


def quiz(request):
    return render(request, 'quiz.html')


def resourse_recommendations(request):
    return render(request, 'resourse_recommendations.html')


def progress(request):
    return render(request, 'progress.html')


def todo_list(request):
    return render(request, 'todo.html')


def qr_gen(request):
    return render(request, 'qr_gen.html')


# ── Admin Dashboard Views ──────────────────────────────────────────────────────

@login_required
def members(request):
    users = User.objects.exclude(is_superuser=True)
    member_data = [
        {
            'username': user.username,
            'email': user.email,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
            'online': is_user_online(user)
        }
        for user in users
    ]
    return render(request, 'members.html', {'members': member_data})


@login_required
def admin_dash(request):
    if not request.user.is_staff:
        return redirect('login_view')

    today = now().date()
    active_today_count = sum(
        1 for user in User.objects.filter(is_staff=False)
        if (ls := cache.get(f'seen_{user.id}')) and ls.date() == today
    )

    context = {
        'total_users': User.objects.filter(is_staff=False).count(),
        'active_sessions': 150,
        'total_courses': 200,
        'pending_requests': 20,
        'todays_active_users': active_today_count,
        'total_tests_created': Test.objects.count(),
        'total_tests_submitted': TestSubmission.objects.count(),
        'new_feedback_count': ContactMessage.objects.filter(is_read=False).count(),
    }
    return render(request, 'admin_dash.html', context)


@login_required
def analytics(request):
    return render(request, 'analytics.html')


@login_required
def classes(request):
    return render(request, 'classes.html')


def view_feedbacks(request):
    if not request.user.is_staff:
        return redirect('login_view')

    deleted = False
    if request.method == 'POST':
        delete_id = request.POST.get('delete_id')
        if delete_id:
            ContactMessage.objects.filter(id=delete_id).delete()
            deleted = True

    ContactMessage.objects.filter(is_read=False).update(is_read=True)
    msgs = ContactMessage.objects.all().order_by('-timestamp')
    return render(request, 'feedbacks.html', {'messages': msgs, 'deleted': deleted})


# ── User Dashboard Views ───────────────────────────────────────────────────────

@login_required
def user_dashboard(request):
    total_progress = 0
    total_courses = len(COURSES)
    completed_courses = 0
    points_per_course = 50
    course_progress_dict = {}

    for course_name in COURSES:
        progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_name=course_name)
        completed_sections = progress_obj.completed_sections or []
        course_pct = (len(completed_sections) / TOTAL_SECTIONS) * 100
        total_progress += course_pct
        course_progress_dict[course_name] = course_pct
        if course_pct == 100:
            completed_courses += 1

    overall_progress = total_progress / total_courses if total_courses > 0 else 0
    total_points = completed_courses * points_per_course

    # ── ML: recommendation ────────────────────────────────────────────────────
    recommended_course = recommend_course(course_progress_dict)

    # ── ML: performance prediction ────────────────────────────────────────────
    submissions = TestSubmission.objects.filter(
        user=request.user
    ).exclude(score=None).order_by('submitted_at')
    scores = [float(s.score) for s in submissions]
    performance_status = predict_performance(scores)
    avg_score = round(sum(scores) / len(scores), 2) if scores else 0

    context = {
        'overall_progress': round(overall_progress, 2),
        'completed_courses': completed_courses,
        'total_points': total_points,
        'recommended_course': recommended_course,
        'performance_status': performance_status,
        'avg_score': avg_score,
        'total_tests_taken': len(scores),
    }
    return render(request, 'user_dashboard.html', context)


@login_required
def ml_dashboard(request):
    """Dedicated ML insights page for the student."""
    submissions = TestSubmission.objects.filter(
        user=request.user
    ).exclude(score=None).order_by('submitted_at')
    scores = [float(s.score) for s in submissions]

    # Per-topic average scores
    topic_data = (
        TestSubmission.objects
        .filter(user=request.user)
        .exclude(score=None)
        .values('test__topic')
        .annotate(avg_score=Avg('score'))
        .order_by('test__topic')
    )

    performance_status = predict_performance(scores)
    avg_score = round(sum(scores) / len(scores), 2) if scores else 0

    # Course progress for recommendation
    course_progress_dict = {}
    for course_name in COURSES:
        progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_name=course_name)
        completed = len(progress_obj.completed_sections or [])
        course_progress_dict[course_name] = round((completed / TOTAL_SECTIONS) * 100, 2)

    recommended_course = recommend_course(course_progress_dict)

    context = {
        'scores': scores,
        'avg_score': avg_score,
        'performance_status': performance_status,
        'total_tests': len(scores),
        'recommended_course': recommended_course,
        'course_progress': course_progress_dict,
        'topic_data': list(topic_data),
    }
    return render(request, 'ml_dashboard.html', context)


@login_required
def your_achievements(request):
    progress_data = []
    for course, url_name in COURSES.items():
        progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_name=course)
        completed_sections = progress_obj.completed_sections or []
        completion_rate = (len(completed_sections) / TOTAL_SECTIONS) * 100
        progress_data.append({
            'course_name': course,
            'completion_rate': round(completion_rate),
            'is_complete': completion_rate == 100
        })
    return render(request, 'your_achievements.html', {'progress_data': progress_data})


@login_required
def rankings(request):
    all_users = User.objects.filter(is_staff=False, is_superuser=False)
    user_rank_data = []
    for user in all_users:
        total_points = 0
        for prog in CourseProgress.objects.filter(user=user):
            completed_sections = prog.completed_sections or []
            total_points += len(completed_sections) * 10
            if len(completed_sections) == 5:
                total_points += 50
        user_rank_data.append({'username': user.username, 'points': total_points})

    ranked_users = sorted(user_rank_data, key=lambda x: x['points'], reverse=True)
    return render(request, 'rankings.html', {'ranked_users': ranked_users})


# ── Chatbot Views ──────────────────────────────────────────────────────────────

@login_required
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests allowed"}, status=405)

    try:
        data = json.loads(request.body)
        user_message = data.get("message", "").strip()
        if not user_message:
            return JsonResponse({"error": "Empty message"}, status=400)
    except Exception:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    chat_history = request.session.get("chat_history", [])

    if not chat_history:
        chat_history.append({
            "role": "system",
            "content": SYSTEM_PROMPT_TEMPLATE.format(
                student_name=request.user.get_full_name() or request.user.username
            )
        })

    chat_history.append({"role": "user", "content": user_message})

    # Try Ollama first, fallback to OpenRouter
    try:
        ollama_resp = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": user_message, "stream": False},
            timeout=60
        )
        if ollama_resp.status_code == 200:
            bot_reply = ollama_resp.json().get("response", "").strip()
        else:
            raise Exception("Ollama unavailable")
    except Exception:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {"model": OPENROUTER_MODEL, "messages": chat_history}
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        if response.status_code != 200:
            return JsonResponse({"error": f"API error {response.status_code}"}, status=500)
        bot_reply = response.json()["choices"][0]["message"]["content"]

    chat_history.append({"role": "assistant", "content": bot_reply})
    request.session["chat_history"] = chat_history
    request.session.modified = True

    return JsonResponse({"reply": bot_reply})


@login_required
def chatbot_view(request):
    user_name = request.user.get_full_name() or request.user.username
    return render(request, "chatbot.html", {"user_name": user_name})


# ── Notes Views ────────────────────────────────────────────────────────────────

@login_required
@csrf_exempt
def save_note(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            content = data.get("content", "").strip()
            if not content:
                return JsonResponse({"error": "Empty note"}, status=400)
            UserNote.objects.create(user=request.user, content=content)
            return JsonResponse({"message": "Note saved"})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "POST only"}, status=405)


@login_required
def view_notes(request):
    notes = UserNote.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "my_notes.html", {"notes": notes})


# ── Course Views ───────────────────────────────────────────────────────────────

@login_required
def current_course(request):
    progress_data = []
    for course, url_name in COURSES.items():
        progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_name=course)
        completed_sections = progress_obj.completed_sections or []
        progress_data.append({
            'course_name': url_name,
            'progress': (len(completed_sections) / TOTAL_SECTIONS) * 100
        })
    return render(request, 'current_course.html', {'progress_data': progress_data})


@csrf_exempt
def update_progress(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        course_name = data.get('course_name')
        section_number = data.get('section')
        if course_name and section_number is not None:
            try:
                progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_name=course_name)
                if progress_obj.completed_sections is None:
                    progress_obj.completed_sections = []
                if section_number not in progress_obj.completed_sections:
                    progress_obj.completed_sections.append(section_number)
                    progress_obj.save()
                return JsonResponse({'message': 'Progress updated successfully'})
            except Exception:
                return JsonResponse({'message': 'Error updating progress'}, status=500)
    return JsonResponse({'message': 'Invalid request'}, status=400)


@login_required
def update_section_progress(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        section = data.get('section')
        course_name = data.get('course_name')
        if section is not None and course_name:
            progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_name=course_name)
            if section not in progress_obj.completed_sections:
                progress_obj.completed_sections.append(section)
                progress_obj.save()
        return JsonResponse({'message': 'Progress updated successfully'})
    return JsonResponse({'message': 'Invalid request'}, status=400)


@login_required
def python_course(request):
    progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_name='Python')
    modules = [
        {"name": "Variables & Data Types", "url_name": "py_vardat"},
        {"name": "Conditional Statements & Loops", "url_name": "py_condloops"},
        {"name": "Functions & Modules", "url_name": "py_funcmod"},
        {"name": "File Handling", "url_name": "py_filehand"},
        {"name": "Libraries & Packages", "url_name": "py_libs"},
    ]
    return render(request, 'courses/python_course/python_course.html', {
        'completed_sections': progress_obj.completed_sections or [],
        'modules': modules
    })


@login_required
def java_course(request):
    progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_name='Java')
    modules = [
        {'name': 'Java Basics', 'url_name': 'java_basics'},
        {'name': 'Classes & OOP', 'url_name': 'java_classobjoop'},
        {'name': 'Collections & Streams', 'url_name': 'collectionstreams'},
        {'name': 'Control Statements', 'url_name': 'java_contstat'},
        {'name': 'Exception Handling', 'url_name': 'java_exhandling'},
    ]
    return render(request, 'courses/java_course/java_course.html', {
        'completed_sections': progress_obj.completed_sections,
        'modules': modules
    })


@login_required
def devops_course(request):
    progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_name='Devops')
    modules = [
        {'name': 'Introduction to DevOps', 'url_name': 'devops_intro'},
        {'name': 'Git & Version Control', 'url_name': 'devops_git'},
        {'name': 'CI/CD Pipelines', 'url_name': 'devops_cicd'},
        {'name': 'Jenkins Automation', 'url_name': 'devops_jenkins'},
        {'name': 'Docker & Containers', 'url_name': 'devops_docker'},
    ]
    return render(request, 'courses/devops_course/devops_course.html', {
        'completed_sections': progress_obj.completed_sections,
        'modules': modules
    })


@login_required
def os_course(request):
    progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_name='OS')
    modules = [
        {'name': 'Introduction to Operating Systems', 'url_name': 'os_intro'},
        {'name': 'Process Management', 'url_name': 'os_procman'},
        {'name': 'Memory Management', 'url_name': 'os_management'},
        {'name': 'CPU Scheduling', 'url_name': 'os_cpuscheduling'},
        {'name': 'Deadlocks & Synchronization', 'url_name': 'os_deadlocksync'},
    ]
    return render(request, 'courses/os_course/os_course.html', {
        'completed_sections': progress_obj.completed_sections or [],
        'modules': modules
    })


@login_required
def cpp_course(request):
    progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_name='C++')
    modules = [
        {'name': 'Syntax & Data Types', 'url_name': 'cpp_syntax'},
        {'name': 'Control Flow & Loops', 'url_name': 'cpp_contloops'},
        {'name': 'Functions & Arrays', 'url_name': 'cpp_funcarr'},
        {'name': 'Object-Oriented Programming', 'url_name': 'cpp_oop'},
        {'name': 'STL (Standard Template Library)', 'url_name': 'cpp_stl'},
    ]
    return render(request, 'courses/cpp_course/cpp_course.html', {
        'completed_sections': progress_obj.completed_sections or [],
        'modules': modules
    })


@login_required
def dbms_course(request):
    progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_name='DBMS')
    modules = [
        {'name': 'Introduction to DBMS', 'url_name': 'dbms_intro'},
        {'name': 'ER Model', 'url_name': 'dbms_er'},
        {'name': 'Normalization', 'url_name': 'dbms_normalization'},
        {'name': 'SQL Queries', 'url_name': 'dbms_sqlqueries'},
        {'name': 'Transaction & Concurrency', 'url_name': 'dbms_transcurrency'},
    ]
    return render(request, 'courses/dbms_course/dbms_course.html', {
        'completed_sections': progress_obj.completed_sections or [],
        'modules': modules
    })


@login_required
def cn_course(request):
    progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_name='Networking')
    modules = [
        {'name': 'Introduction to Networking', 'url_name': 'cn_course_intro'},
        {'name': 'OSI Model', 'url_name': 'cn_course_osi'},
        {'name': 'IP Addressing', 'url_name': 'cn_course_ipadd'},
        {'name': 'Protocols', 'url_name': 'cn_course_protocols'},
        {'name': 'Routing and Switching', 'url_name': 'cn_course_routingswitching'},
    ]
    return render(request, 'courses/cn_course/networking_course.html', {
        'completed_sections': progress_obj.completed_sections or [],
        'modules': modules
    })


# ── Study Room Views ───────────────────────────────────────────────────────────

@login_required
def study_rooms(request):
    rooms = StudyRoom.objects.all().order_by('-created_at')
    return render(request, 'study_rooms.html', {'rooms': rooms, 'user': request.user})


@login_required
def create_study_room(request):
    if request.method == 'POST':
        form = StudyRoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.created_by = request.user
            room.save()
            room.participants.add(request.user)
            return redirect('study_rooms')
    else:
        form = StudyRoomForm()
    return render(request, 'study_rooms/create_room.html', {'form': form})


@login_required
def join_study_room(request, room_id):
    room = get_object_or_404(StudyRoom, id=room_id)
    room.participants.add(request.user)
    return redirect('study_room_chat', room_id=room.id)


@login_required
def leave_study_room(request, room_id):
    room = get_object_or_404(StudyRoom, id=room_id)
    room.participants.remove(request.user)
    return redirect('study_rooms')


@login_required
def delete_study_room(request, room_id):
    room = get_object_or_404(StudyRoom, id=room_id)
    if request.user == room.created_by or request.user.is_staff:
        room.delete()
    return redirect('study_rooms')


@login_required
def study_room_chat(request, room_id):
    try:
        room = StudyRoom.objects.get(id=room_id)
    except StudyRoom.DoesNotExist:
        return redirect('user_dashboard')

    if request.user != room.created_by and request.user not in room.participants.all():
        return HttpResponseForbidden("You are not a participant of this room.")

    messages_in_room = Message.objects.filter(room=room).order_by('timestamp')
    participants = room.participants.all()

    return render(request, 'study_rooms/chat_room.html', {
        'room': room,
        'messages': messages_in_room,
        'participants': participants,
    })


@require_POST
@login_required
def send_message(request, room_id):
    room = get_object_or_404(StudyRoom, id=room_id)
    if request.user != room.created_by and request.user not in room.participants.all():
        return HttpResponseForbidden("Not a participant.")
    content = request.POST.get('content')
    if content:
        Message.objects.create(room=room, sender=request.user, content=content)
    return redirect('study_room_chat', room_id=room.id)


@staff_member_required
def view_room_as_admin(request, room_id):
    room = get_object_or_404(StudyRoom, id=room_id)
    msgs = Message.objects.filter(room=room).order_by('timestamp')
    return render(request, 'study_rooms/chat_room.html', {
        'room': room,
        'messages': msgs,
        'participants': room.participants.all(),
        'is_admin_view': True
    })


# ── MCQ / Test Views ───────────────────────────────────────────────────────────

def generate_mcq(topic, num_questions, difficulty="medium"):
    prompt = f"""
    Generate 20 {difficulty}-level multiple-choice questions (MCQs) for {topic} exam preparation.
    Each question should belong to a specific subtopic (e.g., Data Types, Exception Handling).
    Format each question EXACTLY as follows:

    Question: <MCQ Question> <marks>
    Correct Answer: <Correct Option Letter (e.g. a)>
    (a) <Option 1>
    (b) <Option 2>
    (c) <Option 3>
    (d) <Option 4>
    Subtopic: <Subtopic Name>

    Ensure each question is followed immediately by its correct answer, marks, four options, and the subtopic.
    """
    response_text = ollama_generate(prompt)
    mcq_texts = response_text.strip().split("\n\n")
    formatted_mcqs = []

    for mcq in mcq_texts:
        lines = [line.strip() for line in mcq.strip().split("\n") if line.strip()]
        if len(lines) >= 7:
            question_line = lines[0].replace("Question: ", "").strip()
            parts = question_line.rsplit(" ", 1)
            if len(parts) == 2:
                question_text, marks_str = parts
                try:
                    marks = float(marks_str)
                except ValueError:
                    marks = 1
            else:
                question_text = question_line
                marks = 1

            correct_answer = lines[1].replace("Correct Answer: ", "").strip()
            options = lines[2:6]
            subtopic = lines[6].replace("Subtopic: ", "").strip()

            formatted_mcqs.append({
                'question': question_text,
                'marks': marks,
                'correct_answer': correct_answer,
                'options': options,
                'topic': topic,
                'subtopic': subtopic
            })
    return formatted_mcqs


def mcq_test(request):
    if request.method == "POST":
        topic = request.POST.get("topic")

        # ML: determine difficulty based on past performance
        difficulty = get_difficulty(request.user, topic) if request.user.is_authenticated else "medium"

        mcqs = generate_mcq(topic, 10, difficulty)

        if request.user.is_authenticated:
            Test.objects.create(user=request.user, topic=topic)

        request.session['mcqs'] = mcqs
        request.session['topic'] = topic
        return render(request, "mcq_test.html", {"mcqs": mcqs, "topic": topic, "difficulty": difficulty})

    return render(request, "mcq_test.html")


def fetch_study_material(topic):
    prompt = f"""
    The user has incorrect answers in {topic}. Provide:
    1. Brief explanation
    2. Common mistakes
    3. Example code
    4. Learning resources
    5. YouTube tutorial link
    6. Google search URL
    """
    return ollama_generate(prompt)


@login_required
def submit_test(request):
    if request.method == "POST":
        mcqs = request.session.get("mcqs", [])
        test_submission = []

        website_links = {
            'python': {
                'w3schools': 'https://www.w3schools.com/python/',
                'geeksforgeeks': 'https://www.geeksforgeeks.org/python-programming-language-tutorial/'
            },
            'java': {
                'w3schools': 'https://www.w3schools.com/java/java_intro.asp',
                'geeksforgeeks': 'https://www.geeksforgeeks.org/java/?ref=ghm'
            },
            'operating system': {
                'w3schools': 'https://www.w3schools.in/operating-system/intro',
                'geeksforgeeks': 'https://www.geeksforgeeks.org/operating-systems/'
            },
            'c++': {
                'w3schools': 'https://www.w3schools.com/cpp/cpp_intro.asp',
                'geeksforgeeks': 'https://www.geeksforgeeks.org/c-plus-plus/'
            },
            'computer networks': {
                'w3schools': 'https://www.w3schools.com/cybersecurity/cybersecurity_networking.php',
                'geeksforgeeks': 'https://www.geeksforgeeks.org/computer-network-tutorials/'
            },
            'devops': {
                'w3schools': 'https://www.w3schools.com/training/aws/getting-started-with-devops-on-aws.php',
                'geeksforgeeks': 'https://www.geeksforgeeks.org/devops-tutorial/'
            },
            'dbms': {
                'w3schools': 'https://www.w3schools.com/mysql/mysql_rdbms.asp',
                'geeksforgeeks': 'https://www.geeksforgeeks.org/dbms/'
            }
        }

        youtube_links = {
            'python': 'https://www.youtube.com/watch?v=rfscVS0vtbw',
            'java': 'https://www.youtube.com/watch?v=grEKMHGYyns',
            'operating system': 'https://www.youtube.com/watch?v=26QPDBe-NB8',
            'c++': 'https://www.youtube.com/watch?v=vLnPwxZdW4Y',
            'computer networks': 'https://www.youtube.com/watch?v=qiQR5rTSshw',
            'devops': 'https://www.youtube.com/watch?v=0yWAtQ6wYNM',
            'dbms': 'https://www.youtube.com/watch?v=ztHopE5Wnpc'
        }

        topic = mcqs[0].get('topic', 'unknown').lower() if mcqs else 'unknown'
        links = website_links.get(topic, {})
        yt_link = youtube_links.get(topic)

        correct_count = 0
        total_marks = 0
        earned_marks = 0

        for idx, mcq in enumerate(mcqs, start=1):
            user_answer = request.POST.get(f"q{idx}", "")
            is_correct = user_answer.strip().lower() == mcq["correct_answer"].strip().lower()
            if is_correct:
                correct_count += 1
                earned_marks += mcq["marks"]
            total_marks += mcq["marks"]

            test_submission.append({
                "question": mcq["question"],
                "options": mcq["options"],
                "correct_answer": mcq["correct_answer"],
                "user_answer": user_answer,
                "marks": mcq["marks"],
                "topic": topic,
                "is_correct": is_correct
            })

        # Calculate score as percentage
        score_pct = round((earned_marks / total_marks) * 100, 2) if total_marks > 0 else 0

        # Save submission with score
        test = Test.objects.filter(user=request.user, topic=topic).order_by('-created_at').first()
        if test:
            TestSubmission.objects.create(test=test, user=request.user, score=score_pct)

        # AI analysis using Ollama
        analysis_prompt = f"Analyze this student's test performance and give feedback:\n{json.dumps(test_submission, indent=2)}"
        formatted_analysis = ollama_generate(analysis_prompt).replace("\n", "<br>")

        study_material = {topic: fetch_study_material(topic)}

        request.session["test_report"] = {
            "analysis": formatted_analysis,
            "study_material": study_material,
            "youtube_link": yt_link,
            "website_links": links,
            "topic": topic
        }

        return render(request, "test_result.html", {
            "analysis": formatted_analysis,
            "study_material": study_material,
            "youtube_link": yt_link,
            "website_links": links,
            "topic": topic,
            "score": score_pct,
            "correct_count": correct_count,
            "total_questions": len(mcqs),
        })

    return render(request, "test_result.html", {
        "analysis": "No analysis available yet.",
        "study_material": {},
        "youtube_link": None,
        "website_links": {},
        "topic": "unknown"
    })


# ── PDF Generation ─────────────────────────────────────────────────────────────

def generate_pdf(request):
    test_report = request.session.get("test_report", {})
    if not test_report:
        return HttpResponse("No report data available.", status=400)

    template = get_template("test_report_pdf.html")
    html = template.render(test_report)
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Test_Report.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)
    return response


# ── Static Course Content Views ────────────────────────────────────────────────

# CN Course
@login_required
def cn_course_intro(request):
    return render(request, 'courses/cn_course/content/intro.html')

@login_required
def cn_course_ipadd(request):
    return render(request, 'courses/cn_course/content/ipadd.html')

@login_required
def cn_course_osi(request):
    return render(request, 'courses/cn_course/content/osi.html')

@login_required
def cn_course_protocols(request):
    return render(request, 'courses/cn_course/content/protocols.html')

@login_required
def cn_course_routingswitching(request):
    return render(request, 'courses/cn_course/content/routingswitching.html')

# C++ Course
@login_required
def cpp_contloops(request):
    return render(request, 'courses/cpp_course/content/contloops.html')

@login_required
def cpp_funcarr(request):
    return render(request, 'courses/cpp_course/content/funcarr.html')

@login_required
def cpp_oop(request):
    return render(request, 'courses/cpp_course/content/oop.html')

@login_required
def cpp_stl(request):
    return render(request, 'courses/cpp_course/content/stl.html')

@login_required
def cpp_syntax(request):
    return render(request, 'courses/cpp_course/content/syntax.html')

# DBMS Course
@login_required
def dbms_er(request):
    return render(request, 'courses/dbms_course/content/ER.html')

@login_required
def dbms_intro(request):
    return render(request, 'courses/dbms_course/content/intro.html')

@login_required
def dbms_normalization(request):
    return render(request, 'courses/dbms_course/content/normalization.html')

@login_required
def dbms_sqlqueries(request):
    return render(request, 'courses/dbms_course/content/sqlqueries.html')

@login_required
def dbms_transcurrency(request):
    return render(request, 'courses/dbms_course/content/transcurrency.html')

# DevOps Course
@login_required
def devops_intro(request):
    return render(request, 'courses/devops_course/content/intro.html')

@login_required
def devops_cicd(request):
    return render(request, 'courses/devops_course/content/cicd.html')

@login_required
def devops_git(request):
    return render(request, 'courses/devops_course/content/git.html')

@login_required
def devops_docker(request):
    return render(request, 'courses/devops_course/content/docker.html')

@login_required
def devops_jenkins(request):
    return render(request, 'courses/devops_course/content/jenkins.html')

# Java Course
@login_required
def java_basics(request):
    return render(request, 'courses/java_course/content/basics.html')

@login_required
def java_classobjoop(request):
    return render(request, 'courses/java_course/content/classobjoop.html')

@login_required
def collectionstreams(request):
    return render(request, 'courses/java_course/content/collectionstreams.html')

@login_required
def java_contstat(request):
    return render(request, 'courses/java_course/content/contstat.html')

@login_required
def java_exhandling(request):
    return render(request, 'courses/java_course/content/excepthandle.html')

# OS Course
@login_required
def os_cpuscheduling(request):
    return render(request, 'courses/os_course/content/cpuscheduling.html')

@login_required
def os_deadlocksync(request):
    return render(request, 'courses/os_course/content/deadlocksync.html')

@login_required
def os_intro(request):
    return render(request, 'courses/os_course/content/intro.html')

@login_required
def os_management(request):
    return render(request, 'courses/os_course/content/management.html')

@login_required
def os_procman(request):
    return render(request, 'courses/os_course/content/procman.html')

# Python Course
@login_required
def py_condloops(request):
    return render(request, 'courses/python_course/content/condloops.html')

@login_required
def py_filehand(request):
    return render(request, 'courses/python_course/content/filehand.html')

@login_required
def py_funcmod(request):
    return render(request, 'courses/python_course/content/funcmod.html')

@login_required
def py_libs(request):
    return render(request, 'courses/python_course/content/libs.html')

@login_required
def py_vardat(request):
    return render(request, 'courses/python_course/content/vardat.html')

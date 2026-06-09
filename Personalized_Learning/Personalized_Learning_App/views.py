import os
import json
import uuid
import requests
from dotenv import load_dotenv
import google.generativeai as genai
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
from django.db.models import Count, Prefetch
from django.contrib.admin.views.decorators import staff_member_required
from .models import Test, TestSubmission, ContactMessage, CourseProgress, StudyRoom, Message, UserNote
from .forms import RegistrationForm, StudyRoomForm
from .utils import is_user_online
from .prompts import SYSTEM_PROMPT_TEMPLATE


load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "deepseek/deepseek-r1:free"

api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")


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


# Auth Views

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
            except Exception as e:
                messages.error(request, "Something went wrong while creating your account.")
                return redirect('register')
        else:
            errors = form.non_field_errors()
            if errors:
                messages.error(request, errors[0])
            else:
                messages.error(request, "Please check your input and try again.")
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
            storage = messages.get_messages(request)
            list(storage)
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


# Landing page Views

def index(request):
    return render(request, 'index.html')


def about(request):
    return render(request, 'about.html')


def contact(request):
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


# Admin dashboard views

@login_required
def members(request):
    users = User.objects.exclude(is_superuser=True)

    member_data = []
    for user in users:
        member_data.append({
            'username': user.username,
            'email': user.email,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
            'online': is_user_online(user)
        })

    return render(request, 'members.html', {'members': member_data})


@login_required
def admin_dash(request):
    if not request.user.is_staff:
        return redirect('login_view')

    today = now().date()
    active_today_count = 0

    for user in User.objects.filter(is_staff=False):
        last_seen = cache.get(f'seen_{user.id}')
        if last_seen and last_seen.date() == today:
            active_today_count += 1

    total_tests_created = Test.objects.count()
    total_tests_submitted = TestSubmission.objects.count()
    new_feedback_count = ContactMessage.objects.filter(is_read=False).count()

    context = {
        'total_users': User.objects.filter(is_staff=False).count(),
        'active_sessions': 150,
        'total_courses': 200,
        'pending_requests': 20,
        'todays_active_users': active_today_count,
        'total_tests_created': total_tests_created,
        'total_tests_submitted': total_tests_submitted,
        'new_feedback_count': new_feedback_count,
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
    messages = ContactMessage.objects.all().order_by('-timestamp')

    return render(request, 'feedbacks.html', {
        'messages': messages,
        'deleted': deleted
    })


# User dash board views

@login_required
def user_dashboard(request):
    total_progress = 0
    total_courses = len(COURSES)
    completed_courses = 0
    points_per_course = 50

    for course_name in COURSES:
        progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_name=course_name)
        completed_sections = progress_obj.completed_sections or []
        course_progress = (len(completed_sections) / TOTAL_SECTIONS) * 100
        total_progress += course_progress

        if course_progress == 100:
            completed_courses += 1

    overall_progress = total_progress / total_courses if total_courses > 0 else 0
    total_points = completed_courses * points_per_course

    context = {
        'overall_progress': round(overall_progress, 2),
        'completed_courses': completed_courses,
        'total_points': total_points
    }

    return render(request, 'user_dashboard.html', context)


@login_required
def your_achievements(request):
    progress_data = []

    for course, url_name in COURSES.items():
        progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_name=course)
        if progress_obj.completed_sections is None:
            progress_obj.completed_sections = []
        completion_rate = (len(progress_obj.completed_sections) / TOTAL_SECTIONS) * 100

        progress_data.append({
            'course_name': course,  
            'completion_rate': round(completion_rate),
            'is_complete': completion_rate == 100
        })

    context = {
        'progress_data': progress_data
    }
    return render(request, 'your_achievements.html', context)


@login_required
def rankings(request):
    all_users = User.objects.filter(is_staff=False, is_superuser=False)
    user_rank_data = []

    for user in all_users:
        user_progresses = CourseProgress.objects.filter(user=user)
        total_points = 0

        for progress in user_progresses:
            completed_sections = progress.completed_sections or []
            total_points += len(completed_sections) * 10

            if len(completed_sections) == 5:
                total_points += 50

        user_rank_data.append({
            'username': user.username,
            'points': total_points
        })

    ranked_users = sorted(user_rank_data, key=lambda x: x['points'], reverse=True)

    context = {
        'ranked_users': ranked_users
    }
    return render(request, 'rankings.html', context)



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
        system_message = {
            "role": "system",
            "content": SYSTEM_PROMPT_TEMPLATE.format(student_name=request.user.get_full_name() or request.user.username)
        }
        chat_history.append(system_message)

    chat_history.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": MODEL,
        "messages": chat_history
    }

    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        return JsonResponse({"error": f"API error {response.status_code}"}, status=500)

    response_json = response.json()
    bot_reply = response_json["choices"][0]["message"]["content"]

    chat_history.append({"role": "assistant", "content": bot_reply})

    request.session["chat_history"] = chat_history
    request.session.modified = True

    return JsonResponse({"reply": bot_reply})


@login_required
def chatbot_view(request):
    user_name = request.user.get_full_name() or request.user.username
    return render(request, "chatbot.html", {"user_name": user_name})


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


# Course views 

@login_required
def current_course(request):
    """ View to render the current course page with progress data. """
    progress_data = []

    for course, url_name in COURSES.items():
        progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_name=course)
        if progress_obj.completed_sections is None:
            progress_obj.completed_sections = []
        completion_rate = (len(progress_obj.completed_sections) / TOTAL_SECTIONS) * 100

        progress_data.append({
            'course_name': url_name,
            'progress': completion_rate
        })

    context = {
        'progress_data': progress_data
    }
    return render(request, 'current_course.html', context)


@csrf_exempt
def update_progress(request):
    """ Endpoint to handle progress updates when a section is marked complete. """
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
            except Exception as e:
                return JsonResponse({'message': 'Error updating progress'}, status=500)

    return JsonResponse({'message': 'Invalid request'}, status=400)


@login_required
def update_section_progress(request):
    """ Endpoint for updating the section progress (if needed separately). """
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
    completed_sections = progress_obj.completed_sections or []

    modules = [
        {"name": "Variables & Data Types", "url_name": "py_vardat"},
        {"name": "Conditional Statements & Loops", "url_name": "py_condloops"},
        {"name": "Functions & Modules", "url_name": "py_funcmod"},
        {"name": "File Handling", "url_name": "py_filehand"},
        {"name": "Libraries & Packages", "url_name": "py_libs"},
    ]

    context = {
        'completed_sections': completed_sections,
        'modules': modules
    }
    return render(request, 'courses/python_course/python_course.html', context)


@login_required
def java_course(request):
    progress_obj, created = CourseProgress.objects.get_or_create(user=request.user, course_name='Java')
    completed_sections = progress_obj.completed_sections

    modules = [
        {'name': 'Java Basics', 'url_name': 'java_basics'},
        {'name': 'Classes & OOP', 'url_name': 'java_classobjoop'},
        {'name': 'Collections & Streams', 'url_name': 'collectionstreams'},
        {'name': 'Control Statements', 'url_name': 'java_contstat'},
        {'name': 'Exception Handling', 'url_name': 'java_exhandling'},
    ]

    context = {
        'completed_sections': completed_sections,
        'modules': modules
    }
    return render(request, 'courses/java_course/java_course.html', context)


@login_required
def devops_course(request):
    progress_obj, created = CourseProgress.objects.get_or_create(user=request.user, course_name='Devops')
    completed_sections = progress_obj.completed_sections

    modules = [
        {'name': 'Introduction to DevOps', 'url_name': 'devops_intro'},
        {'name': 'Git & Version Control', 'url_name': 'devops_git'},
        {'name': 'CI/CD Pipelines', 'url_name': 'devops_cicd'},
        {'name': 'Jenkins Automation', 'url_name': 'devops_jenkins'},
        {'name': 'Docker & Containers', 'url_name': 'devops_docker'},
    ]

    context = {
        'completed_sections': completed_sections,
        'modules': modules
    }
    return render(request, 'courses/devops_course/devops_course.html', context)


@login_required
def os_course(request):
    progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_name='OS')
    completed_sections = progress_obj.completed_sections or []

    modules = [
        {'name': 'Introduction to Operating Systems', 'url_name': 'os_intro'},
        {'name': 'Process Management', 'url_name': 'os_procman'},
        {'name': 'Memory Management', 'url_name': 'os_management'},
        {'name': 'CPU Scheduling', 'url_name': 'os_cpuscheduling'},
        {'name': 'Deadlocks & Synchronization', 'url_name': 'os_deadlocksync'},
    ]

    context = {
        'completed_sections': completed_sections,
        'modules': modules
    }
    return render(request, 'courses/os_course/os_course.html', context)


@login_required
def cpp_course(request):
    progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_name='C++')
    completed_sections = progress_obj.completed_sections or []

    modules = [
        {'name': 'Syntax & Data Types', 'url_name': 'cpp_syntax'},
        {'name': 'Control Flow & Loops', 'url_name': 'cpp_contloops'},
        {'name': 'Functions & Arrays', 'url_name': 'cpp_funcarr'},
        {'name': 'Object-Oriented Programming', 'url_name': 'cpp_oop'},
        {'name': 'STL (Standard Template Library)', 'url_name': 'cpp_stl'},
    ]

    context = {
        'completed_sections': completed_sections,
        'modules': modules
    }
    return render(request, 'courses/cpp_course/cpp_course.html', context)


@login_required
def dbms_course(request):
    progress_obj, created = CourseProgress.objects.get_or_create(user=request.user, course_name='DBMS')
    completed_sections = progress_obj.completed_sections or []

    modules = [
        {'name': 'Introduction to DBMS', 'url_name': 'dbms_intro'},
        {'name': 'ER Model', 'url_name': 'dbms_er'},
        {'name': 'Normalization', 'url_name': 'dbms_normalization'},
        {'name': 'SQL Queries', 'url_name': 'dbms_sqlqueries'},
        {'name': 'Transaction & Concurrency', 'url_name': 'dbms_transcurrency'},
    ]

    context = {
        'completed_sections': completed_sections,
        'modules': modules
    }
    return render(request, 'courses/dbms_course/dbms_course.html', context)


@login_required
def cn_course(request):
    progress_obj, created = CourseProgress.objects.get_or_create(user=request.user, course_name='Networking')
    completed_sections = progress_obj.completed_sections or []

    modules = [
        {'name': 'Introduction to Networking', 'url_name': 'cn_course_intro'},
        {'name': 'OSI Model', 'url_name': 'cn_course_osi'},
        {'name': 'IP Addressing', 'url_name': 'cn_course_ipadd'},
        {'name': 'Protocols', 'url_name': 'cn_course_protocols'},
        {'name': 'Routing and Switching', 'url_name': 'cn_course_routingswitching'},
    ]

    context = {
        'completed_sections': completed_sections,
        'modules': modules
    }
    return render(request, 'courses/cn_course/networking_course.html', context)


# Study room views 

@login_required
def study_rooms(request):
    rooms = StudyRoom.objects.all().order_by('-created_at')
    user = request.user
    return render(request, 'study_rooms.html', {'rooms': rooms, 'user': user})


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

    for user in participants:
        if user == 'Admin':
            participants.delete(user)

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
        Message.objects.create(
            room=room,
            sender=request.user,
            content=content
        )

    return redirect('study_room_chat', room_id=room.id)


@staff_member_required
def view_room_as_admin(request, room_id):
    room = get_object_or_404(StudyRoom, id=room_id)
    messages = Message.objects.filter(room=room).order_by('timestamp')
    participants = room.participants.all()

    context = {
        'room': room,
        'messages': messages,
        'participants': participants,
        'is_admin_view': True
    }
    return render(request, 'study_rooms/chat_room.html', context)


def generate_mcq(topic, num_questions):
    prompt = f"""
    Generate 20 multiple-choice questions (MCQs) for {topic} exam preparation.
    Each question should belong to a specific subtopic (e.g., Data Types, Exception Handling).
    Format each question as follows:

    Question: <MCQ Question> <marks>
    Correct Answer: <Correct Option Letter (e.g. a)>
    (a) <Option 1>
    (b) <Option 2>
    (c) <Option 3>
    (d) <Option 4>
    Subtopic: <Subtopic Name (e.g., Data Types)>

    Ensure each question is followed immediately by its correct answer, marks, four options, and the subtopic in a clear and structured manner.
    """
    response = model.generate_content(prompt)
    # Split response into individual questions (using double newline as separator)
    mcq_texts = response.text.strip().split("\n\n")
    formatted_mcqs = []

    for mcq in mcq_texts:
        lines = [line.strip() for line in mcq.strip().split("\n") if line.strip()]
        if len(lines) >= 7:  # Expecting at least 7 lines: 4 options, correct answer, question, and subtopic
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
            subtopic = lines[6].replace("Subtopic: ", "").strip()  # Extract the subtopic

            formatted_mcqs.append({
                'question': question_text,
                'marks': marks,
                'correct_answer': correct_answer,
                'options': options,
                'topic': topic,  # Store the main topic
                'subtopic': subtopic  # Store the subtopic for each question
            })
    return formatted_mcqs


def mcq_test(request):
    if request.method == "POST":
        topic = request.POST.get("topic")
        mcqs = generate_mcq(topic, 10)

        # Save the test entry to the database
        if request.user.is_authenticated:
            Test.objects.create(user=request.user, topic=topic)

        request.session['mcqs'], request.session['topic'] = mcqs, topic
        return render(request, "mcq_test.html", {"mcqs": mcqs, "topic": topic})

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
    return model.generate_content(prompt).text.strip()


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

        for idx, mcq in enumerate(mcqs, start=1):
            user_answer = request.POST.get(f"q{idx}", "")
            test = Test.objects.filter(user=request.user, topic=topic).order_by('-created_at').first()

            test_submission.append({
                "question": mcq["question"],
                "options": mcq["options"],
                "correct_answer": mcq["correct_answer"],
                "user_answer": user_answer,
                "marks": mcq["marks"],
                "topic": topic
            })

        analysis_response = model.generate_content(f"Analyze: {json.dumps(test_submission, indent=2)}")
        formatted_analysis = analysis_response.text.strip().replace("\n", "<br>")

        study_material = {topic: fetch_study_material(topic)}

        request.session["test_report"] = {
            "analysis": formatted_analysis,
            "study_material": study_material,
            "youtube_link": yt_link,
            "website_links": links,
            "topic": topic
        }

        if test:
            TestSubmission.objects.create(test=test, user=request.user)

        return render(request, "test_result.html", {
            "analysis": formatted_analysis,
            "study_material": study_material,
            "youtube_link": yt_link,
            "website_links": links,
            "topic": topic,
        })

    return render(request, "test_result.html", {
        "analysis": "No analysis available yet.",
        "study_material": {},
        "youtube_link": None,
        "website_links": {},
        "topic": "unknown"
    })


# PDF generation
def generate_pdf(request):
    # Retrieve the test report from session
    test_report = request.session.get("test_report", {})

    # Ensure the test report contains necessary keys and data
    if not test_report:
        return HttpResponse("No report data available.", status=400)

    # Fetch the template for PDF generation
    template_path = "test_report_pdf.html"
    template = get_template(template_path)
    html = template.render(test_report)  # Render HTML with data

    # Generate PDF response
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="Test_Report.pdf"'

    # Convert HTML to PDF using xhtml2pdf
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error generating PDF", status=500)

    return response


# Static template Views

# CN Course views
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


# cpp course views
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


# dbms course views
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


# devops course views
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


# java course views
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


# os course views
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


# python course views
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

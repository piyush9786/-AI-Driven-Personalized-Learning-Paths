
from django.urls import path
from . import views

urlpatterns = [

    path('', views.index, name="index"),
    path('ai_analysis/', views.ai_analysis, name="ai_analysis"),
    path('quiz/', views.quiz, name="quiz"),
    path('resourse_recommendations/', views.resourse_recommendations, name="resourse_recommendations"),
    path('progress/', views.progress, name="progress"),
    path('todo_list/', views.todo_list, name="todo_list"),
    path('auth/register/', views.register, name="register"),
    path('contact/', views.contact, name="contact"),
    path('view_feedbacks/', views.view_feedbacks, name='feedbacks'),
    path('about/', views.about, name="about"),
    path('auth/login_view/', views.login_view, name="login_view"),
    path('auth/admin_login/', views.admin_login_view, name="admin_login"),
    path('admin_dash/', views.admin_dash, name="admin_dash"),
    path('analytics/', views.analytics, name="analytics"),
    path('classes/', views.classes, name="classes"),
    path('members/', views.members, name="members"),
    path('admin_logout/', views.admin_logout, name='admin_logout'),
    path('create_test/', views.mcq_test, name='create_test'),
    path('submit_test/', views.submit_test, name='submit_test'),
    path('logout/', views.user_logout, name='logout'),
    path('user_dashboard/', views.user_dashboard, name="user_dashboard"),
    path('update-progress/', views.update_progress, name="update_progress"),
    path('qr_gen/', views.qr_gen, name="qr_gen"),
    path('your_achievements/', views.your_achievements, name="your_achievements"),
    path('view_subjects/', views.view_subjects, name="view_subjects"),
    path("generate_pdf/", views.generate_pdf, name="generate_pdf"),
    path('current_course/', views.current_course, name="current_course"),

    # ── ML Dashboard ──────────────────────────────────────────────────────────
    path('ml_dashboard/', views.ml_dashboard, name="ml_dashboard"),

    # courses urls
    path('courses/cn_course/networking_course/', views.cn_course, name="cn_course"),
    path('courses/cpp_course/cpp_course/', views.cpp_course, name="cpp_course"),
    path('courses/dbms_course/dbms_course/', views.dbms_course, name="dbms_course"),
    path('courses/devops_course/devops_course/', views.devops_course, name="devops_course"),
    path('courses/java_course/java_course/', views.java_course, name="java_course"),
    path('courses/os_course/os_course/', views.os_course, name="os_course"),
    path('courses/python_course/python_course/', views.python_course, name="python_course"),

    # cn course content urls
    path('courses/cn_course/content/intro/', views.cn_course_intro, name="cn_course_intro"),
    path('courses/cn_course/content/osi/', views.cn_course_osi, name="cn_course_osi"),
    path('courses/cn_course/content/ipadd/', views.cn_course_ipadd, name="cn_course_ipadd"),
    path('courses/cn_course/content/protocols/', views.cn_course_protocols, name="cn_course_protocols"),
    path('courses/cn_course/content/routingswitching/', views.cn_course_routingswitching, name="cn_course_routingswitching"),

    # cpp course content urls
    path('courses/cpp_course/content/contloops/', views.cpp_contloops, name="cpp_contloops"),
    path('courses/cpp_course/content/funcarr/', views.cpp_funcarr, name="cpp_funcarr"),
    path('courses/cpp_course/content/oop/', views.cpp_oop, name="cpp_oop"),
    path('courses/cpp_course/content/stl/', views.cpp_stl, name="cpp_stl"),
    path('courses/cpp_course/content/syntax/', views.cpp_syntax, name="cpp_syntax"),

    # dbms course content urls
    path('courses/dbms_course/content/er/', views.dbms_er, name="dbms_er"),
    path('courses/dbms_course/content/intro/', views.dbms_intro, name="dbms_intro"),
    path('courses/dbms_course/content/normalization/', views.dbms_normalization, name="dbms_normalization"),
    path('courses/dbms_course/content/sqlqueries/', views.dbms_sqlqueries, name="dbms_sqlqueries"),
    path('courses/dbms_course/content/transcurrency/', views.dbms_transcurrency, name="dbms_transcurrency"),

    # devops course content urls
    path('courses/devops_course/content/cicd/', views.devops_cicd, name="devops_cicd"),
    path('courses/devops_course/content/docker/', views.devops_docker, name="devops_docker"),
    path('courses/devops_course/content/git/', views.devops_git, name="devops_git"),
    path('courses/devops_course/content/intro/', views.devops_intro, name="devops_intro"),
    path('courses/devops_course/content/jenkins/', views.devops_jenkins, name="devops_jenkins"),

    # java course content urls
    path('courses/java_course/content/basics/', views.java_basics, name="java_basics"),
    path('courses/java_course/content/classobjoop/', views.java_classobjoop, name="java_classobjoop"),
    path('courses/java_course/content/collectionstreams/', views.collectionstreams, name="collectionstreams"),
    path('courses/java_course/content/contstat/', views.java_contstat, name="java_contstat"),
    path('courses/java_course/content/excepthandle/', views.java_exhandling, name="java_exhandling"),

    # os course content urls
    path('courses/os_course/content/cpuscheduling/', views.os_cpuscheduling, name="os_cpuscheduling"),
    path('courses/os_course/content/deadlocksync/', views.os_deadlocksync, name="os_deadlocksync"),
    path('courses/os_course/content/intro/', views.os_intro, name="os_intro"),
    path('courses/os_course/content/management/', views.os_management, name="os_management"),
    path('courses/os_course/content/procman/', views.os_procman, name="os_procman"),

    # python course content urls
    path('courses/python_course/content/condloops/', views.py_condloops, name="py_condloops"),
    path('courses/python_course/content/filehand/', views.py_filehand, name="py_filehand"),
    path('courses/python_course/content/funcmod/', views.py_funcmod, name="py_funcmod"),
    path('courses/python_course/content/libs/', views.py_libs, name="py_libs"),
    path('courses/python_course/content/vardat/', views.py_vardat, name="py_vardat"),

    # Study room urls
    path('study_rooms/', views.study_rooms, name='study_rooms'),
    path('study-rooms/create/', views.create_study_room, name='create_study_room'),
    path('study-rooms/join/<int:room_id>/', views.join_study_room, name='join_study_room'),
    path('study-rooms/leave/<int:room_id>/', views.leave_study_room, name='leave_study_room'),
    path('study-rooms/delete/<int:room_id>/', views.delete_study_room, name='delete_study_room'),
    path('study-rooms/chat/<int:room_id>/', views.study_room_chat, name='study_room_chat'),
    path('study-rooms/chat/<int:room_id>/send/', views.send_message, name='send_message'),

    path('monitor/view-room/<int:room_id>/', views.view_room_as_admin, name='view_room_as_admin'),

    # chatbot urls
    path("chatbot/", views.chatbot_view, name="chatbot"),
    path("chat/", views.chat_api, name="chat_api"),

    # Save Note urls
    path("save_note/", views.save_note, name="save_note"),
    path("my_notes/", views.view_notes, name="view_notes"),

    path('rankings/', views.rankings, name='rankings'),
    path('thirdcard', views.thirdcard, name="thirdcard"),
]

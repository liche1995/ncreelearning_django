from lesson_app.models import *


# 判定是否參加課程
def already_in_lesson(student_id: int, lesson_id: int):
    try:
        query = Studentlist.objects.get(student_id=student_id, lesson_id_id=lesson_id)
        return True
    except Studentlist.DoesNotExist:
        return False


# 是否已繳交作業
def already_submit_hw(student_id: int, hwid: int):
    try:
        query = HomeworkSubmit.objects.get(user_id=student_id, homework_id_id=hwid)
        return True
    except HomeworkSubmit.DoesNotExist:
        return False

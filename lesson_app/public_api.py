from lesson_app.models import *


# 判定是否參加課程
def already_in_lesson(student_id: int, lesson_id: int):
    try:
        query = Studentlist.objects.get(student_id=student_id, lesson_id_id=lesson_id)
        return True
    except Studentlist.DoesNotExist:
        return False

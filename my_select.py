from sqlalchemy import func, select

from database import Session
from models import Grade, Group, Student, Subject, Teacher


def select_1():
    """5 студентів із найбільшим середнім балом з усіх предметів."""
    with Session() as session:
        avg_grade = func.round(func.avg(Grade.grade), 2)
        stmt = (
            select(Student.fullname, avg_grade.label("avg_grade"))
            .join(Grade)
            .group_by(Student.id)
            .order_by(avg_grade.desc())
            .limit(5)
        )
        return session.execute(stmt).all()


def select_2(subject_id: int):
    """Студент із найвищим середнім балом з певного предмета."""
    with Session() as session:
        avg_grade = func.round(func.avg(Grade.grade), 2)
        stmt = (
            select(Student.fullname, avg_grade.label("avg_grade"))
            .join(Grade)
            .where(Grade.subject_id == subject_id)
            .group_by(Student.id)
            .order_by(avg_grade.desc())
            .limit(1)
        )
        return session.execute(stmt).all()


def select_3(subject_id: int):
    """Середній бал у групах з певного предмета."""
    with Session() as session:
        avg_grade = func.round(func.avg(Grade.grade), 2)
        stmt = (
            select(Group.name, avg_grade.label("avg_grade"))
            .join(Student, Student.group_id == Group.id)
            .join(Grade, Grade.student_id == Student.id)
            .where(Grade.subject_id == subject_id)
            .group_by(Group.id)
            .order_by(Group.name)
        )
        return session.execute(stmt).all()


def select_4():
    """Середній бал на потоці."""
    with Session() as session:
        stmt = select(func.round(func.avg(Grade.grade), 2).label("avg_grade"))
        return session.execute(stmt).all()


def select_5(teacher_id: int):
    """Курси, які читає певний викладач."""
    with Session() as session:
        stmt = (
            select(Subject.name)
            .where(Subject.teacher_id == teacher_id)
            .order_by(Subject.name)
        )
        return session.execute(stmt).all()


def select_6(group_id: int):
    """Список студентів у певній групі."""
    with Session() as session:
        stmt = (
            select(Student.fullname)
            .where(Student.group_id == group_id)
            .order_by(Student.fullname)
        )
        return session.execute(stmt).all()


def select_7(group_id: int, subject_id: int):
    """Оцінки студентів у групі з певного предмета."""
    with Session() as session:
        stmt = (
            select(Student.fullname, Grade.grade, Grade.date_of)
            .join(Grade, Grade.student_id == Student.id)
            .where(Student.group_id == group_id, Grade.subject_id == subject_id)
            .order_by(Student.fullname, Grade.date_of)
        )
        return session.execute(stmt).all()


def select_8(teacher_id: int):
    """Середній бал, який ставить певний викладач зі своїх предметів."""
    with Session() as session:
        stmt = (
            select(func.round(func.avg(Grade.grade), 2).label("avg_grade"))
            .join(Subject, Grade.subject_id == Subject.id)
            .where(Subject.teacher_id == teacher_id)
        )
        return session.execute(stmt).all()


def select_9(student_id: int):
    """Список курсів, які відвідує певний студент."""
    with Session() as session:
        stmt = (
            select(Subject.name)
            .join(Grade, Grade.subject_id == Subject.id)
            .where(Grade.student_id == student_id)
            .distinct()
            .order_by(Subject.name)
        )
        return session.execute(stmt).all()


def select_10(student_id: int, teacher_id: int):
    """Курси, які певному студенту читає певний викладач."""
    with Session() as session:
        stmt = (
            select(Subject.name)
            .join(Grade, Grade.subject_id == Subject.id)
            .where(Grade.student_id == student_id, Subject.teacher_id == teacher_id)
            .distinct()
            .order_by(Subject.name)
        )
        return session.execute(stmt).all()


def select_11(teacher_id: int, student_id: int):
    """Середній бал, який певний викладач ставить певному студентові."""
    with Session() as session:
        stmt = (
            select(func.round(func.avg(Grade.grade), 2).label("avg_grade"))
            .join(Subject, Grade.subject_id == Subject.id)
            .where(Grade.student_id == student_id, Subject.teacher_id == teacher_id)
        )
        return session.execute(stmt).all()


def select_12(group_id: int, subject_id: int):
    """Оцінки студентів групи з предмета на останньому занятті."""
    with Session() as session:
        last_date = (
            select(func.max(Grade.date_of))
            .join(Student, Grade.student_id == Student.id)
            .where(Student.group_id == group_id, Grade.subject_id == subject_id)
            .scalar_subquery()
        )
        stmt = (
            select(Student.fullname, Grade.grade, Grade.date_of)
            .join(Grade, Grade.student_id == Student.id)
            .where(
                Student.group_id == group_id,
                Grade.subject_id == subject_id,
                Grade.date_of == last_date,
            )
            .order_by(Student.fullname)
        )
        return session.execute(stmt).all()


def _sample_ids():
    with Session() as session:
        group_id = session.scalar(select(Group.id).order_by(Group.id).limit(1))
        subject_id = session.scalar(select(Subject.id).order_by(Subject.id).limit(1))
        teacher_id = session.scalar(select(Teacher.id).order_by(Teacher.id).limit(1))
        student_id = session.scalar(select(Student.id).order_by(Student.id).limit(1))
    return group_id, subject_id, teacher_id, student_id


def _print(title, rows):
    print(f"\n{title}")
    if not rows:
        print("  (немає даних)")
        return
    for row in rows:
        print(f"  {tuple(row)}")


if __name__ == "__main__":
    group_id, subject_id, teacher_id, student_id = _sample_ids()
    _print("1. Топ-5 студентів за середнім балом", select_1())
    _print(f"2. Найкращий студент із предмета id={subject_id}", select_2(subject_id))
    _print(f"3. Середній бал груп із предмета id={subject_id}", select_3(subject_id))
    _print("4. Середній бал на потоці", select_4())
    _print(f"5. Курси викладача id={teacher_id}", select_5(teacher_id))
    _print(f"6. Студенти групи id={group_id}", select_6(group_id))
    _print(
        f"7. Оцінки групи id={group_id} з предмета id={subject_id}",
        select_7(group_id, subject_id),
    )
    _print(f"8. Середній бал викладача id={teacher_id}", select_8(teacher_id))
    _print(f"9. Курси студента id={student_id}", select_9(student_id))
    _print(
        f"10. Курси викладача id={teacher_id} для студента id={student_id}",
        select_10(student_id, teacher_id),
    )
    _print(
        f"11. Середній бал викладача id={teacher_id} студентові id={student_id}",
        select_11(teacher_id, student_id),
    )
    _print(
        f"12. Оцінки групи id={group_id} з предмета id={subject_id} на останньому занятті",
        select_12(group_id, subject_id),
    )

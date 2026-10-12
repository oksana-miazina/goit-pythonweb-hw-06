import random
from datetime import date, timedelta

from faker import Faker
from sqlalchemy import func, select

from database import Session
from models import Grade, Group, Student, Subject, Teacher

fake = Faker("uk_UA")

SUBJECT_NAMES = [
    "Математика",
    "Фізика",
    "Хімія",
    "Історія",
    "Українська мова",
    "Англійська мова",
    "Інформатика",
    "Біологія",
]


def seed() -> None:
    with Session() as session:
        existing = session.scalar(select(func.count()).select_from(Group))
        if existing:
            print("База вже містить дані, наповнення пропущено.")
            return

        groups = [Group(name=name) for name in ("АД-101", "БВ-202", "ГД-303")]
        teachers = [Teacher(fullname=fake.name()) for _ in range(random.randint(3, 5))]
        subject_names = random.sample(SUBJECT_NAMES, k=random.randint(5, 8))
        subjects = [
            Subject(name=name, teacher=random.choice(teachers)) for name in subject_names
        ]
        students = [
            Student(fullname=fake.name(), group=random.choice(groups))
            for _ in range(random.randint(30, 50))
        ]

        session.add_all(groups + teachers + subjects + students)
        session.flush()

        today = date.today()
        lesson_days = [today - timedelta(days=14 * offset) for offset in range(15)]
        grades = []
        for student in students:
            for subject in subjects:
                for _ in range(random.randint(1, 20)):
                    grades.append(
                        Grade(
                            student_id=student.id,
                            subject_id=subject.id,
                            grade=random.randint(1, 100),
                            date_of=random.choice(lesson_days),
                        )
                    )

        session.add_all(grades)
        session.commit()
        print(
            f"Додано груп: {len(groups)}, студентів: {len(students)}, "
            f"викладачів: {len(teachers)}, предметів: {len(subjects)}, "
            f"оцінок: {len(grades)}."
        )


if __name__ == "__main__":
    seed()

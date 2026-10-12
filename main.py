import argparse
import sys
from datetime import date

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database import Session
from models import Grade, Group, Student, Subject, Teacher

MODELS = {
    "Teacher": Teacher,
    "Group": Group,
    "Student": Student,
    "Subject": Subject,
    "Grade": Grade,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CRUD для бази університету")
    parser.add_argument(
        "-a",
        "--action",
        required=True,
        choices=["create", "list", "update", "remove"],
    )
    parser.add_argument("-m", "--model", required=True, choices=list(MODELS))
    parser.add_argument("-n", "--name")
    parser.add_argument("--id", type=int)
    parser.add_argument("--group-id", type=int)
    parser.add_argument("--teacher-id", type=int)
    parser.add_argument("--student-id", type=int)
    parser.add_argument("--subject-id", type=int)
    parser.add_argument("--grade", type=int)
    parser.add_argument("--date")
    return parser


def _fail(message: str) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(1)


def _require(args: argparse.Namespace, *fields: str) -> None:
    missing = [field for field in fields if getattr(args, field) is None]
    if missing:
        flags = ", ".join(f"--{field.replace('_', '-')}" for field in missing)
        _fail(f"Потрібні аргументи: {flags}")


def _parse_date(value: str | None) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        _fail("Дата має бути у форматі РРРР-ММ-ДД")


def _check_grade(value: int | None) -> None:
    if value is not None and not 1 <= value <= 100:
        _fail("Оцінка має бути цілим числом від 1 до 100")


def _get_or_fail(session, model, record_id: int):
    record = session.get(model, record_id)
    if record is None:
        _fail(f"{model.__name__} з id={record_id} не знайдено")
    return record


def _ensure_exists(session, model, record_id: int) -> None:
    if session.get(model, record_id) is None:
        _fail(f"{model.__name__} з id={record_id} не знайдено")


def _format(record) -> str:
    if isinstance(record, Teacher):
        return f"id={record.id} name={record.fullname}"
    if isinstance(record, Group):
        return f"id={record.id} name={record.name}"
    if isinstance(record, Student):
        return f"id={record.id} name={record.fullname} group_id={record.group_id}"
    if isinstance(record, Subject):
        return f"id={record.id} name={record.name} teacher_id={record.teacher_id}"
    return (
        f"id={record.id} student_id={record.student_id} "
        f"subject_id={record.subject_id} grade={record.grade} date={record.date_of}"
    )


def create(args: argparse.Namespace) -> None:
    with Session() as session:
        if args.model in {"Teacher", "Group", "Student", "Subject"}:
            _require(args, "name")

        if args.model == "Teacher":
            record = Teacher(fullname=args.name)
        elif args.model == "Group":
            record = Group(name=args.name)
        elif args.model == "Student":
            _require(args, "group_id")
            _ensure_exists(session, Group, args.group_id)
            record = Student(fullname=args.name, group_id=args.group_id)
        elif args.model == "Subject":
            _require(args, "teacher_id")
            _ensure_exists(session, Teacher, args.teacher_id)
            record = Subject(name=args.name, teacher_id=args.teacher_id)
        else:
            _require(args, "student_id", "subject_id", "grade")
            _check_grade(args.grade)
            _ensure_exists(session, Student, args.student_id)
            _ensure_exists(session, Subject, args.subject_id)
            record = Grade(
                student_id=args.student_id,
                subject_id=args.subject_id,
                grade=args.grade,
                date_of=_parse_date(args.date) or date.today(),
            )

        session.add(record)
        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            _fail("Запис із такими даними вже існує")
        print(_format(record))


def list_records(args: argparse.Namespace) -> None:
    model = MODELS[args.model]
    with Session() as session:
        records = session.scalars(select(model).order_by(model.id)).all()
        if not records:
            print("Записів немає")
            return
        for record in records:
            print(_format(record))


def update(args: argparse.Namespace) -> None:
    _require(args, "id")
    model = MODELS[args.model]
    with Session() as session:
        record = _get_or_fail(session, model, args.id)
        changed = False

        if args.model == "Teacher" and args.name is not None:
            record.fullname = args.name
            changed = True
        elif args.model == "Group" and args.name is not None:
            record.name = args.name
            changed = True
        elif args.model == "Student":
            if args.name is not None:
                record.fullname = args.name
                changed = True
            if args.group_id is not None:
                _ensure_exists(session, Group, args.group_id)
                record.group_id = args.group_id
                changed = True
        elif args.model == "Subject":
            if args.name is not None:
                record.name = args.name
                changed = True
            if args.teacher_id is not None:
                _ensure_exists(session, Teacher, args.teacher_id)
                record.teacher_id = args.teacher_id
                changed = True
        elif args.model == "Grade":
            if args.student_id is not None:
                _ensure_exists(session, Student, args.student_id)
                record.student_id = args.student_id
                changed = True
            if args.subject_id is not None:
                _ensure_exists(session, Subject, args.subject_id)
                record.subject_id = args.subject_id
                changed = True
            if args.grade is not None:
                _check_grade(args.grade)
                record.grade = args.grade
                changed = True
            parsed_date = _parse_date(args.date)
            if parsed_date is not None:
                record.date_of = parsed_date
                changed = True

        if not changed:
            _fail("Немає полів для оновлення")

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            _fail("Запис із такими даними вже існує")
        print(_format(record))


def remove(args: argparse.Namespace) -> None:
    _require(args, "id")
    model = MODELS[args.model]
    with Session() as session:
        record = _get_or_fail(session, model, args.id)
        session.delete(record)
        session.commit()
        print(f"Видалено {args.model} id={args.id}")


def main() -> None:
    args = build_parser().parse_args()
    {
        "create": create,
        "list": list_records,
        "update": update,
        "remove": remove,
    }[args.action](args)


if __name__ == "__main__":
    main()

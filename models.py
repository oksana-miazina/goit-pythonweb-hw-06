from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    students: Mapped[list["Student"]] = relationship(back_populates="group")


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String(150))
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id", ondelete="CASCADE"))
    group: Mapped["Group"] = relationship(back_populates="students")
    grades: Mapped[list["Grade"]] = relationship(back_populates="student")


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    fullname: Mapped[str] = mapped_column(String(150))
    subjects: Mapped[list["Subject"]] = relationship(back_populates="teacher")


class Subject(Base):
    __tablename__ = "subjects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True)
    teacher_id: Mapped[int] = mapped_column(
        ForeignKey("teachers.id", ondelete="CASCADE")
    )
    teacher: Mapped["Teacher"] = relationship(back_populates="subjects")
    grades: Mapped[list["Grade"]] = relationship(back_populates="subject")


class Grade(Base):
    __tablename__ = "grades"

    id: Mapped[int] = mapped_column(primary_key=True)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE")
    )
    subject_id: Mapped[int] = mapped_column(
        ForeignKey("subjects.id", ondelete="CASCADE")
    )
    grade: Mapped[int] = mapped_column(Integer)
    date_of: Mapped[date] = mapped_column(Date)
    student: Mapped["Student"] = relationship(back_populates="grades")
    subject: Mapped["Subject"] = relationship(back_populates="grades")

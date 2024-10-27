from typing import List, Optional

from sqlalchemy import BigInteger, Column, DateTime, ForeignKeyConstraint, Integer, PrimaryKeyConstraint, String, text
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

Base = declarative_base()


class Policy(Base):
    __tablename__ = 'Policy'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='Policy_pkey'),
    )

    id = mapped_column(BigInteger)
    name = mapped_column(String(255))
    create_at = mapped_column(DateTime(True))
    update_at = mapped_column(DateTime(True))


class Server(Base):
    __tablename__ = 'Server'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='Server_pkey'),
    )

    id = mapped_column(BigInteger)
    ip = mapped_column(String(255), nullable=False)
    name = mapped_column(String(255), nullable=False)
    create_at = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    Container: Mapped[List['Container']] = relationship('Container', uselist=True, back_populates='Server_')


class Tag(Base):
    __tablename__ = 'Tag'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='Tag_pkey'),
    )

    id = mapped_column(BigInteger)
    name = mapped_column(String(255), nullable=False)

    Container: Mapped[List['Container']] = relationship('Container', uselist=True, back_populates='Tag_')


class Container(Base):
    __tablename__ = 'Container'
    __table_args__ = (
        ForeignKeyConstraint(['host_server'], ['Server.id'], name='FK__Server'),
        ForeignKeyConstraint(['tag'], ['Tag.id'], name='FK_Container_Tag'),
        PrimaryKeyConstraint('host_server', 'pid_id', 'mnt_id', name='Container_pkey')
    )

    host_server = mapped_column(BigInteger, nullable=False)
    pid_id = mapped_column(Integer, nullable=False)
    mnt_id = mapped_column(Integer, nullable=False)
    runtime = mapped_column(String(100), nullable=False)
    name = mapped_column(String(255), nullable=False)
    create_at = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    remove_at = mapped_column(DateTime(True), nullable=False)
    tag = mapped_column(BigInteger)

    Server_: Mapped['Server'] = relationship('Server', back_populates='Container')
    Tag_: Mapped[Optional['Tag']] = relationship('Tag', back_populates='Container')

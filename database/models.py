from typing import List, Optional

from sqlalchemy import BigInteger, Column, DateTime, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String, text
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

from database.database import project_base

Base = project_base


class Heartbeat(Base):
    __tablename__ = 'Heartbeat'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='Heartbeat_pkey'),
    )

    id = mapped_column(BigInteger)
    ip = mapped_column(String(255), nullable=False)
    timestamp = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    survival_container_cnt = mapped_column(Integer, nullable=False, server_default=text('0'))


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
        PrimaryKeyConstraint('id', name='Container_pkey'),
        Index('idx_host_pid_mnt', 'host_server', 'pid_id', 'mnt_id')
    )

    host_server = mapped_column(BigInteger, nullable=False)
    runtime = mapped_column(String(100), nullable=False)
    name = mapped_column(String(255), nullable=False)
    create_at = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    id = mapped_column(BigInteger)
    pid_id = mapped_column(Integer)
    mnt_id = mapped_column(Integer)
    tag = mapped_column(BigInteger)
    remove_at = mapped_column(DateTime(True))

    Server_: Mapped['Server'] = relationship('Server', back_populates='Container')
    Tag_: Mapped[Optional['Tag']] = relationship('Tag', back_populates='Container')

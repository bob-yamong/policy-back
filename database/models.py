from typing import List

from sqlalchemy import ARRAY, BigInteger, Column, DateTime, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String, Table, text
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship
from sqlalchemy.orm.base import Mapped

from database.database import project_base

Base = project_base
metadata = Base.metadata

class Heartbeat(Base):
    __tablename__ = 'Heartbeat'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='Heartbeat_pkey'),
    )

    id = mapped_column(BigInteger)
    ip = mapped_column(String(255), nullable=False)
    timestamp = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    survival_container_cnt = mapped_column(Integer, nullable=False, server_default=text('0'))
    req_ip = mapped_column(String(255), nullable=False)


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

    container: Mapped['Container'] = relationship('Container', secondary='Container_tag', back_populates='tag')


class Container(Base):
    __tablename__ = 'Container'
    __table_args__ = (
        ForeignKeyConstraint(['host_server'], ['Server.id'], name='FK__Server'),
        PrimaryKeyConstraint('id', name='Container_pkey'),
        Index('host_server_name', 'host_server', 'name', unique=True)
    )

    host_server = mapped_column(BigInteger, nullable=False)
    runtime = mapped_column(String(100), nullable=False)
    name = mapped_column(String(255), nullable=False)
    create_at = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    id = mapped_column(BigInteger)

    Server_: Mapped['Server'] = relationship('Server', back_populates='Container')
    tag: Mapped['Tag'] = relationship('Tag', secondary='Container_tag', back_populates='container')
    InternalContainerId: Mapped[List['InternalContainerId']] = relationship('InternalContainerId', uselist=True, back_populates='container')


t_Container_tag = Table(
    'Container_tag', metadata,
    Column('container_id', BigInteger, nullable=False),
    Column('tag_id', BigInteger, nullable=False),
    ForeignKeyConstraint(['container_id'], ['Container.id'], name='FK__Container'),
    ForeignKeyConstraint(['tag_id'], ['Tag.id'], name='FK__Tag'),
    PrimaryKeyConstraint('container_id', 'tag_id', name='Container_tag_pkey')
)


class InternalContainerId(Base):
    __tablename__ = 'InternalContainerId'
    __table_args__ = (
        ForeignKeyConstraint(['container_id'], ['Container.id'], name='FK_InternalContainerId_Container'),
        PrimaryKeyConstraint('id', name='InternalContainerId_pkey'),
        Index('container_id_pid_id_mnt_id_cgroup_id', 'container_id', 'pid_id', 'mnt_id', 'cgroup_id', unique=True)
    )

    id = mapped_column(BigInteger)
    container_id = mapped_column(BigInteger, nullable=False)
    pid_id = mapped_column(Integer, nullable=False)
    mnt_id = mapped_column(Integer, nullable=False)
    cgroup_id = mapped_column(Integer, nullable=False)
    reg_time = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    container: Mapped['Container'] = relationship('Container', back_populates='InternalContainerId')

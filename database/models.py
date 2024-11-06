from typing import List

from sqlalchemy import BigInteger, DateTime, Float, ForeignKeyConstraint, Index, Integer, JSON, PrimaryKeyConstraint, Sequence, SmallInteger, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
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
    uuid = mapped_column(String(255), nullable=False)
    timestamp = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    survival_container_cnt = mapped_column(Integer, nullable=False, server_default=text('0'))
    req_ip = mapped_column(String(255), nullable=False)


class Policy(Base):
    __tablename__ = 'Policy'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='Policy_pkey'),
        Index('policy_name', 'name', unique=True)
    )

    id = mapped_column(BigInteger)
    name = mapped_column(String(255), nullable=False)
    created_at = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    api_version = mapped_column(String(255), nullable=False)
    updated_at = mapped_column(DateTime(True))

    LsmFilePolicy: Mapped[List['LsmFilePolicy']] = relationship('LsmFilePolicy', uselist=True, back_populates='policy')
    LsmNetPolicy: Mapped[List['LsmNetPolicy']] = relationship('LsmNetPolicy', uselist=True, back_populates='policy')
    LsmProcPolicy: Mapped[List['LsmProcPolicy']] = relationship('LsmProcPolicy', uselist=True, back_populates='policy')
    RawTracePointPolicy: Mapped[List['RawTracePointPolicy']] = relationship('RawTracePointPolicy', uselist=True, back_populates='policy')
    TracepointPolicy: Mapped[List['TracepointPolicy']] = relationship('TracepointPolicy', uselist=True, back_populates='policy')


class Server(Base):
    __tablename__ = 'Server'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='Server_pkey'),
        Index('uuid', 'uuid', unique=True)
    )

    id = mapped_column(BigInteger)
    uuid = mapped_column(String(255), nullable=False)
    name = mapped_column(String(255), nullable=False)
    created_at = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    containers: Mapped[List['Container']] = relationship('Container', uselist=True, back_populates='server')
    SystemInfo: Mapped[List['SystemInfo']] = relationship('SystemInfo', uselist=True, back_populates='server')

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
    created_at = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))
    id = mapped_column(BigInteger)
    removed_at = mapped_column(DateTime(True))

    server: Mapped['Server'] = relationship('Server', back_populates='containers')
    tag: Mapped['Tag'] = relationship('Tag', secondary='Container_tag', back_populates='container')
    InternalContainerId: Mapped[List['InternalContainerId']] = relationship('InternalContainerId', uselist=True, back_populates='container')
    LsmFilePolicy: Mapped[List['LsmFilePolicy']] = relationship('LsmFilePolicy', uselist=True, back_populates='container')
    LsmNetPolicy: Mapped[List['LsmNetPolicy']] = relationship('LsmNetPolicy', uselist=True, back_populates='container')
    LsmProcPolicy: Mapped[List['LsmProcPolicy']] = relationship('LsmProcPolicy', uselist=True, back_populates='container')
    RawTracePointPolicy: Mapped[List['RawTracePointPolicy']] = relationship('RawTracePointPolicy', uselist=True, back_populates='container')
    TracepointPolicy: Mapped[List['TracepointPolicy']] = relationship('TracepointPolicy', uselist=True, back_populates='container')
    ContainerSysInfo: Mapped[List['ContainerSysInfo']] = relationship('ContainerSysInfo', uselist=True, back_populates='container')

class SystemInfo(Base):
    __tablename__ = 'SystemInfo'
    __table_args__ = (
        ForeignKeyConstraint(['server_id'], ['Server.id'], name='FK_SystemInfo_Server'),
        PrimaryKeyConstraint('server_id', 'timestamp', name='SystemInfo_pkey')
    )

    server_id = mapped_column(BigInteger, nullable=False)
    cpu_logic_core = mapped_column(SmallInteger, nullable=False)
    cpu_physic_core = mapped_column(SmallInteger, nullable=False)
    cpu_percent = mapped_column(Float, nullable=False)
    cpu_core_usage = mapped_column(JSON, nullable=False)
    mem_total = mapped_column(Float, nullable=False)
    mem_used = mapped_column(Float, nullable=False)
    mem_percent = mapped_column(Float, nullable=False)
    disk_read_mb = mapped_column(Float, nullable=False)
    disk_write_mb = mapped_column(Float, nullable=False)
    disk_total = mapped_column(Float, nullable=False)
    disk_used = mapped_column(Float, nullable=False)
    disk_percent = mapped_column(Float, nullable=False)
    net_recv_data_mb = mapped_column(Float, nullable=False)
    net_send_data_mb = mapped_column(Float, nullable=False)
    net_recv_packets = mapped_column(Integer, nullable=False)
    net_send_packets = mapped_column(Integer, nullable=False)
    net_recv_err = mapped_column(Integer, nullable=False)
    net_send_err = mapped_column(Integer, nullable=False)
    timestamp = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    server: Mapped['Server'] = relationship('Server', back_populates='SystemInfo')

class ContainerSysInfo(Base):
    __tablename__ = 'ContainerSysInfo'
    __table_args__ = (
        ForeignKeyConstraint(['container_id'], ['Container.id'], name='FK_ContainerSysInfo_Container'),
        PrimaryKeyConstraint('container_id', 'timestamp', name='ContainerSysInfo_pkey')
    )

    container_id = mapped_column(BigInteger, nullable=False)
    cpu_kernel = mapped_column(Float, nullable=False)
    cpu_user = mapped_column(Float, nullable=False)
    cpu_percent = mapped_column(Float, nullable=False)
    cpu_online = mapped_column(Float, nullable=False)
    disk_read_mb = mapped_column(Float, nullable=False)
    disk_write_mb = mapped_column(Float, nullable=False)
    mem_limit = mapped_column(Float, nullable=False)
    mem_usage = mapped_column(Float, nullable=False)
    mem_percent = mapped_column(Float, nullable=False)
    net_recv_mb = mapped_column(Float, nullable=False)
    net_send_mb = mapped_column(Float, nullable=False)
    net_recv_packets = mapped_column(Integer, nullable=False)
    net_send_packets = mapped_column(Integer, nullable=False)
    proc_cnt = mapped_column(Integer, nullable=False)
    timestamp = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    container: Mapped['Container'] = relationship('Container', back_populates='ContainerSysInfo')


class ContainerTag(Base):
    __tablename__ = 'Container_tag'
    __table_args__ = (
        ForeignKeyConstraint(['container_id'], ['Container.id'], name='FK__Container'),
        ForeignKeyConstraint(['tag_id'], ['Tag.id'], name='FK__Tag'),
        PrimaryKeyConstraint('container_id', 'tag_id', name='Container_tag_pkey')
    )

    container_id = mapped_column(BigInteger, nullable=False, primary_key=True)
    tag_id = mapped_column(BigInteger, nullable=False, primary_key=True)


class InternalContainerId(Base):
    __tablename__ = 'InternalContainerId'
    __table_args__ = (
        ForeignKeyConstraint(['container_id'], ['Container.id'], name='FK_InternalContainerId_Container'),
        PrimaryKeyConstraint('id', name='InternalContainerId_pkey'),
        Index('container_id_pid_id_mnt_id_cgroup_id', 'container_id', 'pid_id', 'mnt_id', 'cgroup_id', unique=True)
    )

    id = mapped_column(BigInteger)
    container_id = mapped_column(BigInteger, nullable=False)
    pid_id = mapped_column(BigInteger, nullable=False)
    mnt_id = mapped_column(BigInteger, nullable=False)
    cgroup_id = mapped_column(BigInteger, nullable=False)
    reg_time = mapped_column(DateTime(True), nullable=False, server_default=text('CURRENT_TIMESTAMP'))

    container: Mapped['Container'] = relationship('Container', back_populates='InternalContainerId')


class LsmFilePolicy(Base):
    __tablename__ = 'LsmFilePolicy'
    __table_args__ = (
        ForeignKeyConstraint(['container_id'], ['Container.id'], name='FK__Container'),
        ForeignKeyConstraint(['policy_id'], ['Policy.id'], name='FK__Policy'),
        PrimaryKeyConstraint('id', name='lsmFilePolicy_pkey'),
        Index('container_id_path', 'container_id', 'path', unique=True)
    )

    id = mapped_column(BigInteger, Sequence('lsmFilePolicy_id_seq'))
    policy_id = mapped_column(BigInteger, nullable=False)
    container_id = mapped_column(BigInteger, nullable=False)
    path = mapped_column(String(4096), nullable=False)
    flags = mapped_column(JSON, nullable=False)
    uid = mapped_column(JSON, nullable=False)

    container: Mapped['Container'] = relationship('Container', back_populates='LsmFilePolicy')
    policy: Mapped['Policy'] = relationship('Policy', back_populates='LsmFilePolicy')


class LsmNetPolicy(Base):
    __tablename__ = 'LsmNetPolicy'
    __table_args__ = (
        ForeignKeyConstraint(['container_id'], ['Container.id'], name='FK__Container'),
        ForeignKeyConstraint(['policy_id'], ['Policy.id'], name='FK__Policy'),
        PrimaryKeyConstraint('id', name='LsmNetPolicy_pkey')
    )

    id = mapped_column(BigInteger)
    policy_id = mapped_column(BigInteger, nullable=False)
    container_id = mapped_column(BigInteger, nullable=False)
    ip = mapped_column(String(256), nullable=False)
    port = mapped_column(Integer, nullable=False)
    protocol = mapped_column(SmallInteger, nullable=False)
    flags = mapped_column(JSON, nullable=False)
    uid = mapped_column(JSON, nullable=False)

    container: Mapped['Container'] = relationship('Container', back_populates='LsmNetPolicy')
    policy: Mapped['Policy'] = relationship('Policy', back_populates='LsmNetPolicy')


class LsmProcPolicy(Base):
    __tablename__ = 'LsmProcPolicy'
    __table_args__ = (
        ForeignKeyConstraint(['container_id'], ['Container.id'], name='FK__Container'),
        ForeignKeyConstraint(['policy_id'], ['Policy.id'], name='FK__Policy'),
        PrimaryKeyConstraint('id', name='LsmProcPolicy_pkey'),
        Index('container_id_comm', 'container_id', 'comm', unique=True)
    )

    id = mapped_column(BigInteger)
    policy_id = mapped_column(BigInteger, nullable=False)
    container_id = mapped_column(BigInteger, nullable=False)
    comm = mapped_column(String(16), nullable=False)
    flags = mapped_column(JSON, nullable=False)
    uid = mapped_column(JSON, nullable=False)

    container: Mapped['Container'] = relationship('Container', back_populates='LsmProcPolicy')
    policy: Mapped['Policy'] = relationship('Policy', back_populates='LsmProcPolicy')


class RawTracePointPolicy(Base):
    __tablename__ = 'RawTracePointPolicy'
    __table_args__ = (
        ForeignKeyConstraint(['container_id'], ['Container.id'], name='FK__Container'),
        ForeignKeyConstraint(['policy_id'], ['Policy.id'], name='FK__Policy'),
        PrimaryKeyConstraint('id', name='RawTracePointPolicy_pkey'),
        Index('container_id_state', 'container_id', 'state', unique=True)
    )

    id = mapped_column(BigInteger)
    policy_id = mapped_column(BigInteger, nullable=False)
    container_id = mapped_column(BigInteger, nullable=False)
    state = mapped_column(String(4), nullable=False)

    container: Mapped['Container'] = relationship('Container', back_populates='RawTracePointPolicy')
    policy: Mapped['Policy'] = relationship('Policy', back_populates='RawTracePointPolicy')


class TracepointPolicy(Base):
    __tablename__ = 'TracepointPolicy'
    __table_args__ = (
        ForeignKeyConstraint(['container_id'], ['Container.id'], name='FK_TracepointPolicy_Container'),
        ForeignKeyConstraint(['policy_id'], ['Policy.id'], name='FK_TracepointPolicy_Policy'),
        PrimaryKeyConstraint('id', name='TracepointPolicy_pkey')
    )

    id = mapped_column(BigInteger)
    policy_id = mapped_column(BigInteger, nullable=False)
    container_id = mapped_column(BigInteger, nullable=False)
    tracepoint = mapped_column(String(100), nullable=False)

    container: Mapped['Container'] = relationship('Container', back_populates='TracepointPolicy')
    policy: Mapped['Policy'] = relationship('Policy', back_populates='TracepointPolicy')

from sqlalchemy.orm import Session
from sqlalchemy import Float, func
from fastapi import Request
from statistics import mean
from datetime import datetime, timedelta

from schema import server_schema
from schema import heartbeat_schema
from database import models
from crud.server_crud import get_server_info_from_ip, create_server

def add_heartbeat(db: Session, req: Request, heartbeat: heartbeat_schema.InfoReq):
    server = get_server_info_from_ip(db, heartbeat.host_ip) 
    if not server:
       server = create_server(db, server_schema.Server(
           ip = heartbeat.host_ip,
           name = str(heartbeat.host_ip)
       ))
       
    db.add(models.SystemInfo(
        server_id = server.id,
        cpu_logic_core = heartbeat.host.cpu.CPU_logical_core,
        cpu_physic_core = heartbeat.host.cpu.CPU_physical_core,
        cpu_percent = heartbeat.host.cpu.CPU_percent,
        cpu_core_usage = heartbeat.host.cpu.core_usage,
        mem_total = heartbeat.host.memory.total_mem_GB,
        mem_used = heartbeat.host.memory.used_mem_GB,
        mem_percent = heartbeat.host.memory.mem_percent,
        disk_read_mb = heartbeat.host.disk.read_MB,
        disk_write_mb = heartbeat.host.disk.write_MB,
        disk_total = heartbeat.host.disk.usage.total_GB,
        disk_used = heartbeat.host.disk.usage.used_GB,
        disk_percent = heartbeat.host.disk.usage.percent,
        net_recv_data_mb = heartbeat.host.network.recv_data_MB,
        net_send_data_mb = heartbeat.host.network.sent_data_MB,
        net_recv_packets = heartbeat.host.network.recv_packets,
        net_send_packets = heartbeat.host.network.sent_packets,
        net_recv_err = heartbeat.host.network.recv_err,
        net_send_err = heartbeat.host.network.sent_err
    ))
    db.commit()
    
    # 기존 컨테이너 목록 조회
    removed_container_ids = db.query(models.Container).filter(models.Container.host_server == server.id).all()
    
    removed_container_ids = [container.id for container in removed_container_ids]
    
    for container in heartbeat.containers:
        container_info = db.query(models.Container).filter(models.Container.name == container.container_name).first()
        
        removed_container_ids.remove(container_info.id)
        
        if not container_info:
            db.add(models.Container(
                host_server = server.id,
                runtime = container.runtime,
                name = container.container_name
            ))
            db.commit()
            
        container_info = db.query(models.Container).filter(models.Container.name == container.container_name).first()
        internal_container_id = db.query(models.InternalContainerId).filter(
            models.InternalContainerId.container_id == container_info.id,
        ).order_by(models.InternalContainerId.reg_time.desc()).first()
        
        if internal_container_id and (
            internal_container_id.pid_id != container.namespace.pid 
            or internal_container_id.mnt_id != container.namespace.mnt 
            or internal_container_id.cgroup_id != container.cgroup_id):
            db.add(models.InternalContainerId(
                container_id = container_info.id,
                pid_id = container.namespace.pid,
                mnt_id = container.namespace.mnt,
                cgroup_id = container.cgroup_id
            ))
            db.commit()
        
        if not internal_container_id:
            db.add(models.InternalContainerId(
            container_id = container_info.id,
            pid_id = container.namespace.pid,
            mnt_id = container.namespace.mnt,
            cgroup_id = container.cgroup_id
            ))
            db.commit()
            
        db.add(models.ContainerSysInfo(
            container_id = container_info.id,
            cpu_kernel = container.stats.cpu.kernel_usage,
            cpu_user = container.stats.cpu.user_usage,
            cpu_percent = container.stats.cpu.usage_percent,
            cpu_online = container.stats.cpu.online_cpus,
            disk_read_mb = container.stats.io.read_mb,
            disk_write_mb = container.stats.io.write_mb,
            mem_limit = container.stats.memory.limit_mb,
            mem_usage = container.stats.memory.usage_mb,
            mem_percent = container.stats.memory.usage_percent,
            net_recv_mb = container.stats.network.rx_mb,
            net_send_mb = container.stats.network.tx_mb,
            net_recv_packets = container.stats.network.rx_packets,
            net_send_packets = container.stats.network.tx_packets,
            proc_cnt = container.stats.proc_cnt
        ))
        db.commit()
    
    # 만약 사라진 컨테이너가 존재하면 removed_at 업데이트
    for container_id in removed_container_ids:
        db.query(models.Container).filter(models.Container.id == container_id).update({"removed_at": datetime.now()})
        db.commit()
    
    insert_data = models.Heartbeat(
        ip = heartbeat.host_ip,
        survival_container_cnt = len(heartbeat.containers),
        req_ip = req.client.host
    )
    
    db.add(insert_data)
    db.commit()
    
    return

def get_server_stats(db: Session, server_id: int, call_back: callable = mean):
    """
    최근 24시간의 서버 상태 정보를 반환합니다.

    Args:
        server_id (int): 조회할 서버 id
    """
    # 1시간 마다 cpu 코어들의 평균을 내서 시간과 값의 리스트 형식으로 반환
    one_day_ago = datetime.now() - timedelta(days=1)
    
    # 1시간 마다 각 CPU 코어별 평균을 계산
    query = db.query(
        func.date_trunc('hour', models.SystemInfo.timestamp).label('hour'),
        models.SystemInfo.cpu_core_usage
    ).filter(
        models.SystemInfo.server_id == server_id,
        models.SystemInfo.timestamp >= one_day_ago
    ).order_by('hour').all()

    # 결과를 처리하여 원하는 형태로 변환
    result = {}
    for record in query:
        hour = record.hour
        cpu_usages = record.cpu_core_usage  # JSON 배열

        if hour not in result:
            result[hour] = {f"cpu{i+1}": [] for i in range(len(cpu_usages))}
        
        # 각 CPU 코어의 사용률을 해당 시간의 리스트에 추가
        for i, usage in enumerate(cpu_usages):
            result[hour][f"cpu{i+1}"].append(float(usage))

    # 각 시간대별로 CPU 코어의 평균 계산
    final_result = []
    for hour, cpu_data in result.items():
        hour_result = {"time": hour.isoformat()}
        for cpu, values in cpu_data.items():
            hour_result[cpu] = call_back(values)
        final_result.append(hour_result)

    # 시간순으로 정렬
    final_result.sort(key=lambda x: x['time'])

    return final_result
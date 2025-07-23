#!/usr/bin/env python
"""
Cross-platform system monitoring utilities for DevWizard
"""
import os
import platform
import subprocess
import psutil

def get_cpu_usage():
    """Get CPU usage percentage"""
    try:
        return psutil.cpu_percent(interval=1)
    except:
        return None

def get_memory_usage():
    """Get memory usage information"""
    try:
        mem = psutil.virtual_memory()
        total_mb = mem.total / (1024 * 1024)
        used_mb = (mem.total - mem.available) / (1024 * 1024)
        percent = mem.percent
        return percent, used_mb, total_mb
    except:
        return None, None, None

def get_disk_usage():
    """Get disk usage information for all partitions"""
    try:
        disk_info = []
        for partition in psutil.disk_partitions():
            if os.name == 'nt' and 'cdrom' in partition.opts or partition.fstype == '':
                # Skip CD-ROM drives on Windows
                continue
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_info.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'percent': usage.percent,
                    'used_gb': usage.used / (1024**3),
                    'total_gb': usage.total / (1024**3)
                })
            except:
                # Some partitions may not be accessible
                pass
        return disk_info
    except:
        return []

def get_process_count():
    """Get the number of running processes"""
    try:
        return len(psutil.pids())
    except:
        return None

def monitor_system():
    """Monitor system resources across platforms"""
    print("📊 System Monitor")
    
    # CPU usage
    cpu_usage = get_cpu_usage()
    if cpu_usage is not None:
        print(f"  CPU Usage: {cpu_usage:.1f}%")
    else:
        print("  CPU Usage: Unable to retrieve")
    
    # Memory usage
    mem_percent, used_mem, total_mem = get_memory_usage()
    if mem_percent is not None:
        print(f"  Memory Usage: {mem_percent:.1f}% ({used_mem:.0f} MB / {total_mem:.0f} MB)")
    else:
        print("  Memory Usage: Unable to retrieve")
    
    # Disk usage
    disk_info = get_disk_usage()
    if disk_info:
        print("  Disk Usage:")
        for disk in disk_info:
            print(f"    {disk['mountpoint']}: {disk['percent']:.1f}% used ({disk['used_gb']:.1f} GB / {disk['total_gb']:.1f} GB)")
    else:
        print("  Disk Usage: Unable to retrieve")
    
    # Process count
    process_count = get_process_count()
    if process_count is not None:
        print(f"  Processes: {process_count} running")
    else:
        print("  Processes: Unable to retrieve")
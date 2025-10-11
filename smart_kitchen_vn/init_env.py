#!/usr/bin/env python3
"""Tạo .env từ .env.example (interactive hoặc --auto)"""
import argparse, os, shutil, time, secrets, string
SENSITIVE_HINTS = ("PASS","PASSWORD","TOKEN","SECRET","KEY","SID","AUTH")
EXAMPLE_NAME = '.env.example'
TARGET_NAME = '.env'
def is_likely_sensitive(k):
    u=k.upper(); return any(h in u for h in SENSITIVE_HINTS)
def gen_secret(n=24):
    alphabet=string.ascii_letters+string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(n))
def backup(target):
    if not os.path.exists(target): return None
    ts=int(time.time()); bak=f"{target}.bak.{ts}"; shutil.copy2(target,bak); return bak
def parse(lines):
    out=[]
    for ln in lines:
        s=ln.rstrip('\n')
        if not s or s.strip().startswith('#') or '=' not in s:
            out.append((ln,None,None,False)); continue
        k,v=s.split('=',1); out.append((ln,k.strip(),v.strip(),True))
    return out
def main():
    p=argparse.ArgumentParser(); p.add_argument('--auto',action='store_true'); p.add_argument('--example',default=EXAMPLE_NAME); p.add_argument('--out',default=TARGET_NAME); args=p.parse_args()
    if not os.path.exists(args.example):
        print('Không tìm thấy .env.example'); return
    with open(args.example,'r',encoding='utf-8') as f: lines=f.readlines()
    parsed=parse(lines)
    if os.path.exists(args.out): bak=backup(args.out); print(f'Đã backup {args.out} -> {bak}')
    out_lines=[]
    for orig,k,v,is_kv in parsed:
        if not is_kv: out_lines.append(orig); continue
        if args.auto and is_likely_sensitive(k): new=gen_secret(32)
        elif args.auto: new=v
        else:
            if is_likely_sensitive(k):
                inp=input(f"{k} (nhạy cảm) [Enter giữ giá trị mẫu / g để sinh]: ")
            else:
                inp=input(f"{k} [Enter giữ mẫu='{v}']: ")
            if inp is None or inp.strip()=='': new=v
            elif inp.strip().lower()=='g': new=gen_secret(32)
            else: new=inp.strip()
        out_lines.append(f"{k}={new}\n")
    with open(args.out,'w',encoding='utf-8') as f: f.writelines(out_lines)
    print(f'Đã ghi {args.out}')
if __name__=='__main__': main()

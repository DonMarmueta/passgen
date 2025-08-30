#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# PassGen (interactive) — Code by Cyber Marmouts
# Uso ético apenas, com autorização.

import argparse
import itertools
import re
from datetime import datetime

LEET_MAP = {
    "a": ["a", "A", "4", "@"],
    "e": ["e", "E", "3"],
    "i": ["i", "I", "1", "!"],
    "o": ["o", "O", "0"],
    "s": ["s", "S", "5", "$"],
    "t": ["t", "T", "7"],
    "g": ["g", "G", "9"],
    "b": ["b", "B", "8"],
}

SEPARATORS = ["", ".", "-", "_"]
COMMON_SUFFIXES = [
    "", "!", "!!", "?", "@", "#", "123", "1234", "12345",
    "2024", "2025", "01", "02", "10", "01!", "123!", "@123"
]

DEFAULT_MAX_CAP = 150_000  # limite padrão

def clean_token(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"\s+", " ", s)
    return s

def split_name(fullname: str):
    fullname = clean_token(fullname)
    parts = [p for p in re.split(r"[ \t]+", fullname) if p]
    return parts

def case_variants(token: str):
    return {token, token.lower(), token.upper(), token.capitalize(), token.title()}

def leet_variants(token: str, max_depth: int = 2):
    token = token.strip()
    indices = [(i, ch.lower()) for i, ch in enumerate(token) if ch.lower() in LEET_MAP]
    variants = {token}
    for depth in range(1, max_depth + 1):
        for combo in itertools.combinations(indices, depth):
            pools = []
            for i, ch in combo:
                pools.append([(i, rep) for rep in LEET_MAP[ch] if rep != token[i]])
            for choice in itertools.product(*pools):
                lst = list(token)
                for i, rep in choice:
                    lst[i] = rep
                variants.add("".join(lst))
    more = set()
    for v in variants:
        more |= case_variants(v)
    variants |= more
    return variants

def parse_birthday(s: str):
    s = (s or "").strip()
    if not s:
        return set()
    fmts = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d/%b/%Y", "%d-%b-%Y", "%d.%m.%Y"]
    dt = None
    for f in fmts:
        try:
            dt = datetime.strptime(s, f)
            break
        except ValueError:
            continue
    if not dt:
        nums = re.sub(r"\D", "", s)
        try:
            if len(nums) == 8:
                dt = datetime.strptime(nums, "%d%m%Y")
            elif len(nums) == 6:
                dt = datetime.strptime(nums, "%d%m%y")
        except ValueError:
            dt = None
    if not dt:
        return set()

    d = f"{dt.day:02d}"
    m = f"{dt.month:02d}"
    y = f"{dt.year:04d}"
    yy = y[-2:]

    combos = {
        d, m, y, yy,
        d+m, m+d,
        d+m+y, y+m+d, y+d+m, m+d+y, d+m+yy, yy+m+d,
        f"{d}-{m}-{y}", f"{y}-{m}-{d}", f"{d}/{m}/{y}", f"{d}.{m}.{y}",
        f"{d}{m}{yy}", f"{d}{m}{y}", f"{yy}{m}{d}",
    }
    return combos

def build_base_tokens(fullname: str, nickname: str, username: str, email: str, extras: list[str]):
    tokens = set()

    # nome
    parts = split_name(fullname)
    if parts:
        first = parts[0]
        last = parts[-1] if len(parts) > 1 else ""
        initials = "".join(p[0] for p in parts if p)
        tokens |= {first, last, "".join(parts), initials, f"{first}{last}"}
        for sep in SEPARATORS:
            if last:
                tokens.add(f"{first}{sep}{last}")
            for a, b in zip(parts, parts[1:]):
                tokens.add(f"{a}{sep}{b}")
        more = set()
        for t in list(tokens):
            more |= case_variants(t)
        tokens |= more

    # apelido
    nickname = clean_token(nickname)
    if nickname:
        tokens |= case_variants(nickname)

    # username
    username = clean_token(username)
    if username:
        tokens |= case_variants(username)

    # e-mail
    email = clean_token(email)
    if email and "@" in email:
        local, _, domain = email.partition("@")
        domain_base = domain.split(".")[0] if domain else ""
        tokens |= case_variants(local)
        if domain_base:
            tokens |= case_variants(domain_base)

    # extras (até 3)
    for w in extras[:3]:
        w = clean_token(w)
        if w:
            tokens |= case_variants(w)

    tokens = {t for t in tokens if t}
    return tokens

def with_suffixes(tokens):
    out = set()
    for t in tokens:
        for suf in COMMON_SUFFIXES:
            out.add(f"{t}{suf}")
    return out

def mix_with_dates(tokens, date_parts):
    if not date_parts:
        return set(tokens)
    out = set(tokens)
    for t in tokens:
        for sep in SEPARATORS:
            for d in date_parts:
                out.add(f"{t}{sep}{d}")
                out.add(f"{d}{sep}{t}")
    return out

def reversed_tokens(tokens):
    out = set(tokens)
    for t in tokens:
        if len(t) > 1:
            out.add(t[::-1])
    return out

def expand_leet(tokens, enable=True, depth=2):
    if not enable or depth <= 0:
        return tokens
    out = set(tokens)
    for t in list(tokens):
        out |= leet_variants(t, max_depth=depth)
    return out

def clamp_length(tokens, min_len, max_len):
    return {t for t in tokens if min_len <= len(t) <= max_len}

def build_wordlist(name, nick, bday, username, email, extras, min_len, max_len,
                   leet_depth, cap):
    base = build_base_tokens(name, nick, username, email, extras)
    dates = parse_birthday(bday)

    tokens = set(base)
    tokens = mix_with_dates(tokens, dates)
    tokens = with_suffixes(tokens)
    tokens = reversed_tokens(tokens)
    tokens = expand_leet(tokens, enable=True, depth=leet_depth)
    tokens = clamp_length(tokens, min_len, max_len)

    ordered = sorted(tokens, key=lambda x: (len(x), x.lower()))
    if cap and len(ordered) > cap:
        ordered = ordered[:cap]
    return ordered

def ask_int(prompt, default):
    raw = input(f"{prompt} [{default}]: ").strip()
    if not raw:
        return default
    try:
        v = int(raw)
        return v if v > 0 else default
    except ValueError:
        return default

def interactive():
    print("=" * 64)
    print(" PassGen — Interactive Mode")
    print(" Code by Cyber Marmouts")
    print("=" * 64)

    name = input("Full name (ex.: John Doe): ").strip()
    bday = input("Birthday (ex.: 09/12/2005 ou 2005-12-09) [opcional]: ").strip()
    nick = input("Nickname [opcional]: ").strip()
    username = input("Username [opcional]: ").strip()
    email = input("E-mail [opcional]: ").strip()
    extras_raw = input("Extras (até 3, separados por vírgula) [opcional]: ").strip()
    output = input("Output file (default: list.txt): ").strip() or "list.txt"

    # presets de performance
    print("\nPerfis sugeridos (para VMs modestas 6GB/2 vCPU):")
    print("  1) Lite    → leet-depth=1, cap=50.000")
    print("  2) Padrão  → leet-depth=3, cap=150.000  (recomendado)")
    print("  3) Turbo   → leet-depth=3, cap=300.000  (pode pesar)")
    choice = (input("Escolha perfil [1/2/3] (Enter=2): ").strip() or "2")

    if choice == "1":
        leet_depth = 1
        cap = 50_000
    elif choice == "3":
        leet_depth = 3
        cap = 300_000
    else:
        leet_depth = 3
        cap = 150_000

    # ajustes finos opcionais
    print("\nAjustes finos (opcionais, Enter mantém):")
    leet_depth = ask_int("Leet depth", leet_depth)
    cap = ask_int("Max combos (cap)", cap)

    # extras
    extras = []
    if extras_raw:
        extras = [e.strip() for e in extras_raw.split(",") if e.strip()][:3]

    min_len, max_len = 6, 24

    print("\n[Resumo]")
    print(f"  leet-depth={leet_depth} | cap={cap} | min={min_len} | max={max_len}")
    print("[+] Gerando combinações...")

    wordlist = build_wordlist(
        name, nick, bday, username, email, extras,
        min_len=min_len, max_len=max_len,
        leet_depth=leet_depth, cap=cap
    )
    with open(output, "w", encoding="utf-8") as f:
        f.write("\n".join(wordlist))
    print(f"[✓] Geradas {len(wordlist):,} senhas -> {output}")
    print(" Done. Code by Cyber Marmouts.")

def main():
    parser = argparse.ArgumentParser(
        description="PassGen — gera wordlist a partir de dados pessoais. Code by Cyber Marmouts."
    )
    parser.add_argument("-n", "--name", help="Nome completo")
    parser.add_argument("-k", "--nick", default="", help="Apelido (opcional)")
    parser.add_argument("-b", "--birthday", default="", help="Data (opcional)")
    parser.add_argument("-u", "--username", default="", help="Username (opcional)")
    parser.add_argument("-e", "--email", default="", help="E-mail (opcional)")
    parser.add_argument("--extra", nargs="*", default=[], help="Extras (máx 3)")
    parser.add_argument("-o", "--output", default="list.txt", help="Arquivo de saída")
    parser.add_argument("--min", type=int, default=6, help="Tamanho mínimo")
    parser.add_argument("--max", type=int, default=24, help="Tamanho máximo")
    parser.add_argument("--leet-depth", type=int, default=3, help="Profundidade leet (padrão 3)")
    parser.add_argument("--cap", type=int, default=DEFAULT_MAX_CAP,
                        help="Máx. combinações (padrão 150000)")
    parser.add_argument("--interactive", action="store_true", help="Modo interativo")

    args = parser.parse_args()

    if args.interactive or not args.name:
        interactive()
        return

    extras = args.extra[:3]
    wl = build_wordlist(
        args.name, args.nick, args.birthday, args.username, args.email, extras,
        min_len=args.min, max_len=args.max,
        leet_depth=args.leet_depth, cap=args.cap
    )
    with open(args.output, "w", encoding="utf-8") as f:
        f.write("\n".join(wl))
    print(f"[✓] Geradas {len(wl):,} senhas -> {args.output}")
    print(" Done. Code by Cyber Marmouts.")

if __name__ == "__main__":
    main()

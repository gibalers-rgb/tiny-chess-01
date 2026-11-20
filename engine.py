import json, os, random, sys, urllib.error, urllib.request

ENV_URL = os.environ.get("MAKEFUN_ENV_URL") or sys.exit("MAKEFUN_ENV_URL is not set")

def post(p, b):
    r = urllib.request.Request(ENV_URL + p, data=json.dumps(b).encode(),
                               headers={"content-type": "application/json"})
    try:
        with urllib.request.urlopen(r) as s:
            return json.load(s)
    except urllib.error.HTTPError as e:
        sys.exit(f"{p}: HTTP {e.code} {e.read().decode(errors='replace')}")

V = [0, 100, 320, 330, 500, 900, 20000]
T = [
[[0,0,0,0],[50,50,50,50],[10,10,20,30],[5,5,10,25],[0,0,0,20],[5,-5,-10,0],[5,10,10,-20],[0,0,0,0]],
[[-50,-40,-30,-30],[-40,-20,0,0],[-30,0,10,15],[-30,5,15,20],[-30,0,15,20],[-30,5,10,15],[-40,-20,0,5],[-50,-40,-30,-30]],
[[-20,-10,-10,-10],[-10,0,0,0],[-10,0,5,10],[-10,5,5,10],[-10,0,10,10],[-10,10,10,10],[-10,5,0,0],[-20,-10,-10,-10]],
[[0,0,0,0],[5,10,10,10],[-5,0,0,0],[-5,0,0,0],[-5,0,0,0],[-5,0,0,0],[-5,0,0,0],[0,0,0,5]],
[[-20,-10,-10,-5,-5,-10,-10,-20],[-10,0,0,0,0,0,0,-10],[-10,0,5,5,5,5,0,-10],[-5,0,5,5,5,5,0,-5],[0,0,5,5,5,5,0,-5],[-10,5,5,5,5,5,0,-10],[-10,0,5,0,0,0,0,-10],[-20,-10,-10,-5,-5,-10,-10,-20]],
[[-30,-40,-40,-50],[-30,-40,-40,-50],[-30,-40,-40,-50],[-30,-40,-40,-50],[-20,-30,-30,-40],[-10,-20,-20,-20],[20,20,0,0],[20,30,10,0]],
]
KN = (-33, -31, -18, -14, 14, 18, 31, 33)
KI = (-17, -16, -15, -1, 1, 15, 16, 17)
BD = (-17, -15, 15, 17)
RD = (-16, -1, 1, 16)
MT = 100000
N = 75000

R = random.Random(12345)
Z = [[R.getrandbits(64) for _ in range(128)] for _ in range(13)]
ZS = R.getrandbits(64)
ZC = [R.getrandbits(64) for _ in range(16)]
ZE = [R.getrandbits(64) for _ in range(8)]

B = [0] * 128
S = 1
C = 0
E = -1
H = 0
WK = 4
BK = 116
U = []
PH = []
TT = {}
KIL = [[0, 0] for _ in range(64)]
HIS = [0] * 16384
nd = 0
SN = {}
RM = [0]

def sqname(sq):
    return "abcdefgh"[sq & 7] + str((sq >> 4) + 1)

def uci(m):
    s = sqname(m & 127) + sqname((m >> 7) & 127)
    pr = m >> 14
    return s + ("", "n", "b", "r", "q")[pr - 1] if pr else s

def u2m(s):
    f = (int(s[1]) - 1) * 16 + "abcdefgh".index(s[0])
    t = (int(s[3]) - 1) * 16 + "abcdefgh".index(s[2])
    pr = ("NBRQ".index(s[4].upper()) + 2) if len(s) == 5 else 0
    return f | (t << 7) | (pr << 14)

def hp():
    h = 0
    for r in range(8):
        for f in range(8):
            p = B[r * 16 + f]
            if p:
                h ^= Z[p + 6][r * 16 + f]
    if S < 0:
        h ^= ZS
    h ^= ZC[C]
    if E >= 0:
        h ^= ZE[E & 7]
    return h

def parse(fen):
    global S, C, E, H, WK, BK
    for i in range(128):
        B[i] = 0
    w = fen.split()
    r = 7
    f = 0
    for ch in w[0]:
        if ch == "/":
            r -= 1
            f = 0
        elif ch.isdigit():
            f += int(ch)
        else:
            sq = r * 16 + f
            p = "PNBRQK".index(ch.upper()) + 1
            if ch.islower():
                p = -p
            B[sq] = p
            if p == 6:
                WK = sq
            elif p == -6:
                BK = sq
            f += 1
    S = 1 if w[1] == "w" else -1
    C = 0
    if len(w) > 2:
        for ch in w[2]:
            if ch == "K":
                C |= 1
            elif ch == "Q":
                C |= 2
            elif ch == "k":
                C |= 4
            elif ch == "q":
                C |= 8
    E = -1
    if len(w) > 3 and w[3] != "-":
        E = (int(w[3][1]) - 1) * 16 + "abcdefgh".index(w[3][0])
    H = hp()

def atk(sq, by):
    if by > 0:
        for d in (-15, -17):
            t = sq + d
            if not t & 0x88 and B[t] == 1:
                return 1
    else:
        for d in (15, 17):
            t = sq + d
            if not t & 0x88 and B[t] == -1:
                return 1
    for d in KN:
        t = sq + d
        if not t & 0x88 and B[t] == 2 * by:
            return 1
    for d in KI:
        t = sq + d
        if not t & 0x88 and B[t] == 6 * by:
            return 1
    for d in BD:
        t = sq + d
        while not t & 0x88:
            p = B[t]
            if p:
                if p == 3 * by or p == 5 * by:
                    return 1
                break
            t += d
    for d in RD:
        t = sq + d
        while not t & 0x88:
            p = B[t]
            if p:
                if p == 4 * by or p == 5 * by:
                    return 1
                break
            t += d
    return 0

def ev():
    s = 0
    wb = 0
    bb = 0
    for r in range(8):
        for f in range(8):
            p = B[r * 16 + f]
            if p:
                t = abs(p)
                if t == 3:
                    if p > 0:
                        wb += 1
                    else:
                        bb += 1
                g = f if f < 4 else 7 - f
                i = (7 - r) if p > 0 else r
                v = T[t - 1][i][f] if t == 5 else T[t - 1][i][g]
                s += (V[t] + v) * (1 if p > 0 else -1)
    if wb > 1:
        s += 30
    if bb > 1:
        s -= 30
    return s if S > 0 else -s

def gen(caps, pl):
    ms = []
    for sq in range(128):
        if sq & 0x88:
            continue
        p = B[sq]
        if not p or (p > 0) != (S > 0):
            continue
        t = abs(p)
        if t == 1:
            d = 16 * S
            t1 = sq + d
            if not t1 & 0x88 and not B[t1]:
                lr = (t1 >> 4) == (7 if S > 0 else 0)
                if lr:
                    for pr, sc in ((5, 950), (4, 520), (3, 340), (2, 330)):
                        ms.append((sc, sq | (t1 << 7) | (pr << 14)))
                elif not caps:
                    ms.append((os(sq, t1, pl), sq | (t1 << 7)))
                    if (sq >> 4) == (1 if S > 0 else 6):
                        t2 = sq + 2 * d
                        if not B[t2]:
                            ms.append((os(sq, t2, pl), sq | (t2 << 7)))
            for dd in (d - 1, d + 1):
                u = sq + dd
                if u & 0x88:
                    continue
                q = B[u]
                if q and (q > 0) != (S > 0):
                    lr = (u >> 4) == (7 if S > 0 else 0)
                    if lr:
                        for pr, sc in ((5, 950), (4, 520), (3, 340), (2, 330)):
                            ms.append((sc + 10 * V[abs(q)], sq | (u << 7) | (pr << 14)))
                    else:
                        ms.append((10 * V[abs(q)] - 6, sq | (u << 7)))
                elif u == E:
                    ms.append((10 * V[1] - 6, sq | (u << 7)))
        elif t == 2 or t == 6:
            for dd in KN if t == 2 else KI:
                u = sq + dd
                if u & 0x88:
                    continue
                q = B[u]
                if not q:
                    if not caps:
                        ms.append((os(sq, u, pl), sq | (u << 7)))
                elif (q > 0) != (S > 0):
                    ms.append((10 * V[abs(q)] - V[t] // 16, sq | (u << 7)))
        else:
            for dd in BD if t == 3 else RD if t == 4 else BD + RD:
                u = sq + dd
                while not u & 0x88:
                    q = B[u]
                    if not q:
                        if not caps:
                            ms.append((os(sq, u, pl), sq | (u << 7)))
                    else:
                        if (q > 0) != (S > 0):
                            ms.append((10 * V[abs(q)] - V[t] // 16, sq | (u << 7)))
                        break
                    u += dd
    if not caps:
        if S > 0:
            if C & 1 and not B[5] and not B[6] and not atk(4, -1) and not atk(5, -1) and not atk(6, -1):
                ms.append((0, 4 | (6 << 7)))
            if C & 2 and not B[3] and not B[2] and not B[1] and not atk(4, -1) and not atk(3, -1) and not atk(2, -1):
                ms.append((0, 4 | (2 << 7)))
        else:
            if C & 4 and not B[117] and not B[118] and not atk(116, 1) and not atk(117, 1) and not atk(118, 1):
                ms.append((0, 116 | (118 << 7)))
            if C & 8 and not B[115] and not B[114] and not B[113] and not atk(116, 1) and not atk(115, 1) and not atk(114, 1):
                ms.append((0, 116 | (114 << 7)))
    ms.sort(reverse=True)
    return [m for _, m in ms]

def os(f, t, pl):
    m = f | (t << 7)
    if pl < 64:
        if KIL[pl][0] == m:
            return 8000
        if KIL[pl][1] == m:
            return 7000
    return HIS[f * 128 + t]

def make(m):
    global C, E, H, S, WK, BK
    f = m & 127
    t = (m >> 7) & 127
    pr = m >> 14
    p = B[f]
    cap = B[t]
    epc = -1
    if p == S and t == E and not cap:
        epc = t - 16 * S
        cap = B[epc]
    U.append((m, cap, C, E, H, WK, BK, epc))
    H ^= ZC[C]
    if E >= 0:
        H ^= ZE[E & 7]
    H ^= Z[p + 6][f]
    if cap:
        H ^= Z[cap + 6][t if epc < 0 else epc]
    if epc >= 0:
        B[epc] = 0
    B[f] = 0
    if pr:
        q = pr * S
        B[t] = q
        H ^= Z[q + 6][t]
    else:
        B[t] = p
        H ^= Z[p + 6][t]
        if abs(p) == 6:
            if S > 0:
                WK = t
            else:
                BK = t
            if t - f == 2:
                B[f + 1] = B[f + 3]
                B[f + 3] = 0
                H ^= Z[4 * S + 6][f + 3] ^ Z[4 * S + 6][f + 1]
            elif f - t == 2:
                B[f - 1] = B[f - 4]
                B[f - 4] = 0
                H ^= Z[4 * S + 6][f - 4] ^ Z[4 * S + 6][f - 1]
    if abs(p) == 6:
        C &= ~(1 | 2) if S > 0 else ~(4 | 8)
    if f == 7 or t == 7:
        C &= ~1
    if f == 0 or t == 0:
        C &= ~2
    if f == 119 or t == 119:
        C &= ~4
    if f == 112 or t == 112:
        C &= ~8
    if p == S and abs(t - f) == 32:
        E = f + 16 * S
    else:
        E = -1
    H ^= ZC[C]
    if E >= 0:
        H ^= ZE[E & 7]
    S = -S
    H ^= ZS

def unmake():
    global C, E, H, S, WK, BK
    m, cap, C, E, H, WK, BK, epc = U.pop()
    f = m & 127
    t = (m >> 7) & 127
    pr = m >> 14
    S = -S
    B[f] = S if pr else B[t]
    B[t] = cap if epc < 0 else 0
    if epc >= 0:
        B[epc] = cap
    if abs(B[f]) == 6 and abs(t - f) == 2:
        if t > f:
            B[f + 3] = B[f + 1]
            B[f + 1] = 0
        else:
            B[f - 4] = B[f - 1]
            B[f - 1] = 0

def nm():
    global S, E, H
    U.append((E, H))
    if E >= 0:
        H ^= ZE[E & 7]
    E = -1
    S = -S
    H ^= ZS

def unm():
    global S, E, H
    E, H = U.pop()
    S = -S

class Abort(Exception):
    pass

def qs(a, b, pl):
    global nd
    nd += 1
    if nd > N:
        raise Abort
    ks = WK if S > 0 else BK
    if atk(ks, -S):
        ms = gen(0, pl)
        best = -MT + pl
        for m in ms:
            make(m)
            if atk(WK if S < 0 else BK, S):
                unmake()
                continue
            s = -qs(-b, -a, pl + 1)
            unmake()
            if s > best:
                best = s
            if s > a:
                a = s
            if a >= b:
                return b
        return best if best > -MT + pl else -MT + pl
    s = ev()
    if s >= b:
        return b
    if s > a:
        a = s
    for m in gen(1, pl):
        t = (m >> 7) & 127
        if not (m >> 14):
            cap = B[t]
            v = 100 if (not cap and t == E) else (V[abs(cap)] if cap else 0)
            if s + v + 200 < a:
                continue
        make(m)
        if atk(WK if S < 0 else BK, S):
            unmake()
            continue
        s = -qs(-b, -a, pl + 1)
        unmake()
        if s >= b:
            return b
        if s > a:
            a = s
    return a

def search(a, b, d, pl):
    global nd
    nd += 1
    if nd > N:
        raise Abort
    if H in PH:
        return 0
    if d <= 0:
        return qs(a, b, pl)
    e = TT.get(H)
    ttm = 0
    if e and e[0] >= d:
        if pl == 0 and e[3]:
            RM[0] = e[3]
        if e[1] == 0:
            return e[2]
        if e[1] == 1 and e[2] >= b:
            return e[2]
        if e[1] == 2 and e[2] <= a:
            return e[2]
        ttm = e[3]
    ks = WK if S > 0 else BK
    if d >= 3 and not atk(ks, -S) and ev() >= b:
        nm()
        s = -search(-b, -b + 1, d - 3, pl + 1)
        unm()
        if s >= b:
            return b
    ms = gen(0, pl)
    if ttm and ttm in ms:
        ms.remove(ttm)
        ms.insert(0, ttm)
    best = -MT - 1
    bm = 0
    lg = 0
    oa = a
    ih = atk(ks, -S)
    PH.append(H)
    for m in ms:
        f = m & 127
        t = (m >> 7) & 127
        pr = m >> 14
        ic = B[t] != 0 or pr != 0 or (abs(B[f]) == 1 and t == E)
        ik = pl < 64 and (m == KIL[pl][0] or m == KIL[pl][1])
        make(m)
        if atk(WK if S < 0 else BK, S):
            unmake()
            continue
        lg += 1
        if lg > 4 and d >= 3 and not ic and not ih and not ik:
            s = -search(-b, -a, d - 2, pl + 1)
            if s > a:
                s = -search(-b, -a, d - 1, pl + 1)
        else:
            s = -search(-b, -a, d - 1, pl + 1)
        unmake()
        if s > best:
            best = s
            bm = m
            if pl == 0:
                RM[0] = m
        if s > a:
            a = s
        if a >= b:
            break
    PH.pop()
    if not lg:
        ks = WK if S > 0 else BK
        return -MT + pl if atk(ks, -S) else 0
    flag = 0
    if best <= oa:
        flag = 2
    elif best >= b:
        flag = 1
    if len(TT) > 300000:
        TT.clear()
    TT[H] = (d, flag, best, bm)
    if best >= b and bm:
        f = bm & 127
        t = (bm >> 7) & 127
        if not B[t] and not (bm >> 14):
            if pl < 64:
                k = KIL[pl]
                if k[0] != bm:
                    k[1] = k[0]
                    k[0] = bm
            HIS[f * 128 + t] += d * d
    return best

def root(fen, lg, start_fen, moves):
    global nd, SN, N
    parse(fen)
    del PH[:]
    del U[:]
    SN = {}
    parse(start_fen)
    SN[H] = 1
    for u in moves:
        make(u2m(u))
        SN[H] = SN.get(H, 0) + 1
    parse(fen)
    rms = [u2m(u) for u in lg]
    if len(rms) == 1:
        return lg[0]
    nd = 0
    bm = rms[0]
    bests = 0
    for d in range(1, 13):
        try:
            s = search(-MT - 1, MT + 1, d, 0)
        except Abort:
            break
        bm = RM[0]
        bests = s
    parse(fen)
    make(bm)
    rep = SN.get(H, 0) >= 2
    unmake()
    if rep and bests > 0:
        saveN = N
        N = nd + 10000
        ba = None
        bc = -MT
        for m in rms:
            if m == bm:
                continue
            make(m)
            if atk(WK if S < 0 else BK, S):
                unmake()
                continue
            if SN.get(H, 0) >= 2:
                unmake()
                continue
            try:
                s = -qs(-MT - 1, MT + 1, 1)
            except Abort:
                s = -MT
            unmake()
            if s > bc:
                bc = s
                ba = m
        N = saveN
        if ba is not None and bc > 0:
            return uci(ba)
    return uci(bm)

def choose(g):
    return root(g["fen"], g["legal_moves"], g["start_fen"], g["moves"])

def main():
    while True:
        g = post("/game", {})
        if g["status"] == "done":
            break
        while g["status"] == "your_move":
            mv = choose(g)
            if mv not in g["legal_moves"]:
                print(f"WARNING: chose illegal {mv}, using {g['legal_moves'][0]}",
                      file=sys.stderr)
                mv = g["legal_moves"][0]
            g = post("/move", {"game": g["game"], "move": mv})
        print(f"game {g['game']}: {g['outcome']} by {g['reason']}", file=sys.stderr)
    print(f"done: {g.get('wins')} won, {g.get('draws')} drawn, {g.get('losses')} lost",
          file=sys.stderr)

if __name__ == "__main__":
    main()

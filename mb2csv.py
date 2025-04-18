
#!/usr/bin/env python3
"""mb2csv_fixed5_csvonly.py
자료마일 .MB → CSV 변환 (패딩 5B 고정, Excel 저장 제거)
Usage:
    python mb2csv_fixed5_csvonly.py STOCK.mb [-o OUTPREFIX]
"""

import argparse, pathlib, struct, pandas as pd

DEF = [
    ("번호",2,4),("분류코드",16,10),("구분1",16,30),("구분2",16,30),
    ("발주서번호",16,30),("계산서발행일",4,4),("계산서발행",16,10),
    ("계산서번호",16,10),("납품일자",4,4),("거래처도착일",4,4),
    ("출고구분코드",16,10),("출고",16,10),("매출구분",16,10),
    ("상품CODE",16,6),("상품명",16,50),("메모",16,70),("LOT",16,30),
    ("국내CODE",16,8),("거래회사",16,30),("결제방식",16,20),
    ("COMPANY",16,42),("공급회사",16,16),("수량",3,8),("단가",3,8),
    ("공급가액",7,8),("단가변동",16,50),("포장단위",16,10),
    ("월",2,4),("외국CODE",16,8),("년",2,4),
    ("출고월",2,4),("출고년",2,4),("업태",16,10)
]

def default_fields():
    off=0; fs=[]
    for n,t,l in DEF:
        fs.append({"name":n,"tc":t,"len":l,"off":off}); off+=l
    return fs

def decode(raw, tc):
    if tc==16:
        return raw.split(b'\x00',1)[0].decode('cp949','ignore').strip()
    if tc in (1,2):
        return struct.unpack('<I', raw[:4])[0]
    if tc==3:
        return struct.unpack('<d', raw[:8])[0]
    if tc==4:
        v=str(struct.unpack('<I', raw[:4])[0])
        return f"{v[:4]}-{v[4:6]}-{v[6:]}" if len(v)==8 else v
    if tc==7:
        return struct.unpack('<Q', raw[:8])[0]
    return raw.hex()

def mb2df(mb_path):
    mb=pathlib.Path(mb_path).read_bytes()
    rec_cnt  = struct.unpack('<I', mb[4:8])[0]
    rec_len  = struct.unpack('<H', mb[10:12])[0]
    hdr_len  = struct.unpack('<I', mb[12:16])[0]
    rec_start= hdr_len + 5           # 상태1B + 패딩4B
    body_len = rec_len - 5
    fields = default_fields()
    rows=[]
    for i in range(rec_cnt):
        base = rec_start + i*rec_len
        if base+rec_len > len(mb): break
        body = mb[base:base+body_len]
        rows.append({f['name']: decode(body[f['off']:f['off']+f['len']], f['tc']) for f in fields})
    return pd.DataFrame(rows)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mb")
    ap.add_argument("-o","--outprefix",default=None)
    args = ap.parse_args()
    out = args.outprefix or pathlib.Path(args.mb).stem
    df = mb2df(args.mb)
    df.to_csv(f"{out}.csv", index=False, encoding="utf-8-sig")
    print(f"✓ {len(df):,} rows → {out}.csv")

if __name__ == "__main__":
    main()

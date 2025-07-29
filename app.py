import pandas as pd
import math

def process_packing_list(file_path):
    df = pd.read_excel(file_path, dtype=str)

    # 숫자형 컬럼 처리 (빈 값은 0으로 대체)
    df['PCS 수량'] = pd.to_numeric(df['PCS 수량'].fillna(0), errors='coerce').fillna(0).astype(int)
    df['박스당 수량'] = pd.to_numeric(df['박스당 수량'].fillna(0), errors='coerce').fillna(0).astype(int)

    # 중복 제거 기준: 팔레트 ID + 제조 Lot + PCS 수량 + 박스당 수량
    dedup_df = df.drop_duplicates(subset=['팔레트 ID', '제조 Lot', 'PCS 수량', '박스당 수량'])

    # 그룹 합산
    grouped = dedup_df.groupby(['팔레트 ID', '제조 Lot', '박스당 수량'], as_index=False)['PCS 수량'].sum()

    # 완박스 수량 / 낱개 수량 분리
    def split_pcs(row):
        full_box_qty = (row['PCS 수량'] // row['박스당 수량']) * row['박스당 수량'] if row['박스당 수량'] > 0 else 0
        loose_qty = row['PCS 수량'] - full_box_qty
        return pd.Series([full_box_qty, loose_qty])

    grouped[['완박스 수량', '낱개 수량']] = grouped.apply(split_pcs, axis=1)

    return grouped

# 예시 실행
if __name__ == '__main__':
    result_df = process_packing_list('250728_2162725752의 복사본.xlsx')
    result_df.to_excel('result_packing_list.xlsx', index=False)
    print("완료: result_packing_list.xlsx 생성됨")

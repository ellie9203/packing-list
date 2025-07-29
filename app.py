import streamlit as st
import pandas as pd
import io

def process_packing_list(file):
    # 엑셀 파일 읽기
    df = pd.read_excel(file, dtype=str)

    # 필요한 열 필터링
    required_cols = ['팔레트 ID', 'PCS 수량', '박스당 수량', '제조 Lot']
    if not all(col in df.columns for col in required_cols):
        missing_cols = [col for col in required_cols if col not in df.columns]
        st.error(f"파일에 '{', '.join(missing_cols)}' 열이 모두 포함되어야 합니다.")
        return None

    # 숫자형 변환
    df['PCS 수량'] = pd.to_numeric(df['PCS 수량'], errors='coerce').fillna(0).astype(int)
    df['박스당 수량'] = pd.to_numeric(df['박스당 수량'], errors='coerce').fillna(0).astype(int)

    # 완전 박스 수량과 낱개 수량 계산
    df['완박스 수량'] = (df['PCS 수량'] // df['박스당 수량']) * df['박스당 수량']
    df['낱개 수량'] = df['PCS 수량'] % df['박스당 수량']

    # 중복 제거 및 합산
    grouped = (
        df.drop_duplicates(subset=['팔레트 ID', '제조 Lot', '완박스 수량', '낱개 수량'])
          .groupby(['팔레트 ID', '제조 Lot'], as_index=False)
          .agg({
              '완박스 수량': 'sum',
              '낱개 수량': 'sum'
          })
    )

    return grouped

# Streamlit UI
st.title("Packing List 자동 생성기")
st.caption("팔레트 ID + 제조 Lot 기준 자동 합산 + 낱개 집계")
uploaded_file = st.file_uploader("\U0001F4C2 원본 파일을 업로드하세요 (.xlsx)", type=["xlsx"])

if uploaded_file:
    result_df = process_packing_list(uploaded_file)
    if result_df is not None:
        st.success("\u2705 계산이 완료되었습니다!")
        st.dataframe(result_df)

        # 다운로드 버튼
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            result_df.to_excel(writer, index=False)
        st.download_button(
            label="\U00002B07 결과 파일 다운로드",
            data=output.getvalue(),
            file_name="packing_list_result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

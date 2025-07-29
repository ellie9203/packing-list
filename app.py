import streamlit as st
import pandas as pd

st.title("📦 Packing List 자동 생성기")
st.caption("팔레트 ID + 제조 Lot 기준 자동 합산 + 낱개 집계")

uploaded_file = st.file_uploader("📂 원본 파일을 업로드하세요 (.xlsx)", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file, header=1)

        # 열 이름 확인
        required_cols = ["팔레트 ID", "PCS 수량", "박스당 수량", "제조 Lot"]
        if not all(col in df.columns for col in required_cols):
            st.error("❌ 파일에 '팔레트 ID', 'PCS 수량', '박스당 수량', '제조 Lot' 열이 모두 포함되어야 합니다.")
        else:
            # 열 이름 단축
            df = df.rename(columns={
                "팔레트 ID": "PalletID",
                "PCS 수량": "PCS",
                "박스당 수량": "BoxQty",
                "제조 Lot": "Lot"
            })

            # 누락 제거 및 타입 변환
            df = df.dropna(subset=["PalletID", "Lot", "PCS", "BoxQty"])
            df["PCS"] = pd.to_numeric(df["PCS"], errors="coerce").fillna(0).astype(int)
            df["BoxQty"] = pd.to_numeric(df["BoxQty"], errors="coerce").fillna(0).astype(int)

            # 완박스 수량 및 낱개 계산
            df["FullBoxQty"] = (df["PCS"] // df["BoxQty"]) * df["BoxQty"]
            df["Remain"] = df["PCS"] % df["BoxQty"]

            # 팔레트 + 제조 Lot 단위로 집계
            grouped = df.groupby(["PalletID", "Lot"]).agg({
                "FullBoxQty": "sum",
                "Remain": "sum"
            }).reset_index()

            grouped = grouped.rename(columns={
                "PalletID": "팔레트 ID",
                "Lot": "제조 Lot",
                "FullBoxQty": "완박스 수량 합계",
                "Remain": "낱개 수량 합계"
            })

            st.success("✅ 집계가 완료되었습니다!")
            st.dataframe(grouped)

            # 다운로드 버튼
            @st.cache_data
            def convert_df(df):
                return df.to_excel(index=False, engine='openpyxl')

            st.download_button(
                label="📥 결과 파일 다운로드",
                data=convert_df(grouped),
                file_name="packing_list_result.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"파일 처리 중 오류가 발생했습니다: {e}")

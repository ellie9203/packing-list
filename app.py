
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Packing List Tool", layout="wide")

st.title("📦 Packing List 자동 생성기")

uploaded_file = st.file_uploader("📁 팔레트 ID 기준 원본 파일을 업로드하세요", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    # 팔레트 ID, 배치번호(AD열), 수량(X열)
    if 'AD' in df.columns and 'X' in df.columns:
        group_cols = ['팔레트ID', 'AD']
        if '팔레트ID' not in df.columns:
            st.error("⚠️ '팔레트ID' 열이 파일에 없습니다.")
        else:
            try:
                df_grouped = df.groupby(group_cols)['X'].sum().reset_index()
                df_grouped = df_grouped.rename(columns={'X': 'PCS'})

                st.success("✅ 자동 계산 완료! 아래에서 다운로드하세요.")
                st.dataframe(df_grouped)

                # 다운로드 버튼
                @st.cache_data
                def convert_df(df):
                    return df.to_excel(index=False, engine='openpyxl')

                st.download_button(
                    label="📥 다운로드 (Excel)",
                    data=convert_df(df_grouped),
                    file_name="PackingList_Result.xlsx"
                )
            except Exception as e:
                st.error(f"🚨 처리 중 오류 발생: {e}")
    else:
        st.error("⚠️ 파일에 'AD'열(배치번호), 'X'열(PCS 수량)이 포함되어야 합니다.")

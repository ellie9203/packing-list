import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="📦 Packing Detail Generator", layout="wide")
st.title("📦 Packing Detail Generator")
st.markdown("""
이 앱은 Raw Data 엑셀 파일을 업로드하면, 팔레트 ID + 제조 LOT 기준으로 완박스 수량과 낱개 수량을 자동으로 계산하여 포맷화된 Packing Detail 파일을 생성합니다.
""")

uploaded_file = st.file_uploader("🗂️ 엑셀 파일을 업로드 해주세요", type=["xlsx"])

def process_file(file):
    df = pd.read_excel(file, header=0, engine='openpyxl')

    df = df[df.iloc[:, 5].notna()]  # 팔레트 ID 비어있지 않은 행만

    df['Pallet_ID'] = df.iloc[:, 5].astype(str)
    df['Material_Name'] = df.iloc[:, 11].astype(str)
    df['Box_Qty'] = pd.to_numeric(df.iloc[:, 23], errors='coerce')
    df['PCS'] = pd.to_numeric(df.iloc[:, 24], errors='coerce')
    df['Lot_No'] = df.iloc[:, 30].astype(str).str.split(".").str[0]  # 소수점 뒤 제거
    df['Right7'] = df['Pallet_ID'].apply(lambda x: str(x)[-7:])

    result_rows = []

    grouped = df.groupby(['Pallet_ID', 'Lot_No'])

    for (pallet, lot), group in grouped:
        box_qty = group['Box_Qty'].iloc[0]
        material_name = group['Material_Name'].iloc[0]
        right7 = group['Right7'].iloc[0]

        full_boxes = group[group['PCS'] == box_qty]
        partials = group[group['PCS'] != box_qty]

        full_box_total = full_boxes['PCS'].sum()

        if full_box_total > 0:
            result_rows.append({
                "Pallet_ID": pallet,
                "Material": material_name,
                "Right7": right7,
                "Box_Qty": box_qty,
                "Full_Box_Total": full_box_total,
                "Lot_No": lot
            })

        if not partials.empty:
            partial_sum = partials['PCS'].sum()
            result_rows.append({
                "Pallet_ID": '',
                "Material": '',
                "Right7": '',
                "Box_Qty": '',
                "Full_Box_Total": partial_sum,
                "Lot_No": ''
            })

    result_df = pd.DataFrame(result_rows)
    return result_df

if uploaded_file is not None:
    try:
        df_result = process_file(uploaded_file)
        st.success("✅ 변환 성공! 아래에서 다운로드 하세요.")

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_result.to_excel(writer, index=False, sheet_name="Packing Details")
        st.download_button(
            label="📥 변환된 파일 다운로드",
            data=output.getvalue(),
            file_name="Packing_Details_Output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    except Exception as e:
        st.error(f"⚠️ 에러가 발생했습니다: {e}") 

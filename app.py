import streamlit as st
import pandas as pd

def clean_lot_number(lot):
    try:
        return str(int(float(lot)))
    except:
        return str(lot)

def process_excel(file):
    df = pd.read_excel(file, header=0)

    # 필요한 열 설정
    df = df.rename(columns=lambda x: str(x).strip())
    df = df[df['PCS'].notnull()]  # PCS 있는 행만

    # 컬럼 이름 강제 지정
    col_palette_id = df.columns[4]    # E
    col_item_name = df.columns[10]    # K
    col_box_qty = df.columns[22]      # W
    col_pcs = df.columns[23]          # X
    col_lot = df.columns[29]          # AD

    df[col_lot] = df[col_lot].apply(clean_lot_number)

    result_rows = []

    for (palette, lot), group in df.groupby([col_palette_id, col_lot]):
        item_name = group[col_item_name].iloc[0]
        box_qty = group[col_box_qty].iloc[0]

        pcs_values = group[col_pcs].tolist()

        full_box_pcs = 0
        remaining_pcs = []

        for pcs in pcs_values:
            if pcs == box_qty:
                full_box_pcs += pcs
            else:
                full_box_pcs += pcs - (pcs % box_qty)
                if pcs % box_qty != 0:
                    remaining_pcs.append(pcs % box_qty)

        # 완박스 로우
        result_rows.append({
            "Pallet ID": palette,
            "Item Name": item_name,
            "Box Q'ty": box_qty,
            "Total PCS": full_box_pcs,
            "LOT": lot
        })

        # 낱개 로우
        if remaining_pcs:
            result_rows.append({
                "Pallet ID": "",
                "Item Name": "",
                "Box Q'ty": "",
                "Total PCS": sum(remaining_pcs),
                "LOT": ""
            })

    result_df = pd.DataFrame(result_rows)

    return result_df

# Streamlit UI
st.title("📦 Packing Details 자동화 프로그램")
uploaded_file = st.file_uploader("📁 원본 Excel 파일 업로드 (.xlsx)", type=["xlsx"])

if uploaded_file is not None:
    try:
        result_df = process_excel(uploaded_file)

        output_filename = "Packing_Details_Output.xlsx"
        result_df.to_excel(output_filename, index=False)

        st.success("✅ 변환 완료! 아래 버튼으로 다운로드하세요.")
        with open(output_filename, "rb") as f:
            st.download_button("📥 결과 파일 다운로드", f, file_name=output_filename)
    except Exception as e:
        st.error(f"❌ 에러 발생: {e}")


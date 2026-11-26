import streamlit as st
from datetime import datetime
import pandas as pd

# 페이지 기본 설정
st.set_page_config(
    page_title="Lab Assistant: Cell & Drug Calculator",
    page_icon="🧪",
    layout="wide"
)

# 세션 상태 초기화
if "culture_log" not in st.session_state:
    st.session_state.culture_log = []

if "counting_log" not in st.session_state:
    st.session_state.counting_log = []

st.title("🧪 Lab Assistant: 세포 배양 & 약물 계산기")
st.caption("세포주 배양 관리 · Duplicate Counting 기록 & 필요 세포 계산 · 약물 희석 계산")

# 3개 탭 구성
tab1, tab2, tab3 = st.tabs([
    "📋 세포주 배양 관리",
    "🔢 Counting 기록 & 세포수 계산",
    "💊 약물 농도 & 희석 계산"
])

# ==============================================================================
# TAB 1: 세포주 배양 관리 (Viability & 분주된 세포수 추가본)
# ==============================================================================
with tab1:
    st.subheader("📋 세포주 배양 이력 관리")

    if "last_uploaded_file_id" not in st.session_state:
        st.session_state["last_uploaded_file_id"] = None

    # 과거 기록 CSV 파일 업로드 기능
    with st.expander("📂 이전 배양 기록(CSV) 불러오기", expanded=False):
        uploaded_culture_file = st.file_uploader(
            "예전에 다운로드한 배양 기록 CSV 파일을 업로드하세요",
            type=["csv"],
            key="cult_up"
        )
        if uploaded_culture_file is not None:
            current_file_id = f"{uploaded_culture_file.name}_{uploaded_culture_file.size}"
            if st.session_state["last_uploaded_file_id"] != current_file_id:
                try:
                    uploaded_culture_file.seek(0)
                    try:
                        df_load = pd.read_csv(uploaded_culture_file, encoding="utf-8-sig")
                    except UnicodeDecodeError:
                        uploaded_culture_file.seek(0)
                        df_load = pd.read_csv(uploaded_culture_file, encoding="cp949")

                    if df_load.empty:
                        st.warning("⚠️ 업로드한 CSV 파일에 데이터가 없습니다.")
                    else:
                        # 옛날 CSV 파일의 컬럼명이 다를 경우 현재 컬럼명으로 통일
                        if "배양 세포수" in df_load.columns and "배양 세포수 (cells/mL)" not in df_load.columns:
                            df_load = df_load.rename(columns={"배양 세포수": "배양 세포수 (cells/mL)"})
                        elif "배양 세포수" in df_load.columns and "배양 세포수 (cells/mL)" in df_load.columns:
                            df_load["배양 세포수 (cells/mL)"] = df_load["배양 세포수 (cells/mL)"].fillna(df_load["배양 세포수"])
                            df_load = df_load.drop(columns=["배양 세포수"])

                        records = df_load.fillna("").astype(str).to_dict(orient="records")
                        for rec in records:
                            rec["선택"] = False

                        st.session_state.culture_log = records
                        st.session_state["last_uploaded_file_id"] = current_file_id
                        st.success("✅ 이전 배양 기록을 성공적으로 불러왔습니다!")
                        st.rerun()
                except Exception as e:
                    st.error(f"⚠️ 파일을 읽는 중 오류가 발생했습니다: {type(e).__name__} - {e}")
        else:
            st.session_state["last_uploaded_file_id"] = None

    with st.expander("➕ 새 배양 기록 추가하기", expanded=True):
        c1, c2, c3 = st.columns(3)
        cell_line_options = ["Hs578T", "AGS", "SNU601", "HPAF-2", "HT-29", "JIMT-1", "B16F10", "직접 입력"]
        selected_cell = c1.selectbox("세포주 선택", cell_line_options, key="cult_cell_sel")

        if selected_cell == "직접 입력":
            m_cell = c1.text_input("직접 입력 세포주명", placeholder="예: RAW 264.7", key="cult_custom_cell")
        else:
            m_cell = selected_cell

        m_pass = c2.text_input("Passage", value="P12", key="cult_pass")
        m_date = c3.text_input("날짜", value=datetime.now().strftime("%Y-%m-%d"), key="cult_date")

        c4, c5 = st.columns(2)
        m_media = c4.text_input("배지 조건", value="DMEM + 10% FBS + 1% AA", key="cult_media")
        m_cultured_cells = c5.text_input("배양 세포수 (cells/mL)", value="1.00 × 10⁶ cells/mL", key="cult_cells")

        c6, c7 = st.columns(2)
        m_viability = c6.text_input("Viability (%)", value="95.0 %", key="cult_viability")
        m_seeded_cells = c7.text_input("분주된 세포수", value="5.00 × 10⁵ cells", key="cult_seeded")

        m_note = st.text_input("비고", placeholder="특이사항, 컨플루언시, 계대배양 비율 등", key="cult_note")

        if st.button("배양 기록 추가", type="primary", key="cult_submit_btn"):
            target_cell_name = m_cell if selected_cell == "직접 입력" else selected_cell
            if selected_cell == "직접 입력" and not m_cell:
                st.error("⚠️ 직접 입력할 세포주 이름을 입력해 주세요.")
            else:
                new_entry = {
                    "선택": False,
                    "날짜": str(m_date),
                    "세포주": str(target_cell_name),
                    "Passage": str(m_pass),
                    "배지 조건": str(m_media),
                    "배양 세포수 (cells/mL)": str(m_cultured_cells),
                    "Viability (%)": str(m_viability),
                    "분주된 세포수": str(m_seeded_cells),
                    "비고": str(m_note) if m_note else ""
                }
                if not isinstance(st.session_state.culture_log, list):
                    st.session_state.culture_log = []
                st.session_state.culture_log.insert(0, new_entry)
                st.success("✅ 배양 기록이 추가되었습니다!")
                st.rerun()

    st.markdown("---")
    st.markdown("### 📄 저장된 배양 기록")
    st.caption("💡 표 맨 앞의 **[선택]** 칸에 체크박스를 체크한 후, 아래의 **[🗑️ 체크한 행 삭제]** 버튼을 누르면 해당 행들이 지워집니다. 셀 더블클릭으로 직접 수정도 가능합니다.")

    if st.session_state.culture_log:
        for item in st.session_state.culture_log:
            if "선택" not in item:
                item["선택"] = False
            else:
                item["선택"] = bool(item["선택"]) if isinstance(item["선택"], bool) else str(item["선택"]).lower() == "true"

        df_out1 = pd.DataFrame(st.session_state.culture_log)

        desired_cols = [
            "선택",
            "날짜",
            "세포주",
            "Passage",
            "배지 조건",
            "배양 세포수 (cells/mL)",
            "Viability (%)",
            "분주된 세포수",
            "비고"
        ]
        for col in desired_cols:
            if col not in df_out1.columns:
                df_out1[col] = False if col == "선택" else ""
        df_out1 = df_out1[desired_cols]

        edited_df1 = st.data_editor(
            df_out1,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            column_config={
                "선택": st.column_config.CheckboxColumn("선택", default=False)
            },
            key="cult_data_editor_chk"
        )

        st.markdown("---")
        btn_c1, btn_c2 = st.columns([1, 3])

        with btn_c1:
            if st.button("🗑️ 체크한 행 삭제", type="primary", key="btn_del_checked"):
                remaining_logs = []
                deleted_count = 0
                for _, row in edited_df1.iterrows():
                    if bool(row["선택"]):
                        deleted_count += 1
                    else:
                        clean_row = {k: str(v) for k, v in row.drop(labels=["선택"]).to_dict().items()}
                        clean_row["선택"] = False
                        remaining_logs.append(clean_row)

                if deleted_count > 0:
                    st.session_state.culture_log = remaining_logs
                    st.success(f"🗑️ 선택한 {deleted_count}개의 기록이 삭제되었습니다!")
                    st.rerun()
                else:
                    st.warning("⚠️ 삭제할 행의 체크박스를 먼저 선택해 주세요.")

        with btn_c2:
            df_for_csv = edited_df1.drop(columns=["선택"]) if "선택" in edited_df1.columns else edited_df1
            csv1 = df_for_csv.to_csv(index=False).encode('utf-8-sig')

            st.download_button(
                label="📥 현재 배양 기록 CSV 다운로드",
                data=csv1,
                file_name=f"cell_culture_log_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

        current_data_check = edited_df1.drop(columns=["선택"]).astype(str).to_dict(orient="records")
        old_data_check = pd.DataFrame(st.session_state.culture_log).drop(columns=["선택"], errors="ignore").astype(str).to_dict(orient="records")

        if current_data_check != old_data_check:
            updated_logs = []
            for _, row in edited_df1.iterrows():
                clean_row = {k: str(v) for k, v in row.drop(labels=["선택"]).to_dict().items()}
                clean_row["선택"] = bool(row["선택"])
                updated_logs.append(clean_row)
            st.session_state.culture_log = updated_logs

    else:
        st.info("등록된 배양 기록이 없습니다. 새 기록을 추가하거나 CSV 파일을 불러와 보세요!")


# ==============================================================================
# TAB 2: Counting 기록지 & 필요 세포 수 계산기
# ==============================================================================
with tab2:
    st.subheader("1. Counting 결과 기록지 (Duplicate 순차 입력)")
    
    with st.expander("📂 이전 Counting 기록(CSV) 불러오기", expanded=False):
        uploaded_cnt_file = st.file_uploader("예전에 다운로드한 Counting 기록 CSV 파일을 업로드하세요", type=["csv"], key="cnt_up")
        if uploaded_cnt_file is not None:
            try:
                df_cnt_load = pd.read_csv(uploaded_cnt_file)
                st.session_state.counting_log = df_cnt_load.to_dict(orient="records")
                st.success("✅ 이전 Counting 기록을 성공적으로 불러왔습니다!")
            except Exception as e:
                st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")

    with st.expander("➕ Counting 결과 기록하기", expanded=True):
        fc1, fc2, fc3 = st.columns(3)
        cnt_date = fc1.text_input("날짜", value=datetime.now().strftime("%Y-%m-%d"), key="cnt_date_in")
        cnt_cell_opts = ["Hs578T", "AGS", "SNU601", "HPAF-2", "HT-29", "JIMT-1", "B16F10", "직접 입력"]
        selected_cnt_cell = fc2.selectbox("세포주", cnt_cell_opts, key="cnt_cell_box")
        if selected_cnt_cell == "직접 입력":
            cnt_cell = fc2.text_input("직접 입력 세포주명", placeholder="예: RAW 264.7", key="cnt_custom_cell")
        else:
            cnt_cell = selected_cnt_cell
        cnt_pass = fc3.text_input("Passage", value="P12", key="cnt_pass_box")
        
        st.markdown("---")
        
        st.markdown("🔹 **1회차 측정 (Count #1 & Viability #1)**")
        dc1, dc2 = st.columns(2)
        c1_val = dc1.number_input("Count #1 (×10⁶ cells/mL)", min_value=0.0, value=2.50, step=0.01, format="%.2f")
        v1_val = dc2.number_input("Viability #1 (%)", min_value=0.0, max_value=100.0, value=95.0, step=0.1, format="%.1f")
        
        st.markdown("")
        
        st.markdown("🔹 **2회차 측정 (Count #2 & Viability #2)** *(※ 1회만 측정한 경우 0으로 두세요)*")
        dc3, dc4 = st.columns(2)
        c2_val = dc3.number_input("Count #2 (×10⁶ cells/mL)", min_value=0.0, value=2.60, step=0.01, format="%.2f")
        v2_val = dc4.number_input("Viability #2 (%)", min_value=0.0, max_value=100.0, value=96.0, step=0.1, format="%.1f")

        st.markdown("---")
        cnt_note = st.text_input("비고", placeholder="예: 1:1 Trypan blue 희석", key="cnt_note_in")
        
        if st.button("Counting 기록 저장", type="primary", key="cnt_submit_btn"):
            if selected_cnt_cell == "직접 입력" and not cnt_cell:
                st.error("⚠️ 직접 입력할 세포주 이름을 입력해 주세요.")
            else:
                if c2_val > 0:
                    avg_c = (c1_val + c2_val) / 2.0
                    conc_display = f"{avg_c:.2f} × 10⁶ cells/mL (#1: {c1_val}, #2: {c2_val})"
                else:
                    avg_c = c1_val
                    conc_display = f"{avg_c:.2f} × 10⁶ cells/mL"

                if v2_val > 0:
                    avg_v = (v1_val + v2_val) / 2.0
                    viab_display = f"{avg_v:.1f}% (#1: {v1_val}%, #2: {v2_val}%)"
                else:
                    avg_v = v1_val
                    viab_display = f"{avg_v:.1f}%"

                cnt_entry = {
                    "날짜": str(cnt_date),
                    "세포주": str(cnt_cell),
                    "Passage": str(cnt_pass),
                    "평균 세포 농도": str(conc_display),
                    "평균 생존율": str(viab_display),
                    "raw_avg_conc": float(avg_c),
                    "비고": str(cnt_note) if cnt_note else ""
                }
                st.session_state.counting_log.insert(0, cnt_entry)
                st.success(f"✅ Counting 저장 완료! (평균 농도: {avg_c:.2f} × 10⁶ cells/mL)")
                st.rerun()

    if st.session_state.counting_log:
        st.markdown("### 📄 저장된 Counting 목록")
        
        df_out2 = pd.DataFrame(st.session_state.counting_log)
        if 'raw_avg_conc' in df_out2.columns:
            df_export2 = df_out2.drop(columns=['raw_avg_conc'])
        else:
            df_export2 = df_out2
            
        st.dataframe(df_export2, use_container_width=True, hide_index=True)

        csv2 = df_export2.to_csv(index=False).encode('utf-8-sig')
        
        st.markdown("---")
        cbtn1, cbtn2 = st.columns([1, 4])
        with cbtn1:
            st.download_button(
                label="📥 Counting 기록 CSV 다운로드",
                data=csv2,
                file_name=f"cell_counting_log_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        with cbtn2:
            if st.button("🗑️ Counting 기록 전체 초기화", key="cnt_clear_btn"):
                st.session_state.counting_log = []
                st.rerun()

    st.markdown("---")
    
    st.subheader("2. 필요 세포 수 & Medium 계산기")
    st.caption("측정된 평균 세포 농도와 Well당 분주 부피를 입력하면 필요한 세포 현탁액 및 배지(Medium) 부피를 계산합니다.")
    
    default_conc = 1.50
    if st.session_state.counting_log:
        try:
            default_conc = float(st.session_state.counting_log[0].get('raw_avg_conc', 1.50))
        except Exception:
            pass

    calc_c1, calc_c2 = st.columns(2)
    with calc_c1:
        measured_conc_val = st.number_input("측정된 세포 농도 (평균, × 10⁶ cells/mL)", min_value=0.01, value=default_conc, step=0.1, format="%.2f")
        vol_per_well_ml = st.number_input("Seeding에 필요한 Well당 부피 (Medium 량, mL)", min_value=0.05, value=1.0, step=0.1, format="%.2f")
    with calc_c2:
        cells_per_unit = st.number_input("Well당 필요한 세포 수 (cells/well)", min_value=100, value=100000, step=10000)
        num_units = st.number_input("필요한 Well 개수 (개)", min_value=1, value=10, step=1)

    conc_cells_per_ml = measured_conc_val * 1e6
    needed_total_cells = cells_per_unit * num_units
    needed_susp_vol_ml = (needed_total_cells / conc_cells_per_ml) if conc_cells_per_ml > 0 else 0
    total_medium_vol_ml = vol_per_well_ml * num_units
    fresh_medium_vol_ml = total_medium_vol_ml - needed_susp_vol_ml

    st.markdown("#### 📊 계산 결과")
    rm1, rm2, rm3, rm4 = st.columns(4)
    rm1.metric("필요한 총 세포 수", f"{needed_total_cells/1e6:.2f} × 10⁶ cells", f"{needed_total_cells:,.0f} cells")
    rm2.metric("취해야 할 세포 현탁액", f"{needed_susp_vol_ml * 1000:,.1f} μL", f"{needed_susp_vol_ml:.3f} mL")
    rm3.metric("총 부피 (총 Medium 량)", f"{total_medium_vol_ml:,.2f} mL", f"{total_medium_vol_ml * 1000:,.0f} μL")
    
    if fresh_medium_vol_ml >= 0:
        rm4.metric("추가할 새 Medium 부피", f"{fresh_medium_vol_ml:,.2f} mL", f"{fresh_medium_vol_ml * 1000:,.1f} μL")
    else:
        rm4.error("⚠️ 세포 농도가 낮아 현탁액 부피가 총 부피를 초과합니다. 원심분리 후 농축하세요.")


# ==============================================================================
# TAB 3: 약물 농도 & 희석 계산
# ==============================================================================
with tab3:
    st.subheader("1. 스톡 용액 희석 계산 (C1V1 = C2V2)")
    
    unit_map = {"M": 1.0, "mM": 1e-3, "μM": 1e-6, "nM": 1e-9}
    
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        c1_val = st.number_input("Stock 농도 (C1, mM 단위 권장)", min_value=0.0001, value=10.0, format="%.4f")
        c1_unit = st.selectbox("C1 단위", list(unit_map.keys()), index=1, key="c1_u")
    with d_col2:
        c2_val = st.number_input("목표 최종 농도 (C2)", min_value=0.0001, value=1.0, format="%.4f")
        c2_unit = st.selectbox("C2 단위", list(unit_map.keys()), index=2, key="c2_u")
        
    v2_col1, v2_col2 = st.columns(2)
    with v2_col1:
        v2_val = st.number_input("만들 최종 용액 부피 (V2)", min_value=0.001, value=5.0, format="%.2f")
    with v2_col2:
        v2_unit = st.selectbox("V2 부피 단위", ["μL", "mL"], index=1)

    c1_in_m = c1_val * unit_map[c1_unit]
    c2_in_m = c2_val * unit_map[c2_unit]
    v2_in_ul = v2_val if v2_unit == "μL" else v2_val * 1000.0

    if c1_in_m > 0:
        if c2_in_m > c1_in_m:
            st.error("⚠️ 목표 농도(C2)가 Stock 농도(C1)보다 높을 수 없습니다.")
        else:
            v1_in_ul = (c2_in_m * v2_in_ul) / c1_in_m
            solvent_in_ul = v2_in_ul - v1_in_ul
            dilution_ratio = c1_in_m / c2_in_m if c2_in_m > 0 else 0

            dm1, dm2, dm3 = st.columns(3)
            dm1.metric("필요한 Stock 부피 (V1)", f"{v1_in_ul:,.2f} μL", f"{v1_in_ul/1000:.4f} mL")
            dm2.metric("용매(Media/DMSO) 부피", f"{solvent_in_ul:,.2f} μL", f"{solvent_in_ul/1000:.4f} mL")
            dm3.metric("희석 배수 (Dilution Factor)", f"1 : {dilution_ratio:,.1f}")

    st.markdown("---")

    st.subheader("2. 분말 시약 Stock 제조 계산 (Molarity → Mass)")
    m_col1, m_col2, m_col3 = st.columns(3)
    with m_col1:
        mw = st.number_input("분자량 (Molecular Weight, g/mol)", min_value=0.1, value=300.0, format="%.2f")
    with m_col2:
        target_m_val = st.number_input("목표 Stock 농도", min_value=0.001, value=10.0, format="%.3f")
        target_m_unit = st.selectbox("Stock 농도 단위", ["M", "mM", "μM"], index=1)
    with m_col3:
        target_vol_ml = st.number_input("제조할 용액 부피 (mL)", min_value=0.01, value=10.0, format="%.2f")

    conc_m = target_m_val * unit_map[target_m_unit]
    vol_l = target_vol_ml / 1000.0
    mass_g = conc_m * vol_l * mw
    mass_mg = mass_g * 1000.0

    mm1, mm2 = st.columns(2)
    mm1.metric("필요한 시약 무게 (mg)", f"{mass_mg:,.3f} mg")
    mm2.metric("필요한 시약 무게 (μg)", f"{mass_mg * 1000:,.1f} μg")

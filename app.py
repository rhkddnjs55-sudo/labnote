# ==============================================================================
# TAB 1: 세포주 배양 관리 (CSV 업로드 로드 오류 수정본)
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
                    df_load = pd.read_csv(uploaded_culture_file)

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
                    st.error(f"파일을 읽는 중 오류가 발생했습니다: {e}")
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
                    "비고": str(m_note) if m_note else ""
                }
                if not isinstance(st.session_state.culture_log, list):
                    st.session_state.culture_log = []
                st.session_state.culture_log.insert(0, new_entry)
                st.success("✅ 배양 기록이 추가되었습니다!")
                st.rerun()

    st.markdown("---")
    st.markdown("### 📄 저장된 배양 기록")
    st.caption("💡 표 맨 앞의 **[선택]** 칸에 체크박스를 체크한 후, 아래의 **[🗑️ 체크한 행 삭제]** 버튼을 누르면 해당 행들이 지워집니다.")

    if st.session_state.culture_log:
        for item in st.session_state.culture_log:
            if "선택" not in item:
                item["선택"] = False
            else:
                item["선택"] = bool(item["선택"]) if isinstance(item["선택"], bool) else str(item["선택"]).lower() == "true"

        df_out1 = pd.DataFrame(st.session_state.culture_log)

        desired_cols = ["선택", "날짜", "세포주", "Passage", "배지 조건", "배양 세포수 (cells/mL)", "비고"]
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

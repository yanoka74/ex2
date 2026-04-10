import pandas as pd

REQUIRED_COLUMNS = ["마켓명", "판매자 고유코드", "상품명", "주문수량", "주문일"]

RESULT_COLUMNS = ["마켓명", "판매자 고유코드", "상품명", "주문수량 합계", "최근 주문일"]


def process_sales_data(file_path):
    """판매 데이터를 처리하여 고유코드+마켓별 집계 결과를 반환한다.

    Args:
        file_path: 엑셀 파일 경로 (.xlsx)

    Returns:
        tuple: (result_df, summary_dict)
            - result_df: 집계 결과 DataFrame
              컬럼: 마켓명, 판매자 고유코드, 상품명, 주문수량 합계, 최근 주문일
            - summary_dict: {"total_rows": int, "skipped_rows": int, "result_rows": int}

    Raises:
        ValueError: 필수 컬럼이 누락된 경우
    """
    df = pd.read_excel(file_path, engine="openpyxl")

    # 필수 컬럼 검증 (D-06, D-07)
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"필수 컬럼이 누락되었습니다: {', '.join(missing)}")

    total_rows = len(df)

    # 비정상 데이터 제외 (D-04, D-05)
    valid_df = df.copy()

    # 판매자 고유코드 또는 마켓명이 빈 행 제외
    valid_df = valid_df[
        valid_df["판매자 고유코드"].astype(str).str.strip().ne("")
        & valid_df["판매자 고유코드"].notna()
    ]
    valid_df = valid_df[
        valid_df["마켓명"].astype(str).str.strip().ne("")
        & valid_df["마켓명"].notna()
    ]

    # 주문수량을 숫자로 변환, 변환 불가한 행 제외
    valid_df = valid_df.assign(
        주문수량=pd.to_numeric(valid_df["주문수량"], errors="coerce")
    )
    valid_df = valid_df[valid_df["주문수량"].notna()]

    skipped_rows = total_rows - len(valid_df)

    # 주문일 변환
    valid_df = valid_df.assign(
        주문일=pd.to_datetime(valid_df["주문일"], errors="coerce")
    )

    # 집계 (D-01, D-02, D-03)
    def aggregate_group(group):
        latest_idx = group["주문일"].idxmax()
        return pd.Series({
            "마켓명": group.name[1],
            "판매자 고유코드": group.name[0],
            "상품명": group.loc[latest_idx, "상품명"],
            "주문수량 합계": group["주문수량"].sum(),
            "최근 주문일": group["주문일"].max(),
        })

    result = (
        valid_df
        .groupby(["판매자 고유코드", "마켓명"])
        .apply(aggregate_group, include_groups=False)
        .reset_index(drop=True)
    )

    # 결과 컬럼 순서 정렬 (D-03)
    result = result[RESULT_COLUMNS]

    summary = {
        "total_rows": total_rows,
        "skipped_rows": skipped_rows,
        "result_rows": len(result),
    }

    return result, summary

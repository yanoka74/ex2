"""Flask 웹 애플리케이션 - 판매정보 분석기.

엑셀 파일(.xlsx)을 업로드하면 판매자 고유코드 기준으로
중복을 제거하고 판매수량 합계를 테이블로 보여준다.
"""
import os
import tempfile

from flask import Flask, request, render_template

from src.processor import process_sales_data

app = Flask(__name__, template_folder="../templates")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB
app.secret_key = os.urandom(24)


@app.template_filter("comma")
def comma_filter(value):
    """천 단위 콤마 포맷: 1234 -> 1,234"""
    return f"{int(value):,}"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")

    if not file or file.filename == "":
        return render_template("index.html", error="파일을 선택해주세요.")

    if not file.filename.lower().endswith(".xlsx"):
        return render_template("index.html", error=".xlsx 파일만 업로드할 수 있습니다.")

    tmp = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False)
    try:
        file.save(tmp.name)
        tmp.close()
        result_df, summary = process_sales_data(tmp.name)

        unique_codes = len(result_df)
        rows = result_df.to_dict("records")

        return render_template(
            "index.html",
            results=rows,
            summary=summary,
            unique_codes=unique_codes,
        )
    except ValueError as e:
        return render_template("index.html", error=str(e))
    except Exception:
        return render_template(
            "index.html",
            error="파일 처리 중 오류가 발생했습니다. 다른 파일로 다시 시도해주세요.",
        )
    finally:
        os.unlink(tmp.name)


@app.errorhandler(413)
def too_large(e):
    return render_template("index.html", error="파일 크기가 너무 큽니다. (최대 16MB)"), 413

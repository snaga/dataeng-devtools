import snowflake.connector
import yaml
import csv
import sys
import argparse

def export_snowflake_to_csv(snowflake_table_name, output_file, snowflake_config_path="snowflake_config.yaml"):
    """
    SnowflakeテーブルのレコードをすべてSELECTし、CSV形式でファイルに出力する関数

    Args:
        snowflake_table_name (str): Snowflakeテーブル名 (DB.スキーマ.テーブル)
        output_file (str): 出力ファイルパス
        snowflake_config_path (str): Snowflake接続情報が記述されたYAMLファイルのパス
    """
    try:
        # YAMLファイルからSnowflake接続情報を読み込む
        with open(snowflake_config_path, "r") as yaml_file:
            snowflake_config = yaml.safe_load(yaml_file)

        # Snowflakeへの接続
        snowflake_conn = snowflake.connector.connect(**snowflake_config)
        snowflake_cursor = snowflake_conn.cursor()

        # SnowflakeテーブルのレコードをすべてSELECTするクエリ
        select_query = f"SELECT * FROM {snowflake_table_name}"
        snowflake_cursor.execute(select_query)
        data = snowflake_cursor.fetchall()
        column_names = [desc[0] for desc in snowflake_cursor.description]

        # CSV形式でファイルに出力
        with open(output_file, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(column_names)  # ヘッダーを書き込む
            writer.writerows(data)  # データを書き込む

    except snowflake.connector.Error as sf_error:
        print(f"Snowflakeエラー: {sf_error}", file=sys.stderr)
    except FileNotFoundError:
        print(f"エラー: {snowflake_config_path} ファイルが見つかりません。", file=sys.stderr)
    except yaml.YAMLError as yaml_error:
        print(f"YAMLエラー: {yaml_error}", file=sys.stderr)
    except IOError as io_error:
        print(f"IOエラー: {io_error}", file=sys.stderr)
    except Exception as e:
        print(f"予期しないエラー: {e}", file=sys.stderr)
    finally:
        # カーソルと接続をクローズ
        if "snowflake_conn" in locals() and snowflake_conn:
            snowflake_cursor.close()
            snowflake_conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SnowflakeテーブルのデータをCSV形式でファイルに出力するスクリプト")
    parser.add_argument("snowflake_table", help="Snowflakeテーブル名 (DB.スキーマ.テーブル)")
    parser.add_argument("output_file", help="出力ファイルパス")
    parser.add_argument("--config", default="snowflake_config.yaml", help="Snowflake接続情報が記述されたYAMLファイルのパス")
    args = parser.parse_args()

    export_snowflake_to_csv(args.snowflake_table, args.output_file, args.config)

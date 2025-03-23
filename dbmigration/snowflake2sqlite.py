import snowflake.connector
import yaml
import argparse

def schema_migration(snowflake_table_name, output_file, snowflake_config_path="snowflake_config.yaml"):
    """
    SnowflakeテーブルのメタデータからSQLiteテーブルのDDL文を生成し、ファイルに出力する関数

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

        # Snowflakeテーブルのメタデータを取得するクエリ
        metadata_query = f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_catalog || '.' || table_schema || '.' || table_name = '{snowflake_table_name}'
        """
        snowflake_cursor.execute(metadata_query)
        metadata = snowflake_cursor.fetchall()

        # SQLiteのDDL文を生成
        sqlite_ddl = f"CREATE TABLE IF NOT EXISTS {snowflake_table_name.split('.')[-1]} (\n"
        for column_name, data_type in metadata:
            # Snowflakeのデータ型をSQLiteのデータ型に変換
            sqlite_data_type = "TEXT"  # デフォルトはTEXT
            if "NUMBER" in data_type:
                sqlite_data_type = "INTEGER"
            elif "FLOAT" in data_type:
                sqlite_data_type = "REAL"
            elif "DATE" in data_type or "TIMESTAMP" in data_type:
                sqlite_data_type = "TEXT"  # SQLiteは日付型をTEXTで扱う

            sqlite_ddl += f"    {column_name} {sqlite_data_type},\n"
        sqlite_ddl = sqlite_ddl.rstrip(",\n") + "\n);"

        # DDL文をファイルに出力
        with open(output_file, "w", encoding="utf-8") as outfile:
            outfile.write(sqlite_ddl)

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
    parser = argparse.ArgumentParser(description="SnowflakeテーブルのメタデータからSQLiteテーブルのDDL文を生成するスクリプト")
    parser.add_argument("snowflake_table", help="Snowflakeテーブル名 (DB.スキーマ.テーブル)")
    parser.add_argument("output_file", help="出力ファイルパス")
    parser.add_argument("--config", default="snowflake_config.yaml", help="Snowflake接続情報が記述されたYAMLファイルのパス")
    args = parser.parse_args()

    schema_migration(args.snowflake_table, args.output_file, args.config)

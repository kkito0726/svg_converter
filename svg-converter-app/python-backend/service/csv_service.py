import os


class CsvService:
    @staticmethod
    def get_csvs(directory):
        return [f for f in os.listdir(directory) if f.endswith(".csv")]

    @staticmethod
    def delete_csv(csv_name):
        os.remove(f"./static/{csv_name}")

    @staticmethod
    def delete_all_csvs():
        delete_all_files_in_directory("./static")


def delete_all_files_in_directory(directory_path):
    # 指定したディレクトリ内のすべてのファイルを削除
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        try:
            if os.path.isfile(file_path):  # ファイルのみを削除
                os.remove(file_path)
            elif os.path.isdir(file_path):  # サブディレクトリも削除したい場合
                os.rmdir(file_path)  # 空のディレクトリのみ削除
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

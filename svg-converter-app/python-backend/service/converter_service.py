import os
from converter.svg2csv import svg2csv
from converter.svg_uploader import svg_upload
from converter.plot_csv import plot_csv
from converter.converter_response import ConverterResponse


class ConvertService:
    def convert(power: float, speed: int) -> ConverterResponse:
        svg_path = svg_upload()
        csv_local_path = svg2csv(svg_path, float(power), int(speed))
        plot_base64_image = plot_csv(csv_local_path, "gradation")

        delete_all_files_in_directory("./uploads")

        return ConverterResponse(
            f"http://localhost:5002{csv_local_path[1:]}", plot_base64_image
        )


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

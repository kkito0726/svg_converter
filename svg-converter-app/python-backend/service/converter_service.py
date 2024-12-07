import os

from converter.converter_response import ConverterResponse
from converter.plot_csv import plot_csv
from converter.svg_converter import svg_converter
from converter.svg_uploader import svg_upload
from service.csv_service import delete_all_files_in_directory


class ConvertService:
    @staticmethod
    def convert(power: float, speed: int) -> ConverterResponse:
        svg_path = svg_upload()
        csv_local_path = svg_converter(svg_path, float(power), int(speed))
        plot_base64_image = plot_csv(csv_local_path, "gradation")

        delete_all_files_in_directory("./uploads")

        return ConverterResponse(
            f"http://localhost:5002{csv_local_path[1:]}", plot_base64_image
        )

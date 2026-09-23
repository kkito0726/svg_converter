import io
from typing import IO

from converter.converter_response import ConverterResponse
from converter.plot_csv import plot_csv
from converter.svg_converter import csv_file_name, svg_converter


class ConvertService:
    @staticmethod
    def convert(
        svg_stream: IO[bytes], svg_file_name: str, power: float, speed: int
    ) -> ConverterResponse:
        # 変換結果はすべてメモリ上で扱い、サーバーには何も保存しない
        csv_text = svg_converter(svg_stream, power, speed)
        plot_base64_image = plot_csv(io.StringIO(csv_text), "gradation")

        return ConverterResponse(
            csv_name=csv_file_name(svg_file_name, power, speed),
            csv_text=csv_text,
            plot_base64_image=plot_base64_image,
        )

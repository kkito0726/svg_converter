import io
import time
from typing import IO

import structlog

from converter.converter_response import ConverterResponse
from converter.plot_csv import plot_csv
from converter.svg_converter import csv_file_name, svg_converter
from stream_utils import stream_size

logger = structlog.get_logger(__name__)


def _elapsed_ms(started: float, finished: float) -> int:
    return round((finished - started) * 1000)


class ConvertService:
    @staticmethod
    def convert(
        svg_stream: IO[bytes], svg_file_name: str, power: float, speed: int
    ) -> ConverterResponse:
        # 変換結果はすべてメモリ上で扱い、サーバーには何も保存しない
        svg_bytes = stream_size(svg_stream)
        started = time.perf_counter()
        csv_text = svg_converter(svg_stream, power, speed)
        converted = time.perf_counter()
        plot_base64_image = plot_csv(io.StringIO(csv_text), "gradation")
        plotted = time.perf_counter()

        logger.info(
            "convert.completed",
            svg_bytes=svg_bytes,
            power=power,
            speed=speed,
            svg2csv_ms=_elapsed_ms(started, converted),
            plot_ms=_elapsed_ms(converted, plotted),
            csv_bytes=len(csv_text.encode()),
        )

        return ConverterResponse(
            csv_name=csv_file_name(svg_file_name, power, speed),
            csv_text=csv_text,
            plot_base64_image=plot_base64_image,
        )

from converter.svg2csv import svg2csv
from converter.svg_uploader import svg_upload
from converter.plot_csv import plot_csv
from repository.minio_repository import MinioRepository
from converter.converter_response import ConverterResponse


class ConvertService:
    def convert(power: float, speed: int) -> ConverterResponse:
        svg_path = svg_upload()
        csv_local_path, csv_buf = svg2csv(svg_path, float(power), int(speed))
        plot_base64_image = plot_csv(csv_local_path, "gradation")

        csv_url = MinioRepository.save_csv(csv_buf)

        return ConverterResponse(csv_url, plot_base64_image)

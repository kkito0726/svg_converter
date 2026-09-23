from dataclasses import dataclass


@dataclass(frozen=True)
class ConverterResponse:
    csv_name: str
    csv_text: str
    plot_base64_image: str

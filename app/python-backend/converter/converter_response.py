class ConverterResponse:
    def __init__(self, csv_url, plot_base64_image) -> None:
        self.csv_url = csv_url
        self.plot_base64_image = plot_base64_image

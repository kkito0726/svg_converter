export type ConverterResponse = {
  csv_name: string;
  csv_text: string;
  plot_base64_image: string;
};

export type ConverterErrorResponse = {
  error: string;
};

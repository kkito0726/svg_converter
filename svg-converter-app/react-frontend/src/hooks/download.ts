export const handleDownloadCSV = (csv_url: string) => {
  const link = document.createElement("a");
  link.href = csv_url;
  link.download = csv_url.split("/").pop() || "data.csv"; // Change the file name and extension to .csv
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

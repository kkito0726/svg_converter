export const handleDownloadCSV = (csvUrl: string, fileName: string) => {
  const link = document.createElement("a");
  link.href = csvUrl;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

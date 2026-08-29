import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const paths = process.argv.slice(2);
for (const path of paths) {
  const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(path));
  const summary = await wb.inspect({
    kind: "workbook,sheet,table,region",
    maxChars: 30000,
    tableMaxRows: 100,
    tableMaxCols: 20,
    tableMaxCellChars: 300,
  });
  process.stdout.write(`\n=== ${path} ===\n${summary.ndjson}\n`);
}

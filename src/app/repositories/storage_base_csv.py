from pathlib import Path
import csv
from typing import List, Dict, Any


class CSVStorage:
    def __init__(self, path: Path, fieldnames: List[str]):
        self.path = path
        self.fieldnames = fieldnames

        if not self.path.exists():
            with open(self.path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=self.fieldnames)
                writer.writeheader()
    
    #returns all rows
    def read_all(self) -> List[Dict[str, Any]]:
        with open(self.path, "r", newline="") as f:
            reader = csv.DictReader(f)
            return list(reader)

    #appends a new to the csv
    def write_row(self, row: Dict[str, Any]) -> None:
        with open(self.path, "a", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writerow(row)

    #finds the first row matching a given condition  
    def find_by(self, column: str, value: Any) -> Dict[str, Any] | None:
        rows = self.read_all()
        for row in rows:
            if row[column] == str(value):
                return row
        return None
    
    #rewrite entire csv file
    def overwrite(self, rows: List[Dict[str, Any]]) -> None:
        with open(self.path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
            writer.writerows(rows)
    
    #updates item with search
    def update(self, column: str, value: Any, new_data: Dict[str, Any]) -> bool:
        rows = self.read_all()
        updated = False

        for row in rows:
            if row[column] == str(value):
                row.update(new_data)
                updated = True

        if updated:
            self.overwrite(rows)
        return updated
    #deletes
    def delete(self, column, value):
        rows = self.read_all()
        rows = [row for row in rows if row[column] != str(value)]
        self.overwrite(rows)
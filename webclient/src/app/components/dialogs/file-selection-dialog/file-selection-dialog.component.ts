import { Component, OnInit, Inject } from '@angular/core';
import {
  MatDialog,
  MatDialogRef,
  MAT_DIALOG_DATA,
} from '@angular/material/dialog';

@Component({
  selector: 'app-file-selection-dialog',
  templateUrl: './file-selection-dialog.component.html',
  styleUrls: ['./file-selection-dialog.component.scss'],
})
export class FileSelectionDialogComponent implements OnInit {
  selectedFileName: string;
  exportDesitination: string;
  s3: boolean;
  constructor(public dialogRef: MatDialogRef<FileSelectionDialogComponent>, @Inject(MAT_DIALOG_DATA) public data: any) {
    this.s3 = data.s3;
    if(!this.s3) {
      this.exportDesitination= "local"
    }
  }

  ngOnInit(): void {}

  confirm() {
    this.dialogRef.close({
      filename: this.selectedFileName,
      exportDesitination: this.exportDesitination,
    });
  }

  cancel(): void {
    this.dialogRef.close();
  }
}
